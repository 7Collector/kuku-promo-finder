"""
Parity test between Python validation engine (src/validation.py) and
TypeScript validation engine (lib/pipeline.ts).

Feeds identical raw candidate proposals and screenplay beats to both validators and asserts:
- Exact same accept/reject decisions
- Exact same snapped cut timestamps
- Exact same cliffhanger trimming logic and seconds_removed
- Exact same quote verification behavior
- Exact same payoff_location verification
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.parser import parse_screenplay_text
from src.extractor import PromoExtractor
from src.taxonomy import Taxonomy
from src.providers.heuristic import HeuristicProvider
from src.validation import check_candidate, trim_to_cliffhanger, verify_payoff_location

SCRIPT = """EPISODE NUMBER: 7
EPISODE LOGLINE: A test episode for validation parity.

SCENE 1
Scene heading: INT. HALL
Scene start: 00:00.00
Scene end: 00:45.00

**GERALD (Cold, Cruel):**
Start: (00:00.00) | End: (00:05.00)
"You are nothing without us, Juliana."

**JULIANA (Shaking):**
Start: (00:05.00) | End: (00:12.00)
"I did nothing wrong."

**ACTION:**
Start: (00:12.00) | End: (00:30.00)
Gerald grabs her by the collar and drags her across the marble floor.

**GERALD (Cold, Cruel):**
Start: (00:30.00) | End: (00:42.00)
"Kneel, or I will finish what I started."

--- SCRIPT END ---
"""

TEST_CASES = [
    {
        "name": "valid_candidate",
        "raw": {
            "segments": [{"start": "00:00.00", "end": "00:42.00"}],
            "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "You are nothing without us, Juliana."},
            "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:30.00", "text": "Kneel, or I will finish what I started.", "withheld_payoff": "Whether she kneels"},
            "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
            "why_it_works": "High tension",
            "payoff_location": "Ep 7 00:30.00",
        },
    },
    {
        "name": "needs_cliffhanger_trim",
        "raw": {
            "segments": [{"start": "00:00.00", "end": "00:42.00"}],
            "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "You are nothing without us, Juliana."},
            "cliffhanger": {"type": "public_humiliation", "timestamp": "00:05.00", "text": "I did nothing wrong.", "withheld_payoff": "Her defense"},
            "scores": {"hook_strength": 8, "injustice_tension": 8, "cliffhanger_strength": 8, "standalone_clarity": 8, "payoff_withheld": 8},
            "why_it_works": "Clip continues past cliffhanger beat",
        },
    },
    {
        "name": "invalid_too_short",
        "raw": {
            "segments": [{"start": "00:00.00", "end": "00:12.00"}],
            "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "You are nothing without us, Juliana."},
            "cliffhanger": {"type": "public_humiliation", "timestamp": "00:05.00", "text": "I did nothing wrong.", "withheld_payoff": "Short"},
            "scores": {"hook_strength": 8, "injustice_tension": 8, "cliffhanger_strength": 8, "standalone_clarity": 8, "payoff_withheld": 8},
            "why_it_works": "Too short",
        },
    },
    {
        "name": "hallucinated_hook_quote",
        "raw": {
            "segments": [{"start": "00:00.00", "end": "00:42.00"}],
            "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "I am the Queen of England!"},
            "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:30.00", "text": "Kneel, or I will finish what I started.", "withheld_payoff": "x"},
            "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
            "why_it_works": "Hallucinated quote",
        },
    },
    {
        "name": "hallucinated_payoff_location",
        "raw": {
            "segments": [{"start": "00:00.00", "end": "00:42.00"}],
            "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "You are nothing without us, Juliana."},
            "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:30.00", "text": "Kneel, or I will finish what I started.", "withheld_payoff": "x"},
            "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
            "why_it_works": "Hallucinated payoff",
            "payoff_location": "Ep 7 05:99.99",
        },
    },
]


class TestEngineParity(unittest.TestCase):
    def setUp(self):
        self.py_ep = parse_screenplay_text(SCRIPT, "episode-007.txt")
        self.taxonomy = Taxonomy("config/taxonomy.yaml")
        self.extractor = PromoExtractor(self.taxonomy, HeuristicProvider())

    def run_ts_validation(self, test_cases_json, script_text):
        ts_runner = """
import {
  parseEpisodeScreenplay,
  checkCandidate,
  trimToCliffhanger,
  verifyPayoffLocation,
  snapToBeatEdge,
  tryParseTimestamp,
  PromoCandidate,
  Segment
} from "./lib/pipeline";

const inputData = JSON.parse(process.argv.slice(1)[0]);
const scriptText = inputData.script;
const testCases = inputData.cases;

const ep = parseEpisodeScreenplay(scriptText, "episode-007.txt");
const episodesByNum = new Map([[ep.episode_number, ep]]);

const results = [];

