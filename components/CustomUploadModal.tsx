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
  HelpCircle,
  Key,
  Layers,
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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMessage(null);

    if (activeTab === "files" && files.length === 0) {
      setErrorMessage("Please select at least one .txt screenplay file or a .zip archive.");
      return;
    }
    if (activeTab === "paste" && !pastedText.trim()) {
      setErrorMessage("Please paste screenplay text formatted with timestamps.");
      return;
    }

    setIsLoading(true);
    setProgressStep("Uploading and parsing screenplay beats...");

    try {
      const formData = new FormData();
      formData.append("provider", provider);
      if (showTitle.trim()) formData.append("showTitle", showTitle.trim());
      if (showPremise.trim()) formData.append("showPremise", showPremise.trim());
      if (customApiKey.trim()) formData.append("apiKey", customApiKey.trim());

      if (activeTab === "files") {
        for (const file of files) {
          formData.append("files", file);
        }
      } else {
        formData.append("screenplayText", pastedText.trim());
      }

      setProgressStep(
        provider === "heuristic"
          ? "Running offline heuristic extraction & rule checks..."
          : `Running ${provider.toUpperCase()} LLM extraction & adversarial quality audit...`
      );

      const res = await fetch("/api/pipeline/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        throw new Error(data.error || "Failed to analyze screenplays");
      }

      setProgressStep("Finalizing MMR diversity ranking...");
      setTimeout(() => {
        setIsLoading(false);
        onSuccess(data);
        onClose();
      }, 500);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || "Failed to run pipeline. Check format or API key.");
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
              <span style={{ fontSize: 12, color: "var(--ink-3)" }}>Screenplay Ingestion</span>
            </div>
            <h2 className="om-title-large" style={{ margin: 0, color: "var(--ink)" }}>
              Upload Custom Screenplay
            </h2>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            style={{
              background: "none",
              border: "none",
              cursor: isLoading ? "not-allowed" : "pointer",
              color: "var(--ink-2)",
              padding: 4,
              borderRadius: "var(--radius-full)",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Input Mode Tabs */}
        <div
          style={{
            display: "flex",
            background: "var(--sunken)",
            padding: 4,
            borderRadius: "var(--radius-md)",
            marginBottom: "var(--s-20)",
            gap: 4,
          }}
        >
          <button
            type="button"
            onClick={() => setActiveTab("files")}
            style={{
              flex: 1,
              padding: "8px 16px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: activeTab === "files" ? "var(--surface)" : "transparent",
              color: activeTab === "files" ? "var(--ink)" : "var(--ink-2)",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer",
              boxShadow: activeTab === "files" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 6,
            }}
          >
            <UploadCloud size={16} /> Upload Files / ZIP
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("paste")}
            style={{
              flex: 1,
              padding: "8px 16px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              background: activeTab === "paste" ? "var(--surface)" : "transparent",
              color: activeTab === "paste" ? "var(--ink)" : "var(--ink-2)",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer",
              boxShadow: activeTab === "paste" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 6,
            }}
          >
            <FileText size={16} /> Paste Screenplay
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
                  padding: "var(--s-32) var(--s-16)",
                  textAlign: "center",
                  cursor: "pointer",
                  background: "var(--paper)",
                  transition: "border-color 0.15s ease",
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".txt,.md,.zip"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
                <UploadCloud size={32} style={{ color: "var(--accent)", margin: "0 auto var(--s-8)" }} />
                <p className="om-body-strong" style={{ margin: "0 0 4px", color: "var(--ink)" }}>
                  Click to choose or drag &amp; drop screenplays
                </p>
                <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                  Supports multiple <strong>.txt</strong> files or a <strong>.zip</strong> archive of microdrama episodes
                </p>
              </div>

              {files.length > 0 && (
                <div style={{ marginTop: "var(--s-12)", background: "var(--sunken)", padding: "var(--s-12)", borderRadius: "var(--radius-md)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span className="om-caption" style={{ fontWeight: 600, color: "var(--ink-2)" }}>
                      Selected files ({files.length}):
                    </span>
                    <button
                      type="button"
                      onClick={() => setFiles([])}
                      style={{ background: "none", border: "none", color: "var(--accent)", fontSize: 11, cursor: "pointer" }}
                    >
                      Clear
                    </button>
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: "var(--ink-2)", maxHeight: 100, overflowY: "auto" }}>
                    {files.slice(0, 10).map((f, i) => (
                      <li key={i}>{f.name} ({(f.size / 1024).toFixed(1)} KB)</li>
                    ))}
                    {files.length > 10 && <li>...and {files.length - 10} more</li>}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Paste Screenplay Tab */}
          {activeTab === "paste" && (
            <div style={{ marginBottom: "var(--s-20)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <label className="om-caption" style={{ fontWeight: 600, color: "var(--ink-2)" }}>
                  Paste Screenplay with Timestamps:
                </label>
                <button
                  type="button"
                  onClick={handleLoadSample}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    textDecoration: "underline",
                  }}
                >
                  Load Sample Episode
                </button>
              </div>
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder={`**SPEAKER (emotion):**\nStart: (00:00.00) | End: (00:04.20)\nText here...`}
                rows={8}
                style={{
                  width: "100%",
                  fontFamily: "monospace",
                  fontSize: 12,
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

          {/* Show Context Inputs */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--s-12)", marginBottom: "var(--s-20)" }}>
            <div>
              <label className="om-caption" style={{ display: "block", marginBottom: 4, color: "var(--ink-2)" }}>
                Show Title (optional)
              </label>
              <input
                type="text"
                value={showTitle}
                onChange={(e) => setShowTitle(e.target.value)}
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
              <label className="om-caption" style={{ display: "block", marginBottom: 4, color: "var(--ink-2)" }}>
                Genre / Premise (optional)
              </label>
              <input
                type="text"
                value={showPremise}
                onChange={(e) => setShowPremise(e.target.value)}
                placeholder="e.g. Secret billionaire, revenge"
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

          {/* Model Provider & API Key Configuration */}
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
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "gemini" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "gemini" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    textAlign: "center",
                  }}
                >
                  ✨ Google Gemini
                </button>
                <button
                  type="button"
                  onClick={() => setProvider("openai")}
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "openai" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "openai" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    textAlign: "center",
                  }}
                >
                  ⚡ OpenAI
                </button>
                <button
                  type="button"
                  onClick={() => setProvider("heuristic")}
                  style={{
                    padding: "8px 10px",
                    borderRadius: "var(--radius-sm)",
                    border: provider === "heuristic" ? "2px solid var(--accent)" : "1px solid var(--hairline)",
                    background: provider === "heuristic" ? "var(--surface)" : "transparent",
                    color: "var(--ink)",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    textAlign: "center",
                  }}
                >
                  🧪 Offline Heuristic
                </button>
              </div>
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
                  placeholder={
                    isServerKeyActive
                      ? "Optional: override Vercel server environment key with your own"
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

            {provider === "heuristic" && (
              <p className="om-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                💡 Runs the deterministic regex taxonomy matcher and hard constraint validator with 0 API calls and 0 cost. Ideal for testing custom screenplay layouts.
              </p>
            )}
          </div>

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

          {/* Submit Action */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--s-12)", alignItems: "center" }}>
            {isLoading && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--accent)", fontSize: 13, fontWeight: 500 }}>
                <Loader2 size={16} className="animate-spin" />
                <span>{progressStep}</span>
              </div>
            )}
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              style={{
                padding: "8px 16px",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--hairline)",
                background: "var(--surface)",
                color: "var(--ink-2)",
                fontSize: 13,
                fontWeight: 500,
                cursor: isLoading ? "not-allowed" : "pointer",
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              style={{
                padding: "8px 20px",
                borderRadius: "var(--radius-sm)",
                border: "none",
                background: "var(--ai-gradient)",
                color: "#fff",
                fontSize: 13,
                fontWeight: 600,
                cursor: isLoading ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: 6,
                boxShadow: "0 2px 8px rgba(11, 61, 145, 0.25)",
              }}
            >
              <Sparkles size={14} />
              {isLoading ? "Analyzing..." : "Run Analysis"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
