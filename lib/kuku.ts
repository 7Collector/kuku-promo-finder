import fs from "fs";
import path from "path";
import YAML from "yaml";

// Locations are configurable so the UI follows whichever show/run is on disk.
const ROOT = process.cwd();
export const ASSETS_DIR = process.env.KUKU_ASSETS_DIR || path.join(ROOT, "assets", "I Married a Broken Soldier. He was a Duke");
export const OUTPUT_DIR = process.env.KUKU_OUTPUT_DIR || path.join(ROOT, "outputs");
export const SHOW = process.env.KUKU_SHOW || "broken_soldier";

export function readJson<T = any>(file: string): T | null {
  try {
    return JSON.parse(fs.readFileSync(file, "utf-8")) as T;
  } catch {
    return null;
  }
}

export function readMeta(): any | null {
  return readJson(path.join(OUTPUT_DIR, "promos.meta.json"));
}

export function readShowProfile(): any {
  const f = path.join(ROOT, "config", "shows", `${SHOW}.yaml`);
  return fs.existsSync(f) ? YAML.parse(fs.readFileSync(f, "utf-8")) : {};
}

export type EpisodeFile = { number: number; filename: string };

export function listEpisodes(): EpisodeFile[] {
  if (!fs.existsSync(ASSETS_DIR)) return [];
  const out: EpisodeFile[] = [];
  for (const filename of fs.readdirSync(ASSETS_DIR).filter((f) => f.endsWith(".txt"))) {
    const head = fs.readFileSync(path.join(ASSETS_DIR, filename), "utf-8").slice(0, 2000);
    const m = head.match(/EPISODE NUMBER:\s*(?:Episode\s*)?(\d+)/i) || filename.match(/episode[-_ ]?0*(\d+)/i);
    if (m) out.push({ number: parseInt(m[1], 10), filename });
  }
  return out.sort((a, b) => a.number - b.number);
}

// Same grammar as src/parser.py. JS has no \Z, so the end anchor is `$` without the `m` flag,
// and the script-end marker is excluded exactly like the Python parser does.
const BEAT_RE =
  /\*\*([^*]+)\*\*\s*\nStart:\s*\(?([0-9:.]+)\)?\s*\|\s*End:\s*\(?([0-9:.]+)\)?\s*\n([\s\S]*?)(?=\n\*\*[^*]+\*\*\s*\nStart:|\nSCENE\s+\d+|\n-{3,}\s*SCRIPT END|$)/g;

export function parseBeats(content: string) {
  return Array.from(content.matchAll(BEAT_RE)).map((m) => {
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
    return {
      type: isCamera ? "CAMERA" : isAction ? "ACTION" : isSound ? "SOUND" : "DIALOGUE",
      speaker,
      emotion,
      start: m[2].trim(),
      end: m[3].trim(),
      text: m[4].trim(),
    };
  });
}
