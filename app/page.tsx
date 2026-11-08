"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import {
  Sparkles,
  Play,
  Copy,
  Check,
  Search,
  Filter,
  Layers,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  SlidersHorizontal,
  Table as TableIcon,
  LayoutGrid,
  X,
  RotateCcw,
  UploadCloud,
  Download,
  FileText,
  ChevronDown,
  ChevronUp,
  Loader2,
  Scissors,
} from "lucide-react";
import CustomUploadModal from "@/components/CustomUploadModal";

interface Promo {
  rank: number;
  promo_id: string;
  promo_type: "single_episode" | "cross_episode";
  episodes: number[];
  segments: {
    episode?: number;
    start: string;
    end: string;
    start_seconds: number;
    end_seconds: number;
    duration: number;
  }[];
  total_duration: number;
  hook: {
    type: string;
    name: string;
    timestamp: string;
    quote: string;
    psychological_trigger: string;
  };
  cliffhanger: {
    type: string;
    name: string;
    timestamp: string;
    quote: string;
    withheld_payoff: string;
  };
  why_it_works: string;
  scores: {
    hook_strength: number;
    injustice_tension: number;
    cliffhanger_strength: number;
    standalone_clarity: number;
    payoff_withheld: number;
    composite_score: number;
    adjusted_score: number;
    diversity_penalty: number;
    conversion_intent?: number;
  };
  conversion_intent?: number;
  conversion_reason?: string;
  payoff_location?: string;
  stages?: string[];
  cold_read?: any;
  audit_panel?: any;
  engine?: string;
  model?: string;
  extractor_model?: string;
  trimmed_from_end?: boolean;
  seconds_removed?: number;
  audit_tier?: number | null;
  judge_verdicts?: {
    judge: string;
    model: string;
    pass: boolean;
    flaw_type?: string | null;
    one_line_reason: string;
    conversion_intent?: number | null;
  }[];
  quality_audit?: {
    passed: boolean;
    method?: "llm" | "rules" | "error" | "not_audited";
    flaw_type?: string;
    critique: string;
    confidence_score: number;
    conversion_intent?: number;
    risks: string[];
  };
  clip_beats?: any[];
}


