"""
Unit tests for cross-episode composite promo builder.
"""

import unittest
from src.taxonomy import Taxonomy
from src.composite import CompositePromoBuilder
from src.models import (
    Episode,
    Scene,
    Beat,
    BeatType,
    PromoCandidate,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
)


class TestCompositePromoBuilder(unittest.TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy("config/taxonomy.yaml")
        self.builder = CompositePromoBuilder(self.taxonomy)

        # Create dummy early and late episodes
        def make_ep(ep_num: int, start_text: str, end_text: str) -> Episode:
            return Episode(
                episode_number=ep_num,
                episode_id=f"ep{ep_num}",
                logline="Test",
                scenes=[
                    Scene(
                        scene_number=1,
                        heading="Scene 1",
                        start_seconds=0.0,
                        end_seconds=60.0,
                        start_str="00:00.00",
                        end_str="01:00.00",
                        beats=[
                            Beat(beat_type=BeatType.DIALOGUE, speaker="A", emotion=None, text=start_text, start_seconds=0.0, end_seconds=12.0, start_str="00:00.00", end_str="00:12.00"),
                            Beat(beat_type=BeatType.ACTION, speaker=None, emotion=None, text="action", start_seconds=12.0, end_seconds=25.0, start_str="00:12.00", end_str="00:25.00"),
                            Beat(beat_type=BeatType.DIALOGUE, speaker="B", emotion=None, text=end_text, start_seconds=25.0, end_seconds=45.0, start_str="00:25.00", end_str="00:45.00"),
                        ]
                    )
                ]
            )

        self.episodes = [make_ep(i, f"Hook {i}", f"Cliff {i}") for i in range(1, 30)]

        # Early candidate in Ep 1
        self.early_cand = PromoCandidate(
            promo_id="ep01_cand_1",
            promo_type="single_episode",
            episodes=[1],
            segments=[Segment(start="00:00.00", end="00:30.00", start_seconds=0.0, end_seconds=30.0, duration=30.0)],
            total_duration=30.0,
            hook=HookInfo(type="public_humiliation", timestamp="00:01.00", timestamp_seconds=1.0, quote="Kneel down!"),
            cliffhanger=CliffhangerInfo(type="interrupted_retaliation", timestamp="00:30.00", timestamp_seconds=30.0, quote="Stop!"),
            scores=PromoScores(injustice_tension=9.0, hook_strength=9.0),
        )

        # Late candidate in Ep 20
        self.late_cand = PromoCandidate(
            promo_id="ep20_cand_1",
            promo_type="single_episode",
            episodes=[20],
            segments=[Segment(start="00:10.00", end="00:45.00", start_seconds=10.0, end_seconds=45.0, duration=35.0)],
            total_duration=35.0,
            hook=HookInfo(type="hidden_identity_irony", timestamp="00:11.00", timestamp_seconds=11.0, quote="Who are you?"),
            cliffhanger=CliffhangerInfo(type="unexpected_savior_arrival", timestamp="00:45.00", timestamp_seconds=45.0, quote="Doors burst open!"),
            scores=PromoScores(cliffhanger_strength=9.0, payoff_withheld=9.0),
        )

    def test_build_cross_episode_composites(self):
        composites = self.builder.build_cross_episode_composites(
            episodes=self.episodes,
            single_candidates=[self.early_cand, self.late_cand],
            max_composites=2,
        )
        self.assertGreaterEqual(len(composites), 1)
        comp = composites[0]
        self.assertEqual(comp.promo_type, "cross_episode")
        self.assertEqual(comp.episodes, [1, 20])
        self.assertEqual(len(comp.segments), 2)
        self.assertTrue(20.0 <= comp.total_duration <= 60.0)
        self.assertEqual(comp.hook.quote, "Kneel down!")
        self.assertEqual(comp.cliffhanger.quote, "Doors burst open!")
        self.assertGreaterEqual(comp.scores.standalone_clarity, 8.5)


if __name__ == "__main__":
    unittest.main()
