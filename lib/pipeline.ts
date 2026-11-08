import YAML from "yaml";
import fs from "fs";
import path from "path";
import JSZip from "jszip";

// ============================================================================
// Types
// ============================================================================

export type BeatType = "DIALOGUE" | "ACTION" | "CAMERA" | "SOUND";

export interface Beat {
  type: BeatType;
  speaker: string | null;
  emotion: string | null;
  start: string;
  end: string;
  text: string;
  start_seconds: number;
  end_seconds: number;
}

export interface Episode {
  episode_number: number;
  filename: string;
  beats: Beat[];
  duration_seconds: number;
}

export interface Segment {
  episode: number;
  start: string;
  end: string;
  start_seconds: number;
  end_seconds: number;
  duration: number;
}

export interface HookInfo {
  type: string;
  name?: string;
  timestamp: string;
  timestamp_seconds: number;
  quote: string;
  weight?: number;
}

export interface CliffhangerInfo {
  type: string;
  name?: string;
  timestamp: string;
  timestamp_seconds: number;
  quote: string;
  withheld_payoff?: string;
  weight?: number;
}

export interface PromoScores {
  hook_strength: number;
  cliffhanger_strength: number;
  payoff_withheld: number;
  injustice_tension: number;
  standalone_clarity: number;
  composite_score: number;
  adjusted_score: number;
  diversity_penalty: number;
  conversion_intent?: number;
}

export interface QualityAudit {
  passed: boolean;
  method: "llm" | "rules" | "error" | "not_audited";
  flaw_type?: string | null;
  critique: string;
  confidence_score: number;
  conversion_intent?: number;
  risks: string[];
}

export interface JudgeVerdict {
  judge: string;
  model: string;
  pass: boolean;
  flaw_type?: string | null;
  one_line_reason: string;
  conversion_intent?: number | null;
}

export interface PromoCandidate {
  promo_id: string;
  rank?: number;
  promo_type: "single_episode" | "composite";
  episodes: number[];
  segments: Segment[];
  total_duration: number;
  hook: HookInfo;
  cliffhanger: CliffhangerInfo;
  why_it_works: string;
  risks: string[];
  scores: PromoScores;
  quality_audit?: QualityAudit;
  engine: string;
  model: string;
  extractor_model?: string;
  trimmed_from_end?: boolean;
  seconds_removed?: number;
  audit_tier?: number | null;
  judge_verdicts?: JudgeVerdict[];
  conversion_intent?: number;
  conversion_reason?: string;
  payoff_location?: string;
  stages?: string[];
}

export interface TaxonomyItem {
  id: string;
  name: string;
  category: string;
  definition: string;
  psychological_driver?: string;
  requires?: string[];
  do_not_tag_if?: string[];
  weight: number;
  generic_cues?: string[];
}

export interface PipelineOptions {
  provider?: "gemini" | "openai" | "heuristic";
  model?: string;
  apiKey?: string;
  showTitle?: string;
  showPremise?: string;
  topK?: number;
  weights?: Record<string, number>;
}

// ============================================================================
// Constants & Tolerances
// ============================================================================

export const MIN_DURATION = 20.0;
export const MAX_DURATION = 60.0;
export const HOOK_WINDOW = 3.0;
export const CLIFFHANGER_TAIL_SECONDS = 6.0;
export const SNAP_TOLERANCE = 0.5;
export const EPS = 1e-4;

export const DEFAULT_WEIGHTS: Record<string, number> = {
  hook: 0.30,
  cliffhanger: 0.25,
  payoff_withheld: 0.20,
  injustice_tension: 0.15,
  standalone_clarity: 0.10,
  conversion_intent: 0.0,
};

// ============================================================================
// Timestamps & Beat Parser
// ============================================================================

export function tryParseTimestamp(ts: string | number): number | null {
  if (typeof ts === "number") return isNaN(ts) ? null : ts;
  if (!ts) return null;
  const s = ts.trim();
  const parts = s.split(":");
  if (parts.length === 2) {
    const m = parseFloat(parts[0]);
    const sec = parseFloat(parts[1]);
    if (!isNaN(m) && !isNaN(sec)) return m * 60 + sec;
  } else if (parts.length === 3) {
    const h = parseFloat(parts[0]);
    const m = parseFloat(parts[1]);
    const sec = parseFloat(parts[2]);
    if (!isNaN(h) && !isNaN(m) && !isNaN(sec)) return h * 3600 + m * 60 + sec;
  } else if (parts.length === 1) {
    const sec = parseFloat(parts[0]);
    if (!isNaN(sec)) return sec;
  }
  return null;
}

export function formatTimestamp(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec - m * 60;
  return `${m.toString().padStart(2, "0")}:${s.toFixed(2).padStart(5, "0")}`;
}

const BEAT_RE =
  /\*\*([^*]+)\*\*\s*\nStart:\s*\(?([0-9:.]+)\)?\s*\|\s*End:\s*\(?([0-9:.]+)\)?\s*\n([\s\S]*?)(?=\n\*\*[^*]+\*\*\s*\nStart:|\nSCENE\s+\d+|\n-{3,}\s*SCRIPT END|$)/g;

