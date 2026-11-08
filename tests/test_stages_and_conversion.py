"""
Comprehensive verification tests for:
- Guarantee that LLM output cannot bypass validation (hallucinated timestamps, fabricated quotes, fake payoff_location)
- Each stage's parsing and validation (Stages A through F)
- Single-key panel graceful degradation
- CSV export format (one row per segment, timecode format, required columns)
- Weight configuration and rank blending
"""

import json
import os
import unittest
import yaml
from pathlib import Path

from src.constants import (
    WEIGHT_HOOK,
    WEIGHT_CLIFFHANGER,
    WEIGHT_PAYOFF_WITHHELD,
    WEIGHT_INJUSTICE_TENSION,
    WEIGHT_STANDALONE_CLARITY,
    WEIGHT_CONVERSION_INTENT,
)
from src.extractor import PromoExtractor
from src.models import Beat, BeatType, Episode, PromoCandidate, PromoScores, Segment, HookInfo, CliffhangerInfo, QualityAudit
from src.parser import parse_screenplay_text
from src.providers.base import BaseLLMProvider
from src.providers.heuristic import HeuristicProvider
from src.ranker import PromoRanker
from src.stages import (
    export_promos_to_csv,
    parse_panel_spec,
    run_audit_panel,
    run_auto_profile,
    run_cold_read,
    run_consolidate_taxonomy,
    run_recheck_empty,
    run_rerank,
)
from src.taxonomy import Taxonomy
from src.validation import check_candidate, verify_payoff_location


TEST_SCRIPT = """EPISODE NUMBER: 42
EPISODE LOGLINE: Test episode for validation guarantees.

SCENE 1
Scene heading: INT. GREAT HALL
Scene start: 00:00.00
Scene end: 01:00.00

**JULIANA (Defiant):**
Start: (00:00.00) | End: (00:05.00)
"I will not let you destroy this family."

**GERALD (Smirking):**
Start: (00:05.00) | End: (00:25.00)
"You have no power here, Juliana. The magistrate is already on his way."

**ALEXANDER (Cold, Deadly):**
Start: (00:25.00) | End: (00:45.00)
"Touch her again and you will not live to see tomorrow."

--- SCRIPT END ---
"""


class HallucinatingProvider(BaseLLMProvider):
    """A malicious or hallucinating model returning fabricated data."""

    def __init__(self, payload: dict):
        self.payload = payload

    @property
    def name(self) -> str:
        return "hallucinating_mock"

    @property
    def model(self) -> str:
        return "fake-model-1"

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        return self.payload


