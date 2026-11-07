"""
Unit tests for ranking, constraint validation, deduplication, and MMR diversity.
"""

import unittest
from src.taxonomy import Taxonomy
from src.ranker import PromoRanker
from src.models import (
    PromoCandidate,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
)


class TestPromoRanker(unittest.TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy("config/taxonomy.yaml")
        self.ranker = PromoRanker(self.taxonomy)

    def test_duration_constraints(self):
        # 15s candidate must fail (< 19.5s)
        cand_short = PromoCandidate(
            promo_id="short",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:15.00", start_seconds=0, end_seconds=15, duration=15)],
            total_duration=15.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:15.00", timestamp_seconds=15.0, quote="test"),
        )
        self.assertFalse(self.ranker.validate_constraints(cand_short))

        # 35s candidate must pass
        cand_valid = PromoCandidate(
            promo_id="valid",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:35.00", start_seconds=0, end_seconds=35, duration=35)],
            total_duration=35.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.50", timestamp_seconds=1.5, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:35.00", timestamp_seconds=35.0, quote="test"),
        )
        self.assertTrue(self.ranker.validate_constraints(cand_valid))

        # 75s candidate must fail (> 60.5s)
        cand_long = PromoCandidate(
            promo_id="long",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="01:15.00", start_seconds=0, end_seconds=75, duration=75)],
            total_duration=75.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="01:15.00", timestamp_seconds=75.0, quote="test"),
        )
        self.assertFalse(self.ranker.validate_constraints(cand_long))

    def test_hook_timing_constraint(self):
        # Hook at second 6 must fail (must be <= 3.5s from start)
        cand_late_hook = PromoCandidate(
            promo_id="late_hook",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:06.00", timestamp_seconds=6.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
        )
        self.assertFalse(self.ranker.validate_constraints(cand_late_hook))

    def test_mmr_diversity_score_monotonicity(self):
        # Create 3 candidates with same hook type and 1 with different hook type
        cands = []
        for i in range(4):
            h_type = "public_humiliation" if i < 3 else "physical_aggression"
            c = PromoCandidate(
                promo_id=f"c_{i}",
                episodes=[i + 1],
                segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
                total_duration=30.0,
                hook=HookInfo(type=h_type, timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
                cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
                scores=PromoScores(composite_score=9.0),
            )
            cands.append(c)

        ranked = self.ranker.rerank_for_diversity(cands, top_k=4)
        self.assertEqual(len(ranked), 4)

        # Monotonicity test: each rank's effective score must be <= previous rank's
        for idx in range(len(ranked) - 1):
            self.assertGreaterEqual(
                ranked[idx].effective_score,
                ranked[idx + 1].effective_score,
                f"Rank {idx+1} score {ranked[idx].effective_score} is not >= Rank {idx+2} score {ranked[idx+1].effective_score}"
            )


if __name__ == "__main__":
    unittest.main()
