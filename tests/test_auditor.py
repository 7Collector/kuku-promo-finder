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
        mock_provider.model = "mock-model"
        mock_provider.is_live = True
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

    def test_screenplay_slice_injected_into_prompt(self):
        from src.models import Episode, Scene, Beat, BeatType
        mock_provider = MagicMock()
        mock_provider.name = "mock_llm"
        mock_provider.model = "mock-model"
        mock_provider.is_live = True
        mock_provider.generate_json.return_value = {
            "pass": True,
            "lethal_flaw": None,
            "critique": "Solid cut.",
            "confidence_score": 9.0,
            "risks": []
        }
        test_ep = Episode(
            episode_number=1,
            episode_id="ep1",
            logline="Test",
            scenes=[
                Scene(
                    scene_number=1,
                    heading="Test Scene",
                    start_seconds=0,
                    end_seconds=60,
                    start_str="00:00.00",
                    end_str="01:00.00",
                    beats=[
                        Beat(beat_type=BeatType.DIALOGUE, speaker="VILLAIN", emotion="Cruel", text="You are ruined, Juliana!", start_seconds=5.0, end_seconds=10.0, start_str="00:05.00", end_str="00:10.00"),
                        Beat(beat_type=BeatType.ACTION, speaker=None, emotion=None, text="Alexander raises his head.", start_seconds=11.0, end_seconds=15.0, start_str="00:11.00", end_str="00:15.00"),
                    ]
                )
            ]
        )
        auditor = PromoAuditor(llm_provider=mock_provider, episodes=[test_ep])
        cand = PromoCandidate(
            promo_id="slice_test",
            episodes=[1],
            segments=[Segment(start="00:05.00", end="00:15.00", start_seconds=5.0, end_seconds=15.0, duration=10.0)],
            total_duration=10.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:05.00", timestamp_seconds=5.0, quote="You are ruined, Juliana!"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:15.00", timestamp_seconds=15.0, quote="Alexander raises his head."),
            scores=PromoScores(payoff_withheld=9.0),
        )
        auditor.audit_candidate(cand)
        user_prompt_arg = mock_provider.generate_json.call_args[0][1]
        self.assertIn("<clip_screenplay>", user_prompt_arg)
        self.assertIn("You are ruined, Juliana!", user_prompt_arg)
        self.assertIn("Alexander raises his head.", user_prompt_arg)


if __name__ == "__main__":
    unittest.main()
