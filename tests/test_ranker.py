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

    def test_audit_failure_penalty_deprioritizes_flawed_promos(self):
        from src.models import QualityAudit
        # Candidate 1 has slightly higher raw score (9.2) but fails audit
        c_flawed = PromoCandidate(
            promo_id="flawed",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
            scores=PromoScores(composite_score=9.2),
            quality_audit=QualityAudit(passed=False, flaw_type="resolution_leak", critique="resolves hook"),
        )
        # Candidate 2 has lower raw score (8.5) but passes audit
        c_clean = PromoCandidate(
            promo_id="clean",
            episodes=[2],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="physical_aggression", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
            scores=PromoScores(composite_score=8.5),
            quality_audit=QualityAudit(passed=True, flaw_type=None, critique="clean"),
        )

        ranked = self.ranker.rerank_for_diversity([c_flawed, c_clean], top_k=2)
        # Clean candidate should be Rank 1 because flawed candidate receives audit penalty
        self.assertEqual(ranked[0].promo_id, "clean")
        self.assertEqual(ranked[1].promo_id, "flawed")
        self.assertLess(ranked[1].effective_score, ranked[0].effective_score)

    def test_cross_episode_deduplication_isolation(self):
        # Single episode candidate on ep 1
        c_single = PromoCandidate(
            promo_id="single",
            promo_type="single_episode",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
            scores=PromoScores(composite_score=9.0),
        )
        # Composite candidate using a subsegment of ep 1 and ep 25
        c_comp = PromoCandidate(
            promo_id="comp",
            promo_type="cross_episode",
            episodes=[1, 25],
            segments=[
                Segment(start="00:00.00", end="00:15.00", start_seconds=0, end_seconds=15, duration=15),
                Segment(start="01:00.00", end="01:30.00", start_seconds=60, end_seconds=90, duration=30),
            ],
            total_duration=45.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="unexpected_savior_arrival", timestamp="01:30.00", timestamp_seconds=90.0, quote="test"),
            scores=PromoScores(composite_score=8.8),
        )

        deduped = self.ranker.deduplicate([c_single, c_comp])
        # Both must survive because composite is not pruned against single-episode
        self.assertEqual(len(deduped), 2)


if __name__ == "__main__":
    unittest.main()
