"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileText,
  Sparkles,
  X,
  Loader2,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  RotateCcw,
  Key,
  Layers,
  StopCircle,
} from "lucide-react";

interface CustomUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (data: any) => void;
  serverKeyStatus: {
    hasGeminiKey: boolean;
    hasOpenaiKey: boolean;
  };
}

const SAMPLE_SCREENPLAY = `EPISODE NUMBER: Episode 1

**JULIANA (devastated):**
Start: (00:00.00) | End: (00:04.20)
I cannot marry you, Julian! You swore your loyalty to my father!

**GERALD (sneering):**
Start: (00:04.20) | End: (00:09.50)
Your father is ruined, and you are a pauper. Why would I wed a beggar?

**CLARISSA (mocking):**
Start: (00:09.50) | End: (00:15.00)
Look at her dress. She honestly thought she would become a Duchess today.

**ACTION:**
Start: (00:15.00) | End: (00:18.40)
Clarissa violently shoves Juliana back against the cathedral stone pillar.

**ALEXANDER (commanding):**
Start: (00:18.40) | End: (00:25.00)
Take your hands off my wife before I break your wrist where you stand.

**GERALD (shocked):**
Start: (00:25.00) | End: (00:30.50)
Your wife? Who do you think you are, crippled soldier?

**ALEXANDER (cold deadly):**
Start: (00:30.50) | End: (00:35.80)
Choose your next words with great care. They will be the last you ever speak in this city.
--- SCRIPT END ---`;

const VERCEL_MAX_BODY_BYTES = 4.5 * 1024 * 1024; // 4.5 MB (source: https://vercel.com/docs/functions/limitations)

async function fetchWith429Retry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  let attempt = 0;
  while (attempt <= maxRetries) {
    if (options.signal?.aborted) throw new Error("Operation cancelled by user.");
    const res = await fetch(url, options);
    if (res.status === 429 && attempt < maxRetries) {
      attempt++;
      const delayMs = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s backoff
      await new Promise((r) => setTimeout(r, delayMs));
      continue;
    }
    return res;
  }
  return fetch(url, options);
}

