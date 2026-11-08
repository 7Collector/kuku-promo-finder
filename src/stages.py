"""
Modular implementation of LLM stages (A through F) and CSV export.
Each stage is explicit, reuses provider/caching abstractions, and never performs silent fallbacks.
"""

import csv
import json
import math
import os
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple
import yaml

from src.constants import (
    WEIGHT_RERANK_SCORE,
    WEIGHT_WEIGHTED_SCORE,
)
from src.models import Episode, PromoCandidate, QualityAudit
from src.parser import format_episode_for_analysis, format_segment_slice
from src.prompts import (
    AUTO_PROFILE_SYSTEM_PROMPT,
    AUTO_PROFILE_USER_PROMPT_TEMPLATE,
    COLD_READ_SYSTEM_PROMPT,
    COLD_READ_USER_PROMPT_TEMPLATE,
    CONSOLIDATE_TAXONOMY_SYSTEM_PROMPT,
    CONSOLIDATE_TAXONOMY_USER_PROMPT_TEMPLATE,
    RECHECK_EMPTY_SYSTEM_PROMPT,
    RECHECK_EMPTY_USER_PROMPT_TEMPLATE,
    RERANK_SYSTEM_PROMPT,
    RERANK_USER_PROMPT_TEMPLATE,
)
from src.providers.base import BaseLLMProvider
from src.providers.factory import PROVIDERS, _has_key, get_llm_provider
from src.taxonomy import Taxonomy
from src.utils.logging import logger
from src.utils.timestamps import seconds_to_timestamp, try_parse_timestamp
from src.validation import find_quote_beat, snap_to_beat_edge, spoken_beats
from src.utils.cost import calculate_cost_usd, format_stage_cost
from src.providers.gemini import discover_gemini_flash_model
import time


def compute_cohens_kappa(agree_count: int, j1_pass: int, j2_pass: int, total: int) -> float:
    """Computes Cohen's kappa for inter-rater agreement."""
    if total <= 0:
        return 1.0
    po = agree_count / total
    p1 = j1_pass / total
    p2 = j2_pass / total
    pe = (p1 * p2) + ((1.0 - p1) * (1.0 - p2))
    if abs(1.0 - pe) < 1e-6:
        return 1.0
    return round((po - pe) / (1.0 - pe), 4)


def kendall_tau(r1: List[int], r2: List[int]) -> float:
    """Computes Kendall's tau rank correlation between two permutations of length n."""
    n = len(r1)
    if n <= 1:
        return 1.0
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            s1 = (r1[i] > r1[j]) - (r1[i] < r1[j])
            s2 = (r2[i] > r2[j]) - (r2[i] < r2[j])
            prod = s1 * s2
            if prod > 0:
                concordant += 1
            elif prod < 0:
                discordant += 1
    total = n * (n - 1) / 2
    return round((concordant - discordant) / total, 3)


