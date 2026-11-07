"""Validation layer: LLM proposals must be snapped to real beats and carry real quotes."""

import unittest
from src.extractor import PromoExtractor
from src.parser import parse_screenplay_text
from src.providers.heuristic import HeuristicProvider
from src.taxonomy import Taxonomy
from src.utils.timestamps import try_parse_timestamp
from src.validation import check_candidate

SCRIPT = """EPISODE NUMBER: 7
EPISODE LOGLINE: A test.

SCENE 1
Scene heading: INT. HALL
Scene start: 00:00.00
Scene end: 00:40.00

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


def raw(**over):
    base = {
        "segments": [{"start": "00:00.00", "end": "00:42.00"}],
        "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "You are nothing without us, Juliana."},
        "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:42.00",
                        "text": "Kneel, or I will finish what I started.", "withheld_payoff": "x"},
        "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9,
                   "standalone_clarity": 9, "payoff_withheld": 9},
        "why_it_works": "w",
    }
    base.update(over)
    return base


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.ep = parse_screenplay_text(SCRIPT, "episode-007.txt")
        self.ex = PromoExtractor(Taxonomy("config/taxonomy.yaml"), HeuristicProvider())

    def convert(self, rc):
        return self.ex._convert_raw_to_candidate(rc, self.ep, 0)

    def test_script_end_marker_not_in_last_beat(self):
        self.assertNotIn("SCRIPT END", self.ep.all_beats[-1].text)

    def test_valid_candidate_accepted_and_passes_check(self):
        cand, reason = self.convert(raw())
        self.assertIsNotNone(cand, reason)
        self.assertEqual(check_candidate(cand, {7: self.ep}), [])

    def test_near_miss_timestamp_is_snapped_to_beat_edge(self):
        cand, _ = self.convert(raw(segments=[{"start": "00:00.30", "end": "00:41.80"}]))
        self.assertEqual((cand.segments[0].start, cand.segments[0].end), ("00:00.00", "00:42.00"))

    def test_off_beat_cut_rejected(self):
        cand, reason = self.convert(raw(segments=[{"start": "00:00.00", "end": "00:36.00"}]))
        self.assertIsNone(cand)
        self.assertIn("beat edge", reason)

    def test_invented_quote_rejected(self):
        bad = raw(hook={"type": "public_humiliation", "timestamp": "00:00.00", "text": "Something never said."})
        cand, reason = self.convert(bad)
        self.assertIsNone(cand)
        self.assertIn("hook quote", reason)

    def test_action_prefix_in_quote_tolerated(self):
        rc = raw(cliffhanger={"type": "mortal_ultimatum", "timestamp": "00:42.00",
                              "text": "Kneel, or I will finish what I started.", "withheld_payoff": "x"})
        self.assertIsNotNone(self.convert(rc)[0])

    def test_cliffhanger_must_be_at_the_end(self):
        early = raw(cliffhanger={"type": "mortal_ultimatum", "timestamp": "00:05.00",
                                 "text": "I did nothing wrong.", "withheld_payoff": "x"})
        cand, reason = self.convert(early)
        self.assertIsNone(cand)
        self.assertIn("last 6s", reason)

    def test_duration_out_of_range_rejected(self):
        cand, reason = self.convert(raw(segments=[{"start": "00:00.00", "end": "00:12.00"}]))
        self.assertIsNone(cand)

    def test_scores_clamped_and_unknown_type_namespaced(self):
        rc = raw(scores={"hook_strength": 99, "injustice_tension": -5, "cliffhanger_strength": 9,
                         "standalone_clarity": 9, "payoff_withheld": 9})
        rc["hook"]["type"] = "Made Up Type"
        cand, _ = self.convert(rc)
        self.assertEqual(cand.scores.hook_strength, 10.0)
        self.assertEqual(cand.scores.injustice_tension, 0.0)
        self.assertEqual(cand.hook.type, "new:made_up_type")

    def test_impossible_timestamp_rejected(self):
        self.assertIsNone(try_parse_timestamp("09:99.00"))
        self.assertEqual(try_parse_timestamp("(01:05.50)"), 65.5)


if __name__ == "__main__":
    unittest.main()
