"use client";

import React, { useState } from "react";
import { Sparkles, Play, ShieldAlert, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";

export default function AnalyzeToolPage() {
  const [start, setStart] = useState("00:33.80");
  const [end, setEnd] = useState("01:18.50");
  const [hookQuote, setHookQuote] = useState("Why are you holding her hand? / Because he is marrying me.");
  const [cliffQuote] = useState("Long enough to know he was never going to marry you.");
  const [hookType, setHookType] = useState("intimate_betrayal");
  const [cliffType, setCliffType] = useState("interrupted_retaliation");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const presets = [
    {
      name: "The Wedding Betrayal (Ep 1)",
      start: "00:33.80",
      end: "01:18.50",
      hook: "Why are you holding her hand? / Because he is marrying me.",
      cliff: "Long enough to know he was never going to marry you.",
      hookType: "intimate_betrayal",
      cliffType: "interrupted_retaliation",
    },
    {
      name: "Sadistic Blackthorn Crawl (Ep 12)",
      start: "00:20.00",
      end: "00:58.50",
      hook: "Crawl through the blackthorn garden, Juliana, or watch your husband hang.",
      cliff: "Juliana drops to her knees as Clarissa sneers above her.",
      hookType: "public_humiliation",
      cliffType: "mortal_ultimatum",
    },
    {
      name: "Cathedral Gate Shattered (Ep 42)",
      start: "00:10.00",
      end: "00:46.00",
      hook: "Who dares enter this royal sanctuary without permission?",
      cliff: "The smoke parts as Alexander steps forth in full ducal crest.",
      hookType: "hidden_identity_irony",
      cliffType: "unexpected_savior_arrival",
    },
  ];

  function applyPreset(p: (typeof presets)[0]) {
    setStart(p.start);
    setEnd(p.end);
    setHookQuote(p.hook);
    setHookType(p.hookType);
    setCliffType(p.cliffType);
    setResult(null);
  }

  async function handleAnalyze() {
    setLoading(true);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start,
          end,
          hookQuote,
          cliffQuote,
          selectedHook: hookType,
          selectedCliff: cliffType,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="kuku-container">
      <div style={{ marginBottom: "var(--s-32)" }}>
        <span
          style={{
            background: "var(--ai-gradient)",
            color: "#fff",
            padding: "4px 10px",
            borderRadius: "var(--radius-full)",
            fontSize: 12,
            fontWeight: 600,
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            marginBottom: "var(--s-8)",
          }}
        >
          <Sparkles size={13} /> Interactive Tool
        </span>
        <h1 className="om-display">Reusable Promo Cut Tester</h1>
        <p className="om-body" style={{ color: "var(--ink-2)", maxWidth: 720 }}>
          Test any cut candidate against the &ldquo;Blood Boils&rdquo; hook taxonomy, physical duration constraints,
          and adversarial quality checks. Runs dynamically for any screenplay clip.
        </p>
      </div>

      {/* Presets */}
      <div style={{ display: "flex", alignItems: "center", gap: "var(--s-8)", marginBottom: "var(--s-24)", flexWrap: "wrap" }}>
        <span className="om-caption" style={{ color: "var(--ink-3)" }}>
          Try a preset cut:
        </span>
        {presets.map((p, idx) => (
          <button
            key={idx}
            onClick={() => applyPreset(p)}
            className="kuku-chip"
            style={{ fontSize: 13 }}
          >
            {p.name}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "var(--s-24)" }}>
        {/* Input Form */}
        <div className="om-surface" style={{ border: "1px solid var(--hairline)" }}>
          <h3 className="om-headline" style={{ marginBottom: "var(--s-16)" }}>
            Cut Parameters
          </h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--s-12)", marginBottom: "var(--s-16)" }}>
            <div>
              <label className="om-caption" style={{ color: "var(--ink-2)", display: "block", marginBottom: 4 }}>
                Start timestamp
              </label>
              <input
                type="text"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                style={{
                  width: "100%",
                  height: 40,
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--hairline)",
                  padding: "0 var(--s-12)",
                  fontSize: 14,
                }}
              />
            </div>
            <div>
              <label className="om-caption" style={{ color: "var(--ink-2)", display: "block", marginBottom: 4 }}>
                End timestamp
              </label>
              <input
                type="text"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                style={{
                  width: "100%",
                  height: 40,
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--hairline)",
                  padding: "0 var(--s-12)",
                  fontSize: 14,
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: "var(--s-16)" }}>
            <label className="om-caption" style={{ color: "var(--ink-2)", display: "block", marginBottom: 4 }}>
              Hook archetype
            </label>
            <select
              value={hookType}
              onChange={(e) => setHookType(e.target.value)}
              style={{
                width: "100%",
                height: 40,
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--hairline)",
                padding: "0 var(--s-12)",
                fontSize: 14,
                background: "var(--surface)",
              }}
            >
              <option value="public_humiliation">Public Humiliation & Scorn (Weight 1.0)</option>
              <option value="physical_aggression">Physical Aggression / Violence (Weight 0.95)</option>
              <option value="intimate_betrayal">Intimate Betrayal / Altar Abandonment (Weight 0.95)</option>
              <option value="class_status_contempt">Class & Status Contempt (Weight 0.90)</option>
              <option value="hidden_identity_irony">Ignorant Disrespect / Dramatic Irony (Weight 0.90)</option>
              <option value="unjust_accusation">Unjust Framing / False Blame (Weight 0.85)</option>
            </select>
          </div>

          <div style={{ marginBottom: "var(--s-16)" }}>
            <label className="om-caption" style={{ color: "var(--ink-2)", display: "block", marginBottom: 4 }}>
              Opening hook dialogue / action quote
            </label>
            <textarea
              rows={2}
              value={hookQuote}
              onChange={(e) => setHookQuote(e.target.value)}
              placeholder="e.g. Why are you holding her hand?"
              style={{
                width: "100%",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--hairline)",
                padding: "var(--s-8) var(--s-12)",
                fontSize: 14,
                resize: "vertical",
              }}
            />
          </div>

          <div style={{ marginBottom: "var(--s-20)" }}>
            <label className="om-caption" style={{ color: "var(--ink-2)", display: "block", marginBottom: 4 }}>
              Cliffhanger closing beat
            </label>
            <select
              value={cliffType}
              onChange={(e) => setCliffType(e.target.value)}
              style={{
                width: "100%",
                height: 40,
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--hairline)",
                padding: "0 var(--s-12)",
                fontSize: 14,
                background: "var(--surface)",
              }}
            >
              <option value="interrupted_retaliation">Interrupted Retaliation / Comeuppance Cut (Weight 1.0)</option>
              <option value="unexpected_savior_arrival">The Power Arrival / Mysterious Protector (Weight 0.95)</option>
              <option value="truth_half_revealed">The Half-Revealed Truth (Weight 0.90)</option>
              <option value="mortal_ultimatum">The Impossible Ultimatum (Weight 0.85)</option>
            </select>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="om-button"
            style={{ width: "100%", minHeight: 44, gap: 8 }}
          >
            {loading ? <span className="om-spinner" /> : <Play size={16} />}
            <span>Evaluate promo cut</span>
          </button>
        </div>

        {/* Results Panel */}
        <div className="om-surface" style={{ border: "1px solid var(--hairline)" }}>
          <h3 className="om-headline" style={{ marginBottom: "var(--s-16)" }}>
            Analysis & Scorecard
          </h3>

          {!result ? (
            <div style={{ padding: "var(--s-32) 0", textAlign: "center", color: "var(--ink-3)" }}>
              <p>Configure cut parameters or pick a preset, then click Evaluate.</p>
            </div>
          ) : (
            <div>
              {/* Score badge & Duration */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  background: "var(--paper)",
                  padding: "var(--s-16)",
                  borderRadius: "var(--radius-lg)",
                  marginBottom: "var(--s-16)",
                }}
              >
                <div>
                  <span className="om-caption" style={{ color: "var(--ink-3)", display: "block" }}>
                    Composite promo score
                  </span>
                  <span className="om-display om-num" style={{ color: "var(--ink)" }}>
                    {result.scores.composite_score}
                    <span style={{ fontSize: 16, color: "var(--ink-3)" }}> / 10</span>
                  </span>
                </div>

                <div style={{ textAlign: "right" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)", display: "block" }}>
                    Duration
                  </span>
                  <span
                    className="om-headline om-num"
                    style={{ color: result.durationValid ? "var(--success-strong)" : "var(--danger-strong)" }}
                  >
                    {result.duration}s
                  </span>
                  <span className="om-caption" style={{ display: "block", color: "var(--ink-3)" }}>
                    {result.durationValid ? "✓ Within 20-60s window" : "✗ Out of bounds"}
                  </span>
                </div>
              </div>

              {/* Sub-scores */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, textAlign: "center", marginBottom: "var(--s-20)" }}>
                <div style={{ background: "var(--sunken)", padding: "8px", borderRadius: "var(--radius-md)" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Hook</span>
                  <p className="om-body-strong om-num">{result.scores.hook_strength}</p>
                </div>
                <div style={{ background: "var(--sunken)", padding: "8px", borderRadius: "var(--radius-md)" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Injustice</span>
                  <p className="om-body-strong om-num">{result.scores.injustice_tension}</p>
                </div>
                <div style={{ background: "var(--sunken)", padding: "8px", borderRadius: "var(--radius-md)" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Cliff</span>
                  <p className="om-body-strong om-num">{result.scores.cliffhanger_strength}</p>
                </div>
                <div style={{ background: "var(--sunken)", padding: "8px", borderRadius: "var(--radius-md)" }}>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>Payoff</span>
                  <p className="om-body-strong om-num">{result.scores.payoff_withheld}</p>
                </div>
              </div>

              {/* Psychological Trigger */}
              <div style={{ borderLeft: "3px solid var(--accent)", paddingLeft: "var(--s-12)", marginBottom: "var(--s-16)" }}>
                <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                  Psychological driver
                </span>
                <p className="om-body-strong" style={{ fontSize: 14 }}>
                  {result.hook.psychological_trigger}
                </p>
              </div>

              {/* Quality Audit */}
              <div style={{ borderTop: "1px solid var(--hairline)", paddingTop: "var(--s-16)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  {result.audit.passed ? (
                    <CheckCircle2 size={16} style={{ color: "var(--success-strong)" }} />
                  ) : (
                    <ShieldAlert size={16} style={{ color: "var(--warning-strong)" }} />
                  )}
                  <span className="om-body-strong" style={{ fontSize: 14 }}>
                    {result.audit.passed ? "Adversarial audit passed" : "Adversarial audit flagged"}
                  </span>
                </div>
                <p className="om-subhead" style={{ color: "var(--ink-2)", fontSize: 13, marginBottom: 8 }}>
                  {result.audit.critique}
                </p>
                {result.audit.risks.map((r: string, idx: number) => (
                  <span
                    key={idx}
                    style={{
                      display: "inline-block",
                      background: "var(--warning-container)",
                      color: "var(--warning-on-container)",
                      padding: "2px 8px",
                      borderRadius: "var(--radius-xs)",
                      fontSize: 12,
                      marginRight: 6,
                    }}
                  >
                    ⚠️ {r}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
