"""
Unit tests for adversarial quality auditor.
"""

import unittest
from unittest.mock import MagicMock
from src.auditor import PromoAuditor
from src.providers.heuristic import HeuristicProvider
from src.models import (
    PromoCandidate,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
)


class TestPromoAuditor(unittest.TestCase):
    def setUp(self):
        show_context = {
            "antagonists": [{"name": "Gerald"}, {"name": "Clarissa"}],
            "male_lead": {"name": "Alexander"}
        }
        self.auditor = PromoAuditor(
            llm_provider=HeuristicProvider(),
            show_context=show_context,
        )

    def test_resolution_leak_detected(self):
        # candidate with low payoff_withheld (conflict resolved) must fail audit
        cand = PromoCandidate(
            promo_id="res_leak",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="test"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="test"),
            scores=PromoScores(payoff_withheld=4.0),
        )
        audit = self.auditor.audit_candidate(cand)
        self.assertFalse(audit.passed)
        self.assertEqual(audit.flaw_type, "resolution_leak")

    def test_visual_dependency_flagged(self):
        cand = PromoCandidate(
            promo_id="vis_dep",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="Symmetrical framing on church doors"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="Close-up gazing down with disdain"),
            scores=PromoScores(payoff_withheld=9.0),
        )
        audit = self.auditor.audit_candidate(cand)
        self.assertTrue(audit.passed)
        self.assertTrue(any("visual" in r.lower() for r in audit.risks))

    def test_llm_provider_audit_with_mock(self):
        mock_provider = MagicMock()
        mock_provider.name = "mock_llm"
        mock_provider.generate_json.return_value = {
            "pass": True,
            "lethal_flaw": None,
            "critique": "High tension cold hook with sharp cut.",
            "confidence_score": 9.2,
            "risks": ["Minor character lore ambiguity"],
        }
        auditor = PromoAuditor(llm_provider=mock_provider)
        cand = PromoCandidate(
            promo_id="llm_test",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30, duration=30)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="You are nothing!"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="Who are you calling nothing?"),
            scores=PromoScores(payoff_withheld=8.5),
        )
        audit = auditor.audit_candidate(cand)
        self.assertTrue(audit.passed)
        self.assertEqual(audit.critique, "High tension cold hook with sharp cut.")
        self.assertEqual(len(audit.risks), 1)
        mock_provider.generate_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()
