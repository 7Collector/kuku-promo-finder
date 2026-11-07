"""
Ranking, physical constraint enforcement, deduplication, and diversity reranking (MMR).
"""

from typing import List, Dict, Any, Optional
from src.models import PromoCandidate, Segment
from src.taxonomy import Taxonomy


class PromoRanker:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def score_candidate(self, candidate: PromoCandidate) -> float:
        """
        Computes composite score:
        Base = 0.30*hook + 0.25*cliffhanger + 0.20*injustice + 0.15*clarity + 0.10*payoff
        Final = Base * hook_taxonomy_weight * cliffhanger_taxonomy_weight
        """
        sc = candidate.scores
        base_score = (
            0.30 * sc.hook_strength
            + 0.25 * sc.cliffhanger_strength
            + 0.20 * sc.injustice_tension
            + 0.15 * sc.standalone_clarity
            + 0.10 * sc.payoff_withheld
        )

        h_weight = self.taxonomy.get_hook_weight(candidate.hook.type)
        c_weight = self.taxonomy.get_cliffhanger_weight(candidate.cliffhanger.type)
        
        final_score = base_score * h_weight * c_weight
        candidate.scores.composite_score = round(final_score, 2)
        return candidate.scores.composite_score

    def validate_constraints(self, candidate: PromoCandidate) -> bool:
        """
        Enforces hard constraints:
        1. Total duration between 20s and 60s (with 0.5s tolerance).
        2. Hook inside first 3.5s of the first segment.
        3. Segments have positive duration.
        """
        if not (19.5 <= candidate.total_duration <= 60.5):
            return False

        if not candidate.segments:
            return False

        first_seg = candidate.segments[0]
        hook_delay = candidate.hook.timestamp_seconds - first_seg.start_seconds
        if hook_delay < -0.1 or hook_delay > 3.5:
            return False

        for seg in candidate.segments:
            if seg.duration <= 0.0:
                return False

        return True

    def deduplicate(
        self, candidates: List[PromoCandidate], overlap_threshold: float = 0.40
    ) -> List[PromoCandidate]:
        """
        Removes candidates from the same episode that have > threshold temporal overlap.
        Keeps higher scoring candidates.
        """
        # Sort by composite score descending
        sorted_cands = sorted(candidates, key=lambda c: c.scores.composite_score, reverse=True)
        kept: List[PromoCandidate] = []

        for cand in sorted_cands:
            is_duplicate = False
            for existing in kept:
                # Only check overlap if they share at least one episode
                shared_eps = set(cand.episodes).intersection(set(existing.episodes))
                if not shared_eps:
                    continue

                # Check segment overlaps
                for seg_c in cand.segments:
                    for seg_e in existing.segments:
                        start_max = max(seg_c.start_seconds, seg_e.start_seconds)
                        end_min = min(seg_c.end_seconds, seg_e.end_seconds)
                        if end_min > start_max:
                            overlap_sec = end_min - start_max
                            min_dur = min(seg_c.duration, seg_e.duration)
                            if min_dur > 0 and (overlap_sec / min_dur) > overlap_threshold:
                                is_duplicate = True
                                break
                    if is_duplicate:
                        break
            if not is_duplicate:
                kept.append(cand)

        return kept

    def rerank_for_diversity(
        self, candidates: List[PromoCandidate], top_k: int = 15, hook_penalty_factor: float = 0.88
    ) -> List[PromoCandidate]:
        """
        Applies diversity reranking (MMR-style) to prevent the top promos from being
        dominated by a single hook type or the same episode.
        """
        available = list(candidates)
        ranked: List[PromoCandidate] = []
        hook_counts: Dict[str, int] = {}
        episode_counts: Dict[int, int] = {}

        while available and len(ranked) < top_k:
            best_idx = -1
            best_adjusted_score = -1.0

            for i, cand in enumerate(available):
                h_type = cand.hook.type
                h_count = hook_counts.get(h_type, 0)
                
                # Penalty for repeated hook type
                penalty = hook_penalty_factor ** h_count

                # Penalty for same episode dominance
                ep_count = sum(episode_counts.get(ep, 0) for ep in cand.episodes)
                ep_penalty = 0.90 ** ep_count

                adj_score = cand.scores.composite_score * penalty * ep_penalty
                if adj_score > best_adjusted_score:
                    best_adjusted_score = adj_score
                    best_idx = i

            chosen = available.pop(best_idx)
            chosen.rank = len(ranked) + 1
            ranked.append(chosen)

            # Update frequencies
            h_type = chosen.hook.type
            hook_counts[h_type] = hook_counts.get(h_type, 0) + 1
            for ep in chosen.episodes:
                episode_counts[ep] = episode_counts.get(ep, 0) + 1

        return ranked