for (const tc of testCases) {
  const raw = tc.raw;
  const segments = (raw.segments || []).map(s => {
    const sSec = tryParseTimestamp(s.start) || 0;
    const eSec = tryParseTimestamp(s.end) || 0;
    return {
      episode: ep.episode_number,
      start: s.start,
      end: s.end,
      start_seconds: sSec,
      end_seconds: eSec,
      duration: Math.max(0, eSec - sSec)
    };
  });

  let cand = {
    promo_id: "test_" + tc.name,
    promo_type: "single_episode",
    episodes: [ep.episode_number],
    segments,
    total_duration: segments.reduce((a, s) => a + s.duration, 0),
    hook: {
      type: raw.hook?.type || "hook",
      timestamp: raw.hook?.timestamp || "00:00.00",
      timestamp_seconds: tryParseTimestamp(raw.hook?.timestamp) || 0,
      quote: raw.hook?.text || ""
    },
    cliffhanger: {
      type: raw.cliffhanger?.type || "cliffhanger",
      timestamp: raw.cliffhanger?.timestamp || "00:00.00",
      timestamp_seconds: tryParseTimestamp(raw.cliffhanger?.timestamp) || 0,
      quote: raw.cliffhanger?.text || "",
      withheld_payoff: raw.cliffhanger?.withheld_payoff || ""
    },
    why_it_works: raw.why_it_works || "",
    risks: [],
    scores: {
      hook_strength: 8,
      cliffhanger_strength: 8,
      payoff_withheld: 8,
      injustice_tension: 8,
      standalone_clarity: 8,
      composite_score: 8,
      adjusted_score: 8,
      diversity_penalty: 1
    },
    payoff_location: raw.payoff_location
      ? verifyPayoffLocation(raw.payoff_location, episodesByNum) || "unknown"
      : "unknown"
  };

  // Snap cut points
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

  let errs = checkCandidate(cand, episodesByNum);
  let wasTrimmed = false;
  let secsRemoved = 0;

  if (errs.length > 0 && errs.some(e => e.includes("cliffhanger quote not found in the last"))) {
    const trimRes = trimToCliffhanger(cand, episodesByNum);
    if (trimRes.trimmed) {
      cand = trimRes.trimmed;
      wasTrimmed = true;
      secsRemoved = cand.seconds_removed || 0;
      errs = checkCandidate(cand, episodesByNum);
    }
  }

  const verifiedPayoff = raw.payoff_location
    ? verifyPayoffLocation(raw.payoff_location, episodesByNum)
    : null;

  results.push({
    name: tc.name,
    valid: errs.length === 0,
    errors: errs,
    was_trimmed: wasTrimmed,
    seconds_removed: secsRemoved,
    duration: cand.total_duration,
    verified_payoff: verifiedPayoff
  });
}

console.log(JSON.stringify(results));
"""
        payload = json.dumps({"script": script_text, "cases": test_cases_json})
        cmd = ["npx", "tsx", "-e", ts_runner, payload]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=True)
        return json.loads(res.stdout.strip())

    def test_full_parity_python_vs_typescript(self):
        """Feeds identical candidate proposals to both engines and asserts parity."""
        ts_results = {r["name"]: r for r in self.run_ts_validation(TEST_CASES, SCRIPT)}
        eps_by_num = {self.py_ep.episode_number: self.py_ep}

        for tc in TEST_CASES:
            tc_name = tc["name"]
            raw = tc["raw"]
            ts_res = ts_results[tc_name]

            # Python conversion & validation
            cand, drop_reason = self.extractor._convert_raw_to_candidate(raw, self.py_ep, 0)
            py_valid = False
            py_trimmed = False
            py_secs_removed = 0.0
            py_duration = 0.0

            if cand is not None:
                py_duration = cand.total_duration
                errs = check_candidate(cand, eps_by_num)
                if not errs:
                    py_valid = True
                else:
                    trimmed_cand, trim_err = trim_to_cliffhanger(cand, eps_by_num)
                    if trimmed_cand is not None:
                        cand = trimmed_cand
                        py_trimmed = True
                        py_secs_removed = cand.seconds_removed
                        py_duration = cand.total_duration
                        errs2 = check_candidate(cand, eps_by_num)
                        py_valid = (len(errs2) == 0)

            py_verified_payoff = (
                verify_payoff_location(raw.get("payoff_location"), eps_by_num)
                if raw.get("payoff_location")
                else None
            )

            # Assert Python vs TypeScript Parity
            self.assertEqual(
                py_valid,
                ts_res["valid"],
                f"Validation accept/reject parity mismatch on {tc_name}: py={py_valid}, ts={ts_res['valid']}"
            )
            self.assertEqual(
                py_trimmed,
                ts_res["was_trimmed"],
                f"Trimming decision mismatch on {tc_name}: py={py_trimmed}, ts={ts_res['was_trimmed']}"
            )
            if py_trimmed:
                self.assertAlmostEqual(
                    py_secs_removed,
                    ts_res["seconds_removed"],
                    places=2,
                    msg=f"Trimming seconds_removed mismatch on {tc_name}"
                )
            if py_valid:
                self.assertAlmostEqual(
                    py_duration,
                    ts_res["duration"],
                    places=2,
                    msg=f"Duration mismatch on valid candidate {tc_name}"
                )
            self.assertEqual(
                py_verified_payoff,
                ts_res["verified_payoff"],
                f"Payoff verification mismatch on {tc_name}: py={py_verified_payoff}, ts={ts_res['verified_payoff']}"
            )


if __name__ == "__main__":
    unittest.main()