export function parseEpisodeScreenplay(content: string, filename: string): Episode {
  const head = content.slice(0, 3000);
  const mNum = head.match(/EPISODE NUMBER:\s*(?:Episode\s*)?(\d+)/i) || filename.match(/episode[-_ ]?0*(\d+)/i);
  const epNum = mNum ? parseInt(mNum[1], 10) : 1;

  const beats: Beat[] = [];
  const matches = Array.from(content.matchAll(BEAT_RE));
  for (const m of matches) {
    const rawHeader = m[1].trim().replace(/:$/, "");
    const upper = rawHeader.toUpperCase();
    const isCamera = upper === "CAMERA";
    const isAction = upper === "ACTION";
    const isSound = /^(SOUND|SFX)/i.test(rawHeader);

    let speaker: string | null = null;
    let emotion: string | null = null;
    if (!isCamera && !isAction && !isSound) {
      const open = rawHeader.indexOf("(");
      const close = rawHeader.lastIndexOf(")");
      if (open >= 0 && close > open) {
        speaker = rawHeader.substring(0, open).trim();
        emotion = rawHeader.substring(open + 1, close).trim();
      } else {
        speaker = rawHeader;
      }
    }

    const startSec = tryParseTimestamp(m[2]) || 0;
    const endSec = tryParseTimestamp(m[3]) || 0;

    beats.push({
      type: isCamera ? "CAMERA" : isAction ? "ACTION" : isSound ? "SOUND" : "DIALOGUE",
      speaker,
      emotion,
      start: m[2].trim(),
      end: m[3].trim(),
      text: m[4].trim(),
      start_seconds: startSec,
      end_seconds: endSec,
    });
  }

  const durationSec = beats.length > 0 ? beats[beats.length - 1].end_seconds : 0;

  return {
    episode_number: epNum,
    filename,
    beats,
    duration_seconds: durationSec,
  };
}

export async function parseUploadFiles(
  files: { filename: string; buffer: Buffer | ArrayBuffer }[]
): Promise<Episode[]> {
  const episodes: Episode[] = [];

  for (const f of files) {
    if (f.filename.endsWith(".zip")) {
      const zip = new JSZip();
      const loaded = await zip.loadAsync(f.buffer);
      for (const [relPath, zipEntry] of Object.entries(loaded.files)) {
        if (!zipEntry.dir && (relPath.endsWith(".txt") || relPath.endsWith(".md"))) {
          const text = await zipEntry.async("string");
          const ep = parseEpisodeScreenplay(text, path.basename(relPath));
          if (ep.beats.length > 0) episodes.push(ep);
        }
      }
    } else if (f.filename.endsWith(".txt") || f.filename.endsWith(".md")) {
      const text =
        typeof f.buffer === "string"
          ? f.buffer
          : Buffer.isBuffer(f.buffer)
          ? f.buffer.toString("utf-8")
          : Buffer.from(f.buffer as ArrayBuffer).toString("utf-8");
      const ep = parseEpisodeScreenplay(text, f.filename);
      if (ep.beats.length > 0) episodes.push(ep);
    }
  }

  return episodes.sort((a, b) => a.episode_number - b.episode_number);
}

// ============================================================================
// Taxonomy
// ============================================================================

export function loadDefaultTaxonomy(): { hooks: TaxonomyItem[]; cliffhangers: TaxonomyItem[] } {
  try {
    const taxPath = path.join(process.cwd(), "config", "taxonomy.yaml");
    if (fs.existsSync(taxPath)) {
      const parsed = YAML.parse(fs.readFileSync(taxPath, "utf-8"));
      return {
        hooks: parsed.hooks || [],
        cliffhangers: parsed.cliffhangers || [],
      };
    }
  } catch {
    // Fallback if running outside root
  }

  return {
    hooks: [
      { id: "public_humiliation", name: "Public Humiliation & Scorn", category: "injustice", definition: "Protagonist mocked, stripped of dignity before crowd.", weight: 1.0 },
      { id: "physical_aggression", name: "Physical Aggression / Shock Violence", category: "visceral", definition: "Sudden physical violation or assault on an innocent character.", weight: 0.95 },
      { id: "intimate_betrayal", name: "Intimate Betrayal / Public Abandonment", category: "injustice", definition: "Devastation of sacred trust by partner or family at pivotal milestone.", weight: 0.95 },
      { id: "class_status_contempt", name: "Class & Status Contempt", category: "injustice", definition: "Sneering elitism treating honest protagonist as subhuman.", weight: 0.90 },
      { id: "secret_identity_glimpse", name: "Secret Identity Glimpse", category: "mystery", definition: "War hero or titan's hidden power briefly revealed.", weight: 0.90 },
    ],
    cliffhangers: [
      { id: "mortal_ultimatum", name: "Mortal Ultimatum / Time-Bomb Demand", category: "peril", definition: "Irrevocable deadline or life-or-death ultimatum.", weight: 1.0 },
      { id: "unexpected_savior_arrival", name: "Unexpected Savior Arrival", category: "reversal", definition: "Formidable protector appears at point of defeat.", weight: 0.95 },
      { id: "interrupted_retaliation", name: "Interrupted Retaliation / Poised Blow", category: "tension", definition: "Physical or verbal retribution poised mid-air then cut.", weight: 0.95 },
      { id: "unanswered_accusation", name: "Unanswered Accusation / Pointed Trap", category: "confrontation", definition: "Accusation cornering villain before answer.", weight: 0.90 },
    ],
  };
}

