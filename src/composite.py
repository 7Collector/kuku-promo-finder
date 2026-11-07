"""
EXPERIMENTAL composite promo builder (opt-in via `run.py --composites`).
Pairs an early high-injustice setup with a late climactic cliffhanger. It has no notion of plot,
so pairs are not guaranteed to cohere; the quality audit is what decides whether they ship.
Slices authentic beat boundaries with exact start/end timestamps.
"""

from typing import List, Dict
from src.models import (
    Episode,
    PromoCandidate,
    Segment,
    PromoScores,
)
from src.taxonomy import Taxonomy
from src.utils.timestamps import seconds_to_timestamp
from src.utils.logging import logger


class CompositePromoBuilder:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def build_cross_episode_composites(
        self,
        episodes: List[Episode],
        single_candidates: List[PromoCandidate],
        max_composites: int = 4,
    ) -> List[PromoCandidate]:
        """
        Dynamically pairs an early high-injustice setup hook (first 25% of episodes)
        with a late climactic confrontation cliffhanger (last 50% of episodes).
        Snaps all cut points to authentic beat boundaries in the screenplay.
        Ensures total duration is between 20s and 60s.
        """
        if len(episodes) < 4 or not single_candidates:
            logger.info("Not enough episodes or candidates to synthesize cross-episode composites.")
            return []

        episodes_by_num: Dict[int, Episode] = {ep.episode_number: ep for ep in episodes}
        # Cutoffs are expressed in real episode numbers, so gaps in numbering cannot skew them.
        numbers = sorted(episodes_by_num)
        cutoff_early = numbers[max(0, len(numbers) // 4 - 1)]
        cutoff_late = numbers[len(numbers) // 2]

        early_setups = [
            c for c in single_candidates
            if c.episodes[0] <= cutoff_early and c.scores.injustice_tension >= 7.5
        ]
        late_climaxes = [
            c for c in single_candidates
            if c.episodes[0] >= cutoff_late and c.scores.cliffhanger_strength >= 7.5
        ]

        if not early_setups or not late_climaxes:
            logger.info("No candidates qualified for dynamic cross-episode composite pairing.")
            return []

        composites: List[PromoCandidate] = []
        used_pairs = set()

        for setup in early_setups:
            setup_ep = episodes_by_num.get(setup.episodes[0])
            if not setup_ep or not setup.segments:
                continue
            setup_seg = setup.segments[0]
            setup_beats = [
                b for b in setup_ep.all_beats
                if b.start_seconds >= setup_seg.start_seconds - 0.1
            ]
            if not setup_beats:
                continue

            # Snap seg1 end to a beat boundary giving 10-18s duration
            target_seg1_dur = min(18.0, max(10.0, setup_seg.duration * 0.4))
            best_seg1_beat = setup_beats[0]
            for b in setup_beats:
                dur = b.end_seconds - setup_seg.start_seconds
                if dur >= 9.0:
                    best_seg1_beat = b
                    if dur >= target_seg1_dur:
                        break

            seg1_start_sec = setup_seg.start_seconds
            seg1_end_sec = best_seg1_beat.end_seconds
            seg1_dur = round(seg1_end_sec - seg1_start_sec, 2)
            if seg1_dur <= 0:
                continue

            seg1 = Segment(
                episode=setup.episodes[0],
                start=setup_seg.start,
                end=best_seg1_beat.end_str,
                start_seconds=seg1_start_sec,
                end_seconds=seg1_end_sec,
                duration=seg1_dur,
            )

            for climax in late_climaxes:
                pair_key = (setup.episodes[0], climax.episodes[0])
                if pair_key in used_pairs:
                    continue

                climax_ep = episodes_by_num.get(climax.episodes[0])
                if not climax_ep or not climax.segments:
                    continue
                climax_seg = climax.segments[-1]

                # Climax target duration: 20-35s such that total is 30-55s
                target_total = 45.0
                target_seg2_dur = min(35.0, max(18.0, target_total - seg1_dur))

                climax_beats = [
                    b for b in climax_ep.all_beats
                    if b.end_seconds <= climax_seg.end_seconds + 0.1 and b.start_seconds >= climax_seg.start_seconds - 0.1
                ]
                if not climax_beats:
                    continue

                # Find beat start that gives approx target_seg2_dur before climax_seg.end_seconds
                best_seg2_beat = climax_beats[0]
                for b in climax_beats:
                    dur = climax_seg.end_seconds - b.start_seconds
                    if dur <= target_seg2_dur + 3.0:
                        best_seg2_beat = b
                        break

                seg2_start_sec = best_seg2_beat.start_seconds
                seg2_end_sec = climax_seg.end_seconds
                seg2_dur = round(seg2_end_sec - seg2_start_sec, 2)
                if seg2_dur <= 0:
                    continue

                seg2 = Segment(
                    episode=climax.episodes[0],
                    start=best_seg2_beat.start_str,
                    end=climax_seg.end,
                    start_seconds=seg2_start_sec,
                    end_seconds=seg2_end_sec,
                    duration=seg2_dur,
                )

                total_dur = round(seg1.duration + seg2.duration, 2)
                if not (20.0 <= total_dur <= 60.0):
                    continue

                # Scores are inherited from the two parts, never floored or boosted: a spliced
                # clip is only as clear as its weaker half.
                scores = PromoScores(
                    hook_strength=setup.scores.hook_strength,
                    injustice_tension=setup.scores.injustice_tension,
                    cliffhanger_strength=climax.scores.cliffhanger_strength,
                    standalone_clarity=min(setup.scores.standalone_clarity, climax.scores.standalone_clarity),
                    payoff_withheld=climax.scores.payoff_withheld,
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
                        f"EXPERIMENTAL pairing (no narrative matching): Ep {setup.episodes[0]} setup spliced with "
                        f"Ep {climax.episodes[0]} climax. The auditor decides whether the join makes sense."
                    ),
                    scores=scores,
                    engine=setup.engine,
                    model=setup.model,
                )
                composites.append(comp)
                used_pairs.add(pair_key)

                if len(composites) >= max_composites:
                    return composites

        return composites
