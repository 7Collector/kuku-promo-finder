"use client";

import React, { useState, useEffect } from "react";
import { BookOpen, Clock, Film, MessageSquare, Sparkles, ChevronLeft, ChevronRight } from "lucide-react";

export default function EpisodesPage() {
  const [selectedEp, setSelectedEp] = useState(1);
  const [selectedRange, setSelectedRange] = useState("all");
  const [epData, setEpData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [epNumbers, setEpNumbers] = useState<number[]>([]);
  const maxEp = epNumbers.length ? epNumbers[epNumbers.length - 1] : 1;

  useEffect(() => {
    fetchEpisode(selectedEp);
  }, [selectedEp]);

  async function fetchEpisode(ep: number) {
    setLoading(true);
    try {
      const res = await fetch(`/api/episodes?ep=${ep}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setEpData(data);
      if (data.episodes) setEpNumbers(data.episodes.map((e: any) => e.number));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  function handlePrev() {
    const i = epNumbers.indexOf(selectedEp);
    if (i > 0) setSelectedEp(epNumbers[i - 1]);
  }

  function handleNext() {
    const i = epNumbers.indexOf(selectedEp);
    if (i >= 0 && i < epNumbers.length - 1) setSelectedEp(epNumbers[i + 1]);
  }

  // Filter visible episodes by decade tab
  const visibleEpisodes = epNumbers.filter((num) => {
    if (selectedRange === "all") return true;
    const [start, end] = selectedRange.split("-").map(Number);
    return num >= start && num <= end;
  });

  return (
    <div className="kuku-container">
      <div style={{ marginBottom: "var(--s-32)" }}>
        <h1 className="om-display">Screenplay Beat Browser</h1>
        <p className="om-body" style={{ color: "var(--ink-2)", maxWidth: 720 }}>
          Inspect the deterministic parsing of any episode of the show.
          Every dialogue line, action beat, and camera cut is indexed with its centisecond timestamps.
        </p>
      </div>

      {/* Episode Selector Strip with Zero Horizontal Scrollbars */}
      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--hairline)",
          borderRadius: "var(--radius-lg)",
          padding: "var(--s-20)",
          marginBottom: "var(--s-24)",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: "var(--s-12)" }}>
          <span className="om-caption" style={{ color: "var(--ink-3)", fontWeight: 500 }}>
            Select episode ({selectedEp} of {maxEp}):
          </span>

          {/* Range quick filter tabs */}
          <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
            {[
              { id: "all", label: "All 50" },
              { id: "1-10", label: "1–10" },
              { id: "11-20", label: "11–20" },
              { id: "21-30", label: "21–30" },
              { id: "31-40", label: "31–40" },
              { id: "41-50", label: "41–50" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedRange(tab.id)}
                className={`kuku-chip kuku-chip--compact ${selectedRange === tab.id ? "active" : ""}`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Wrapped Episode Grid */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {visibleEpisodes.map((num) => (
            <button
              key={num}
              onClick={() => setSelectedEp(num)}
              className={`kuku-chip ${selectedEp === num ? "active" : ""}`}
              style={{
                minWidth: 42,
                height: 36,
                padding: "0 10px",
                fontWeight: selectedEp === num ? 600 : 500,
              }}
            >
              {num}
            </button>
          ))}
        </div>
      </div>

      {loading || !epData ? (
        <div style={{ padding: "var(--s-48) 0", textAlign: "center", color: "var(--ink-3)" }}>
          <div className="om-spinner" style={{ marginBottom: 12 }}>
            <svg viewBox="0 0 18 18">
              <circle cx="9" cy="9" r="8" />
            </svg>
          </div>
          <p>Loading episode screenplay...</p>
        </div>
      ) : (
        <div>
          {/* Episode Info Surface with Prev / Next Navigation */}
          <div
            className="om-surface"
            style={{
              border: "1px solid var(--hairline)",
              marginBottom: "var(--s-20)",
              padding: "var(--s-20)",
              borderRadius: "var(--radius-lg)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span className="om-title-medium">Episode {epData.episodeNumber}</span>
                <span
                  className="om-caption om-num"
                  style={{
                    background: "var(--sunken)",
                    color: "var(--ink-2)",
                    padding: "3px 8px",
                    borderRadius: "var(--radius-full)",
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  {epData.beatsCount} beats parsed
                </span>
              </div>

              {/* Prev / Next controls */}
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <button
                  onClick={handlePrev}
                  disabled={selectedEp <= 1}
                  className="om-button om-button--compact"
                  style={{
                    background: selectedEp <= 1 ? "var(--sunken)" : "var(--surface)",
                    color: selectedEp <= 1 ? "var(--ink-3)" : "var(--ink)",
                    border: "1px solid var(--hairline)",
                    minHeight: 34,
                    padding: "0 10px",
                    cursor: selectedEp <= 1 ? "not-allowed" : "pointer",
                  }}
                >
                  <ChevronLeft size={15} />
                  <span>Prev</span>
                </button>
                <button
                  onClick={handleNext}
                  disabled={selectedEp >= maxEp}
                  className="om-button om-button--compact"
                  style={{
                    background: selectedEp >= maxEp ? "var(--sunken)" : "var(--surface)",
                    color: selectedEp >= maxEp ? "var(--ink-3)" : "var(--ink)",
                    border: "1px solid var(--hairline)",
                    minHeight: 34,
                    padding: "0 10px",
                    cursor: selectedEp >= maxEp ? "not-allowed" : "pointer",
                  }}
                >
                  <span>Next</span>
                  <ChevronRight size={15} />
                </button>
              </div>
            </div>

            <p className="om-body" style={{ color: "var(--ink-2)", fontSize: 14, lineHeight: "1.5" }}>
              {epData.logline}
            </p>
          </div>

          {/* Beats Timeline */}
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {epData.beats.map((beat: any, idx: number) => {
              const isDialogue = beat.type === "DIALOGUE";
              const isAction = beat.type === "ACTION";
              const isCamera = beat.type === "CAMERA";

              return (
                <div
                  key={idx}
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--hairline)",
                    borderRadius: "var(--radius-md)",
                    padding: "12px 16px",
                    display: "grid",
                    gridTemplateColumns: "minmax(90px, 120px) minmax(110px, 150px) 1fr",
                    gap: "var(--s-16)",
                    alignItems: "center",
                  }}
                >
                  {/* Timestamp */}
                  <span className="om-num" style={{ fontSize: 13, color: "var(--ink-3)", fontWeight: 500 }}>
                    {beat.start} → {beat.end}
                  </span>

                  {/* Type / Speaker */}
                  <div>
                    {isDialogue ? (
                      <div>
                        <span className="om-body-strong" style={{ fontSize: 13, color: "var(--ink)" }}>
                          {beat.speaker}
                        </span>
                        {beat.emotion && (
                          <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", fontSize: 11 }}>
                            ({beat.emotion})
                          </span>
                        )}
                      </div>
                    ) : (
                      <span
                        className="om-tag"
                        style={{
                          background: isAction ? "var(--accent-container)" : "var(--sunken)",
                          color: isAction ? "var(--on-accent-container)" : "var(--ink-3)",
                          padding: "3px 8px",
                          borderRadius: "var(--radius-full)",
                          fontSize: 11,
                          fontWeight: 600,
                        }}
                      >
                        {beat.type}
                      </span>
                    )}
                  </div>

                  {/* Text Content */}
                  <div>
                    <p
                      className="om-body"
                      style={{
                        fontSize: 14,
                        color: isDialogue ? "var(--ink)" : "var(--ink-2)",
                        fontStyle: isDialogue ? "normal" : "italic",
                        lineHeight: "1.4",
                      }}
                    >
                      {beat.text}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