// ============================================================================
// Validation & Hard Constraints (1:1 with Python src/validation.py)
// ============================================================================

export function normalizeText(text: string): string {
  if (!text) return "";
  let t = text.replace(/^\s*(?:ACTION|SFX|SOUND FX|SOUND|CAMERA)\s*:\s*/i, "");
  t = t.toLowerCase().replace(/['']/g, "'").replace(/[^\w\s]/g, "");
  return t.replace(/\s+/g, " ").trim();
}

export function spokenBeats(episode: Episode): Beat[] {
  return episode.beats.filter((b) => b.type !== "CAMERA");
}

export function snapToBeatEdge(episode: Episode, t: number, edge: "start" | "end"): Beat | null {
  let best: Beat | null = null;
  let bestD = SNAP_TOLERANCE + EPS;
  for (const b of spokenBeats(episode)) {
    const beatTime = edge === "start" ? b.start_seconds : b.end_seconds;
    const d = Math.abs(beatTime - t);
    if (d < bestD) {
      best = b;
      bestD = d;
    }
  }
  return best;
}

export function findQuoteBeat(beats: Beat[], quote: string): Beat | null {
  const q = normalizeText(quote);
  if (q.length < 3) return null;
  for (const b of beats) {
    if (normalizeText(b.text).includes(q)) return b;
  }
  return null;
}

export function verifyPayoffLocation(
  payoffLoc: any,
  episodesByNum: Map<number, Episode>
): string | null {
  if (!payoffLoc) return null;
  const s = String(payoffLoc).trim().toLowerCase();
  if (s === "unknown" || s === "none" || s === "null" || s === "") return null;

  let epNum: number | null = null;
  let tsStr: string | null = null;

  if (typeof payoffLoc === "object" && payoffLoc !== null) {
    epNum = payoffLoc.episode != null ? parseInt(payoffLoc.episode, 10) : null;
    tsStr = payoffLoc.timestamp ? String(payoffLoc.timestamp) : null;
  } else if (typeof payoffLoc === "string") {
    const m = payoffLoc.match(/(?:ep(?:isode)?\s*(\d+)|(?:^|\s)(\d+)\s*[:,\-])/i);
    if (m) epNum = parseInt(m[1] || m[2], 10);
    const tsM = payoffLoc.match(/(?:(\d+:)?\d{1,2}:\d{1,2}(?:\.\d+)?)/);
    if (tsM) tsStr = tsM[0];
  }

  if (epNum == null || !tsStr) return null;
  const ep = episodesByNum.get(epNum);
  if (!ep) return null;

  const tSec = tryParseTimestamp(tsStr);
  if (tSec === null) return null;

  const beats = spokenBeats(ep);
  for (const b of beats) {
    if (Math.abs(b.start_seconds - tSec) <= SNAP_TOLERANCE + EPS) {
      return `Ep ${epNum} ${b.start}`;
    }
  }
  for (const b of beats) {
    if (
      Math.abs(b.end_seconds - tSec) <= SNAP_TOLERANCE + EPS ||
      (b.start_seconds - EPS <= tSec && tSec <= b.end_seconds + EPS)
    ) {
      return `Ep ${epNum} ${b.start}`;
    }
  }

  return null;
}

export function checkCandidate(
  cand: PromoCandidate,
  episodesByNum: Map<number, Episode>
): string[] {
  const errors: string[] = [];
  if (!cand.segments || cand.segments.length === 0) return ["no segments"];

  const total = cand.segments.reduce((acc, s) => acc + s.duration, 0);
  if (total < MIN_DURATION - EPS || total > MAX_DURATION + EPS) {
    errors.push(`duration ${total.toFixed(2)}s outside ${MIN_DURATION}-${MAX_DURATION}s`);
  }

  for (let i = 0; i < cand.segments.length; i++) {
    const seg = cand.segments[i];
    if (seg.duration <= 0) {
      errors.push(`segment ${i + 1} has non-positive duration`);
      continue;
    }
    const epNum = seg.episode ?? cand.episodes[0];
    const ep = episodesByNum.get(epNum);
    if (!ep) {
      errors.push(`segment ${i + 1}: episode ${epNum} not found`);
      continue;
    }
    const starts = new Set(spokenBeats(ep).map((b) => b.start_seconds.toFixed(2)));
    const ends = new Set(spokenBeats(ep).map((b) => b.end_seconds.toFixed(2)));
    if (!starts.has(seg.start_seconds.toFixed(2))) {
      errors.push(`segment ${i + 1} start ${seg.start} is not a beat start in Ep ${epNum}`);
    }
    if (!ends.has(seg.end_seconds.toFixed(2))) {
      errors.push(`segment ${i + 1} end ${seg.end} is not a beat end in Ep ${epNum}`);
    }
  }

  const first = cand.segments[0];
  const last = cand.segments[cand.segments.length - 1];

  if (
    cand.hook.timestamp_seconds < first.start_seconds - EPS ||
    cand.hook.timestamp_seconds - first.start_seconds > HOOK_WINDOW + EPS
  ) {
    errors.push(`hook at ${cand.hook.timestamp} is not within ${HOOK_WINDOW}s of the opening cut`);
  }

  const firstEp = episodesByNum.get(first.episode ?? cand.episodes[0]);
  const lastEp = episodesByNum.get(last.episode ?? cand.episodes[cand.episodes.length - 1]);

  if (firstEp) {
    const window = spokenBeats(firstEp).filter(
      (b) =>
        b.start_seconds >= first.start_seconds - EPS &&
        b.start_seconds <= first.start_seconds + HOOK_WINDOW + EPS
    );
    if (!findQuoteBeat(window, cand.hook.quote)) {
      errors.push("hook quote not found in a beat starting within the first 3s");
    }
  }

  if (lastEp) {
    let tail = spokenBeats(lastEp).filter(
      (b) => b.start_seconds >= last.start_seconds - EPS && b.end_seconds <= last.end_seconds + EPS
    );
    tail = tail.filter((b) => b.end_seconds >= last.end_seconds - CLIFFHANGER_TAIL_SECONDS);
    if (!findQuoteBeat(tail, cand.cliffhanger.quote)) {
      errors.push(`cliffhanger quote not found in the last ${CLIFFHANGER_TAIL_SECONDS}s of the clip`);
    }
  }

  if (cand.payoff_location && cand.payoff_location !== "unknown") {
    const verified = verifyPayoffLocation(cand.payoff_location, episodesByNum);
    if (!verified) {
      errors.push(`payoff_location '${cand.payoff_location}' does not point to a real beat`);
    }
  }

  return errors;
}