export default function HomePage() {
  const [promos, setPromos] = useState<Promo[]>([]);
  const [allPromos, setAllPromos] = useState<Promo[]>([]);
  const [loading, setLoading] = useState(true);
  const [meta, setMeta] = useState<any>(null);
  const [selectedHook, setSelectedHook] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [minScore, setMinScore] = useState(5.0);
  const [expandedReasons, setExpandedReasons] = useState<Record<number, boolean>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeModalPromo, setActiveModalPromo] = useState<Promo | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isCustomActive, setIsCustomActive] = useState(false);
  const [baselinePromos, setBaselinePromos] = useState<Promo[]>([]);
  const [baselineMeta, setBaselineMeta] = useState<any>(null);
  const [serverKeyStatus, setServerKeyStatus] = useState({ hasGeminiKey: false, hasOpenaiKey: false });
  const [isScriptOpen, setIsScriptOpen] = useState(false);
  const [scriptFilter, setScriptFilter] = useState<"all" | "dialogue">("all");
  const [scriptCopied, setScriptCopied] = useState(false);
  const [modalBeats, setModalBeats] = useState<any[]>([]);
  const [loadingScript, setLoadingScript] = useState(false);
  const [episodeBeatsCache, setEpisodeBeatsCache] = useState<Record<number, any[]>>({});

  // Fetch full dataset once for accurate category counts & server status
  useEffect(() => {
    fetch("/api/promos")
      .then((res) => res.json())
      .then((data) => {
        const fetchedPromos = data.promos || [];
        setAllPromos(fetchedPromos);
        setBaselinePromos(fetchedPromos);
        setMeta(data.meta || null);
        setBaselineMeta(data.meta || null);
      })
      .catch(() => {});

    fetch("/api/pipeline/status")
      .then((res) => res.json())
      .then((data) => {
        setServerKeyStatus({
          hasGeminiKey: Boolean(data.hasGeminiKey),
          hasOpenaiKey: Boolean(data.hasOpenaiKey),
        });
      })
      .catch(() => {});
  }, []);

  // Listen for Escape key to close modal
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setActiveModalPromo(null);
        setIsUploadModalOpen(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  function parseTimestampSeconds(ts: string): number {
    if (!ts) return 0;
    const parts = ts.split(":");
    if (parts.length === 2) {
      return parseFloat(parts[0]) * 60 + parseFloat(parts[1]);
    }
    return parseFloat(ts) || 0;
  }

  // Load screenplay beats for active modal promo
  useEffect(() => {
    if (!activeModalPromo) {
      setModalBeats([]);
      setIsScriptOpen(false);
      return;
    }

    if (activeModalPromo.clip_beats && activeModalPromo.clip_beats.length > 0) {
      setModalBeats(activeModalPromo.clip_beats);
      return;
    }

    let isMounted = true;
    async function loadPromoBeats() {
      if (!activeModalPromo) return;
      setLoadingScript(true);
      try {
        const targetEpisodes = Array.from(
          new Set(activeModalPromo.segments.map((s) => s.episode || activeModalPromo.episodes[0] || 1))
        );

        const updatedCache = { ...episodeBeatsCache };
        for (const ep of targetEpisodes) {
          if (!updatedCache[ep]) {
            const res = await fetch(`/api/episodes?ep=${ep}`);
            if (res.ok) {
              const data = await res.json();
              if (data.beats) {
                updatedCache[ep] = data.beats;
              }
            }
          }
        }
        if (!isMounted) return;
        setEpisodeBeatsCache(updatedCache);

        const matched: any[] = [];
        for (const seg of activeModalPromo.segments) {
          const ep = seg.episode || activeModalPromo.episodes[0] || 1;
          const beats = updatedCache[ep] || [];
          const segBeats = beats.filter((b: any) => {
            const bStart = b.start_seconds ?? parseTimestampSeconds(b.start);
            const bEnd = b.end_seconds ?? parseTimestampSeconds(b.end);
            return bEnd > seg.start_seconds && bStart < seg.end_seconds;
          });
          matched.push(...segBeats);
        }
        setModalBeats(matched);
      } catch (err) {
        console.error("Error loading promo screenplay beats:", err);
      } finally {
        if (isMounted) setLoadingScript(false);
      }
    }

    loadPromoBeats();
    return () => {
      isMounted = false;
    };
  }, [activeModalPromo]);

  function copyFullScript() {
    if (!activeModalPromo || modalBeats.length === 0) return;
    const lines: string[] = [];
    lines.push(`PROMO AD SCRIPT: Rank #${activeModalPromo.rank} — ${activeModalPromo.hook.name}`);
    lines.push(`Total Duration: ${activeModalPromo.total_duration.toFixed(1)}s`);
    lines.push(`Target Cuts: ${activeModalPromo.segments.map((s) => `${s.start} → ${s.end}`).join(" | ")}`);
    lines.push("");

    const beatsToExport = scriptFilter === "dialogue"
      ? modalBeats.filter((b) => b.type === "DIALOGUE" || (!["CAMERA", "ACTION", "SOUND", "SFX"].includes(b.type) && b.speaker))
      : modalBeats;

    for (const b of beatsToExport) {
      if (b.type === "DIALOGUE" || (!["CAMERA", "ACTION", "SOUND", "SFX"].includes(b.type) && b.speaker)) {
        const spk = b.emotion ? `${b.speaker} (${b.emotion})` : b.speaker || "SPEAKER";
        lines.push(`[${b.start} - ${b.end}] ${spk}:`);
        lines.push(`"${b.text}"\n`);
      } else {
        lines.push(`[${b.start} - ${b.end}] [${b.type}]: ${b.text}\n`);
      }
    }

    navigator.clipboard.writeText(lines.join("\n"));
    setScriptCopied(true);
    setTimeout(() => setScriptCopied(false), 2000);
  }

  useEffect(() => {
    if (isCustomActive) {
      filterCustomPromos();
    } else {
      fetchPromos();
    }
  }, [selectedHook, selectedType, minScore, searchQuery, isCustomActive, allPromos]);

  function filterCustomPromos() {
    let filtered = [...allPromos];
    if (selectedHook !== "all") {
      filtered = filtered.filter((p) => p.hook.type === selectedHook);
    }
    if (selectedType !== "all") {
      filtered = filtered.filter((p) => p.promo_type === selectedType);
    }
    if (minScore > 0) {
      filtered = filtered.filter(
        (p) => (p.scores?.adjusted_score || p.scores?.composite_score || 0) >= minScore
      );
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter((p) =>
        (
          (p.hook?.quote || "") +
          " " +
          (p.cliffhanger?.quote || "") +
          " " +
          (p.why_it_works || "") +
          " " +
          (p.hook?.name || "")
        )
          .toLowerCase()
          .includes(q)
      );
    }
    setPromos(filtered);
    setLoading(false);
  }

  async function fetchPromos() {
    try {
      const params = new URLSearchParams();
      if (selectedHook !== "all") params.append("hook", selectedHook);
      if (selectedType !== "all") params.append("type", selectedType);
      if (minScore > 0) params.append("min_score", minScore.toString());
      if (searchQuery) params.append("q", searchQuery);

      const res = await fetch(`/api/promos?${params.toString()}`);
      const data = await res.json();
      setPromos(data.promos || []);
    } catch (e) {
      console.error("Failed to fetch promos", e);
    } finally {
      setLoading(false);
    }
  }

  function handleCustomRunSuccess(data: any) {
    setIsCustomActive(true);
    setAllPromos(data.ranked_promos || []);
    setPromos(data.ranked_promos || []);
    setMeta({
      show: data.show_title || "Custom Show",
      episodes: data.episodes_analyzed || 1,
      beats: data.total_beats || 0,
      extractor: {
        provider: data.meta?.provider || "llm",
        model: data.meta?.model || "active",
      },
      auditor: {
        method: data.meta?.provider === "heuristic" ? "rules" : "llm",
      },
    });
    resetFilters();
  }

  function handleResetToBaseline() {
    setIsCustomActive(false);
    setAllPromos(baselinePromos);
    setPromos(baselinePromos);
    setMeta(baselineMeta);
    resetFilters();
  }

  function downloadCustomCsv() {
    const headers = [
      "promo_id",
      "rank",
      "episode",
      "segment_order",
      "start_time",
      "end_time",
      "duration_seconds",
      "hook_quote",
      "cliffhanger_quote",
      "payoff_location",
      "audit_verdict",
    ];
    const rows = [headers.join(",")];
    promos.forEach((p) => {
      p.segments.forEach((seg, idx) => {
        rows.push(
          [
            `"${p.promo_id}"`,
            p.rank || "",
            seg.episode ?? p.episodes[0] ?? "",
            idx + 1,
            `"${seg.start}"`,
            `"${seg.end}"`,
            (seg.duration || seg.end_seconds - seg.start_seconds).toFixed(2),
            `"${(p.hook?.quote || "").replace(/"/g, '""')}"`,
            `"${(p.cliffhanger?.quote || "").replace(/"/g, '""')}"`,
            `"${p.payoff_location || "unknown"}"`,
            `"${p.quality_audit?.passed ? "PASS" : "FAIL"}"`,
          ].join(",")
        );
      });
    });
    const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "custom_promos.csv";
    a.click();
  }

  function downloadCustomJson() {
    const blob = new Blob([JSON.stringify(promos, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "custom_promos.json";
    a.click();
  }

  const hookCounts = useMemo(() => {
    const map: Record<string, number> = { all: allPromos.length };
    allPromos.forEach((p) => {
      map[p.hook.type] = (map[p.hook.type] || 0) + 1;
    });
    return map;
  }, [allPromos]);

  const typeCounts = useMemo(() => {
    const map: Record<string, number> = { all: allPromos.length };
    allPromos.forEach((p) => {
      map[p.promo_type] = (map[p.promo_type] || 0) + 1;
    });
    return map;
  }, [allPromos]);

  const scoreValues = allPromos.map((p) => p.scores?.adjusted_score ?? p.scores?.composite_score ?? 0).filter((s) => s > 0);
  const dataMin = scoreValues.length > 0 ? Math.floor(Math.min(...scoreValues) * 10) / 10 : 5.0;
  const dataMax = scoreValues.length > 0 ? Math.ceil(Math.max(...scoreValues) * 10) / 10 : 8.0;

  const isFiltered =
    selectedHook !== "all" ||
    selectedType !== "all" ||
    minScore > dataMin ||
    searchQuery.trim() !== "";

  function resetFilters() {
    setSelectedHook("all");
    setSelectedType("all");
    setMinScore(dataMin);
    setSearchQuery("");
  }

  function copyTimestamps(promo: Promo) {
    const text = promo.segments
      .map((s) => `${s.start} -> ${s.end}`)
      .join(", ");
    navigator.clipboard.writeText(text);
    setCopiedId(promo.promo_id);
    setTimeout(() => setCopiedId(null), 2000);
  }

  const heroPromo = promos.length > 0 ? promos[0] : null;

  return (
    <div className="kuku-container">
      {/* ── Top Overview Banner ───────────────────────── */}
      <div style={{ marginBottom: "var(--s-32)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "var(--s-16)" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)", marginBottom: "var(--s-8)" }}>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "4px 10px",
                  borderRadius: "var(--radius-full)",
                  background: "var(--surface)",
                  border: "1px solid var(--hairline)",
                  fontSize: 12,
                  fontWeight: 500,
                  color: "var(--ink-2)",
                }}
              >
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: isCustomActive ? "var(--success-strong)" : "var(--accent)" }} />
                Show: {meta?.show ?? "(no run found)"}
              </span>
              <span
                style={{
                  padding: "4px 10px",
                  borderRadius: "var(--radius-full)",
                  background: "var(--sunken)",
                  fontSize: 12,
                  color: "var(--ink-3)",
                }}
              >
                {meta ? `${meta.episodes} episodes · ${meta.extractor?.provider || meta.provider || "llm"}/${meta.extractor?.model || meta.model || "frontier"}` : ""}
              </span>
            </div>

            {meta && meta.auditor?.method !== "llm" && !isCustomActive && (
              <p className="om-caption" style={{ color: "var(--warning-strong)", marginBottom: "var(--s-12)" }}>
                Smoke-test output from the offline keyword engine. "Passed rule lint" is not a quality judgement.
              </p>
            )}
            <h1 className="om-display" style={{ color: "var(--ink)", marginBottom: "var(--s-8)" }}>
              Viral Acquisition Promos
            </h1>
            <p className="om-body" style={{ color: "var(--ink-2)", maxWidth: 760 }}>
              Ranked 20–60 second ad cuts for Instagram Reels, TikTok, and YouTube Shorts.
              Optimized for unearned interpersonal injustice (&ldquo;blood boils&rdquo;) with withheld catharsis.
            </p>
          </div>

          <div style={{ display: "flex", gap: "var(--s-8)", flexWrap: "wrap", alignItems: "center" }}>
            <button
              onClick={() => setIsUploadModalOpen(true)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "10px 18px",
                borderRadius: "var(--radius-md)",
                background: "var(--ai-gradient)",
                color: "#fff",
                border: "none",
                fontWeight: 600,
                fontSize: 13,
                cursor: "pointer",
                boxShadow: "0 4px 14px rgba(11, 61, 145, 0.2)",
              }}
            >
              <UploadCloud size={16} />
              <span>Upload Custom Script</span>
            </button>
            <Link
              href="/episodes"
              className="om-button om-button--secondary"
              style={{ padding: "10px 16px", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6 }}
            >
              <Layers size={14} />
              <span>Browse Beats</span>
            </Link>
          </div>
        </div>

        {/* Custom Run Active Banner */}
        {isCustomActive && (
          <div
            style={{
              marginTop: "var(--s-16)",
              padding: "var(--s-12) var(--s-16)",
              borderRadius: "var(--radius-lg)",
              background: "var(--sunken)",
              border: "1px solid var(--accent)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "var(--s-12)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Sparkles size={16} style={{ color: "var(--accent)" }} />
              <div>
                <strong style={{ fontSize: 13, color: "var(--ink)" }}>Custom Screenplay Analysis Active</strong>
                <span style={{ fontSize: 12, color: "var(--ink-2)", marginLeft: 6 }}>
                  ({allPromos.length} candidate promos ranked)
                </span>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={downloadCustomCsv}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "6px 12px",
                  borderRadius: "var(--radius-sm)",
                  background: "var(--surface)",
                  border: "1px solid var(--hairline)",
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--ink)",
                  cursor: "pointer",
                }}
              >
                <Download size={13} /> Export CSV
              </button>
              <button
                onClick={downloadCustomJson}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "6px 12px",
                  borderRadius: "var(--radius-sm)",
                  background: "var(--surface)",
                  border: "1px solid var(--hairline)",
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--ink)",
                  cursor: "pointer",
                }}
              >
                <Download size={13} /> Export JSON
              </button>
              <button
                onClick={handleResetToBaseline}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  padding: "6px 12px",
                  borderRadius: "var(--radius-sm)",
                  background: "var(--sunken)",
                  border: "1px solid var(--hairline)",
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--accent)",
                  cursor: "pointer",
                }}
              >
                <RotateCcw size={13} /> Reset to Shipped Show
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Featured Hero Board (The One Dark Surface) ──── */}
      {heroPromo && (
        <section className="kuku-board" style={{ marginBottom: "var(--s-40)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "var(--s-16)", marginBottom: "var(--s-20)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--s-12)" }}>
              <span
                style={{
                  background: "var(--ai-gradient)",
                  color: "#fff",
                  padding: "4px 12px",
                  borderRadius: "var(--radius-full)",
                  fontSize: 12,
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <Sparkles size={14} /> Rank #1 Top ad cut
              </span>

              <span
                style={{
                  background: "var(--board-raised)",
                  color: "var(--on-board-2)",
                  padding: "4px 10px",
                  borderRadius: "var(--radius-xs)",
                  fontSize: 12,
                  fontFamily: "var(--font-sans)",
                }}
              >
                {heroPromo.promo_type === "cross_episode" ? "Cross-episode composite" : "Single episode"}
              </span>

              <span className="om-num" style={{ color: "var(--on-board-2)", fontSize: 13 }}>
                Episodes {heroPromo.episodes.join(" & ")} · {heroPromo.total_duration.toFixed(1)}s
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)" }}>
              <button
                onClick={() => copyTimestamps(heroPromo)}
                className="om-button om-button--compact"
                style={{
                  background: "var(--board-raised)",
                  color: "var(--on-board)",
                  border: "1px solid var(--board-rule)",
                  minHeight: 36,
                }}
              >
                {copiedId === heroPromo.promo_id ? <Check size={14} /> : <Copy size={14} />}
                <span>{copiedId === heroPromo.promo_id ? "Copied" : "Copy timestamps"}</span>
              </button>

              <button
                onClick={() => setActiveModalPromo(heroPromo)}
                className="om-button om-button--compact"
                style={{
                  background: "var(--accent)",
                  color: "var(--on-accent)",
                  minHeight: 36,
                }}
              >
                <Play size={14} />
                <span>Inspect cut</span>
              </button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 280px), 1fr))", gap: "var(--s-24)", marginBottom: "var(--s-24)" }}>
            <div style={{ background: "rgba(255,255,255,0.04)", padding: "var(--s-20)", borderRadius: "var(--radius-lg)", border: "1px solid var(--board-rule)" }}>
              <span className="om-caption" style={{ color: "var(--on-board-2)", display: "block", marginBottom: 6 }}>
                The hook (first 3 seconds) · {heroPromo.hook.name}
              </span>
              <p className="om-body-strong" style={{ color: "var(--on-board)", fontSize: 18, marginBottom: 8 }}>
                &ldquo;{heroPromo.hook.quote}&rdquo;
              </p>
              <span style={{ fontSize: 13, color: "var(--accent-mark-on-board)" }}>
                {heroPromo.hook.psychological_trigger || (heroPromo.hook.type?.startsWith("new:") ? "Model-proposed type (no taxonomy driver)" : "")}
              </span>
            </div>

            <div style={{ background: "rgba(255,255,255,0.04)", padding: "var(--s-20)", borderRadius: "var(--radius-lg)", border: "1px solid var(--board-rule)" }}>
              <span className="om-caption" style={{ color: "var(--on-board-2)", display: "block", marginBottom: 6 }}>
                The cliffhanger (payoff withheld)
              </span>
              <p className="om-body-strong" style={{ color: "var(--on-board)", fontSize: 18, marginBottom: 8 }}>
                &ldquo;{heroPromo.cliffhanger.quote}&rdquo;
              </p>
              <span style={{ fontSize: 13, color: "var(--on-board-2)" }}>
                {heroPromo.cliffhanger.withheld_payoff}
              </span>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--board-rule)", paddingTop: "var(--s-16)", flexWrap: "wrap", gap: "var(--s-16)" }}>
            <p className="om-subhead" style={{ color: "var(--on-board-2)", maxWidth: 700 }}>
              <strong style={{ color: "var(--on-board)" }}>Why it works:</strong> {heroPromo.why_it_works}
            </p>
            <div style={{ textAlign: "right" }}>
              <span
                className="om-caption"
                style={{ color: "var(--on-board-2)", display: "block", cursor: "help" }}
                title="Weighted prior over hook, cliffhanger, payoff, injustice and clarity. Not a conversion prediction."
              >
                Rank index (relative, uncalibrated)
              </span>
              <span className="om-display om-num" style={{ color: "var(--on-board)", fontSize: 28 }}>
                {(heroPromo.scores.adjusted_score || heroPromo.scores.composite_score).toFixed(2)}
              </span>
              <div style={{ display: "flex", gap: 6, justifyContent: "flex-end", marginTop: 6, flexWrap: "wrap", alignItems: "center" }}>
                {heroPromo.audit_tier && (
                  <span className="kuku-pill" style={{ background: "rgba(255,255,255,0.18)", color: "#fff", border: "1px solid rgba(255,255,255,0.25)" }}>
                    Tier {heroPromo.audit_tier}
                  </span>
                )}
                {heroPromo.judge_verdicts?.map((jv, i) => (
                  <span key={i} className="kuku-pill" style={{ background: jv.pass ? "rgba(46, 125, 50, 0.45)" : "rgba(198, 40, 40, 0.45)", color: "#fff", border: "1px solid rgba(255,255,255,0.25)" }}>
                    {jv.judge === "openai" ? "GPT-6" : "Gemini"}: {jv.pass ? "PASS" : "FAIL"}
                  </span>
                ))}
                {heroPromo.conversion_intent != null && (
                  <span className="kuku-pill" style={{ background: "rgba(255,255,255,0.18)", color: "#fff", border: "1px solid rgba(255,255,255,0.25)" }}>
                    Conv: {heroPromo.conversion_intent}/10
                  </span>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ── Filters & Controls Strip ──────────────────── */}
      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--hairline)",
          borderRadius: "var(--radius-lg)",
          padding: "var(--s-20)",
          marginBottom: "var(--s-24)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--s-16)",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "var(--s-12)" }}>
          {/* Search box */}
          <div style={{ position: "relative", minWidth: 260, flex: "1 1 320px" }}>
            <Search
              size={16}
              style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--ink-3)" }}
            />
            <input
              type="text"
              placeholder="Search quotes, characters, or beats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                height: 42,
                padding: "0 38px 0 40px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--hairline)",
                background: "var(--paper)",
                color: "var(--ink)",
                fontSize: 14,
                outline: "none",
                transition: "border-color 0.15s ease",
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                style={{
                  position: "absolute",
                  right: 12,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "transparent",
                  border: "none",
                  color: "var(--ink-3)",
                  cursor: "pointer",
                  padding: 4,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
                title="Clear search"
              >
                <X size={15} />
              </button>
            )}
          </div>

          {/* View toggle */}
          <div style={{ display: "flex", alignItems: "center", gap: 4, background: "var(--sunken)", padding: 4, borderRadius: "var(--radius-md)" }}>
            <button
              onClick={() => setViewMode("grid")}
              className={`om-button om-button--compact ${viewMode === "grid" ? "is-pressed" : ""}`}
              style={{
                minHeight: 34,
                padding: "0 12px",
                background: viewMode === "grid" ? "var(--surface)" : "transparent",
                color: viewMode === "grid" ? "var(--ink)" : "var(--ink-3)",
                borderRadius: "var(--radius-sm)",
                fontWeight: viewMode === "grid" ? 600 : 400,
                boxShadow: viewMode === "grid" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
                border: "none",
                cursor: "pointer",
              }}
            >
              <LayoutGrid size={15} />
              <span>Cards</span>
            </button>
            <button
              onClick={() => setViewMode("table")}
              className={`om-button om-button--compact ${viewMode === "table" ? "is-pressed" : ""}`}
              style={{
                minHeight: 34,
                padding: "0 12px",
                background: viewMode === "table" ? "var(--surface)" : "transparent",
                color: viewMode === "table" ? "var(--ink)" : "var(--ink-3)",
                borderRadius: "var(--radius-sm)",
                fontWeight: viewMode === "table" ? 600 : 400,
                boxShadow: viewMode === "table" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
                border: "none",
                cursor: "pointer",
              }}
            >
              <TableIcon size={15} />
              <span>Table</span>
            </button>
          </div>
        </div>

        {/* Hook Filter Chips */}
        <div>
          <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 8 }}>
            Filter by hook trigger:
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)", flexWrap: "wrap" }}>
            {[
              { id: "all", label: "All hooks" },
              { id: "public_humiliation", label: "Public humiliation" },
              { id: "physical_aggression", label: "Physical aggression" },
              { id: "intimate_betrayal", label: "Intimate betrayal" },
              { id: "class_status_contempt", label: "Class contempt" },
              { id: "hidden_identity_irony", label: "Hidden identity" },
              { id: "unjust_accusation", label: "Unjust accusation" },
            ].map((chip) => {
              const count = hookCounts[chip.id];
              return (
                <button
                  key={chip.id}
                  onClick={() => setSelectedHook(chip.id)}
                  className={`kuku-chip ${selectedHook === chip.id ? "active" : ""}`}
                >
                  <span>{chip.label}</span>
                  {count !== undefined && (
                    <span className="kuku-chip-count">{count}</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Format & Score Slider */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "var(--s-16)", paddingTop: "var(--s-12)", borderTop: "1px solid var(--hairline)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)", flexWrap: "wrap" }}>
            <span className="om-caption" style={{ color: "var(--ink-3)", marginRight: 2 }}>
              Format:
            </span>
            {[
              { id: "all", label: "All formats" },
              { id: "single_episode", label: "Single episode" },
              { id: "cross_episode", label: "Cross-episode composite" },
            ].map((chip) => {
              const count = typeCounts[chip.id] || 0;
              const isCross = chip.id === "cross_episode";
              if (isCross && count === 0) {
                return (
                  <button
                    key={chip.id}
                    disabled
                    className="kuku-chip"
                    style={{ opacity: 0.5, cursor: "not-allowed" }}
                    title="Cross-episode composites are off by default"
                  >
                    <span>Cross-episode (off by default)</span>
                    <span className="kuku-chip-count">0</span>
                  </button>
                );
              }
              return (
                <button
                  key={chip.id}
                  onClick={() => setSelectedType(chip.id)}
                  className={`kuku-chip ${selectedType === chip.id ? "active" : ""}`}
                >
                  <span>{chip.label}</span>
                  {count !== undefined && (
                    <span className="kuku-chip-count">{count}</span>
                  )}
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "var(--s-12)" }}>
            <span
              className="om-caption"
              style={{ color: "var(--ink-3)", cursor: "help" }}
              title="Weighted prior over hook, cliffhanger, payoff, injustice and clarity. Not a conversion prediction."
            >
              Min rank index: <strong className="om-num" style={{ color: "var(--ink)" }}>{minScore.toFixed(2)}</strong>
            </span>
            <input
              type="range"
              min={dataMin}
              max={dataMax}
              step="0.05"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              style={{ width: 130, accentColor: "var(--accent)" }}
            />
          </div>
        </div>

        {/* Filter Feedback Strip */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "var(--s-8)", paddingTop: "var(--s-8)", borderTop: "1px dashed var(--hairline)", fontSize: 13 }}>
          <span style={{ color: "var(--ink-2)" }}>
            Showing <strong className="om-num" style={{ color: "var(--ink)" }}>{promos.length}</strong> of <span className="om-num">{allPromos.length || promos.length}</span> ranked promos
            {selectedHook !== "all" && <span> · Hook: <em>{selectedHook.replace(/_/g, " ")}</em></span>}
            {selectedType !== "all" && <span> · Format: <em>{selectedType.replace(/_/g, " ")}</em></span>}
          </span>
          {isFiltered && (
            <button
              onClick={resetFilters}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                background: "transparent",
                border: "none",
                color: "var(--accent)",
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 600,
                padding: "2px 6px",
                borderRadius: "var(--radius-xs)",
              }}
            >
              <RotateCcw size={12} />
              <span>Reset all filters</span>
            </button>
          )}
        </div>
      </div>

      {/* ── Main Promos Display ───────────────────────── */}
      {loading ? (
        <div style={{ padding: "var(--s-48) 0", textAlign: "center", color: "var(--ink-3)" }}>
          <div className="om-spinner" style={{ marginBottom: 12 }}>
            <svg viewBox="0 0 18 18">
              <circle cx="9" cy="9" r="8" />
            </svg>
          </div>
          <p>Analyzing screenplays against taxonomy...</p>
        </div>
      ) : promos.length === 0 ? (
        <div
          style={{
            background: "var(--surface)",
            padding: "var(--s-48)",
            borderRadius: "var(--radius-lg)",
            textAlign: "center",
            border: "1px solid var(--hairline)",
          }}
        >
          <AlertTriangle size={32} style={{ color: "var(--warning-strong)", margin: "0 auto var(--s-12)" }} />
          <h3 className="om-headline">No promos match current filters</h3>
          <p className="om-subhead" style={{ color: "var(--ink-3)", marginTop: 4 }}>
            Try lowering the minimum score threshold or selecting &ldquo;All hooks&rdquo;.
          </p>
        </div>
      ) : viewMode === "grid" ? (
        <div className="kuku-grid">
          {promos.map((p) => {
            const isTop3 = p.rank <= 3;
            const effScore = p.scores.adjusted_score || p.scores.composite_score;
            const penalty = p.scores.diversity_penalty;
            const isCopied = copiedId === p.promo_id;

            return (
              <div key={p.promo_id} className="kuku-card">
                {/* Header Row */}
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "var(--s-12)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)" }}>
                    <span
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: "var(--radius-full)",
                        background: p.rank === 1 ? "var(--board)" : isTop3 ? "var(--accent)" : "var(--sunken)",
                        color: isTop3 ? "#ffffff" : "var(--ink)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 13,
                        fontWeight: 700,
                        fontFamily: "var(--font-sans)",
                        boxShadow: isTop3 ? "0 2px 6px rgba(0,0,0,0.15)" : "none",
                        flexShrink: 0,
                      }}
                    >
                      {p.rank}
                    </span>
                    <div>
                      <span className="om-body-strong" style={{ display: "block", fontSize: 15 }}>
                        {p.hook.name}
                      </span>
                      <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                        Ep {p.episodes.join(" & ")} · {p.promo_type === "cross_episode" ? "Composite" : "Single ep"}
                      </span>
                    </div>
                  </div>

                  <div style={{ textAlign: "right", display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
                    <span
                      className="om-headline om-num"
                      style={{ color: "var(--accent)", fontSize: 22, fontWeight: 700, lineHeight: 1.1 }}
                      title={`Rank index (relative, uncalibrated). Weighted prior over hook, cliffhanger, payoff, injustice and clarity.${penalty < 1.0 ? ` (penalty ×${penalty.toFixed(2)})` : ""}`}
                    >
                      {effScore.toFixed(2)}
                    </span>
                    <div style={{ display: "flex", gap: 5, justifyContent: "flex-end", marginTop: 5, flexWrap: "wrap", alignItems: "center" }}>
                      {p.audit_tier && (
                        <span
                          className="kuku-pill"
                          style={{
                            background: p.audit_tier === 1 ? "var(--success-container)" : p.audit_tier === 2 ? "var(--warning-container)" : "var(--sunken)",
                            color: p.audit_tier === 1 ? "var(--success-on-container)" : p.audit_tier === 2 ? "var(--warning-on-container)" : "var(--ink-2)",
                            fontSize: 10,
                          }}
                        >
                          Tier {p.audit_tier}
                        </span>
                      )}
                      {p.conversion_intent != null && (
                        <span className="kuku-pill" style={{ background: "var(--sunken)", color: "var(--ink-2)", fontSize: 10 }}>
                          Conv: {p.conversion_intent}/10
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Timestamps Pill & Visual Duration Track */}
                <div style={{ marginBottom: "var(--s-12)" }}>
                  <div
                    style={{
                      background: "var(--sunken)",
                      borderRadius: "var(--radius-md)",
                      padding: "7px 10px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: 12,
                    }}
                  >
                    <span className="om-num" style={{ color: "var(--ink)", fontWeight: 600 }}>
                      {p.segments.map((s) => `${s.start} → ${s.end}`).join(" | ")}
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span
                        className="om-tag"
                        style={{
                          background: "var(--surface)",
                          border: "1px solid var(--hairline)",
                          fontSize: 11,
                          padding: "2px 7px",
                          borderRadius: "var(--radius-full)",
                        }}
                      >
                        {p.total_duration.toFixed(1)}s
                      </span>
                      <button
                        onClick={() => copyTimestamps(p)}
                        style={{
                          color: isCopied ? "var(--success-strong)" : "var(--ink-2)",
                          background: isCopied ? "var(--success-container)" : "transparent",
                          borderRadius: "var(--radius-xs)",
                          padding: "3px 6px",
                          border: "none",
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          gap: 3,
                          fontSize: 11,
                          fontWeight: 500,
                          transition: "all 0.15s ease",
                        }}
                        title="Copy timestamps"
                      >
                        {isCopied ? <Check size={12} /> : <Copy size={12} />}
                        <span>{isCopied ? "Copied" : "Copy"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Visual Duration Meter (20-60s) */}
                  <div style={{ width: "100%", height: 3, background: "var(--hairline)", borderRadius: 2, overflow: "hidden", marginTop: 4 }}>
                    <div
                      style={{
                        width: `${Math.min(100, (p.total_duration / 60) * 100)}%`,
                        height: "100%",
                        background: p.total_duration <= 35 ? "var(--accent)" : p.total_duration <= 50 ? "var(--info-strong)" : "var(--tip-strong)",
                        borderRadius: 2,
                      }}
                    />
                  </div>
                </div>

                {/* Hook Quote */}
                <div style={{ marginBottom: "var(--s-12)", flex: "1 0 auto" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 4 }}>
                    Hook (first 3s):
                  </span>
                  <p className="om-body" style={{ color: "var(--ink)", fontStyle: "italic", fontSize: 14, lineHeight: "1.4" }}>
                    &ldquo;{p.hook.quote}&rdquo;
                  </p>
                </div>

                {/* Cliffhanger Quote */}
                <div style={{ marginBottom: "var(--s-12)" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 4 }}>
                    Cliffhanger (payoff withheld):
                  </span>
                  <p className="om-subhead" style={{ color: "var(--ink-2)", fontSize: 13, lineHeight: "1.4" }}>
                    &ldquo;{p.cliffhanger.quote}&rdquo;
                  </p>
                </div>

                {/* Why it works & Audit flags */}
                <div style={{ borderTop: "1px solid var(--hairline)", paddingTop: "var(--s-12)", marginTop: "auto" }}>
                  {p.payoff_location && p.payoff_location !== "unknown" && (
                    <div style={{ marginBottom: 6, fontSize: 11, color: "var(--accent)", fontWeight: 500 }}>
                      Payoff: {p.payoff_location}
                    </div>
                  )}
                  {p.conversion_intent != null && (
                    <div style={{ marginBottom: 6, fontSize: 11, color: "var(--ink-2)" }}>
                      Conversion Intent: <strong>{p.conversion_intent}/10</strong>
                    </div>
                  )}
                  {p.audit_tier != null && (
                    <div style={{ marginBottom: 6 }}>
                      <span
                        className="kuku-pill"
                        style={{
                          fontSize: 11,
                          background: p.audit_tier === 1 ? "var(--success-container)" : p.audit_tier === 2 ? "var(--warning-container)" : "var(--sunken)",
                          color: p.audit_tier === 1 ? "var(--success-on-container)" : p.audit_tier === 2 ? "var(--warning-on-container)" : "var(--ink-2)",
                        }}
                      >
                        Tier {p.audit_tier}: {p.audit_tier === 1 ? "Both judges pass" : p.audit_tier === 2 ? "Split verdict (needs editor look)" : "Both fail"}
                      </span>
                    </div>
                  )}
                  {p.trimmed_from_end && (
                    <div style={{ marginBottom: 6, fontSize: 11, color: "var(--ink-3)", display: "flex", alignItems: "center", gap: 4 }}>
                      <Scissors size={12} /> Trimmed to cliffhanger (-{p.seconds_removed}s)
                    </div>
                  )}
                  <p className="om-caption" style={{ color: "var(--ink-2)", marginBottom: "var(--s-8)", lineHeight: "1.4" }}>
                    {p.why_it_works}
                  </p>

                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    {p.quality_audit?.method === "error" ? (
                      <span style={{ fontSize: 12, color: "var(--warning-strong)", display: "flex", alignItems: "center", gap: 4, fontWeight: 500 }}>
                        <AlertTriangle size={14} /> Unaudited
                      </span>
                    ) : p.audit_tier != null ? (
                      <span style={{ fontSize: 12, color: p.audit_tier === 1 ? "var(--success-strong)" : p.audit_tier === 2 ? "var(--warning-strong)" : "var(--ink-2)", display: "flex", alignItems: "center", gap: 4, fontWeight: 500 }}>
                        <ShieldCheck size={14} /> Tier {p.audit_tier} ({p.judge_verdicts?.map(v => `${v.judge === 'openai' ? 'GPT-6' : 'Gemini'}:${v.pass ? 'PASS' : 'FAIL'}`).join(', ') || (p.audit_tier === 1 ? "Consensus Pass" : "Split")})
                      </span>
                    ) : p.quality_audit?.passed ? (
                      <span style={{ fontSize: 12, color: "var(--success-strong)", display: "flex", alignItems: "center", gap: 4, fontWeight: 500 }}>
                        <ShieldCheck size={14} /> {p.quality_audit.method === "llm" ? "Audited" : "Passed rule lint"}
                      </span>
                    ) : (
                      <span style={{ fontSize: 12, color: "var(--warning-strong)", display: "flex", alignItems: "center", gap: 4, fontWeight: 500 }}>
                        <AlertTriangle size={14} /> Failed audit{p.quality_audit?.flaw_type ? `: ${p.quality_audit.flaw_type}` : ""}
                      </span>
                    )}

                    <button
                      onClick={() => setActiveModalPromo(p)}
                      style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: "var(--accent)",
                        display: "flex",
                        alignItems: "center",
                        gap: 3,
                        background: "transparent",
                        border: "none",
                        cursor: "pointer",
                        padding: "4px 6px",
                        borderRadius: "var(--radius-xs)",
                      }}
                    >
                      Inspect cut <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Table View */
        <div style={{ background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: "var(--radius-lg)", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.02)" }}>
          <div className="no-scrollbar" style={{ width: "100%", overflowX: "auto", WebkitOverflowScrolling: "touch" }}>
            <table style={{ width: "100%", minWidth: 780, borderCollapse: "collapse", textAlign: "left", fontSize: 14 }}>
              <thead>
                <tr style={{ background: "var(--paper)", borderBottom: "1px solid var(--hairline)", color: "var(--ink-3)", fontSize: 12 }}>
                  <th style={{ padding: "12px 16px" }}>Rank</th>
                  <th style={{ padding: "12px 16px" }}>Score</th>
                  <th style={{ padding: "12px 16px" }}>Episode</th>
                  <th style={{ padding: "12px 16px" }}>Duration</th>
                  <th style={{ padding: "12px 16px" }}>Hook archetype</th>
                  <th style={{ padding: "12px 16px" }}>Opening quote</th>
                  <th style={{ padding: "12px 16px" }}>Timestamps</th>
                  <th style={{ padding: "12px 16px", textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {promos.map((p) => (
                  <tr key={p.promo_id} style={{ borderBottom: "1px solid var(--hairline)" }}>
                    <td style={{ padding: "12px 16px", fontWeight: 700 }}>#{p.rank}</td>
                    <td style={{ padding: "12px 16px" }} className="om-num">
                      <strong style={{ color: "var(--accent)", fontSize: 16 }}>{(p.scores.adjusted_score || p.scores.composite_score).toFixed(2)}</strong>
                      {p.audit_tier && (
                        <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                          <span
                            className="kuku-pill"
                            style={{
                              background: p.audit_tier === 1 ? "var(--success-container)" : p.audit_tier === 2 ? "var(--warning-container)" : "var(--sunken)",
                              color: p.audit_tier === 1 ? "var(--success-on-container)" : p.audit_tier === 2 ? "var(--warning-on-container)" : "var(--ink-2)",
                              fontSize: 10,
                            }}
                          >
                            Tier {p.audit_tier}
                          </span>
                          {p.conversion_intent != null && (
                            <span className="kuku-pill" style={{ background: "var(--sunken)", color: "var(--ink-2)", fontSize: 10 }}>
                              Conv {p.conversion_intent}/10
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: "12px 16px" }}>Ep {p.episodes.join(" & ")}</td>
                    <td style={{ padding: "12px 16px" }} className="om-num">
                      {p.total_duration.toFixed(1)}s
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <span className="om-tag" style={{ background: "var(--sunken)", padding: "3px 8px", borderRadius: "var(--radius-full)", fontSize: 12 }}>
                        {p.hook.name}
                      </span>
                    </td>
                    <td style={{ padding: "12px 16px", maxWidth: 260, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      &ldquo;{p.hook.quote}&rdquo;
                    </td>
                    <td style={{ padding: "12px 16px", fontFamily: "var(--font-sans)", fontSize: 12 }} className="om-num">
                      {p.segments.map((s) => `${s.start}→${s.end}`).join(", ")}
                    </td>
                    <td style={{ padding: "12px 16px", textAlign: "right" }}>
                      <button
                        onClick={() => setActiveModalPromo(p)}
                        className="om-button om-button--compact"
                        style={{ background: "var(--paper)", color: "var(--accent)", minHeight: 30, padding: "0 10px", border: "1px solid var(--hairline)" }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Detail Modal / Drawer ───────────────────────── */}
      {activeModalPromo && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(23, 25, 27, 0.45)",
            backdropFilter: "blur(6px)",
            WebkitBackdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "var(--page-margin)",
          }}
          onClick={() => setActiveModalPromo(null)}
        >
          <div
            style={{
              background: "var(--surface)",
              borderRadius: "var(--radius-xl)",
              maxWidth: 680,
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "var(--s-32)",
              boxShadow: "0 24px 64px rgba(0,0,0,0.24)",
              border: "1px solid var(--hairline)",
            }}
            onClick={(e) => e.stopPropagation()}
            className="no-scrollbar"
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--s-20)" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                    Promo Rank #{activeModalPromo.rank} · {activeModalPromo.promo_type.replace("_", " ")}
                  </span>
                  <span
                    className="kuku-pill"
                    title="Weighted prior over hook, cliffhanger, payoff, injustice and clarity. Not a conversion prediction."
                    style={{
                      background: "var(--accent)",
                      color: "#fff",
                      cursor: "help",
                    }}
                  >
                    Rank index: {(activeModalPromo.scores.adjusted_score || activeModalPromo.scores.composite_score).toFixed(2)}
                  </span>
                  {activeModalPromo.audit_tier && (
                    <span
                      className="kuku-pill"
                      style={{
                        background: activeModalPromo.audit_tier === 1 ? "var(--success-container)" : "var(--warning-container)",
                        color: activeModalPromo.audit_tier === 1 ? "var(--success-on-container)" : "var(--warning-on-container)",
                      }}
                    >
                      Tier {activeModalPromo.audit_tier}
                    </span>
                  )}
                  {activeModalPromo.conversion_intent != null && (
                    <span
                      className="kuku-pill"
                      style={{
                        background: "var(--sunken)",
                        color: "var(--ink-2)",
                      }}
                    >
                      Conv: {activeModalPromo.conversion_intent}/10
                    </span>
                  )}
                </div>
                <h2 className="om-title-large" style={{ marginTop: 4 }}>
                  {activeModalPromo.hook.name}
                </h2>
              </div>
              <button
                onClick={() => setActiveModalPromo(null)}
                style={{
                  padding: "6px 10px",
                  color: "var(--ink-3)",
                  background: "var(--sunken)",
                  border: "none",
                  borderRadius: "var(--radius-full)",
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: 600,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
                title="Close modal (Esc)"
              >
                <X size={16} />
              </button>
            </div>

            {/* Timestamps Bar */}
            <div
              style={{
                background: "var(--sunken)",
                borderRadius: "var(--radius-md)",
                padding: "var(--s-16)",
                marginBottom: "var(--s-20)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: 12,
              }}
            >
              <div>
                <span className="om-caption" style={{ display: "block", color: "var(--ink-3)" }}>
                  Target cut timestamps ({activeModalPromo.total_duration.toFixed(1)}s total)
                </span>
                <span className="om-headline om-num" style={{ color: "var(--ink)" }}>
                  {activeModalPromo.segments.map((s) => `${s.start} → ${s.end}`).join("  |  ")}
                </span>
              </div>
              <button
                onClick={() => copyTimestamps(activeModalPromo)}
                className="om-button om-button--compact"
                style={{ background: "var(--surface)", color: "var(--ink)", border: "1px solid var(--hairline)" }}
              >
                {copiedId === activeModalPromo.promo_id ? <Check size={14} /> : <Copy size={14} />}
                <span>{copiedId === activeModalPromo.promo_id ? "Copied" : "Copy"}</span>
              </button>
            </div>

            {/* Hook and Cliffhanger Blocks */}
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-16)", marginBottom: "var(--s-24)" }}>
              <div style={{ borderLeft: "3px solid var(--accent)", paddingLeft: "var(--s-16)" }}>
                <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                  The psychological hook ({activeModalPromo.hook.type})
                </span>
                <p className="om-body-strong" style={{ fontSize: 16, marginTop: 4 }}>
                  &ldquo;{activeModalPromo.hook.quote}&rdquo;
                </p>
                <p className="om-subhead" style={{ color: "var(--ink-2)", marginTop: 4, fontSize: 13 }}>
                  <strong>Driver:</strong> {activeModalPromo.hook.psychological_trigger || (activeModalPromo.hook.type?.startsWith("new:") ? "Model-proposed type (no taxonomy driver)" : "N/A")}
                </p>
              </div>

              <div style={{ borderLeft: "3px solid var(--warning-strong)", paddingLeft: "var(--s-16)" }}>
                <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                  The cliffhanger cut point ({activeModalPromo.cliffhanger.type})
                </span>
                <p className="om-body-strong" style={{ fontSize: 16, marginTop: 4 }}>
                  &ldquo;{activeModalPromo.cliffhanger.quote}&rdquo;
                </p>
                <p className="om-subhead" style={{ color: "var(--ink-2)", marginTop: 4, fontSize: 13 }}>
                  <strong>Withheld payoff:</strong> {activeModalPromo.cliffhanger.withheld_payoff}
                </p>
              </div>
            </div>

            {/* ── Collapsible Full Ad Screenplay & Script ── */}
            <div
              style={{
                background: "var(--surface)",
                border: "1px solid var(--hairline)",
                borderRadius: "var(--radius-lg)",
                marginBottom: "var(--s-24)",
                overflow: "hidden",
                boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
              }}
            >
              <button
                type="button"
                onClick={() => setIsScriptOpen(!isScriptOpen)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "14px 18px",
                  background: isScriptOpen ? "var(--sunken)" : "transparent",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background var(--dur-fast)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                  <FileText size={16} style={{ color: "var(--accent)" }} />
                  <span className="om-body-strong" style={{ fontSize: 14, color: "var(--ink)" }}>
                    Full Ad Script & Screenplay
                  </span>
                  <span className="kuku-pill" style={{ background: "var(--sunken)", color: "var(--ink-2)", fontSize: 11 }}>
                    {modalBeats.length} beats
                  </span>
                  <span className="kuku-pill" style={{ background: "var(--accent-container)", color: "var(--accent-strong)", fontSize: 11 }}>
                    {modalBeats.filter((b) => b.type === "DIALOGUE" || (!["CAMERA", "ACTION", "SOUND", "SFX"].includes(b.type) && b.speaker)).length} spoken lines
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--ink-3)", fontSize: 12, fontWeight: 500 }}>
                  <span>{isScriptOpen ? "Hide script" : "Show full ad script"}</span>
                  {isScriptOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </button>

              {isScriptOpen && (
                <div style={{ borderTop: "1px solid var(--hairline)", padding: "var(--s-16)", background: "var(--paper)" }}>
                  {/* Controls Bar */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10, marginBottom: "var(--s-12)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <button
                        type="button"
                        onClick={() => setScriptFilter("all")}
                        className={`kuku-chip kuku-chip--compact ${scriptFilter === "all" ? "active" : ""}`}
                        style={{ minHeight: 28, padding: "2px 10px", fontSize: 11 }}
                      >
                        All Screenplay Beats
                      </button>
                      <button
                        type="button"
                        onClick={() => setScriptFilter("dialogue")}
                        className={`kuku-chip kuku-chip--compact ${scriptFilter === "dialogue" ? "active" : ""}`}
                        style={{ minHeight: 28, padding: "2px 10px", fontSize: 11 }}
                      >
                        Spoken Dialogue Only
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={copyFullScript}
                      className="om-button om-button--compact"
                      style={{ background: "var(--surface)", color: scriptCopied ? "var(--success-strong)" : "var(--ink)", border: "1px solid var(--hairline)", minHeight: 28, padding: "0 10px", fontSize: 11 }}
                    >
                      {scriptCopied ? <Check size={12} /> : <Copy size={12} />}
                      <span>{scriptCopied ? "Copied Script" : "Copy Ad Script"}</span>
                    </button>
                  </div>

                  {/* Beats List */}
                  {loadingScript ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "32px 0", color: "var(--ink-3)" }}>
                      <Loader2 size={16} className="animate-spin" />
                      <span style={{ fontSize: 13 }}>Loading screenplay beats for this cut...</span>
                    </div>
                  ) : modalBeats.length === 0 ? (
                    <div style={{ padding: "20px 0", textAlign: "center", color: "var(--ink-3)", fontSize: 13 }}>
                      No screenplay beats found in this segment timestamp window.
                    </div>
                  ) : (
                    <div
                      className="no-scrollbar"
                      style={{
                        maxHeight: 380,
                        overflowY: "auto",
                        display: "flex",
                        flexDirection: "column",
                        gap: 8,
                        paddingRight: 4,
                      }}
                    >
                      {modalBeats
                        .filter((b) => (scriptFilter === "dialogue" ? b.type === "DIALOGUE" || (!["CAMERA", "ACTION", "SOUND", "SFX"].includes(b.type) && b.speaker) : true))
                        .map((beat, idx) => {
                          const isDialogue = beat.type === "DIALOGUE" || (!["CAMERA", "ACTION", "SOUND", "SFX"].includes(beat.type) && Boolean(beat.speaker));
                          const isHookBeat = activeModalPromo.hook.quote && beat.text && (beat.text.includes(activeModalPromo.hook.quote.slice(0, 20)) || activeModalPromo.hook.quote.includes(beat.text.slice(0, 20)));
                          const isCliffBeat = activeModalPromo.cliffhanger.quote && beat.text && (beat.text.includes(activeModalPromo.cliffhanger.quote.slice(0, 20)) || activeModalPromo.cliffhanger.quote.includes(beat.text.slice(0, 20)));

                          if (isDialogue) {
                            return (
                              <div
                                key={idx}
                                style={{
                                  background: "var(--surface)",
                                  border: isHookBeat ? "1px solid var(--accent)" : isCliffBeat ? "1px solid var(--warning-strong)" : "1px solid var(--hairline)",
                                  borderLeft: isHookBeat ? "3px solid var(--accent)" : isCliffBeat ? "3px solid var(--warning-strong)" : "3px solid var(--hairline)",
                                  borderRadius: "var(--radius-md)",
                                  padding: "10px 14px",
                                }}
                              >
                                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
                                  <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                                    <span className="kuku-pill" style={{ background: "var(--board)", color: "#fff", fontWeight: 700, fontSize: 11 }}>
                                      {beat.speaker || "SPEAKER"}
                                    </span>
                                    {beat.emotion && (
                                      <span style={{ fontSize: 11, color: "var(--ink-2)", fontStyle: "italic" }}>
                                        ({beat.emotion})
                                      </span>
                                    )}
                                    {isHookBeat && (
                                      <span className="kuku-pill" style={{ background: "var(--accent)", color: "#fff", fontSize: 10 }}>
                                        Hook
                                      </span>
                                    )}
                                    {isCliffBeat && (
                                      <span className="kuku-pill" style={{ background: "var(--warning-strong)", color: "#fff", fontSize: 10 }}>
                                        Cliffhanger
                                      </span>
                                    )}
                                  </div>
                                  <span className="om-num" style={{ fontSize: 11, color: "var(--ink-3)" }}>
                                    {beat.start} → {beat.end}
                                  </span>
                                </div>
                                <p style={{ margin: 0, fontSize: 13.5, color: "var(--ink)", lineHeight: 1.5, fontWeight: 500 }}>
                                  &ldquo;{beat.text}&rdquo;
                                </p>
                              </div>
                            );
                          }

                          const isAction = beat.type === "ACTION";
                          const isCamera = beat.type === "CAMERA";
                          const isSound = beat.type === "SOUND" || /^(SOUND|SFX)/i.test(beat.type);

                          return (
                            <div
                              key={idx}
                              style={{
                                background: "var(--sunken)",
                                borderRadius: "var(--radius-md)",
                                padding: "8px 12px",
                                display: "flex",
                                flexDirection: "column",
                                gap: 3,
                              }}
                            >
                              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                                <span
                                  className="kuku-pill"
                                  style={{
                                    background: "var(--surface)",
                                    color: isAction ? "var(--accent-strong)" : "var(--ink-3)",
                                    border: "1px solid var(--hairline)",
                                    fontSize: 10,
                                    padding: "1px 6px",
                                  }}
                                >
                                  {isAction ? "ACTION" : isCamera ? "CAMERA" : isSound ? "SFX" : beat.type}
                                </span>
                                <span className="om-num" style={{ fontSize: 10, color: "var(--ink-3)" }}>
                                  {beat.start} → {beat.end}
                                </span>
                              </div>
                              <p style={{ margin: 0, fontSize: 12, color: "var(--ink-2)", fontStyle: isAction ? "normal" : "italic", lineHeight: 1.4 }}>
                                {beat.text}
                              </p>
                            </div>
                          );
                        })}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Score Grid */}
            <div style={{ background: "var(--paper)", padding: "var(--s-16)", borderRadius: "var(--radius-lg)", marginBottom: "var(--s-24)" }}>
              <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 8 }}>
                Scoring matrix (0 to 10 scale)
              </span>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, textAlign: "center" }}>
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Hook</span>
                  <p className="om-headline om-num">{activeModalPromo.scores.hook_strength}</p>
                </div>
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Injustice</span>
                  <p className="om-headline om-num">{activeModalPromo.scores.injustice_tension}</p>
                </div>
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Cliffhanger</span>
                  <p className="om-headline om-num">{activeModalPromo.scores.cliffhanger_strength}</p>
                </div>
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Clarity</span>
                  <p className="om-headline om-num">{activeModalPromo.scores.standalone_clarity}</p>
                </div>
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Withheld</span>
                  <p className="om-headline om-num">{activeModalPromo.scores.payoff_withheld}</p>
                </div>
              </div>
            </div>

            {/* Quality Audit Section */}
            {(activeModalPromo.conversion_intent != null || (activeModalPromo.payoff_location && activeModalPromo.payoff_location !== "unknown") || (activeModalPromo.stages && activeModalPromo.stages.length > 0)) && (
              <div style={{ background: "var(--paper)", padding: "var(--s-16)", borderRadius: "var(--radius-lg)", marginBottom: "var(--s-24)" }}>
                {activeModalPromo.conversion_intent != null && (
                  <div style={{ marginBottom: 6 }}>
                    <span className="om-caption" style={{ color: "var(--ink-3)" }}>Conversion Intent: </span>
                    <strong style={{ color: "var(--ink)" }}>{activeModalPromo.conversion_intent} / 10</strong>
                    {activeModalPromo.conversion_reason && <span style={{ color: "var(--ink-2)", fontSize: 13 }}> — {activeModalPromo.conversion_reason}</span>}
                  </div>
                )}
                {activeModalPromo.payoff_location && activeModalPromo.payoff_location !== "unknown" && (
                  <div style={{ marginBottom: 6 }}>
                    <span className="om-caption" style={{ color: "var(--ink-3)" }}>Payoff Location: </span>
                    <strong style={{ color: "var(--accent)" }}>{activeModalPromo.payoff_location}</strong>
                  </div>
                )}
                {activeModalPromo.stages && activeModalPromo.stages.length > 0 && (
                  <div>
                    <span className="om-caption" style={{ color: "var(--ink-3)" }}>Stages: </span>
                    <span style={{ fontSize: 12, color: "var(--ink-2)" }}>{activeModalPromo.stages.join(", ")}</span>
                  </div>
                )}
              </div>
            )}

            {/* Judge Panel Verdicts */}
            {activeModalPromo.judge_verdicts && activeModalPromo.judge_verdicts.length > 0 && (
              <div style={{ background: "var(--paper)", padding: "var(--s-16)", borderRadius: "var(--radius-lg)", marginBottom: "var(--s-20)" }}>
                <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 8 }}>
                  Judge Panel Verdicts {activeModalPromo.audit_tier != null ? `(Tier ${activeModalPromo.audit_tier})` : ""}
                </span>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {activeModalPromo.judge_verdicts.map((jv, idx) => {
                    const isLong = (jv.one_line_reason || "").length > 140;
                    const isExpanded = Boolean(expandedReasons[idx]);
                    const displayText = isLong && !isExpanded
                      ? jv.one_line_reason.slice(0, 140) + "…"
                      : jv.one_line_reason;
                    return (
                      <div key={idx} style={{ fontSize: 12, borderLeft: jv.pass ? "3px solid var(--success-strong)" : "3px solid var(--warning-strong)", paddingLeft: 8 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 600 }}>
                          <span style={{ color: jv.pass ? "var(--success-strong)" : "var(--warning-strong)" }}>
                            {jv.pass ? "PASS" : `FAIL (${jv.flaw_type || "unspecified"})`}
                          </span>
                          <span style={{ color: "var(--ink-2)" }}>· {jv.judge}:{jv.model}</span>
                          {jv.conversion_intent != null && <span style={{ color: "var(--ink-3)" }}>· conv: {jv.conversion_intent}/10</span>}
                        </div>
                        <p style={{ margin: "2px 0 0", color: "var(--ink-2)", lineHeight: "1.4" }}>
                          {displayText}
                          {isLong && (
                            <button
                              onClick={() => setExpandedReasons(prev => ({ ...prev, [idx]: !prev[idx] }))}
                              style={{
                                marginLeft: 6,
                                background: "none",
                                border: "none",
                                color: "var(--accent)",
                                cursor: "pointer",
                                fontSize: 11,
                                fontWeight: 600,
                                padding: 0,
                                textDecoration: "underline",
                              }}
                            >
                              {isExpanded ? "Show less" : "Show full reason"}
                            </button>
                          )}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {activeModalPromo.quality_audit && (
              <div style={{ borderTop: "1px solid var(--hairline)", paddingTop: "var(--s-16)", marginBottom: "var(--s-20)" }}>
                <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 6 }}>
                  Adversarial quality audit
                </span>
                <p className="om-subhead" style={{ color: "var(--ink)" }}>
                  {activeModalPromo.quality_audit.critique}
                </p>
                {activeModalPromo.quality_audit.risks.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    {activeModalPromo.quality_audit.risks.map((r, idx) => (
                      <span
                        key={idx}
                        className="kuku-pill"
                        style={{
                          background: "var(--warning-container)",
                          color: "var(--warning-on-container)",
                          fontSize: 12,
                          marginRight: 6,
                          marginBottom: 4,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 4,
                        }}
                      >
                        <AlertTriangle size={12} /> {r}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--s-8)" }}>
              <button
                onClick={() => setActiveModalPromo(null)}
                className="om-button om-button--compact"
                style={{ background: "var(--paper)", color: "var(--ink)" }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Custom Upload Modal ───────────────────────────── */}
      <CustomUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={handleCustomRunSuccess}
        serverKeyStatus={serverKeyStatus}
      />
    </div>
  );
}