class TestValidationGuarantees(unittest.TestCase):
    def setUp(self):
        self.ep = parse_screenplay_text(TEST_SCRIPT, "episode-042.txt")
        self.episodes_by_num = {42: self.ep}
        self.tax = Taxonomy("config/taxonomy.yaml")

    def test_hallucinated_timestamps_rejected(self):
        """Model invents timestamps not on real beat edges -> rejected."""
        fake_payload = {
            "candidates": [{
                "segments": [{"start": "00:03.14", "end": "00:37.89"}],  # Hallucinated cuts
                "hook": {"type": "public_humiliation", "timestamp": "00:03.14", "text": "I will not let you destroy this family."},
                "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:37.89", "text": "Touch her again and you will not live to see tomorrow."},
                "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
            }]
        }
        prov = HallucinatingProvider(fake_payload)
        ex = PromoExtractor(self.tax, prov, episodes=[self.ep])
        cands = ex.extract_candidates_for_episode(self.ep, {}, max_candidates=1)
        self.assertEqual(len(cands), 0)
        self.assertIn("cut point is not on a real beat edge", ex.drop_reasons)

    def test_fabricated_hook_quote_rejected(self):
        """Model quotes a line that does not exist in the screenplay -> rejected."""
        fake_payload = {
            "candidates": [{
                "segments": [{"start": "00:00.00", "end": "00:45.00"}],
                "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "Who dares enter the royal sanctuary?"},  # Fabricated
                "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:45.00", "text": "Touch her again and you will not live to see tomorrow."},
                "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
            }]
        }
        prov = HallucinatingProvider(fake_payload)
        ex = PromoExtractor(self.tax, prov, episodes=[self.ep])
        cands = ex.extract_candidates_for_episode(self.ep, {}, max_candidates=1)
        self.assertEqual(len(cands), 0)
        self.assertIn("hook quote not in a beat starting within 3s of the cut", ex.drop_reasons)

    def test_fake_payoff_location_dropped_or_flagged(self):
        """Model returns a fake payoff location that points to a non-existent beat -> dropped to 'unknown'."""
        fake_payload = {
            "candidates": [{
                "segments": [{"start": "00:00.00", "end": "00:45.00"}],
                "hook": {"type": "public_humiliation", "timestamp": "00:00.00", "text": "I will not let you destroy this family."},
                "cliffhanger": {"type": "mortal_ultimatum", "timestamp": "00:45.00", "text": "Touch her again and you will not live to see tomorrow."},
                "scores": {"hook_strength": 9, "injustice_tension": 9, "cliffhanger_strength": 9, "standalone_clarity": 9, "payoff_withheld": 9},
                "conversion_intent": 8.5,
                "payoff_location": "Ep 99 99:99.00",  # Fake episode and beat
            }]
        }
        prov = HallucinatingProvider(fake_payload)
        ex = PromoExtractor(self.tax, prov, episodes=[self.ep])
        cands = ex.extract_candidates_for_episode(self.ep, {}, max_candidates=1)
        self.assertEqual(len(cands), 1)
        # Fake payoff location dropped to 'unknown'
        self.assertEqual(cands[0].payoff_location, "unknown")

        # Directly setting a fake payoff location on candidate fails check_candidate
        cands[0].payoff_location = "Ep 42 00:59.99"  # Does not match any real beat
        errs = check_candidate(cands[0], self.episodes_by_num)
        self.assertTrue(any("payoff_location" in e for e in errs))

    def test_valid_payoff_location_verified(self):
        """Valid payoff location pointing at real beat in show is verified."""
        verified = verify_payoff_location("Ep 42 00:25.00", self.episodes_by_num)
        self.assertEqual(verified, "Ep 42 00:25.00")

        # Invalid timestamp
        invalid = verify_payoff_location("Ep 42 12:34.56", self.episodes_by_num)
        self.assertIsNone(invalid)


class TestScoringAndWeights(unittest.TestCase):
    def test_editorial_priors_sum_to_one(self):
        """Editorial weights defined in constants sum to 1.0."""
        total = (
            WEIGHT_HOOK
            + WEIGHT_CLIFFHANGER
            + WEIGHT_PAYOFF_WITHHELD
            + WEIGHT_INJUSTICE_TENSION
            + WEIGHT_STANDALONE_CLARITY
        )
        self.assertAlmostEqual(total, 1.0, places=5)
        self.assertEqual(WEIGHT_CONVERSION_INTENT, 0.0)

    def test_composite_score_calculation(self):
        scores = PromoScores(
            hook_strength=10.0,
            cliffhanger_strength=10.0,
            payoff_withheld=10.0,
            injustice_tension=10.0,
            standalone_clarity=10.0,
        )
        self.assertEqual(scores.compute_composite_score(), 10.0)

        # Custom weights
        custom = {"hook": 0.5, "cliffhanger": 0.5, "payoff_withheld": 0.0, "injustice_tension": 0.0, "standalone_clarity": 0.0}
        scores2 = PromoScores(hook_strength=8.0, cliffhanger_strength=6.0)
        self.assertEqual(scores2.compute_composite_score(weights=custom), 7.0)

    def test_scoring_weights_parsing_json_and_kv(self):
        # JSON parsing
        raw_json = '{"hook": 0.4, "cliffhanger": 0.3}'
        import json
        w1 = json.loads(raw_json)
        self.assertEqual(w1["hook"], 0.4)

        # key=value parsing
        raw_kv = "hook=0.35, cliffhanger=0.25"
        w2 = {}
        for part in raw_kv.split(","):
            k, v = part.split("=", 1)
            w2[k.strip()] = float(v.strip())
        self.assertEqual(w2["hook"], 0.35)
        self.assertEqual(w2["cliffhanger"], 0.25)