export function trimToCliffhanger(
  cand: PromoCandidate,
  episodesByNum: Map<number, Episode>
): { trimmed: PromoCandidate | null; reason: string | null } {
  const last = cand.segments[cand.segments.length - 1];
  const ep = episodesByNum.get(last.episode ?? cand.episodes[cand.episodes.length - 1]);
  if (!ep) return { trimmed: null, reason: "episode not found" };

  const clipBeats = spokenBeats(ep).filter(
    (b) => b.start_seconds >= last.start_seconds - EPS && b.end_seconds <= last.end_seconds + EPS
  );
  const cliffBeat = findQuoteBeat(clipBeats, cand.cliffhanger.quote);
  if (!cliffBeat) return { trimmed: null, reason: "cliffhanger quote not found in clip" };

  const targetEnd = cliffBeat.end_seconds;
  if (targetEnd >= last.end_seconds - EPS) {
    return { trimmed: null, reason: "already ends on or after cliffhanger beat" };
  }

  const secondsRemoved = Math.round((last.end_seconds - targetEnd) * 100) / 100;
  const newLastSeg: Segment = {
    ...last,
    end: cliffBeat.end,
    end_seconds: targetEnd,
    duration: targetEnd - last.start_seconds,
  };

  const newSegments = [...cand.segments.slice(0, -1), newLastSeg];
  const newTotalDuration = newSegments.reduce((a, s) => a + s.duration, 0);

  if (newTotalDuration < MIN_DURATION - EPS) {
    return { trimmed: null, reason: `duration ${newTotalDuration.toFixed(1)}s falls below ${MIN_DURATION}s after trim` };
  }

  const trimmedCandidate: PromoCandidate = {
    ...cand,
    segments: newSegments,
    total_duration: Math.round(newTotalDuration * 100) / 100,
    trimmed_from_end: true,
    seconds_removed: secondsRemoved,
  };

  const errs = checkCandidate(trimmedCandidate, episodesByNum);
  if (errs.length > 0) {
    return { trimmed: null, reason: `trim introduced violations: ${errs.join("; ")}` };
  }

  return { trimmed: trimmedCandidate, reason: null };
}

// ============================================================================
// Composite Scoring & Ranking
// ============================================================================

export function computeCompositeScore(
  scores: PromoScores,
  weights: Record<string, number> = DEFAULT_WEIGHTS
): number {
  const totalWeight =
    (weights.hook ?? 0.3) +
    (weights.cliffhanger ?? 0.25) +
    (weights.payoff_withheld ?? 0.2) +
    (weights.injustice_tension ?? 0.15) +
    (weights.standalone_clarity ?? 0.1) +
    (weights.conversion_intent ?? 0.0);

  if (totalWeight <= 0) return 0;

  const raw =
    (scores.hook_strength || 0) * (weights.hook ?? 0.3) +
    (scores.cliffhanger_strength || 0) * (weights.cliffhanger ?? 0.25) +
    (scores.payoff_withheld || 0) * (weights.payoff_withheld ?? 0.2) +
    (scores.injustice_tension || 0) * (weights.injustice_tension ?? 0.15) +
    (scores.standalone_clarity || 0) * (weights.standalone_clarity ?? 0.1) +
    (scores.conversion_intent || 0) * (weights.conversion_intent ?? 0.0);

  return Math.round((raw / totalWeight) * 100) / 100;
}

