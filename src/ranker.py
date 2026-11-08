"""
Ranking, physical constraint enforcement, deduplication, and diversity reranking.
"""

from typing import List, Dict
from src.constants import EPS, HOOK_WINDOW, MAX_DURATION, MIN_DURATION
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
        Enforces the brief's hard constraints (see src/constants.py):
        1. Total duration 20-60s (float tolerance only).
        2. Hook within the first 3s of the first segment.
        3. Segments have positive duration.
        """
        if not (MIN_DURATION - EPS <= candidate.total_duration <= MAX_DURATION + EPS):
            return False

        if not candidate.segments:
            return False

        first_seg = candidate.segments[0]
        hook_delay = candidate.hook.timestamp_seconds - first_seg.start_seconds
        if hook_delay < -EPS or hook_delay > HOOK_WINDOW + EPS:
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
                # Do not deduplicate cross-episode composites against single-episode clips
                if cand.promo_type != existing.promo_type:
                    continue

                shared_eps = set(cand.episodes).intersection(set(existing.episodes))
                if not shared_eps:
                    continue

                for seg_c in cand.segments:
                    for seg_e in existing.segments:
                        # Clock times only mean something inside the same episode.
                        if seg_c.episode != seg_e.episode and None not in (seg_c.episode, seg_e.episode):
                            continue
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
        hook_penalty_factor: float = 0.82,
        episode_penalty_factor: float = 0.85,
        audit_failure_penalty: float = 0.78,
    ) -> List[PromoCandidate]:
        """
        Greedy diversity-penalised ranking (a count-based penalty per repeated hook type and
        episode). Audit outcome is a gate: while any audited-passing
        candidate remains, failing ones cannot be picked, so every pass outranks every fail.
        Failing candidates are still listed after the passes, with a 0.78x multiplier
        (0.65x for a resolution leak), so the report shows them honestly flagged.
        adjusted_score, diversity_penalty and audit_multiplier are stored on each candidate.
        """
        available = list(candidates)
        ranked: List[PromoCandidate] = []
        hook_counts: Dict[str, int] = {}
        episode_counts: Dict[int, int] = {}

        # Check if tiered ranking is active (i.e. candidates have audit_tier assigned)
        has_tiers = any(getattr(c, "audit_tier", None) in (1, 2, 3) for c in available)

        if has_tiers:
            # Exclude audit_error and not_audited candidates from top-15 selection
            eligible = [
                c for c in available
                if getattr(c, "audit_tier", None) in (1, 2, 3)
                and not (c.quality_audit and c.quality_audit.method in ("error", "not_audited"))
            ]
            tier_1 = [c for c in eligible if c.audit_tier == 1]
            tier_2 = [c for c in eligible if c.audit_tier == 2]
            tier_3 = [c for c in eligible if c.audit_tier == 3]

            def _greedy_select_pool(pool: List[PromoCandidate], pool_audit_multiplier: float, fill_target: int):
                while pool and len(ranked) < fill_target:
                    best_idx = -1
                    best_score = -1.0
                    best_tot_penalty = 1.0
                    best_mult = pool_audit_multiplier

                    for i, cand in enumerate(pool):
                        h_count = hook_counts.get(cand.hook.type, 0)
                        h_penalty = hook_penalty_factor ** h_count

                        ep_count = sum(episode_counts.get(ep, 0) for ep in cand.episodes)
                        ep_penalty = episode_penalty_factor ** ep_count

                        total_penalty = h_penalty * ep_penalty
                        mult = pool_audit_multiplier
                        if cand.quality_audit and cand.quality_audit.flaw_type == "resolution_leak":
                            mult = mult * 0.85

                        adj_score = cand.scores.composite_score * total_penalty * mult
                        if adj_score > best_score:
                            best_score = adj_score
                            best_tot_penalty = total_penalty
                            best_mult = mult
                            best_idx = i

                    chosen = pool.pop(best_idx)
                    chosen.rank = len(ranked) + 1
                    chosen.scores.adjusted_score = round(best_score, 2)
                    chosen.scores.diversity_penalty = round(best_tot_penalty, 3)
                    chosen.scores.audit_multiplier = round(best_mult, 3)
                    ranked.append(chosen)

                    hook_counts[chosen.hook.type] = hook_counts.get(chosen.hook.type, 0) + 1
                    for ep in chosen.episodes:
                        episode_counts[ep] = episode_counts.get(ep, 0) + 1

            # 1. Rank Tier 1 first
            _greedy_select_pool(tier_1, 1.0, top_k)

            # 2. If fewer than top_k, fill from Tier 2 and say so
            if len(ranked) < top_k and tier_2:
                needed = top_k - len(ranked)
                print(f"  • Tier 1 has only {len(ranked)} candidates (< {top_k}); filling {needed} from Tier 2 (split verdicts).")
                _greedy_select_pool(tier_2, 0.85, top_k)

            # 3. If still fewer than top_k, fill from Tier 3
            if len(ranked) < top_k and tier_3:
                _greedy_select_pool(tier_3, audit_failure_penalty, top_k)

            return ranked

        # Fallback single-judge mode: pass-first, diversity-penalised
        # Exclude audit_error and not_audited from top-15
        eligible = [
            c for c in available
            if not (c.quality_audit and (c.quality_audit.method in ("error", "not_audited") or c.quality_audit.flaw_type in ("audit_error", "not_audited")))
        ]
        available = list(eligible)

        while available and len(ranked) < top_k:
            best_idx = -1
            best_adjusted_score = -1.0
            best_total_penalty = 1.0
            best_audit_factor = 1.0

            any_passing = any(not (c.quality_audit and not c.quality_audit.passed) for c in available)

            for i, cand in enumerate(available):
                if any_passing and cand.quality_audit and not cand.quality_audit.passed:
                    continue
                h_type = cand.hook.type
                h_count = hook_counts.get(h_type, 0)
                h_penalty = hook_penalty_factor ** h_count

                ep_count = sum(episode_counts.get(ep, 0) for ep in cand.episodes)
                ep_penalty = episode_penalty_factor ** ep_count

                total_penalty = h_penalty * ep_penalty

                # Audit quality gate
                audit_factor = 1.0
                if cand.quality_audit:
                    if not cand.quality_audit.passed:
                        if cand.quality_audit.flaw_type == "resolution_leak":
                            audit_factor = audit_failure_penalty * 0.85
                        else:
                            audit_factor = audit_failure_penalty

                adj_score = cand.scores.composite_score * total_penalty * audit_factor

                if adj_score > best_adjusted_score:
                    best_adjusted_score = adj_score
                    best_total_penalty = total_penalty
                    best_audit_factor = audit_factor
                    best_idx = i

            chosen = available.pop(best_idx)
            chosen.rank = len(ranked) + 1
            chosen.scores.adjusted_score = round(best_adjusted_score, 2)
            chosen.scores.diversity_penalty = round(best_total_penalty, 3)
            chosen.scores.audit_multiplier = round(best_audit_factor, 3)
            ranked.append(chosen)

            # Update frequencies
            h_type = chosen.hook.type
            hook_counts[h_type] = hook_counts.get(h_type, 0) + 1
            for ep in chosen.episodes:
                episode_counts[ep] = episode_counts.get(ep, 0) + 1

        return ranked