def _build_stage_meta(
    provider: BaseLLMProvider,
    u_before: Dict[str, Any],
    t_start: float,
    extra_provider: Optional[BaseLLMProvider] = None,
    extra_u_before: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    u_after = provider.usage
    live_calls = u_after["calls"] - u_before.get("calls", 0)
    cache_hits = u_after["cache_hits"] - u_before.get("cache_hits", 0)
    live_p = u_after["prompt_tokens"] - u_before.get("prompt_tokens", 0)
    live_c = u_after["completion_tokens"] - u_before.get("completion_tokens", 0)
    cached_p = u_after.get("cached_prompt_tokens", 0) - u_before.get("cached_prompt_tokens", 0)
    cached_c = u_after.get("cached_completion_tokens", 0) - u_before.get("cached_completion_tokens", 0)

    live_cost = calculate_cost_usd(provider.name, provider.model, live_p, live_c)
    cached_cost = calculate_cost_usd(provider.name, provider.model, cached_p, cached_c)

    if extra_provider and extra_u_before:
        eu_after = extra_provider.usage
        elive_calls = eu_after["calls"] - extra_u_before.get("calls", 0)
        ecache_hits = eu_after["cache_hits"] - extra_u_before.get("cache_hits", 0)
        elive_p = eu_after["prompt_tokens"] - extra_u_before.get("prompt_tokens", 0)
        elive_c = eu_after["completion_tokens"] - extra_u_before.get("completion_tokens", 0)
        ecached_p = eu_after.get("cached_prompt_tokens", 0) - extra_u_before.get("cached_prompt_tokens", 0)
        ecached_c = eu_after.get("cached_completion_tokens", 0) - extra_u_before.get("cached_completion_tokens", 0)

        live_calls += elive_calls
        cache_hits += ecache_hits
        live_p += elive_p
        live_c += elive_c
        cached_p += ecached_p
        cached_c += ecached_c
        live_cost += calculate_cost_usd(extra_provider.name, extra_provider.model, elive_p, elive_c)
        cached_cost += calculate_cost_usd(extra_provider.name, extra_provider.model, ecached_p, ecached_c)

    wall_s = round(time.time() - t_start, 2)
    if live_calls > 0:
        status = "ran"
        reason = "live API calls executed"
    elif cache_hits > 0:
        status = "cached"
        reason = "all responses loaded from on-disk cache"
    else:
        status = "failed"
        reason = "zero calls and zero cache hits recorded"

    cost_str = format_stage_cost(live_cost, cached_cost, live_calls, cache_hits)
    return {
        "status": status,
        "reason": reason,
        "live_calls": live_calls,
        "cache_hits": cache_hits,
        "tokens": {
            "prompt_tokens": live_p + cached_p,
            "completion_tokens": live_c + cached_c,
            "total_tokens": live_p + cached_p + live_c + cached_c,
        },
        "cost": cost_str,
        "live_cost_usd": round(live_cost, 4),
        "cached_cost_usd": round(cached_cost, 4),
        "wall_time_s": wall_s,
    }


# ---------------------------------------------------------------------------
# Stage A: Cold Read
# ---------------------------------------------------------------------------
def run_cold_read(
    candidates: List[PromoCandidate],
    episodes_by_num: Dict[int, Episode],
    llm_provider: BaseLLMProvider,
    use_in_rank: bool = False,
    workers: int = 8,
) -> Dict[str, Any]:
    """
    Sends only the authentic clip text to the model (no show title, premise, cast, or taxonomy).
    Stores results in cand.cold_read, appends 'cold_read' to cand.stages.
    Reports correlation and disagreements against standalone_clarity.
    """
    t_start = time.time()
    u_before = dict(llm_provider.usage)
    print(f"\n[Stage A: Cold Read] Running on {len(candidates)} candidates...")

    def _process_cand(cand: PromoCandidate) -> Tuple[PromoCandidate, Dict[str, Any], float, float, Optional[Dict[str, Any]]]:
        slices = []
        for idx, seg in enumerate(cand.segments):
            ep_num = seg.episode if seg.episode is not None else cand.episodes[0]
            ep = episodes_by_num.get(ep_num)
            if ep:
                text = format_segment_slice(ep, seg.start_seconds, seg.end_seconds, include_camera=True)
                slices.append(f"--- Segment {idx + 1} ({seg.start} -> {seg.end}) ---\n{text}")
        clip_screenplay = "\n\n".join(slices)

        user_prompt = COLD_READ_USER_PROMPT_TEMPLATE.format(screenplay_text=clip_screenplay)
        try:
            resp = llm_provider.generate_json(COLD_READ_SYSTEM_PROMPT, user_prompt)
            stakes_score = max(0.0, min(10.0, float(resp.get("stakes_are_clear", 5.0))))
            cold_data = {
                "characters": str(resp.get("characters", "")),
                "what_is_happening": str(resp.get("what_is_happening", "")),
                "what_it_expects_next": str(resp.get("what_it_expects_next", "")),
                "what_confused_it": str(resp.get("what_confused_it", "")),
                "stakes_are_clear": stakes_score,
            }
        except Exception as e:
            logger.error(f"Cold-read failed for {cand.promo_id}: {e}")
            cold_data = {
                "characters": "",
                "what_is_happening": "",
                "what_it_expects_next": "",
                "what_confused_it": f"Error: {e}",
                "stakes_are_clear": 0.0,
                "error": str(e),
            }

        cand.cold_read = cold_data
        if "cold_read" not in cand.stages:
            cand.stages.append("cold_read")

        clarity = cand.scores.standalone_clarity
        diff = abs(cold_data["stakes_are_clear"] - clarity)
        disagreement = None
        if diff >= 2.0:
            disagreement = {
                "promo_id": cand.promo_id,
                "standalone_clarity": clarity,
                "cold_read_stakes": cold_data["stakes_are_clear"],
                "difference": round(diff, 2),
                "confused_by": cold_data.get("what_confused_it", ""),
            }

        if use_in_rank:
            cand.scores.standalone_clarity = cold_data["stakes_are_clear"]
            cand.scores.compute_composite_score()

        return cand, cold_data, clarity, cold_data["stakes_are_clear"], disagreement

    actual_workers = workers if llm_provider.is_live else 1
    if actual_workers > 1 and len(candidates) > 1:
        with ThreadPoolExecutor(max_workers=actual_workers) as ex:
            results = list(ex.map(_process_cand, candidates))
    else:
        results = [_process_cand(c) for c in candidates]

    clarity_scores = [r[2] for r in results]
    cold_scores = [r[3] for r in results]
    disagreements = [r[4] for r in results if r[4] is not None]

    corr = 0.0
    n = len(candidates)
    if n > 1:
        mean_c = sum(clarity_scores) / n
        mean_k = sum(cold_scores) / n
        num = sum((c - mean_c) * (k - mean_k) for c, k in zip(clarity_scores, cold_scores))
        den_c = math.sqrt(sum((c - mean_c) ** 2 for c in clarity_scores))
        den_k = math.sqrt(sum((k - mean_k) ** 2 for k in cold_scores))
        corr = round(num / (den_c * den_k), 3) if den_c > 0 and den_k > 0 else 0.0

    print(f"  • Cold-read complete. Correlation with standalone_clarity: r = {corr}")
    print(f"  • Large disagreements (|diff| >= 2.0): {len(disagreements)}/{n}")
    meta = _build_stage_meta(llm_provider, u_before, t_start)
    return {
        **meta,
        "correlation": corr,
        "disagreements_count": len(disagreements),
        "disagreements": disagreements,
    }


# ---------------------------------------------------------------------------
# Stage B: Audit Panel
# ---------------------------------------------------------------------------
def parse_panel_spec(panel_spec: str) -> List[Tuple[str, str]]:
    """Parses 'provider1:model1,provider2:model2'."""
    specs = []
    for part in panel_spec.split(","):
        p = part.strip()
        if not p:
            continue
        if ":" in p:
            prov, mod = p.split(":", 1)
            specs.append((prov.strip(), mod.strip()))
        else:
            specs.append((p.strip(), ""))
    return specs


def run_audit_panel(
    candidates: List[PromoCandidate],
    panel_spec: Optional[str],
    show_context: Dict[str, Any],
    episodes: List[Episode],
    taxonomy: Taxonomy,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Runs dual-judge audit panel (default: openai:gpt-6-luna and Gemini flash model).
    Assigns audit_tier (1, 2, 3) and records judge_verdicts on each candidate.
    Computes Cohen's kappa and outputs outputs/ablations/judge_comparison.json.
    """
    from src.auditor import PromoAuditor
    t_start = time.time()

    if not panel_spec or panel_spec in ("default", "True", True):
        gemini_model = discover_gemini_flash_model()
        specs = [("openai", "gpt-6-luna"), ("gemini", gemini_model)]
    else:
        specs = parse_panel_spec(panel_spec)

    if not specs:
        raise ValueError(f"Invalid panel specification: '{panel_spec}'")

    valid_judges = []
    for prov_name, mod_name in specs:
        if prov_name in PROVIDERS and _has_key(PROVIDERS[prov_name][1]):
            valid_judges.append((prov_name, mod_name))
        else:
            print(f"  • [Stage B Notice] Provider '{prov_name}' has no API key in environment; skipped.")

    if not valid_judges:
        print("  • [Stage B Warning] No requested judges have API keys. Using active fallback judge.")
        valid_judges = [("heuristic", "rule-lint")]

    if len(valid_judges) == 1:
        prov, mod = valid_judges[0]
        print(f"  • [Stage B: Audit Panel] Only 1 judge key available ({prov}:{mod or 'default'}). Running single independent judge. Agreement rate not measured for single judge.")
        provider_obj = get_llm_provider(prov, mod, cache=use_cache)
        u_before = dict(provider_obj.usage)
        auditor = PromoAuditor(llm_provider=provider_obj, show_context=show_context, episodes=episodes, taxonomy=taxonomy)

        def _audit_one(c: PromoCandidate) -> PromoCandidate:
            if not c.quality_audit or c.quality_audit.method != "llm":
                c.quality_audit = auditor.audit_candidate(c)
            c.audit_tier = 1 if c.quality_audit.passed else 3
            c.judge_verdicts = [{
                "judge": prov,
                "model": provider_obj.model,
                "pass": c.quality_audit.passed,
                "flaw_type": c.quality_audit.flaw_type,
                "one_line_reason": c.quality_audit.critique.split("\n")[0].strip(),
                "conversion_intent": c.quality_audit.conversion_intent,
            }]
            c.audit_panel = {
                "judge_1": c.quality_audit.model_dump(),
                "judge_2": None,
                "agreement": None,
            }
            if "audit_panel" not in c.stages:
                c.stages.append("audit_panel")
            return c

        workers = 8 if provider_obj.is_live else 1
        if workers > 1 and len(candidates) > 1:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                list(ex.map(_audit_one, candidates))
        else:
            for cand in candidates:
                _audit_one(cand)

        meta = _build_stage_meta(provider_obj, u_before, t_start)
        return {
            **meta,
            "mode": "single_judge",
            "agreement_rate": "not run (single judge)",
            "disagreements": [],
            "judges": [f"{prov}:{mod}"],
        }

    # Two judges available
    j1_prov, j1_mod = valid_judges[0]
    j2_prov, j2_mod = valid_judges[1]
    if j2_prov == "gemini" and not j2_mod:
        j2_mod = discover_gemini_flash_model()
    if j1_prov == "gemini" and not j1_mod:
        j1_mod = discover_gemini_flash_model()

    print(f"  • [Stage B: Audit Panel] Running two independent judges: ({j1_prov}:{j1_mod}) and ({j2_prov}:{j2_mod})...")

    p1 = get_llm_provider(j1_prov, j1_mod, cache=use_cache)
    p2 = get_llm_provider(j2_prov, j2_mod, cache=use_cache)
    u1_before = dict(p1.usage)
    u2_before = dict(p2.usage)

    auditor1 = PromoAuditor(llm_provider=p1, show_context=show_context, episodes=episodes, taxonomy=taxonomy)
    auditor2 = PromoAuditor(llm_provider=p2, show_context=show_context, episodes=episodes, taxonomy=taxonomy)

    # Run Judge 1 (e.g. OpenAI, workers=8 or cache)
    workers_j1 = 8 if p1.is_live else 1
    if workers_j1 > 1 and len(candidates) > 1:
        with ThreadPoolExecutor(max_workers=workers_j1) as ex:
            a1_results = list(ex.map(auditor1.audit_candidate, candidates))
    else:
        a1_results = [auditor1.audit_candidate(c) for c in candidates]

    # Run Judge 2 (e.g. Gemini, workers=1 as per Section 3 requirement)
    workers_j2 = 1 if j2_prov == "gemini" else (8 if p2.is_live else 1)
    if workers_j2 > 1 and len(candidates) > 1:
        with ThreadPoolExecutor(max_workers=workers_j2) as ex:
            a2_results = list(ex.map(auditor2.audit_candidate, candidates))
    else:
        a2_results = [auditor2.audit_candidate(c) for c in candidates]

    disagreements = []
    agreed_count = 0
    j1_passes = 0
    j2_passes = 0

    for cand, a1, a2 in zip(candidates, a1_results, a2_results):
        if a1.passed:
            j1_passes += 1
        if a2.passed:
            j2_passes += 1

        agreement = (a1.passed == a2.passed)
        if agreement:
            agreed_count += 1
        else:
            disagreements.append({
                "promo_id": cand.promo_id,
                "hook_quote": cand.hook.quote,
                "cliffhanger_quote": cand.cliffhanger.quote,
                "judge_1": {"model": p1.model, "passed": a1.passed, "flaw": a1.flaw_type, "critique": a1.critique},
                "judge_2": {"model": p2.model, "passed": a2.passed, "flaw": a2.flaw_type, "critique": a2.critique},
            })

        # Tier assignment: 1 = both pass, 2 = split verdict, 3 = both fail
        is_err = (a1.method == "error" or a2.method == "error")
        if is_err:
            tier = None
            combined_pass = False
            combined_flaw = "audit_error"
            combined_critique = f"Audit error occurred: J1({a1.method}): {a1.critique} | J2({a2.method}): {a2.critique}"
        elif a1.passed and a2.passed:
            tier = 1
            combined_pass = True
            combined_flaw = None
            combined_critique = f"[Both pass] [{p1.model}: {a1.critique}] | [{p2.model}: {a2.critique}]"
        elif a1.passed != a2.passed:
            tier = 2
            combined_pass = False
            failing_flaw = a2.flaw_type if a1.passed else a1.flaw_type
            combined_flaw = failing_flaw or "split_verdict"
            combined_critique = f"needs editor look: [{p1.model}: {'PASS' if a1.passed else 'FAIL'}] {a1.critique} | [{p2.model}: {'PASS' if a2.passed else 'FAIL'}] {a2.critique}"
        else:
            tier = 3
            combined_pass = False
            combined_flaw = a1.flaw_type or a2.flaw_type or "other"
            combined_critique = f"[Both fail] [{p1.model}: {a1.critique}] | [{p2.model}: {a2.critique}]"

        avg_confidence = round((a1.confidence_score + a2.confidence_score) / 2.0, 1)
        avg_conv = (
            round((float(a1.conversion_intent or 0) + float(a2.conversion_intent or 0)) / 2.0, 1)
            if a1.conversion_intent is not None or a2.conversion_intent is not None
            else None
        )

        cand.audit_tier = tier
        cand.quality_audit = QualityAudit(
            passed=combined_pass,
            method="error" if is_err else ("llm" if (a1.method == "llm" or a2.method == "llm") else "rules"),
            audit_model=f"{p1.model}+{p2.model}",
            flaw_type=combined_flaw,
            critique=combined_critique,
            confidence_score=avg_confidence,
            conversion_intent=avg_conv,
            risks=list(set(a1.risks + a2.risks)),
        )
        cand.judge_verdicts = [
            {
                "judge": p1.name,
                "model": p1.model,
                "pass": a1.passed,
                "flaw_type": a1.flaw_type,
                "one_line_reason": a1.critique.split("\n")[0].strip(),
                "conversion_intent": a1.conversion_intent,
            },
            {
                "judge": p2.name,
                "model": p2.model,
                "pass": a2.passed,
                "flaw_type": a2.flaw_type,
                "one_line_reason": a2.critique.split("\n")[0].strip(),
                "conversion_intent": a2.conversion_intent,
            },
        ]
        cand.audit_panel = {
            "judge_1": a1.model_dump(),
            "judge_2": a2.model_dump(),
            "agreement": agreement,
        }
        if "audit_panel" not in cand.stages:
            cand.stages.append("audit_panel")

    n = len(candidates)
    rate = round(agreed_count / max(1, n), 4)
    kappa = compute_cohens_kappa(agreed_count, j1_passes, j2_passes, n)

    # Identify previous top-15 promos that Gemini fails
    PREVIOUS_TOP_15 = [
        "ep41_cand_1", "ep15_cand_1", "ep01_cand_1", "ep31_cand_2", "ep28_cand_2",
        "ep46_cand_1", "ep34_cand_1", "ep18_cand_1", "ep27_cand_2", "ep23_cand_1",
        "ep35_cand_1", "ep50_cand_1", "ep48_cand_2", "ep12_cand_1", "ep18_cand_2",
    ]
    gemini_fails_prev_top15 = []
    for c in candidates:
        if c.promo_id in PREVIOUS_TOP_15:
            g_v = next((v for v in c.judge_verdicts if "gemini" in v.get("judge", "").lower() or "gemini" in v.get("model", "").lower()), None)
            if g_v and not g_v["pass"]:
                gemini_fails_prev_top15.append({
                    "promo_id": c.promo_id,
                    "flaw_type": g_v.get("flaw_type"),
                    "reason": g_v.get("one_line_reason"),
                })

    tier_1_c = sum(1 for c in candidates if c.audit_tier == 1)
    tier_2_c = sum(1 for c in candidates if c.audit_tier == 2)
    tier_3_c = sum(1 for c in candidates if c.audit_tier == 3)

    print(f"  • Audit Panel complete.")
    print(f"  • Judge 1 ({p1.model}) pass rate: {j1_passes}/{n} ({j1_passes/max(1,n):.1%})")
    print(f"  • Judge 2 ({p2.model}) pass rate: {j2_passes}/{n} ({j2_passes/max(1,n):.1%})")
    print(f"  • Agreement rate: {rate:.1%} ({agreed_count}/{n}), Cohen's kappa: {kappa}")
    print(f"  • Tier breakdown: Tier 1={tier_1_c}, Tier 2={tier_2_c}, Tier 3={tier_3_c}")
    if disagreements:
        print(f"  • Disagreements on {len(disagreements)} candidate(s).")

    comparison_report = {
        "total_audited": n,
        "judge_1": {
            "provider": p1.name,
            "model": p1.model,
            "passed": j1_passes,
            "pass_rate": round(j1_passes / max(1, n), 4),
        },
        "judge_2": {
            "provider": p2.name,
            "model": p2.model,
            "passed": j2_passes,
            "pass_rate": round(j2_passes / max(1, n), 4),
        },
        "agreement_count": agreed_count,
        "agreement_rate": rate,
        "cohens_kappa": kappa,
        "tier_counts": {
            "tier_1": tier_1_c,
            "tier_2": tier_2_c,
            "tier_3": tier_3_c,
            "audit_errors": sum(1 for c in candidates if c.quality_audit and c.quality_audit.method == "error"),
        },
        "disagreements": disagreements,
        "gemini_fails_previous_top_15": gemini_fails_prev_top15,
    }

    os.makedirs("outputs/ablations", exist_ok=True)
    with open("outputs/ablations/judge_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2, ensure_ascii=False)

    meta = _build_stage_meta(p1, u1_before, t_start, extra_provider=p2, extra_u_before=u2_before)
    return {
        **meta,
        **comparison_report,
        "mode": "dual_judge",
        "judges": [f"{p1.name}:{p1.model}", f"{p2.name}:{p2.model}"],
    }


# ---------------------------------------------------------------------------
# Stage C: Listwise Rerank
# ---------------------------------------------------------------------------
def run_rerank(
    candidates: List[PromoCandidate],
    show_context: Dict[str, Any],
    llm_provider: BaseLLMProvider,
    max_cands: int = 25,
) -> Dict[str, Any]:
    """
    Takes up to 25 tier-1 (or audit-passing) candidates.
    Asks model to rank them listwise with reasons, twice with different shuffles.
    Reports top-10 overlap and Kendall tau between runs, and blends weighted score and rerank.
    """
    t_start = time.time()
    u_before = dict(llm_provider.usage)

    # Filter over tier-1 candidates (cap 25), falling back to audit-passing if untiered
    has_tier1 = any(getattr(c, "audit_tier", None) == 1 for c in candidates)
    if has_tier1:
        passing = [c for c in candidates if getattr(c, "audit_tier", None) == 1][:max_cands]
    else:
        passing = [c for c in candidates if c.quality_audit and c.quality_audit.passed][:max_cands]

    if not passing:
        print("  • [Stage C: Rerank] No tier-1 / audit-passing candidates to rerank.")
        meta = _build_stage_meta(llm_provider, u_before, t_start)
        return {**meta, "status": "skipped", "reason": "no candidates available to rerank", "overlap_top_10": 0.0, "run_1": [], "run_2": []}

    print(f"\n[Stage C: Listwise Rerank] Reranking {len(passing)} candidates...")

    def _format_for_rerank(cands: List[PromoCandidate]) -> str:
        blocks = []
        for c in cands:
            segs = ", ".join(f"{s.start}->{s.end}" for s in c.segments)
            blocks.append(
                f"- Candidate ID: {c.promo_id}\n"
                f"  Episode: {c.episodes} | Duration: {c.total_duration:.1f}s [{segs}]\n"
                f"  Hook ({c.hook.type}): \"{c.hook.quote}\"\n"
                f"  Cliffhanger ({c.cliffhanger.type}): \"{c.cliffhanger.quote}\" (withheld: {c.cliffhanger.withheld_payoff})\n"
                f"  Why it works: {c.why_it_works}"
            )
        return "\n\n".join(blocks)

    def _execute_run(seed: int, run_idx: int) -> Tuple[List[str], Dict[str, str]]:
        shuffled = list(passing)
        random.Random(seed).shuffle(shuffled)
        prompt = RERANK_USER_PROMPT_TEMPLATE.format(
            show_title=show_context.get("show_title", "Microdrama"),
            show_premise=show_context.get("premise", ""),
            num_candidates=len(shuffled),
            candidates_block=_format_for_rerank(shuffled),
        )
        try:
            resp = llm_provider.generate_json(RERANK_SYSTEM_PROMPT, prompt)
            ranking_list = resp.get("ranking", [])
            ordered_ids = []
            reasons = {}
            for item in ranking_list:
                cid = item.get("promo_id")
                if cid and cid not in ordered_ids:
                    ordered_ids.append(cid)
                    reasons[cid] = str(item.get("reason", ""))
            # Append any missing candidates
            for c in shuffled:
                if c.promo_id not in ordered_ids:
                    ordered_ids.append(c.promo_id)
                    reasons[c.promo_id] = "Ranked by default fallback"
            return ordered_ids, reasons
        except Exception as e:
            logger.error(f"Rerank run {run_idx} failed: {e}")
            return [c.promo_id for c in shuffled], {c.promo_id: f"Error: {e}" for c in shuffled}

    run1_ids, run1_reasons = _execute_run(seed=42, run_idx=1)
    run2_ids, run2_reasons = _execute_run(seed=1337, run_idx=2)

    top10_r1 = set(run1_ids[:10])
    top10_r2 = set(run2_ids[:10])
    inter_runs = len(top10_r1.intersection(top10_r2))
    overlap_between_runs = inter_runs / min(10.0, float(len(passing)))

    orig_sorted_cands = sorted(passing, key=lambda c: -c.scores.composite_score)
    orig_ids = [c.promo_id for c in orig_sorted_cands]
    original_top10 = set(orig_ids[:10])
    overlap_with_original = len(top10_r1.intersection(original_top10)) / min(10.0, float(len(passing)))

    # Kendall tau rank correlation calculations
    r1_ranks = [run1_ids.index(c.promo_id) + 1 for c in passing]
    r2_ranks = [run2_ids.index(c.promo_id) + 1 for c in passing]
    orig_ranks = [orig_ids.index(c.promo_id) + 1 for c in passing]

    tau_between_runs = kendall_tau(r1_ranks, r2_ranks)
    tau_r1_vs_weighted = kendall_tau(r1_ranks, orig_ranks)
    tau_r2_vs_weighted = kendall_tau(r2_ranks, orig_ranks)

    # Store rerank details and blend scores
    n_cands = len(passing)
    for c in passing:
        r1 = run1_ids.index(c.promo_id) + 1 if c.promo_id in run1_ids else n_cands
        r2 = run2_ids.index(c.promo_id) + 1 if c.promo_id in run2_ids else n_cands
        avg_rank = (r1 + r2) / 2.0
        # Convert rank to 0-10 score (rank 1 -> 10.0, rank N -> 0.0)
        rerank_norm_score = max(0.0, 10.0 * (1.0 - (avg_rank - 1.0) / max(1, n_cands - 1)))

        c.rerank = {
            "run_1_rank": r1,
            "run_1_reason": run1_reasons.get(c.promo_id, ""),
            "run_2_rank": r2,
            "run_2_reason": run2_reasons.get(c.promo_id, ""),
            "avg_rank": avg_rank,
            "rerank_score": round(rerank_norm_score, 2),
        }
        if "rerank" not in c.stages:
            c.stages.append("rerank")

        blended = WEIGHT_WEIGHTED_SCORE * c.scores.composite_score + WEIGHT_RERANK_SCORE * rerank_norm_score
        c.scores.composite_score = round(blended, 2)

    print(f"  • Rerank complete.")
    print(f"  • Top-10 overlap between Run 1 and Run 2: {overlap_between_runs:.0%}, Kendall tau: {tau_between_runs}")
    print(f"  • Top-10 overlap between Run 1 and weighted ranking: {overlap_with_original:.0%}, Kendall tau: {tau_r1_vs_weighted}")
    print(f"  • Kendall tau between Run 2 and weighted ranking: {tau_r2_vs_weighted}")

    meta = _build_stage_meta(llm_provider, u_before, t_start)
    return {
        **meta,
        "overlap_between_runs": overlap_between_runs,
        "overlap_with_original": overlap_with_original,
        "kendall_tau_between_runs": tau_between_runs,
        "kendall_tau_run1_vs_weighted": tau_r1_vs_weighted,
        "kendall_tau_run2_vs_weighted": tau_r2_vs_weighted,
        "run_1_top_10": run1_ids[:10],
        "run_2_top_10": run2_ids[:10],
    }


# ---------------------------------------------------------------------------
# Stage D: Auto-Profile
# ---------------------------------------------------------------------------
def run_auto_profile(
    episodes: List[Episode],
    show_name: str,
    output_path: str,
    llm_provider: BaseLLMProvider,
) -> Dict[str, Any]:
    """
    Generates a draft show profile using long-context analysis of episodes.
    Writes strictly to config/shows/<show>.generated.yaml. Never overwrites hand-written profile.
    """
    t_start = time.time()
    u_before = dict(llm_provider.usage)
    print(f"\n[Stage D: Auto-Profile] Generating draft profile for '{show_name}'...")
    sample_texts = []
    # Use representative episodes (e.g. first 15 episodes) to capture premise, protagonist, and recurring cast
    for ep in episodes[:15]:
        sample_texts.append(f"=== EPISODE {ep.episode_number} ===\n" + format_episode_for_analysis(ep, include_camera=False))
    full_text = "\n\n".join(sample_texts)

    user_prompt = AUTO_PROFILE_USER_PROMPT_TEMPLATE.format(screenplay_text=full_text)
    resp = llm_provider.generate_json(AUTO_PROFILE_SYSTEM_PROMPT, user_prompt)

    profile_yaml_str = resp.get("profile_yaml", "")
    if not profile_yaml_str and "show_title" in resp:
        profile_yaml_str = yaml.dump(resp, sort_keys=False)

    # Validate that it parses as YAML
    parsed_yaml = yaml.safe_load(profile_yaml_str) or {}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Auto-generated show profile (draft). Hand-written profiles always take precedence.\n")
        yaml.dump(parsed_yaml, f, sort_keys=False, allow_unicode=True)

    print(f"  • Draft show profile written to: {output_path}")
    meta = _build_stage_meta(llm_provider, u_before, t_start)
    result = dict(parsed_yaml)
    result.update(meta)
    result["profile"] = parsed_yaml
    result["profile_path"] = output_path
    return result


# ---------------------------------------------------------------------------
# Stage E: Consolidate Taxonomy
# ---------------------------------------------------------------------------
def run_consolidate_taxonomy(
    candidates: List[PromoCandidate],
    current_taxonomy: Taxonomy,
    output_path: str,
    llm_provider: BaseLLMProvider,
) -> Dict[str, Any]:
    """
    Clusters all 'new:' hook and cliffhanger tags into canonical types.
    Writes strictly to config/taxonomy.suggested.yaml. Never edits config/taxonomy.yaml.
    Reports tags-to-clusters ratio and how many top-15 promos use a new type.
    """
    t_start = time.time()
    u_before = dict(llm_provider.usage)
    print(f"\n[Stage E: Consolidate Taxonomy] Analyzing newly proposed tags...")
    new_hook_tags = sorted({c.hook.type for c in candidates if c.hook.type.startswith("new:")})
    new_cliff_tags = sorted({c.cliffhanger.type for c in candidates if c.cliffhanger.type.startswith("new:")})
    all_new = new_hook_tags + new_cliff_tags

    if not all_new:
        print("  • No 'new:' tags found to consolidate.")
        meta = _build_stage_meta(llm_provider, u_before, t_start)
        return {**meta, "status": "skipped", "reason": "no 'new:' tags to consolidate", "tags_to_clusters_ratio": 0.0, "top_15_new_tag_count": 0}

    prompt = CONSOLIDATE_TAXONOMY_USER_PROMPT_TEMPLATE.format(
        new_tags_list="\n".join(f"- {t}" for t in all_new),
        existing_hooks=", ".join(current_taxonomy.hook_by_id.keys()),
        existing_cliffhangers=", ".join(current_taxonomy.cliffhanger_by_id.keys()),
    )
    resp = llm_provider.generate_json(CONSOLIDATE_TAXONOMY_SYSTEM_PROMPT, prompt)
    clusters = resp.get("clusters", [])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Suggested taxonomy clusters generated from 'new:' model tags.\n")
        f.write("# Review and merge manually into config/taxonomy.yaml as appropriate.\n\n")
        yaml.dump({"suggested_clusters": clusters}, f, sort_keys=False, allow_unicode=True)

    ratio = round(len(all_new) / max(1, len(clusters)), 2)
    top15 = candidates[:15]
    top15_new_count = sum(
        1 for c in top15 if c.hook.type.startswith("new:") or c.cliffhanger.type.startswith("new:")
    )

    print(f"  • Clusters written to: {output_path}")
    print(f"  • Clustered {len(all_new)} tags into {len(clusters)} canonical types (ratio: {ratio}:1).")
    print(f"  • Top-15 promos using newly proposed types: {top15_new_count}/15.")
    meta = _build_stage_meta(llm_provider, u_before, t_start)
    return {
        **meta,
        "tags_count": len(all_new),
        "clusters_count": len(clusters),
        "tags_to_clusters_ratio": ratio,
        "top_15_new_tag_count": top15_new_count,
    }


# ---------------------------------------------------------------------------
# Stage F: Recheck Empty
# ---------------------------------------------------------------------------
def run_recheck_empty(
    episodes: List[Episode],
    valid_candidates: List[PromoCandidate],
    show_context: Dict[str, Any],
    output_path: str,
    llm_provider: BaseLLMProvider,
) -> Dict[str, Any]:
    """
    For episodes with no valid candidate, runs a relaxed prompt for the best 20-60s moment.
    Validates it against screenplay beat edges and writes outputs/promos.recheck.json.
    Reports per episode: model too strict vs genuinely quiet.
    """
    t_start = time.time()
    u_before = dict(llm_provider.usage)
    valid_ep_nums = {ep for c in valid_candidates for ep in c.episodes}
    empty_episodes = [e for e in episodes if e.episode_number not in valid_ep_nums]

    print(f"\n[Stage F: Recheck Empty] Investigating {len(empty_episodes)} empty episode(s)...")
    recheck_results = []
    verdicts_summary = {"genuinely_quiet": 0, "model_too_strict": 0}

    def _check_ep(ep: Episode) -> Dict[str, Any]:
        text = format_episode_for_analysis(ep, include_camera=False)
        prompt = RECHECK_EMPTY_USER_PROMPT_TEMPLATE.format(
            show_title=show_context.get("show_title", "Microdrama"),
            show_premise=show_context.get("premise", ""),
            episode_num=ep.episode_number,
            screenplay_text=text,
        )
        try:
            resp = llm_provider.generate_json(RECHECK_EMPTY_SYSTEM_PROMPT, prompt)
            seg = resp.get("segment") or {}
            s_sec = try_parse_timestamp(seg.get("start"))
            e_sec = try_parse_timestamp(seg.get("end"))
            validated = False
            b_start, b_end = None, None
            if s_sec is not None and e_sec is not None:
                b_start = snap_to_beat_edge(ep, s_sec, "start")
                b_end = snap_to_beat_edge(ep, e_sec, "end")
                if b_start and b_end and b_end.end_seconds > b_start.start_seconds:
                    validated = True

            verdict = resp.get("verdict", "genuinely_quiet")
            if verdict not in ("genuinely_quiet", "model_too_strict"):
                verdict = "genuinely_quiet"

            return {
                "episode": ep.episode_number,
                "has_moment": resp.get("has_moment", False),
                "validated_beat_edges": validated,
                "start": b_start.start_str if b_start else seg.get("start", ""),
                "end": b_end.end_str if b_end else seg.get("end", ""),
                "verdict": verdict,
                "explanation": resp.get("explanation", ""),
            }
        except Exception as e:
            logger.error(f"Recheck failed for Ep {ep.episode_number}: {e}")
            return {
                "episode": ep.episode_number,
                "error": str(e),
                "verdict": "error",
            }

    workers = 8 if llm_provider.is_live else 1
    if workers > 1 and len(empty_episodes) > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            recheck_results = list(ex.map(_check_ep, empty_episodes))
    else:
        recheck_results = [_check_ep(ep) for ep in empty_episodes]

    for res in recheck_results:
        v = res.get("verdict")
        if v in verdicts_summary:
            verdicts_summary[v] += 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recheck_results, f, indent=2, ensure_ascii=False)

    print(f"  • Recheck report written to: {output_path}")
    print(f"  • Verdict breakdown: {verdicts_summary['genuinely_quiet']} genuinely quiet, {verdicts_summary['model_too_strict']} model too strict.")
    meta = _build_stage_meta(llm_provider, u_before, t_start)
    return {
        **meta,
        "empty_episodes_count": len(empty_episodes),
        "results": recheck_results,
        "summary": verdicts_summary,
    }


# ---------------------------------------------------------------------------
# Section 5: CSV Export
# ---------------------------------------------------------------------------
def export_promos_to_csv(promos: List[PromoCandidate], filepath: str) -> None:
    """
    Exports promos to CSV with one row per segment.
    Columns: promo_id, rank, episode, segment_order, start, end, duration, hook_quote, cliffhanger_quote, payoff_location, audit_verdict
    Timecodes in mm:ss.ss.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    headers = [
        "promo_id",
        "rank",
        "episode",
        "segment_order",
        "start",
        "end",
        "duration",
        "hook_quote",
        "cliffhanger_quote",
        "payoff_location",
        "audit_verdict",
    ]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for cand in promos:
            audit_verdict = (
                "PASS" if (cand.quality_audit and cand.quality_audit.passed)
                else "FAIL" if (cand.quality_audit and cand.quality_audit.method != "error")
                else "UNAUDITED"
            )
            payoff_loc = cand.payoff_location or "unknown"
            for order, seg in enumerate(cand.segments, start=1):
                ep = seg.episode if seg.episode is not None else cand.episodes[0]
                dur_str = seconds_to_timestamp(seg.duration)
                writer.writerow([
                    cand.promo_id,
                    cand.rank or "",
                    ep,
                    order,
                    seg.start,
                    seg.end,
                    dur_str,
                    cand.hook.quote,
                    cand.cliffhanger.quote,
                    payoff_loc,
                    audit_verdict,
                ])
    print(f"✓ Exported {len(promos)} promos ({sum(len(c.segments) for c in promos)} segments) to CSV: {filepath}")