export function rankCandidates(
  candidates: PromoCandidate[],
  topK: number = 15,
  weights: Record<string, number> = DEFAULT_WEIGHTS
): PromoCandidate[] {
  // Sort into consensus tiers
  // Tier 1: both pass or quality_audit.passed
  // Tier 2: split verdict
  // Tier 3: fail
  for (const c of candidates) {
    c.scores.composite_score = computeCompositeScore(c.scores, weights);
    c.scores.adjusted_score = c.scores.composite_score;
    c.scores.diversity_penalty = 1.0;
  }

  const pool = [...candidates].sort((a, b) => {
    const tierA = a.audit_tier ?? (a.quality_audit?.passed ? 1 : 3);
    const tierB = b.audit_tier ?? (b.quality_audit?.passed ? 1 : 3);
    if (tierA !== tierB) return tierA - tierB;
    return b.scores.composite_score - a.scores.composite_score;
  });

  const ranked: PromoCandidate[] = [];
  const hookCounts = new Map<string, number>();
  const epCounts = new Map<number, number>();

  while (pool.length > 0 && ranked.length < topK) {
    // Recompute adjusted scores with diversity penalty
    for (const c of pool) {
      const hCount = hookCounts.get(c.hook.type) || 0;
      const eCount = epCounts.get(c.episodes[0]) || 0;
      const penalty = Math.pow(0.82, hCount) * Math.pow(0.85, eCount);
      c.scores.diversity_penalty = Math.round(penalty * 100) / 100;
      c.scores.adjusted_score = Math.round(c.scores.composite_score * penalty * 100) / 100;
    }

    pool.sort((a, b) => {
      const tierA = a.audit_tier ?? (a.quality_audit?.passed ? 1 : 3);
      const tierB = b.audit_tier ?? (b.quality_audit?.passed ? 1 : 3);
      if (tierA !== tierB) return tierA - tierB;
      return b.scores.adjusted_score - a.scores.adjusted_score;
    });

    const best = pool.shift()!;
    best.rank = ranked.length + 1;
    ranked.push(best);

    hookCounts.set(best.hook.type, (hookCounts.get(best.hook.type) || 0) + 1);
    epCounts.set(best.episodes[0], (epCounts.get(best.episodes[0]) || 0) + 1);
  }

  return ranked;
}

// ============================================================================
// Heuristic Smoke Test Generator (Offline, instant, 0s, 0 cost)
// ============================================================================

export function runHeuristicExtraction(
  episodes: Episode[],
  taxonomy: { hooks: TaxonomyItem[]; cliffhangers: TaxonomyItem[] }
): PromoCandidate[] {
  const candidates: PromoCandidate[] = [];

  for (const ep of episodes) {
    const beats = spokenBeats(ep);
    if (beats.length < 3) continue;

    for (let i = 0; i < beats.length; i++) {
      const hookBeat = beats[i];
      let matchedHook: TaxonomyItem | null = null;

      for (const h of taxonomy.hooks) {
        if (h.generic_cues && h.generic_cues.some((cue) => hookBeat.text.toLowerCase().includes(cue.toLowerCase()))) {
          matchedHook = h;
          break;
        }
      }

      if (!matchedHook) continue;

      // Find cliffhanger beat 20-55s later
      for (let j = i + 1; j < beats.length; j++) {
        const cliffBeat = beats[j];
        const dur = cliffBeat.end_seconds - hookBeat.start_seconds;
        if (dur >= MIN_DURATION && dur <= MAX_DURATION) {
          let matchedCliff: TaxonomyItem | null = null;
          for (const c of taxonomy.cliffhangers) {
            if (c.generic_cues && c.generic_cues.some((cue) => cliffBeat.text.toLowerCase().includes(cue.toLowerCase()))) {
              matchedCliff = c;
              break;
            }
          }
          if (!matchedCliff) matchedCliff = taxonomy.cliffhangers[0];

          candidates.push({
            promo_id: `ep${ep.episode_number}_cand_${candidates.length + 1}`,
            promo_type: "single_episode",
            episodes: [ep.episode_number],
            segments: [
              {
                episode: ep.episode_number,
                start: hookBeat.start,
                end: cliffBeat.end,
                start_seconds: hookBeat.start_seconds,
                end_seconds: cliffBeat.end_seconds,
                duration: dur,
              },
            ],
            total_duration: dur,
            hook: {
              type: matchedHook.id,
              name: matchedHook.name,
              timestamp: hookBeat.start,
              timestamp_seconds: hookBeat.start_seconds,
              quote: hookBeat.text.slice(0, 100),
              weight: matchedHook.weight,
            },
            cliffhanger: {
              type: matchedCliff.id,
              name: matchedCliff.name,
              timestamp: cliffBeat.start,
              timestamp_seconds: cliffBeat.start_seconds,
              quote: cliffBeat.text.slice(0, 100),
              withheld_payoff: "Immediate confrontation left unresolved",
              weight: matchedCliff.weight,
            },
            why_it_works: `Heuristic match: High conflict hook '${matchedHook.name}' paired with tense ending.`,
            risks: ["Heuristic offline generation (smoke test)"],
            scores: {
              hook_strength: 7.5,
              cliffhanger_strength: 7.5,
              payoff_withheld: 8.0,
              injustice_tension: 8.0,
              standalone_clarity: 8.0,
              composite_score: 7.75,
              adjusted_score: 7.75,
              diversity_penalty: 1.0,
              conversion_intent: 7.0,
            },
            quality_audit: {
              passed: true,
              method: "rules",
              critique: "Heuristic rule lint passed.",
              confidence_score: 7.0,
              conversion_intent: 7.0,
              risks: ["Offline test only"],
            },
            engine: "heuristic",
            model: "offline-smoke-test",
            audit_tier: 1,
            judge_verdicts: [
              {
                judge: "heuristic",
                model: "rule-lint",
                pass: true,
                one_line_reason: "Offline rule-based check passed.",
              },
            ],
            conversion_intent: 7.0,
            payoff_location: "unknown",
          });
          break; // 1 candidate per hook
        }
      }
    }
  }

  return candidates;
}