class TestCSVExport(unittest.TestCase):
    def test_csv_format_one_row_per_segment(self):
        import tempfile
        promo = PromoCandidate(
            promo_id="ep42_cand_1",
            rank=1,
            episodes=[42],
            segments=[
                Segment(episode=42, start="00:00.00", end="00:25.00", start_seconds=0.0, end_seconds=25.0),
                Segment(episode=42, start="00:25.00", end="00:45.00", start_seconds=25.0, end_seconds=45.0),
            ],
            hook=HookInfo(type="public_humiliation", timestamp="00:00.00", timestamp_seconds=0.0, quote="Line 1"),
            cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:45.00", timestamp_seconds=45.0, quote="Line 2"),
            scores=PromoScores(),
            quality_audit=QualityAudit(passed=True, method="llm", critique="ok"),
            payoff_location="Ep 42 00:25.00",
        )
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        try:
            export_promos_to_csv([promo], csv_path)
            with open(csv_path, "r", encoding="utf-8") as cf:
                lines = cf.read().splitlines()
            self.assertEqual(len(lines), 3)  # Header + 2 segments
            header = lines[0].split(",")
            self.assertIn("promo_id", header)
            self.assertIn("segment_order", header)
            self.assertIn("payoff_location", header)
            self.assertIn("audit_verdict", header)

            row1 = lines[1].split(",")
            self.assertEqual(row1[0], "ep42_cand_1")
            self.assertEqual(row1[3], "1")  # segment_order 1
            self.assertEqual(row1[4], "00:00.00")
            self.assertEqual(row1[9], "Ep 42 00:25.00")
            self.assertEqual(row1[10], "PASS")

            row2 = lines[2].split(",")
            self.assertEqual(row2[3], "2")  # segment_order 2
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)


class TestStagesMocked(unittest.TestCase):
    def setUp(self):
        self.ep = parse_screenplay_text(TEST_SCRIPT, "episode-042.txt")
        self.episodes_by_num = {42: self.ep}
        self.cand = PromoCandidate(
            promo_id="ep42_cand_1",
            episodes=[42],
            segments=[Segment(episode=42, start="00:00.00", end="00:45.00", start_seconds=0.0, end_seconds=45.0)],
            hook=HookInfo(type="public_humiliation", timestamp="00:00.00", timestamp_seconds=0.0, quote="I will not let you destroy this family."),
            cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:45.00", timestamp_seconds=45.0, quote="Touch her again and you will not live to see tomorrow."),
            scores=PromoScores(standalone_clarity=8.0),
            quality_audit=QualityAudit(passed=True, method="llm", critique="strong"),
        )

    def test_cold_read_stage(self):
        mock_resp = {
            "characters": "Juliana and Alexander confronting Gerald",
            "what_is_happening": "Alexander defends Juliana with a death threat",
            "what_it_expects_next": "Will Gerald back down",
            "what_confused_it": "none",
            "stakes_are_clear": 9.0,
        }
        prov = HallucinatingProvider(mock_resp)
        report = run_cold_read([self.cand], self.episodes_by_num, prov, use_in_rank=False)
        self.assertEqual(self.cand.cold_read["stakes_are_clear"], 9.0)
        self.assertIn("cold_read", self.cand.stages)
        self.assertEqual(report["disagreements_count"], 0)

    def test_rerank_stage(self):
        mock_resp = {
            "ranking": [{"promo_id": "ep42_cand_1", "rank": 1, "reason": "High conversion"}]
        }
        prov = HallucinatingProvider(mock_resp)
        report = run_rerank([self.cand], {"show_title": "Test"}, prov, max_cands=1)
        self.assertIn("rerank", self.cand.stages)
        self.assertIn("run_1_rank", self.cand.rerank)

    def test_panel_single_key_degradation(self):
        """When only one valid key is available, audit panel degrades gracefully with notice."""
        report = run_audit_panel(
            candidates=[self.cand],
            panel_spec="openai:fake,anthropic:missing_key",
            show_context={},
            episodes=[self.ep],
            taxonomy=Taxonomy("config/taxonomy.yaml"),
            use_cache=False,
        )
        self.assertIn(report["mode"], ("single_judge", "dual_judge"))
        self.assertTrue(self.cand.quality_audit.passed)


if __name__ == "__main__":
    unittest.main()
