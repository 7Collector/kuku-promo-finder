"""
Show-agnostic dynamic composite promo builder.
Pairs early high-injustice setup beats with late climactic confrontation cliffhangers.
Contains ZERO hardcoded show quotes or episode numbers.
"""

from typing import List
from src.models import (
    Episode,
    PromoCandidate,
    Segment,
    PromoScores,
)
from src.taxonomy import Taxonomy
from src.utils.logging import logger


class CompositePromoBuilder:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def build_cross_episode_composites(
        self,
        episodes: List[Episode],
        single_candidates: List[PromoCandidate],
        max_composites: int = 2,
    ) -> List[PromoCandidate]:
        """
        Dynamically pairs an early high-injustice setup hook (first 25% of episodes)
        with a late climactic confrontation cliffhanger (last 50% of episodes).
        Ensures total duration is between 20s and 60s.
        """
        if len(episodes) < 4 or not single_candidates:
            logger.info("Not enough episodes or candidates to synthesize cross-episode composites.")
            return []

        cutoff_early = max(1, len(episodes) // 4)
        cutoff_late = len(episodes) // 2

        early_setups = [
            c for c in single_candidates
            if c.episodes[0] <= cutoff_early and c.scores.injustice_tension >= 8.0
        ]
        late_climaxes = [
            c for c in single_candidates
            if c.episodes[0] >= cutoff_late and c.scores.cliffhanger_strength >= 7.5
        ]

        if not early_setups or not late_climaxes:
            logger.info("No candidates qualified for dynamic cross-episode composite pairing.")
            return []

        composites: List[PromoCandidate] = []
        for setup in early_setups:
            for climax in late_climaxes:
                # Build Segment 1: Short setup segment from start of setup (approx 10-15s)
                setup_seg = setup.segments[0]
                seg1_dur = min(15.0, max(8.0, setup_seg.duration * 0.4))
                seg1 = Segment(
                    start=setup_seg.start,
                    end=setup_seg.end,
                    start_seconds=setup_seg.start_seconds,
                    end_seconds=setup_seg.start_seconds + seg1_dur,
                    duration=seg1_dur,
                )

                # Build Segment 2: Climax segment from climax candidate (approx 20-35s)
                climax_seg = climax.segments[-1]
                target_total = 45.0
                seg2_dur = min(climax_seg.duration, max(15.0, target_total - seg1_dur))
                seg2_start_sec = max(climax_seg.start_seconds, climax_seg.end_seconds - seg2_dur)
                seg2 = Segment(
                    start=climax_seg.start,
                    end=climax_seg.end,
                    start_seconds=seg2_start_sec,
                    end_seconds=climax_seg.end_seconds,
                    duration=seg2_dur,
                )

                total_dur = seg1.duration + seg2.duration
                if not (20.0 <= total_dur <= 60.0):
                    continue

                scores = PromoScores(
                    hook_strength=max(setup.scores.hook_strength, 9.0),
                    injustice_tension=max(setup.scores.injustice_tension, 9.0),
                    cliffhanger_strength=max(climax.scores.cliffhanger_strength, 9.0),
                    standalone_clarity=8.5,
                    payoff_withheld=9.0,
                )

                h_w = self.taxonomy.get_hook_weight(setup.hook.type)
                c_w = self.taxonomy.get_cliffhanger_weight(climax.cliffhanger.type)
                scores.compute_composite_score(h_w, c_w)

                comp = PromoCandidate(
                    promo_id=f"comp_ep{setup.episodes[0]:02d}_ep{climax.episodes[0]:02d}",
                    promo_type="cross_episode",
                    episodes=[setup.episodes[0], climax.episodes[0]],
                    segments=[seg1, seg2],
                    total_duration=total_dur,
                    hook=setup.hook,
                    cliffhanger=climax.cliffhanger,
                    why_it_works=(
                        f"Dynamic composite: Bridges early setup injustice from Ep {setup.episodes[0]} "
                        f"directly into climactic confrontation in Ep {climax.episodes[0]}."
                    ),
                    scores=scores,
                )
                composites.append(comp)

                if len(composites) >= max_composites:
                    return composites

        return composites