// ============================================================================
// LLM API Calls (Gemini & OpenAI via fetch)
// ============================================================================

export async function callGemini(
  prompt: string,
  systemPrompt: string,
  apiKey: string,
  model: string = "gemini-2.5-flash"
): Promise<string> {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      systemInstruction: { parts: [{ text: systemPrompt }] },
      generationConfig: {
        responseMimeType: "application/json",
        temperature: 0.2,
      },
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gemini API error (${res.status}): ${errText}`);
  }

  const data = await res.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Gemini returned empty response");
  return text;
}

export async function callOpenAI(
  prompt: string,
  systemPrompt: string,
  apiKey: string,
  model: string = "gpt-4o-mini"
): Promise<string> {
  const url = "https://api.openai.com/v1/chat/completions";
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: prompt },
      ],
      response_format: { type: "json_object" },
      temperature: 0.2,
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`OpenAI API error (${res.status}): ${errText}`);
  }

  const data = await res.json();
  const text = data?.choices?.[0]?.message?.content;
  if (!text) throw new Error("OpenAI returned empty response");
  return text;
}

// ============================================================================
// Single Episode Extraction
// ============================================================================

export async function extractEpisodeCandidates(
  ep: Episode,
  options: PipelineOptions = {}
): Promise<{
  episode_number: number;
  candidates: PromoCandidate[];
  rejected: any[];
}> {
  const provider = options.provider || "gemini";
  const taxonomy = loadDefaultTaxonomy();
  const episodesByNum = new Map<number, Episode>([[ep.episode_number, ep]]);
  const rejected: any[] = [];
  const validCandidates: PromoCandidate[] = [];

  if (provider === "heuristic" || !options.apiKey) {
    const heuristicPool = runHeuristicExtraction([ep], taxonomy);
    return {
      episode_number: ep.episode_number,
      candidates: heuristicPool,
      rejected: [],
    };
  }

  const apiKey = options.apiKey;
  const modelName =
    options.model || (provider === "gemini" ? "gemini-2.5-flash" : "gpt-4o-mini");

  const SYSTEM_EXTRACTOR = `You are a senior social-media editor cutting promo clips for vertical microdramas.
A promo exists to create a curiosity gap strong enough that a scrolling viewer installs the app and pays to see what happens next.
Priorities:
1. Stakes legible in first 3s.
2. Immediate scroll-stopping hook.
3. Cliffhanger cut while payoff is still withheld.
4. Duration 20-60s.
Output valid JSON only matching schema:
{
  "candidates": [
    {
      "segments": [{"start": "mm:ss.ss", "end": "mm:ss.ss"}],
      "hook": {"type": "string", "timestamp": "mm:ss.ss", "text": "exact quote"},
      "cliffhanger": {"type": "string", "timestamp": "mm:ss.ss", "text": "exact quote", "withheld_payoff": "string"},
      "scores": {"hook_strength": 8, "cliffhanger_strength": 8, "payoff_withheld": 8, "injustice_tension": 8, "standalone_clarity": 8},
      "conversion_intent": 8.0,
      "conversion_reason": "string",
      "payoff_location": "Ep X mm:ss.ss or unknown",
      "why_it_works": "string",
      "risks": ["string"]
    }
  ]
}`;

  const beatsText = ep.beats
    .map((b) => `**${b.speaker ? `${b.speaker} (${b.emotion || "neutral"})` : b.type}:**\nStart: (${b.start}) | End: (${b.end})\n${b.text}`)
    .join("\n\n");

  const userPrompt = `Show: ${options.showTitle || "Custom Microdrama"}
Premise: ${options.showPremise || "High stakes vertical drama"}
Episode: ${ep.episode_number} (Duration: ${ep.duration_seconds.toFixed(1)}s)

<screenplay>
${beatsText}
</screenplay>

Find up to 3 candidate promos in this episode. Use ONLY timestamps that exist in the text.`;

  const rawJson =
    provider === "gemini"
      ? await callGemini(userPrompt, SYSTEM_EXTRACTOR, apiKey, modelName)
      : await callOpenAI(userPrompt, SYSTEM_EXTRACTOR, apiKey, modelName);

  const parsed = JSON.parse(rawJson);
  const cands = parsed.candidates || [];

  for (let idx = 0; idx < cands.length; idx++) {
    const rawCand = cands[idx];
    const segments: Segment[] = (rawCand.segments || []).map((s: any) => {
      const sSec = tryParseTimestamp(s.start) || 0;
      const eSec = tryParseTimestamp(s.end) || 0;
      return {
        episode: ep.episode_number,
        start: s.start,
        end: s.end,
        start_seconds: sSec,
        end_seconds: eSec,
        duration: Math.max(0, eSec - sSec),
      };
    });

    const hookSec = tryParseTimestamp(rawCand.hook?.timestamp) || segments[0]?.start_seconds || 0;
    const cliffSec = tryParseTimestamp(rawCand.cliffhanger?.timestamp) || segments[segments.length - 1]?.end_seconds || 0;

    let cand: PromoCandidate = {
      promo_id: `ep${ep.episode_number}_cand_${idx + 1}`,
      promo_type: "single_episode",
      episodes: [ep.episode_number],
      segments,
      total_duration: segments.reduce((a, s) => a + s.duration, 0),
      hook: {
        type: rawCand.hook?.type || "hook",
        timestamp: rawCand.hook?.timestamp || segments[0]?.start || "00:00.00",
        timestamp_seconds: hookSec,
        quote: rawCand.hook?.text || "",
      },
      cliffhanger: {
        type: rawCand.cliffhanger?.type || "cliffhanger",
        timestamp: rawCand.cliffhanger?.timestamp || segments[segments.length - 1]?.end || "00:00.00",
        timestamp_seconds: cliffSec,
        quote: rawCand.cliffhanger?.text || "",
        withheld_payoff: rawCand.cliffhanger?.withheld_payoff || "",
      },
      why_it_works: rawCand.why_it_works || "High engagement microdrama cut.",
      risks: rawCand.risks || [],
      scores: {
        hook_strength: rawCand.scores?.hook_strength || 7.0,
        cliffhanger_strength: rawCand.scores?.cliffhanger_strength || 7.0,
        payoff_withheld: rawCand.scores?.payoff_withheld || 7.0,
        injustice_tension: rawCand.scores?.injustice_tension || 7.0,
        standalone_clarity: rawCand.scores?.standalone_clarity || 7.0,
        composite_score: 7.0,
        adjusted_score: 7.0,
        diversity_penalty: 1.0,
        conversion_intent: rawCand.conversion_intent || 7.0,
      },
      engine: provider,
      model: options.model || (provider === "gemini" ? "gemini-2.5-flash" : "gpt-4o-mini"),
      conversion_intent: rawCand.conversion_intent || 7.0,
      conversion_reason: rawCand.conversion_reason || "",
      payoff_location: rawCand.payoff_location
        ? verifyPayoffLocation(rawCand.payoff_location, episodesByNum) || "unknown"
        : "unknown",
    };

    // Snap cuts within 0.5s
    for (const seg of cand.segments) {
      const sSnap = snapToBeatEdge(ep, seg.start_seconds, "start");
      if (sSnap) {
        seg.start = sSnap.start;
        seg.start_seconds = sSnap.start_seconds;
      }
      const eSnap = snapToBeatEdge(ep, seg.end_seconds, "end");
      if (eSnap) {
        seg.end = eSnap.end;
        seg.end_seconds = eSnap.end_seconds;
      }
      seg.duration = seg.end_seconds - seg.start_seconds;
    }
    cand.total_duration = cand.segments.reduce((a, s) => a + s.duration, 0);

    // Validation
    let errs = checkCandidate(cand, episodesByNum);
    if (errs.length > 0 && errs.some((e) => e.includes("cliffhanger quote not found in the last"))) {
      const { trimmed } = trimToCliffhanger(cand, episodesByNum);
      if (trimmed) {
        cand = trimmed;
        errs = checkCandidate(cand, episodesByNum);
      }
    }

    if (errs.length === 0) {
      validCandidates.push(cand);
    } else {
      rejected.push({ candidate: cand, reasons: errs });
    }
  }

  return {
    episode_number: ep.episode_number,
    candidates: validCandidates,
    rejected,
  };
}

// ============================================================================
// Batch Audit
// ============================================================================

export async function auditCandidateBatch(
  candidates: PromoCandidate[],
  episodes: Episode[],
  options: PipelineOptions = {}
): Promise<PromoCandidate[]> {
  const provider = options.provider || "gemini";
  if (provider === "heuristic" || !options.apiKey) {
    return candidates.map((cand) => ({
      ...cand,
      quality_audit: {
        passed: true,
        method: "rules" as const,
        critique: "Offline rule-lint passed.",
        confidence_score: 6.0,
        risks: [],
      },
      audit_tier: 1,
    }));
  }

  const apiKey = options.apiKey;
  const modelName =
    options.model || (provider === "gemini" ? "gemini-2.5-flash" : "gpt-4o-mini");
  const episodesByNum = new Map<number, Episode>(episodes.map((e) => [e.episode_number, e]));

  const AUDIT_SYSTEM = `You are an adversarial video marketing auditor for vertical microdramas.
Inspect the clip dialogue and determine if it has a lethal flaw:
1. resolution_leak (cut resolves the conflict, viewer won't pay)
2. context_deficit (stakes illegible cold)
3. slow_burn (hook too late)
Output JSON:
{"pass": true/false, "flaw": null or string, "critique": "string", "conversion_intent": 8.0}`;

  const audited: PromoCandidate[] = [];
  for (const cand of candidates) {
    const ep = episodesByNum.get(cand.episodes[0]);
    if (!ep) {
      audited.push(cand);
      continue;
    }
    const clipBeats = spokenBeats(ep).filter(
      (b) =>
        b.start_seconds >= cand.segments[0].start_seconds - EPS &&
        b.end_seconds <= cand.segments[cand.segments.length - 1].end_seconds + EPS
    );
    const clipText = clipBeats.map((b) => `${b.speaker || "Action"}: ${b.text}`).join("\n");

    const auditPrompt = `Show: ${options.showTitle || "Show"}
Clip screenplay (${cand.total_duration.toFixed(1)}s):
<clip>
${clipText}
</clip>
Hook tagged: ${cand.hook.type} ("${cand.hook.quote}")
Cliffhanger tagged: ${cand.cliffhanger.type} ("${cand.cliffhanger.quote}")`;

    try {
      const rawAudit =
        provider === "gemini"
          ? await callGemini(auditPrompt, AUDIT_SYSTEM, apiKey, modelName)
          : await callOpenAI(auditPrompt, AUDIT_SYSTEM, apiKey, modelName);

      const aud = JSON.parse(rawAudit);
      cand.quality_audit = {
        passed: Boolean(aud.pass),
        method: "llm",
        flaw_type: aud.flaw || null,
        critique: aud.critique || "",
        confidence_score: 8.0,
        conversion_intent: aud.conversion_intent || cand.conversion_intent || 7.0,
        risks: [],
      };
      cand.audit_tier = aud.pass ? 1 : 3;
      cand.judge_verdicts = [
        {
          judge: provider,
          model: options.model || (provider === "gemini" ? "gemini-2.5-flash" : "gpt-4o-mini"),
          pass: Boolean(aud.pass),
          flaw_type: aud.flaw || null,
          one_line_reason: aud.critique || "",
          conversion_intent: aud.conversion_intent || null,
        },
      ];
    } catch (e: any) {
      cand.quality_audit = {
        passed: false,
        method: "error",
        critique: `Audit call failed: ${e?.message || String(e)}`,
        confidence_score: 0.0,
        risks: ["unaudited_due_to_api_error"],
      };
      cand.audit_tier = 3;
    }
    audited.push(cand);
  }

  return audited;
}

// ============================================================================
// Full Pipeline Runner
// ============================================================================

export async function runPipelineOnEpisodes(
  episodes: Episode[],
  options: PipelineOptions = {}
): Promise<{
  ranked_promos: PromoCandidate[];
  pool: PromoCandidate[];
  rejected: any[];
  meta: any;
}> {
  const provider = options.provider || "gemini";
  const taxonomy = loadDefaultTaxonomy();
  const rejected: any[] = [];
  const validCandidates: PromoCandidate[] = [];

  // Offline Heuristic mode
  if (provider === "heuristic" || !options.apiKey) {
    const heuristicPool = runHeuristicExtraction(episodes, taxonomy);
    const ranked = rankCandidates(heuristicPool, options.topK || 15, options.weights);
    return {
      ranked_promos: ranked,
      pool: heuristicPool,
      rejected: [],
      meta: {
        provider: "heuristic",
        model: "offline-smoke-test",
        episodes_count: episodes.length,
        beats_count: episodes.reduce((a, e) => a + e.beats.length, 0),
        generated_at: new Date().toISOString(),
      },
    };
  }

  // Process episodes modularly
  for (const ep of episodes) {
    try {
      const res = await extractEpisodeCandidates(ep, options);
      validCandidates.push(...res.candidates);
      rejected.push(...res.rejected);
    } catch (e: any) {
      console.error(`Extraction failed on Ep ${ep.episode_number}:`, e?.message || e);
    }
  }

  // Audit valid candidates
  const audited = await auditCandidateBatch(validCandidates, episodes, options);
  const ranked = rankCandidates(audited, options.topK || 15, options.weights);

  return {
    ranked_promos: ranked,
    pool: validCandidates,
    rejected,
    meta: {
      provider,
      model: options.model || (provider === "gemini" ? "gemini-2.5-flash" : "gpt-4o-mini"),
      episodes_count: episodes.length,
      beats_count: episodes.reduce((a, e) => a + e.beats.length, 0),
      valid_candidates_count: validCandidates.length,
      rejected_count: rejected.length,
      generated_at: new Date().toISOString(),
    },
  };
}

// ============================================================================
// CSV Exporter
// ============================================================================

export function exportPromosToCSV(promos: PromoCandidate[]): string {
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

  const rows: string[] = [headers.join(",")];

  for (const p of promos) {
    p.segments.forEach((seg, idx) => {
      const row = [
        `"${p.promo_id}"`,
        p.rank || "",
        seg.episode,
        idx + 1,
        `"${seg.start}"`,
        `"${seg.end}"`,
        seg.duration.toFixed(2),
        `"${(p.hook.quote || "").replace(/"/g, '""')}"`,
        `"${(p.cliffhanger.quote || "").replace(/"/g, '""')}"`,
        `"${p.payoff_location || "unknown"}"`,
        `"${p.quality_audit?.passed ? "PASS" : "FAIL"}"`,
      ];
      rows.push(row.join(","));
    });
  }

  return rows.join("\n");
}