export default function CustomUploadModal({
  isOpen,
  onClose,
  onSuccess,
  serverKeyStatus,
}: CustomUploadModalProps) {
  const [activeTab, setActiveTab] = useState<"files" | "paste">("files");
  const [files, setFiles] = useState<File[]>([]);
  const [pastedText, setPastedText] = useState("");
  const [showTitle, setShowTitle] = useState("");
  const [showPremise, setShowPremise] = useState("");
  const [provider, setProvider] = useState<"gemini" | "openai" | "heuristic">(
    serverKeyStatus.hasGeminiKey ? "gemini" : serverKeyStatus.hasOpenaiKey ? "openai" : "gemini"
  );
  const [customApiKey, setCustomApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [progressStep, setProgressStep] = useState("");
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Partial execution state for failed episode handling & retries
  const [parsedEpisodes, setParsedEpisodes] = useState<any[]>([]);
  const [validCandidates, setValidCandidates] = useState<any[]>([]);
  const [failedEpisodes, setFailedEpisodes] = useState<Array<{ episode_number: number; error: string }>>([]);
  const [totalParsedBeats, setTotalParsedBeats] = useState<number>(0);

  const abortControllerRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles(selected);
      setErrorMessage(null);
    }
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const dropped = Array.from(e.dataTransfer.files);
      setFiles(dropped);
      setErrorMessage(null);
    }
  }

  function handleLoadSample() {
    setPastedText(SAMPLE_SCREENPLAY);
    setShowTitle("The Duke's Vengeance");
    setShowPremise("An abandoned bride is rescued at the altar by a mysterious scarred war hero.");
    setActiveTab("paste");
    setErrorMessage(null);
  }

  function handleCancelRun() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
    setProgressStep("Run cancelled by user.");
  }

  async function runOrchestration(episodesToProcess: any[], existingCandidates: any[] = []) {
    setIsLoading(true);
    setErrorMessage(null);
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    const currentValidCandidates = [...existingCandidates];
    const currentFailedEpisodes: Array<{ episode_number: number; error: string }> = [];

    // Step 2: Extraction per episode
    // Concurrency: Gemini defaults to 1 (free-tier bursts 429); OpenAI defaults to 4; Heuristic = 8
    const concurrency = provider === "gemini" ? 1 : provider === "openai" ? 4 : 8;
    const totalEps = episodesToProcess.length;
    let completedCount = 0;

    setProgressStep(
      `Extracting candidate promos from ${totalEps} episode(s) (concurrency: ${concurrency})...`
    );
    setProgressPercent(10);

    const queue = [...episodesToProcess];
    async function worker() {
      while (queue.length > 0) {
        if (signal.aborted) throw new Error("Operation cancelled by user.");
        const ep = queue.shift();
        if (!ep) break;

        try {
          const res = await fetchWith429Retry(
            "/api/pipeline/extract",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                episode: ep,
                provider,
                apiKey: customApiKey.trim() || undefined,
                showTitle: showTitle.trim() || undefined,
                showPremise: showPremise.trim() || undefined,
              }),
              signal,
            },
            3
          );

          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || `HTTP ${res.status}`);
          }

          const data = await res.json();
          if (data.candidates && Array.isArray(data.candidates)) {
            currentValidCandidates.push(...data.candidates);
          }
        } catch (err: any) {
          if (signal.aborted) throw err;
          // Failed episode is recorded and NEVER treated as empty or passed
          currentFailedEpisodes.push({
            episode_number: ep.episode_number,
            error: err?.message || String(err),
          });
        } finally {
          completedCount++;
          const pct = Math.min(75, 10 + Math.round((completedCount / totalEps) * 65));
          setProgressPercent(pct);
          setProgressStep(
            `Extracted Ep ${ep.episode_number} (${completedCount}/${totalEps} processed${
              currentFailedEpisodes.length > 0 ? `, ${currentFailedEpisodes.length} failed` : ""
            })...`
          );
        }
      }
    }

    try {
      const workers = Array.from({ length: Math.min(concurrency, totalEps) }, () => worker());
      await Promise.all(workers);

      setValidCandidates(currentValidCandidates);
      setFailedEpisodes(currentFailedEpisodes);

      if (currentFailedEpisodes.length > 0 && currentValidCandidates.length === 0) {
        setIsLoading(false);
        setErrorMessage(
          `Extraction failed on ${currentFailedEpisodes.length} episode(s). Check API limits or retry below.`
        );
        return;
      }

      // Step 3: Candidate Audit in small batches (2-3 per call)
      setProgressStep(`Auditing ${currentValidCandidates.length} candidate(s)...`);
      setProgressPercent(80);

      const auditedCandidates: any[] = [];
      const batchSize = 3;
      for (let i = 0; i < currentValidCandidates.length; i += batchSize) {
        if (signal.aborted) throw new Error("Operation cancelled by user.");
        const batch = currentValidCandidates.slice(i, i + batchSize);

        const auditRes = await fetchWith429Retry(
          "/api/pipeline/audit",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              candidates: batch,
              episodes: episodesToProcess,
              provider,
              apiKey: customApiKey.trim() || undefined,
              showTitle: showTitle.trim() || undefined,
              showPremise: showPremise.trim() || undefined,
            }),
            signal,
          },
          3
        );

        if (!auditRes.ok) {
          // If audit fails, mark as unaudited instead of failing run
          batch.forEach((c) => {
            c.quality_audit = {
              passed: false,
              method: "error",
              critique: `Audit call returned HTTP ${auditRes.status}`,
              confidence_score: 0,
              risks: ["unaudited_due_to_api_error"],
            };
            c.audit_tier = 3;
          });
          auditedCandidates.push(...batch);
        } else {
          const auditData = await auditRes.json();
          auditedCandidates.push(...(auditData.audited_candidates || batch));
        }
      }

      // Step 4: Deterministic Rank
      setProgressStep("Finalizing diversity ranking...");
      setProgressPercent(95);

      const rankRes = await fetch("/api/pipeline/rank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidates: auditedCandidates,
          topK: 15,
        }),
        signal,
      });

      if (!rankRes.ok) {
        throw new Error("Ranking failed.");
      }

      const rankData = await rankRes.json();
      setProgressPercent(100);
      setProgressStep("Complete!");

      setTimeout(() => {
        setIsLoading(false);
        onSuccess({
          show_title: showTitle.trim() || "Custom Screenplay",
          episodes_analyzed: episodesToProcess.length,
          total_beats: totalParsedBeats,
          ranked_promos: rankData.ranked_promos || [],
          failed_episodes: currentFailedEpisodes,
          meta: {
            provider,
            model: provider === "gemini" ? "gemini-2.5-flash" : provider === "openai" ? "gpt-4o-mini" : "heuristic",
          },
        });
        onClose();
      }, 400);
    } catch (err: any) {
      setIsLoading(false);
      if (signal.aborted) {
        setProgressStep("Run cancelled by user.");
      } else {
        setErrorMessage(err?.message || "Execution failed.");
      }
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage(null);
    setFailedEpisodes([]);

    // Check Vercel 4.5 MB request body limit
    if (activeTab === "files") {
      if (files.length === 0) {
        setErrorMessage("Please select at least one .txt screenplay file or a .zip archive.");
        return;
      }
      const totalSize = files.reduce((acc, f) => acc + f.size, 0);
      if (totalSize > VERCEL_MAX_BODY_BYTES) {
        setErrorMessage(
          `Total upload size (${(totalSize / 1024 / 1024).toFixed(1)} MB) exceeds Vercel's 4.5 MB request limit (source: https://vercel.com/docs/functions/limitations). Please split your zip file into smaller batches or paste individual scripts.`
        );
        return;
      }
    } else if (activeTab === "paste" && !pastedText.trim()) {
      setErrorMessage("Please paste screenplay text formatted with timestamps.");
      return;
    }

    setIsLoading(true);
    setProgressStep("Uploading and parsing screenplay beats...");
    setProgressPercent(5);
    abortControllerRef.current = new AbortController();

    try {
      const formData = new FormData();
      if (activeTab === "files") {
        for (const file of files) {
          formData.append("files", file);
        }
      } else {
        formData.append("screenplayText", pastedText.trim());
      }

      const parseRes = await fetch("/api/pipeline/parse", {
        method: "POST",
        body: formData,
        signal: abortControllerRef.current.signal,
      });

      if (!parseRes.ok) {
        const errData = await parseRes.json().catch(() => ({}));
        throw new Error(errData.error || `Parsing failed with HTTP ${parseRes.status}`);
      }

      const parseData = await parseRes.json();
      const eps = parseData.episodes || [];
      if (eps.length === 0) {
        throw new Error("No episodes could be parsed from upload.");
      }

      setParsedEpisodes(eps);
      setTotalParsedBeats(parseData.total_beats || 0);

      // Begin browser orchestration across parsed episodes
      await runOrchestration(eps, []);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err?.message || "Failed to start analysis.");
    }
  }

  async function handleRetryFailed() {
    if (failedEpisodes.length === 0 || parsedEpisodes.length === 0) return;
    const failedEpNums = new Set(failedEpisodes.map((f) => f.episode_number));
    const epsToRetry = parsedEpisodes.filter((e) => failedEpNums.has(e.episode_number));
    await runOrchestration(epsToRetry, validCandidates);
  }

  async function handleViewPartial() {
    if (validCandidates.length === 0) return;
    setIsLoading(true);
    setProgressStep("Ranking partial candidate set...");

    try {
      const rankRes = await fetch("/api/pipeline/rank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidates: validCandidates,
          topK: 15,
        }),
      });

      const rankData = await rankRes.json();
      onSuccess({
        show_title: showTitle.trim() || "Custom Screenplay (Partial)",
        episodes_analyzed: parsedEpisodes.length - failedEpisodes.length,
        total_beats: totalParsedBeats,
        ranked_promos: rankData.ranked_promos || [],
        failed_episodes: failedEpisodes,
        meta: {
          provider,
          model: provider === "gemini" ? "gemini-2.5-flash" : provider === "openai" ? "gpt-4o-mini" : "heuristic",
          is_partial: true,
        },
      });
      onClose();
    } catch (err: any) {
      setErrorMessage("Failed to rank partial candidates.");
    } finally {
      setIsLoading(false);
    }
  }

  const isServerKeyActive =
    (provider === "gemini" && serverKeyStatus.hasGeminiKey) ||
    (provider === "openai" && serverKeyStatus.hasOpenaiKey);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(18, 20, 23, 0.65)",
        backdropFilter: "blur(4px)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--s-16)",
      }}
    >
      <div
        className="no-scrollbar"
        style={{
          background: "var(--surface)",
          border: "1px solid var(--hairline)",
          borderRadius: "var(--radius-xl)",
          maxWidth: 680,
          width: "100%",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: "var(--s-24)",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.2)",
          position: "relative",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--s-20)" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <span
                style={{
                  background: "var(--ai-gradient)",
                  color: "#fff",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  fontSize: 11,
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <Sparkles size={12} /> Custom Pipeline
              </span>
              <span style={{ fontSize: 12, color: "var(--ink-3)" }}>Browser-Orchestrated Run</span>
            </div>
            <h2 className="om-title-large" style={{ margin: 0, color: "var(--ink)" }}>
              Analyze Custom Screenplays
            </h2>
            <p className="om-subhead" style={{ margin: "4px 0 0", color: "var(--ink-2)", fontSize: 13 }}>
              Stepwise execution across parse, per-episode extract, chunked audit, and diversity rank.
            </p>
          </div>
          <button
            onClick={isLoading ? handleCancelRun : onClose}
            style={{
              padding: "6px 8px",
              background: "var(--sunken)",
              border: "none",
              borderRadius: "var(--radius-full)",
              color: "var(--ink-3)",
              cursor: "pointer",
            }}
            title={isLoading ? "Cancel running execution" : "Close modal"}
          >
            <X size={16} />
          </button>
        </div>

        {/* Tab Selector */}
        <div
          style={{
            display: "flex",
            gap: 4,
            background: "var(--sunken)",
            padding: 4,
            borderRadius: "var(--radius-md)",
            marginBottom: "var(--s-20)",
          }}
        >
          <button
            type="button"
            onClick={() => setActiveTab("files")}
            disabled={isLoading}
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              padding: "8px 12px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: activeTab === "files" ? "var(--surface)" : "transparent",
              color: activeTab === "files" ? "var(--ink)" : "var(--ink-3)",
              fontWeight: activeTab === "files" ? 600 : 400,
              cursor: isLoading ? "not-allowed" : "pointer",
              boxShadow: activeTab === "files" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              fontSize: 13,
            }}
          >
            <UploadCloud size={16} />
            <span>Upload Files / ZIP</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("paste")}
            disabled={isLoading}
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              padding: "8px 12px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: activeTab === "paste" ? "var(--surface)" : "transparent",
              color: activeTab === "paste" ? "var(--ink)" : "var(--ink-3)",
              fontWeight: activeTab === "paste" ? 600 : 400,
              cursor: isLoading ? "not-allowed" : "pointer",
              boxShadow: activeTab === "paste" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              fontSize: 13,
            }}
          >
            <FileText size={16} />
            <span>Paste Screenplay</span>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* File Upload Tab */}
          {activeTab === "files" && (
            <div style={{ marginBottom: "var(--s-20)" }}>
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: "2px dashed var(--hairline)",
                  borderRadius: "var(--radius-lg)",
                  padding: "var(--s-24)",
                  textAlign: "center",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  background: "var(--paper)",
                  transition: "border-color 0.15s ease",
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".txt,.zip"
                  onChange={handleFileChange}
                  disabled={isLoading}
                  style={{ display: "none" }}
                />
                <UploadCloud size={32} style={{ color: "var(--accent)", margin: "0 auto var(--s-8)" }} />
                <p className="om-body-strong" style={{ margin: "0 0 4px", color: "var(--ink)" }}>
                  Click to select or drag and drop
                </p>
                <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                  Supports multiple <code>.txt</code> files or a single <code>.zip</code> archive (max 4.5 MB on Vercel)
                </p>
              </div>

              {files.length > 0 && (
                <div style={{ marginTop: "var(--s-12)", display: "flex", flexDirection: "column", gap: 4 }}>
                  <span className="om-caption" style={{ color: "var(--ink-2)", fontWeight: 600 }}>
                    Selected ({files.length} file{files.length > 1 ? "s" : ""}, total{" "}
                    {(files.reduce((a, f) => a + f.size, 0) / 1024).toFixed(1)} KB):
                  </span>
                  <div style={{ maxHeight: 90, overflowY: "auto", display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {files.map((f, i) => (
                      <span
                        key={i}
                        className="om-tag"
                        style={{ background: "var(--sunken)", fontSize: 11, color: "var(--ink-2)" }}
                      >
                        📄 {f.name} ({(f.size / 1024).toFixed(0)} KB)
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Paste Tab */}
          {activeTab === "paste" && (
            <div style={{ marginBottom: "var(--s-20)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <label className="om-caption" style={{ color: "var(--ink-2)", fontWeight: 600 }}>
                  Screenplay Text (with timestamps):
                </label>
                <button
                  type="button"
                  onClick={handleLoadSample}
                  disabled={isLoading}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: isLoading ? "not-allowed" : "pointer",
                    textDecoration: "underline",
                  }}
                >
                  Load Sample Scene
                </button>
              </div>
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                disabled={isLoading}
                placeholder={`EPISODE NUMBER: Episode 1\n\n**JULIANA (devastated):**\nStart: (00:00.00) | End: (00:04.20)\nI cannot marry you, Julian!`}
                style={{
                  width: "100%",
                  minHeight: 180,
                  fontFamily: "monospace",
                  fontSize: 12,
                  lineHeight: "1.5",
                  padding: "var(--s-12)",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--hairline)",
                  background: "var(--paper)",
                  color: "var(--ink)",
                  resize: "vertical",
                }}
              />
            </div>
          )}

          {/* Show Context Metadata */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--s-12)", marginBottom: "var(--s-20)" }}>
            <div>
              <label className="om-caption" style={{ display: "block", fontWeight: 600, marginBottom: 4, color: "var(--ink)" }}>
                Show Title (optional):
              </label>
              <input
                type="text"
                value={showTitle}
                onChange={(e) => setShowTitle(e.target.value)}
                disabled={isLoading}
                placeholder="e.g. Broken Soldier"
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--hairline)",
                  background: "var(--paper)",
                  fontSize: 13,
                  color: "var(--ink)",
                }}
              />
            </div>
            <div>
              <label className="om-caption" style={{ display: "block", fontWeight: 600, marginBottom: 4, color: "var(--ink)" }}>
                Show Premise (optional):
              </label>
              <input
                type="text"
                value={showPremise}
                onChange={(e) => setShowPremise(e.target.value)}
                disabled={isLoading}
                placeholder="e.g. Revenge & secret identity"
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--hairline)",
                  background: "var(--paper)",
                  fontSize: 13,
                  color: "var(--ink)",
                }}
              />
            </div>
          </div>

          {/* Execution Settings */}
          <div
            style={{
              background: "var(--sunken)",
              padding: "var(--s-16)",
              borderRadius: "var(--radius-lg)",
              marginBottom: "var(--s-20)",
            }}
          >
            <div style={{ marginBottom: "var(--s-12)" }}>
              <label className="om-caption" style={{ display: "block", fontWeight: 600, marginBottom: 6, color: "var(--ink)" }}>
                Model Provider:
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                <button
                  type="button"
                  onClick={() => setProvider("gemini")}
                  disabled={isLoading}
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "gemini" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "gemini" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: isLoading ? "not-allowed" : "pointer",
                    textAlign: "center",
                  }}
                >
                  ✨ Google Gemini
                </button>
                <button
                  type="button"
                  onClick={() => setProvider("openai")}
                  disabled={isLoading}
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "openai" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "openai" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: isLoading ? "not-allowed" : "pointer",
                    textAlign: "center",
                  }}
                >
                  ⚡ OpenAI
                </button>
                <button
                  type="button"
                  onClick={() => setProvider("heuristic")}
                  disabled={isLoading}
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "heuristic" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "heuristic" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: isLoading ? "not-allowed" : "pointer",
                    textAlign: "center",
                  }}
                >
                  🧪 Offline Heuristic
                </button>
              </div>
            </div>

            {/* Provider Notes & Concurrency */}
            <div style={{ marginBottom: 10 }}>
              {provider === "gemini" && (
                <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)", fontSize: 11 }}>
                  ℹ️ <strong>Gemini Runner:</strong> Concurrency is locked to 1 with patient retry on HTTP 429. Free-tier keys may encounter rate limits, so execution proceeds deliberately.
                </p>
              )}
              {provider === "openai" && (
                <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)", fontSize: 11 }}>
                  ℹ️ <strong>OpenAI Runner:</strong> Concurrency is set to 4 concurrent episode extractions.
                </p>
              )}
              {provider === "heuristic" && (
                <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)", fontSize: 11 }}>
                  💡 <strong>Offline Engine:</strong> Deterministic regex taxonomy matcher and hard constraint validator. 0 API calls, 0 cost.
                </p>
              )}
            </div>

            {/* API Key Status / Custom input */}
            {provider !== "heuristic" && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                  <label className="om-caption" style={{ color: "var(--ink-2)", display: "flex", alignItems: "center", gap: 4 }}>
                    <Key size={12} /> {provider.toUpperCase()} API Key:
                  </label>
                  {isServerKeyActive && !customApiKey && (
                    <span
                      style={{
                        fontSize: 11,
                        color: "var(--success-strong)",
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                        fontWeight: 600,
                      }}
                    >
                      <CheckCircle2 size={12} /> Using Vercel Server Key ({provider === "gemini" ? "GEMINI_API_KEY" : "OPENAI_API_KEY"})
                    </span>
                  )}
                </div>
                <input
                  type="password"
                  value={customApiKey}
                  onChange={(e) => setCustomApiKey(e.target.value)}
                  disabled={isLoading}
                  placeholder={
                    isServerKeyActive
                      ? "Optional: override server environment key for this request"
                      : `Enter your ${provider.toUpperCase()} API key`
                  }
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--hairline)",
                    background: "var(--paper)",
                    fontSize: 13,
                    color: "var(--ink)",
                  }}
                />
              </div>
            )}
          </div>

          {/* Failed Episodes Recovery Banner */}
          {failedEpisodes.length > 0 && !isLoading && (
            <div
              style={{
                background: "var(--warning-container)",
                color: "var(--warning-on-container)",
                padding: "var(--s-16)",
                borderRadius: "var(--radius-md)",
                marginBottom: "var(--s-16)",
                fontSize: 13,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600, marginBottom: 6 }}>
                <AlertTriangle size={16} />
                <span>{failedEpisodes.length} episode(s) failed extraction:</span>
              </div>
              <ul style={{ margin: "0 0 10px 20px", padding: 0, fontSize: 12 }}>
                {failedEpisodes.map((fe, idx) => (
                  <li key={idx}>
                    Episode {fe.episode_number}: <code>{fe.error}</code>
                  </li>
                ))}
              </ul>
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  type="button"
                  onClick={handleRetryFailed}
                  className="om-button om-button--compact"
                  style={{ background: "var(--surface)", color: "var(--ink)", display: "flex", alignItems: "center", gap: 4 }}
                >
                  <RotateCcw size={13} />
                  <span>Retry Failed Episodes</span>
                </button>
                {validCandidates.length > 0 && (
                  <button
                    type="button"
                    onClick={handleViewPartial}
                    className="om-button om-button--compact"
                    style={{ background: "var(--accent)", color: "#fff" }}
                  >
                    View Partial Results ({validCandidates.length} candidate{validCandidates.length > 1 ? "s" : ""})
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Error Notice */}
          {errorMessage && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: "var(--warning-container)",
                color: "var(--warning-on-container)",
                padding: "var(--s-12)",
                borderRadius: "var(--radius-md)",
                marginBottom: "var(--s-16)",
                fontSize: 13,
              }}
            >
              <AlertCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Progress Indicator */}
          {isLoading && (
            <div style={{ marginBottom: "var(--s-16)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6, fontSize: 12 }}>
                <span style={{ color: "var(--accent)", fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
                  <Loader2 size={14} className="animate-spin" />
                  {progressStep}
                </span>
                <span className="om-num" style={{ color: "var(--ink-2)", fontWeight: 600 }}>
                  {progressPercent}%
                </span>
              </div>
              <div style={{ background: "var(--sunken)", height: 6, borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                <div
                  style={{
                    background: "var(--accent)",
                    height: "100%",
                    width: `${progressPercent}%`,
                    transition: "width 0.3s ease",
                  }}
                />
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--s-12)", alignItems: "center" }}>
            {isLoading ? (
              <button
                type="button"
                onClick={handleCancelRun}
                className="om-button om-button--compact"
                style={{
                  padding: "8px 16px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--warning-strong)",
                  background: "var(--surface)",
                  color: "var(--warning-strong)",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <StopCircle size={15} />
                <span>Cancel Run</span>
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={onClose}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--hairline)",
                    background: "var(--surface)",
                    color: "var(--ink-2)",
                    fontSize: 13,
                    fontWeight: 500,
                    cursor: "pointer",
                  }}
                >
                  Close
                </button>
                <button
                  type="submit"
                  style={{
                    padding: "8px 20px",
                    borderRadius: "var(--radius-sm)",
                    border: "none",
                    background: "var(--ai-gradient)",
                    color: "#fff",
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    boxShadow: "0 2px 8px rgba(11, 61, 145, 0.25)",
                  }}
                >
                  <Sparkles size={14} />
                  <span>Run Analysis</span>
                </button>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
