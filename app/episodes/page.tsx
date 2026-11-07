"use client";

import React, { useState, useEffect } from "react";
import { BookOpen, Clock, Film, MessageSquare, Sparkles } from "lucide-react";

export default function EpisodesPage() {
  const [selectedEp, setSelectedEp] = useState(1);
  const [epData, setEpData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEpisode(selectedEp);
  }, [selectedEp]);

  async function fetchEpisode(ep: number) {
    setLoading(true);
    try {
      const res = await fetch(`/api/episodes?ep=${ep}`);
      const data = await res.json();
      setEpData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="kuku-container">
      <div style={{ marginBottom: "var(--s-32)" }}>
        <h1 className="om-display">Screenplay Beat Browser</h1>
        <p className="om-body" style={{ color: "var(--ink-2)", maxWidth: 720 }}>
          Inspect the deterministic parsing of any of the 50 microdrama episodes.
          Every dialogue line, action beat, and camera cut is indexed with millisecond timestamps.
        </p>
      </div>

      {/* Episode Selector Strip */}
      <div
        style={{
          background: "var(--surface)",
          border: "1px solid var(--hairline)",
          borderRadius: "var(--radius-lg)",
          padding: "var(--s-16)",
          marginBottom: "var(--s-24)",
        }}
      >
        <span className="om-caption" style={{ color: "var(--ink-3)", display: "block", marginBottom: 8 }}>
          Jump to episode:
        </span>
        <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 6 }}>
          {Array.from({ length: 50 }, (_, i) => i + 1).map((num) => (
            <button
              key={num}
              onClick={() => setSelectedEp(num)}
              className={`om-button om-button--compact ${selectedEp === num ? "is-pressed" : ""}`}
              style={{
                minWidth: 38,
                height: 34,
                padding: "0 6px",
                background: selectedEp === num ? "var(--accent)" : "var(--sunken)",
                color: selectedEp === num ? "var(--on-accent)" : "var(--ink)",
                borderRadius: "var(--radius-md)",
                fontSize: 13,
                fontWeight: selectedEp === num ? 600 : 400,
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
          {/* Episode Info Surface */}
          <div className="om-surface" style={{ border: "1px solid var(--hairline)", marginBottom: "var(--s-20)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8, marginBottom: 8 }}>
              <span className="om-title-medium">Episode {epData.episodeNumber}</span>
              <span className="om-caption om-num" style={{ color: "var(--ink-3)" }}>
                {epData.beatsCount} beats parsed
              </span>
            </div>
            <p className="om-body" style={{ color: "var(--ink-2)", fontSize: 15 }}>
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
                    gridTemplateColumns: "100px 140px 1fr",
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
                        <span className="om-body-strong" style={{ fontSize: 13 }}>
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
                          padding: "2px 8px",
                          borderRadius: "var(--radius-xs)",
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
