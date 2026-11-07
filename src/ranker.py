"""
Ranking, physical constraint enforcement, deduplication, and MMR diversity reranking.
"""

from typing import List, Dict
from src.models import PromoCandidate
from src.taxonomy import Taxonomy
from src.utils.timestamps import calculate_temporal_overlap


class PromoRanker:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def score_candidate(self, candidate: PromoCandidate) -> float:
        """Computes composite score using the canonical scoring formula."""
        h_weight = self.taxonomy.get_hook_weight(candidate.hook.type)
        c_weight = self.taxonomy.get_cliffhanger_weight(candidate.cliffhanger.type)
        return candidate.scores.compute_composite_score(h_weight, c_weight)

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
        self, candidates: List[PromoCandidate], overlap_threshold: float = 0.35
    ) -> List[PromoCandidate]:
        """
        Removes candidates from the same episode with > threshold temporal overlap.
        Keeps higher-scoring candidate.
        """
        sorted_cands = sorted(candidates, key=lambda c: c.scores.composite_score, reverse=True)
        kept: List[PromoCandidate] = []

        for cand in sorted_cands:
            is_duplicate = False
            for existing in kept:
                shared_eps = set(cand.episodes).intersection(set(existing.episodes))
                if not shared_eps:
                    continue

                for seg_c in cand.segments:
                    for seg_e in existing.segments:
                        _, ratio = calculate_temporal_overlap(
                            seg_c.start_seconds,
                            seg_c.end_seconds,
                            seg_e.start_seconds,
                            seg_e.end_seconds,
                        )
                        if ratio > overlap_threshold:
                            is_duplicate = True
                            break
                    if is_duplicate:
                        break
            if not is_duplicate:
                kept.append(cand)

        return kept

    def rerank_for_diversity(
        self,
        candidates: List[PromoCandidate],
        top_k: int = 15,
        hook_penalty_factor: float = 0.88,
        episode_penalty_factor: float = 0.90,
    ) -> List[PromoCandidate]:
        """
        Applies MMR diversity reranking to balance promo types and episodes.
        Saves adjusted_score and diversity_penalty onto candidate so ranking order
        is strictly monotonic and completely transparent.
        """
        available = list(candidates)
        ranked: List[PromoCandidate] = []
        hook_counts: Dict[str, int] = {}
        episode_counts: Dict[int, int] = {}

        while available and len(ranked) < top_k:
            best_idx = -1
            best_adjusted_score = -1.0
            best_total_penalty = 1.0

            for i, cand in enumerate(available):
                h_type = cand.hook.type
                h_count = hook_counts.get(h_type, 0)
                h_penalty = hook_penalty_factor ** h_count

                ep_count = sum(episode_counts.get(ep, 0) for ep in cand.episodes)
                ep_penalty = episode_penalty_factor ** ep_count

                total_penalty = h_penalty * ep_penalty
                adj_score = cand.scores.composite_score * total_penalty

                if adj_score > best_adjusted_score:
                    best_adjusted_score = adj_score
                    best_total_penalty = total_penalty
                    best_idx = i

            chosen = available.pop(best_idx)
            chosen.rank = len(ranked) + 1
            chosen.scores.adjusted_score = round(best_adjusted_score, 2)
            chosen.scores.diversity_penalty = round(best_total_penalty, 3)
            ranked.append(chosen)

            # Update frequencies
            h_type = chosen.hook.type
            hook_counts[h_type] = hook_counts.get(h_type, 0) + 1
            for ep in chosen.episodes:
                episode_counts[ep] = episode_counts.get(ep, 0) + 1

        return ranked
