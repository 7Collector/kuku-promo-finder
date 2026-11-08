"""
Main execution pipeline for Kuku Promo Finder.
Parses screenplays, generates candidate promos, reranks for diversity, runs quality auditing,
and orchestrates measured LLM stages.
"""

import os
import sys
import json
import time
import argparse
import subprocess
import yaml
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.parser import parse_all_episodes
from src.taxonomy import Taxonomy
from src.providers.factory import get_llm_provider, ProviderConfigError, PROVIDERS, _has_key
from src.providers.gemini import discover_gemini_flash_model
from src.validation import check_candidate
from src.extractor import PromoExtractor
from src.composite import CompositePromoBuilder
from src.ranker import PromoRanker
from src.auditor import PromoAuditor
from src.models import PromoCandidate, QualityAudit
from src.utils.logging import setup_logger, logger
from src.utils.cost import calculate_cost_usd, format_stage_cost
from src.constants import (
    WEIGHT_HOOK,
    WEIGHT_CLIFFHANGER,
    WEIGHT_PAYOFF_WITHHELD,
    WEIGHT_INJUSTICE_TENSION,
    WEIGHT_STANDALONE_CLARITY,
    WEIGHT_CONVERSION_INTENT,
)
from src.stages import (
    run_cold_read,
    run_audit_panel,
    run_rerank,
    run_auto_profile,
    run_consolidate_taxonomy,
    run_recheck_empty,
    export_promos_to_csv,
    parse_panel_spec,
)


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


DEFAULT_INPUT_DIR = "assets/I Married a Broken Soldier. He was a Duke"
DEFAULT_SHOW = "broken_soldier"


class PipelineError(Exception):
    """A condition under which nothing should be written. `code` becomes the process exit status."""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def _sibling(path: str, suffix: str) -> str:
    return os.path.splitext(path)[0] + suffix


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


def _run_parallel(fn, items, workers):
    if workers <= 1:
        return [fn(i) for i in items]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def run_pipeline(
    input_dir: str,
    taxonomy_path: str,
    context_path: str,
    output_json: str,
    output_md: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    audit_provider: Optional[str] = None,
    audit_model: Optional[str] = None,
    allow_self_audit: bool = False,
    audit_top_n: Optional[int] = None,
    top_k: int = 15,
    verbose: bool = False,
    composites: bool = False,
    use_cache: bool = True,
    workers: int = 8,
    allow_empty: bool = False,
    # Measured LLM stages
    cold_read: bool = False,
    use_cold_read_in_rank: bool = False,
    audit_panel: Optional[str] = None,
    rerank: bool = False,
    auto_profile: bool = False,
    consolidate_taxonomy: bool = False,
    recheck_empty: bool = False,
    export_csv: bool = False,
    scoring_weights: Optional[Dict[str, float]] = None,
) -> List[PromoCandidate]:
    setup_logger(verbose=verbose)
    t_start = time.time()
    print("=" * 70)
    print("KUKU PROMO FINDER - MICRODRAMA VIRAL CLIP PIPELINE")
    print("=" * 70)

    stages_enabled = ["extraction", "audit"]
    if cold_read:
        stages_enabled.append("cold_read")
    if audit_panel:
        stages_enabled.append("audit_panel")
    if rerank:
        stages_enabled.append("rerank")
    if auto_profile:
        stages_enabled.append("auto_profile")
    if consolidate_taxonomy:
        stages_enabled.append("consolidate_taxonomy")
    if recheck_empty:
        stages_enabled.append("recheck_empty")
    if export_csv:
        stages_enabled.append("export_csv")

    stage_reports: Dict[str, Any] = {}

    # 1. Configuration
    print(f"\n[1/6] Loading taxonomy from {taxonomy_path} and show context from {context_path}...")
    if not os.path.exists(context_path) and auto_profile:
        print(f"  • Show profile '{context_path}' not found; --auto-profile active, will generate draft profile.")
        taxonomy = Taxonomy(taxonomy_path)
        show_context = {}
    else:
        taxonomy = Taxonomy(taxonomy_path, show_context_path=context_path)
        show_context = load_yaml(context_path)
    show_slug = os.path.splitext(os.path.basename(context_path))[0].replace(".generated", "")
    print(f"  • Hook types: {len(taxonomy.hooks)}, cliffhanger types: {len(taxonomy.cliffhangers)}")
    print(f"  • Show: {show_context.get('show_title', '(to be auto-profiled)')}")

    # Initialize extraction LLM provider
    extractor_provider_name = provider or "openai"
    extractor_model_name = model or ("gpt-6-luna" if extractor_provider_name == "openai" else None)
    llm_provider = get_llm_provider(provider_name=extractor_provider_name, model_name=extractor_model_name, cache=use_cache)
    print(f"  • Extractor: {llm_provider.name} (model: {llm_provider.model})")
    if not llm_provider.is_live:
        print("  • NOTE: offline keyword engine. Output is a smoke test, not LLM-judged.")

    # Validate audit configuration early (Refuse-same-model rule)
    discovered_gemini_model = None
    if _has_key(PROVIDERS["gemini"][1]):
        try:
            discovered_gemini_model = discover_gemini_flash_model()
        except Exception as e:
            logger.warning(f"Could not discover Gemini model: {e}")

    if audit_panel:
        p_specs = parse_panel_spec(audit_panel) if audit_panel not in ("default", "True", True) else [("openai", "gpt-6-luna"), ("gemini", discovered_gemini_model)]
        if all(s[0] == llm_provider.name and (s[1] is None or s[1] == llm_provider.model) for s in p_specs):
            if not allow_self_audit and llm_provider.is_live:
                raise PipelineError(f"Refusing to run: audit panel consists solely of the extractor model ('{llm_provider.model}') without --allow-self-audit. An independent model must judge.", code=2)
    else:
        effective_audit_provider = audit_provider or ("gemini" if _has_key(PROVIDERS["gemini"][1]) else llm_provider.name)
        effective_audit_model = audit_model
        if effective_audit_provider == "gemini" and not effective_audit_model:
            effective_audit_model = discovered_gemini_model

        is_same_model = (effective_audit_provider == llm_provider.name and (effective_audit_model == llm_provider.model or (not effective_audit_model and not llm_provider.model)))
        if is_same_model and llm_provider.is_live and not allow_self_audit:
            raise PipelineError(
                f"Refusing to run: extractor model ('{llm_provider.model}') cannot be the sole auditor without --allow-self-audit. "
                "Configure an independent judge (e.g. Gemini) or pass --allow-self-audit.",
                code=2,
            )

    # 2. Parse
    print(f"\n[2/6] Parsing screenplays from: {input_dir}...")
    episodes = parse_all_episodes(input_dir)
    total_beats = sum(len(ep.all_beats) for ep in episodes)
    print(f"  • Parsed {len(episodes)} episodes, {total_beats} beats.")
    if not episodes or total_beats == 0:
        raise PipelineError(f"No beats could be parsed from {input_dir}. Expected '**HEADER**' then 'Start: (mm:ss.ss) | End: (mm:ss.ss)' per beat. Nothing was written.")
    episodes_by_num = {e.episode_number: e for e in episodes}
    prev_logline = {}
    for prev, cur in zip(episodes, episodes[1:]):
        prev_logline[cur.episode_number] = f"Episode {prev.episode_number}: {prev.logline}"

    # Stage D: Auto-Profile (if enabled)
    if auto_profile:
        profile_gen_path = os.path.join("config", "shows", f"{show_slug}.generated.yaml")
        stage_reports["auto_profile"] = run_auto_profile(
            episodes=episodes, show_name=show_slug, output_path=profile_gen_path, llm_provider=llm_provider
        )
        if not show_context:
            show_context = stage_reports["auto_profile"].get("profile", {})
            taxonomy = Taxonomy(taxonomy_path, show_context_path=profile_gen_path)

    # 3. Extraction
    print(f"\n[3/6] Extracting promo candidates...")
    extractor = PromoExtractor(taxonomy=taxonomy, llm_provider=llm_provider, episodes=episodes)

    def process_ep(ep):
        return extractor.extract_candidates_for_episode(
            episode=ep, show_context=show_context,
            prev_episode_summary=prev_logline.get(ep.episode_number, ""), max_candidates=2,
        )

    single_candidates: List[PromoCandidate] = []
    for r in _run_parallel(process_ep, episodes, workers if llm_provider.is_live else 1):
        single_candidates.extend(r)
    print(f"  • {len(single_candidates)} single-episode candidates.")
    if extractor.drop_reasons:
        print(f"  • Rejected by validation: {dict(extractor.drop_reasons)}")
    if extractor.failures:
        print(f"  • WARNING: extraction FAILED for {len(extractor.failures)} episode(s): {sorted(extractor.failures)}")
        if len(extractor.failures) == len(episodes):
            raise PipelineError("Extraction failed for every episode; nothing was written. First error: "
                                + next(iter(extractor.failures.values())), code=3)

    composite_list: List[PromoCandidate] = []
    if composites:
        composite_list = CompositePromoBuilder(taxonomy=taxonomy).build_cross_episode_composites(
            episodes=episodes, single_candidates=single_candidates, max_composites=2)
        print(f"  • {len(composite_list)} EXPERIMENTAL cross-episode composites.")
    all_candidates = single_candidates + composite_list

    # 4. Scoring and constraint enforcement
    print(f"\n[4/6] Scoring and enforcing hard constraints (20-60s, hook within 3s, real beat edges, real quotes)...")
    ranker = PromoRanker(taxonomy=taxonomy)
    valid: List[PromoCandidate] = []
    violations: Counter = Counter()
    for cand in all_candidates:
        cand.scores.compute_composite_score(
            taxonomy.get_hook_weight(cand.hook.type),
            taxonomy.get_cliffhanger_weight(cand.cliffhanger.type),
            weights=scoring_weights,
        )
        errs = check_candidate(cand, episodes_by_num)
        if errs or not ranker.validate_constraints(cand):
            for e in errs or ["constraint check failed"]:
                violations[e.split(" in Ep")[0]] += 1
            continue
        valid.append(cand)
    print(f"  • {len(valid)}/{len(all_candidates)} candidates satisfy every hard constraint.")
    deduped = ranker.deduplicate(valid, overlap_threshold=0.35)
    print(f"  • {len(deduped)} remain after de-duplication.")

    # Stage F: Recheck Empty (if enabled)
    if recheck_empty:
        recheck_path = _sibling(output_json, ".recheck.json")
        stage_reports["recheck_empty"] = run_recheck_empty(
            episodes=episodes,
            valid_candidates=valid,
            show_context=show_context,
            output_path=recheck_path,
            llm_provider=llm_provider,
        )

    # 5. Audit
    discovered_gemini_model = None
    if _has_key(PROVIDERS["gemini"][1]):
        try:
            discovered_gemini_model = discover_gemini_flash_model()
        except Exception as e:
            logger.warning(f"Could not discover Gemini model: {e}")

    # --audit-top-n filtering
    if audit_top_n is not None and audit_top_n < len(deduped):
        print(f"  • --audit-top-n {audit_top_n} active: auditing only top {audit_top_n} candidates by score; rest marked 'not audited'.")
        deduped_sorted = sorted(deduped, key=lambda c: -c.scores.composite_score)
        to_audit = deduped_sorted[:audit_top_n]
        not_audited = deduped_sorted[audit_top_n:]
        for c in not_audited:
            c.audit_tier = None
            c.quality_audit = QualityAudit(
                passed=False,
                method="not_audited",
                flaw_type="not_audited",
                critique="Excluded from audit by --audit-top-n threshold.",
                confidence_score=0.0,
            )
            c.judge_verdicts = []
    else:
        to_audit = deduped
        not_audited = []

    if audit_panel:
        print(f"\n[5/6] Auditing via Dual-Judge Panel: {audit_panel}...")
        p_specs = parse_panel_spec(audit_panel) if audit_panel not in ("default", "True", True) else [("openai", "gpt-6-luna"), ("gemini", discovered_gemini_model)]
        if all(s[0] == llm_provider.name and (s[1] is None or s[1] == llm_provider.model) for s in p_specs):
            if not allow_self_audit and llm_provider.is_live:
                raise PipelineError(f"Refusing to run: audit panel consists solely of the extractor model ('{llm_provider.model}') without --allow-self-audit. An independent model must judge.", code=2)
        stage_reports["audit_panel"] = run_audit_panel(
            candidates=to_audit,
            panel_spec=audit_panel,
            show_context=show_context,
            episodes=episodes,
            taxonomy=taxonomy,
            use_cache=use_cache,
        )
        audit_provider_obj = llm_provider
    else:
        effective_audit_provider = audit_provider or ("gemini" if _has_key(PROVIDERS["gemini"][1]) else llm_provider.name)
        effective_audit_model = audit_model
        if effective_audit_provider == "gemini" and not effective_audit_model:
            effective_audit_model = discovered_gemini_model

        # Refuse-same-model rule
        is_same_model = (effective_audit_provider == llm_provider.name and (effective_audit_model == llm_provider.model or (not effective_audit_model and not llm_provider.model)))
        if is_same_model and llm_provider.is_live and not allow_self_audit:
            raise PipelineError(
                f"Refusing to run: extractor model ('{llm_provider.model}') cannot be the sole auditor without --allow-self-audit. "
                "Configure an independent judge (e.g. Gemini) or pass --allow-self-audit.",
                code=2,
            )

        audit_provider_obj = get_llm_provider(
            provider_name=effective_audit_provider,
            model_name=effective_audit_model,
            cache=use_cache,
        )
        print(f"\n[5/6] Auditing {len(to_audit)} candidates ({audit_provider_obj.name}, model {audit_provider_obj.model})...")
        auditor = PromoAuditor(llm_provider=audit_provider_obj, show_context=show_context, episodes=episodes, taxonomy=taxonomy)

        def audit_cand(cand):
            cand.quality_audit = auditor.audit_candidate(cand)
            cand.audit_tier = 1 if cand.quality_audit.passed else 3
            cand.judge_verdicts = [{
                "judge": audit_provider_obj.name,
                "model": audit_provider_obj.model,
                "pass": cand.quality_audit.passed,
                "flaw_type": cand.quality_audit.flaw_type,
                "one_line_reason": cand.quality_audit.critique.split("\n")[0][:150] if cand.quality_audit.critique else "",
                "conversion_intent": cand.quality_audit.conversion_intent,
            }]
            return cand

        audit_workers = 1 if audit_provider_obj.name == "gemini" else (workers if audit_provider_obj.is_live else 1)
        _run_parallel(audit_cand, to_audit, audit_workers)

    deduped = to_audit + not_audited
    n_pass = sum(1 for c in deduped if c.quality_audit and c.quality_audit.passed)
    n_err = sum(1 for c in deduped if c.quality_audit and c.quality_audit.method == "error")
    n_not_audited = sum(1 for c in deduped if c.quality_audit and c.quality_audit.method == "not_audited")
    n_fail = len(deduped) - n_pass - n_err - n_not_audited
    tier_1_c = sum(1 for c in deduped if getattr(c, "audit_tier", None) == 1)
    tier_2_c = sum(1 for c in deduped if getattr(c, "audit_tier", None) == 2)
    tier_3_c = sum(1 for c in deduped if getattr(c, "audit_tier", None) == 3)

    label = "passed" if (audit_panel or audit_provider_obj.is_live) else "passed rule lint (not a quality judgement)"
    print(f"  • {n_pass} {label}, {n_fail} failed, {n_err} unaudited (audit error), {n_not_audited} not audited.")

    # Stage A: Cold Read (if enabled)
    if cold_read:
        stage_reports["cold_read"] = run_cold_read(
            candidates=deduped,
            episodes_by_num=episodes_by_num,
            llm_provider=llm_provider,
            use_in_rank=use_cold_read_in_rank,
        )

    # Stage C: Listwise Rerank (if enabled)
    if rerank:
        stage_reports["rerank"] = run_rerank(
            candidates=deduped,
            show_context=show_context,
            llm_provider=llm_provider,
            max_cands=25,
        )

    # 6. Rank
    print(f"\n[6/6] Ranking (audit-passing first, diversity-penalised)...")
    final_ranked = ranker.rerank_for_diversity(deduped, top_k=top_k)
    print(f"  • Selected top {len(final_ranked)}.")
    if not final_ranked and not allow_empty:
        raise PipelineError("No promos survived the hard constraints; existing outputs were left untouched "
                            "(use --allow-empty to write an empty result).", code=3)

    # Stage E: Consolidate Taxonomy (if enabled)
    if consolidate_taxonomy:
        suggested_tax_path = "config/taxonomy.suggested.yaml"
        stage_reports["consolidate_taxonomy"] = run_consolidate_taxonomy(
            candidates=deduped,
            current_taxonomy=taxonomy,
            output_path=suggested_tax_path,
            llm_provider=llm_provider,
        )

    # CSV Export (if enabled)
    if export_csv:
        csv_path = _sibling(output_json, ".csv") if (export_csv in ("default", True)) else export_csv
        export_promos_to_csv(final_ranked, csv_path)

    # Check that requested stages made calls or hits (honesty check)
    for s_name in stages_enabled:
        if s_name in stage_reports and isinstance(stage_reports[s_name], dict):
            sr = stage_reports[s_name]
            if sr.get("live_calls", 0) == 0 and sr.get("cache_hits", 0) == 0:
                raise PipelineError(f"Requested stage '{s_name}' made zero live calls and zero cache hits.", code=2)
    if llm_provider.is_live and llm_provider.usage.get("calls", 0) == 0 and llm_provider.usage.get("cache_hits", 0) == 0:
        raise PipelineError("Extraction stage made zero live calls and zero cache hits.", code=2)

    # Outputs
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pool_path, meta_path, rejected_path = (_sibling(output_json, s) for s in (".pool.json", ".meta.json", ".rejected.json"))
    for path in (output_json, output_md, pool_path, meta_path, rejected_path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if audit_provider_obj is llm_provider:
        usage = {"extractor_and_auditor_combined": llm_provider.usage}
    else:
        usage = {"extractor": llm_provider.usage, "auditor": audit_provider_obj.usage}

    effective_weights = {
        "hook": scoring_weights.get("hook", WEIGHT_HOOK) if scoring_weights else WEIGHT_HOOK,
        "cliffhanger": scoring_weights.get("cliffhanger", WEIGHT_CLIFFHANGER) if scoring_weights else WEIGHT_CLIFFHANGER,
        "payoff_withheld": scoring_weights.get("payoff_withheld", WEIGHT_PAYOFF_WITHHELD) if scoring_weights else WEIGHT_PAYOFF_WITHHELD,
        "injustice_tension": scoring_weights.get("injustice_tension", WEIGHT_INJUSTICE_TENSION) if scoring_weights else WEIGHT_INJUSTICE_TENSION,
        "standalone_clarity": scoring_weights.get("standalone_clarity", WEIGHT_STANDALONE_CLARITY) if scoring_weights else WEIGHT_STANDALONE_CLARITY,
        "conversion_intent": scoring_weights.get("conversion_intent", WEIGHT_CONVERSION_INTENT) if scoring_weights else WEIGHT_CONVERSION_INTENT,
    }

    all_ep_nums = {e.episode_number for e in episodes}
    episodes_with_valid = {ep for c in valid for ep in c.episodes}
    empty_eps = sorted(list(all_ep_nums - episodes_with_valid))

    # Stage meta records
    ex_live_p = llm_provider.usage.get("prompt_tokens", 0)
    ex_live_c = llm_provider.usage.get("completion_tokens", 0)
    ex_cached_p = llm_provider.usage.get("cached_prompt_tokens", 0)
    ex_cached_c = llm_provider.usage.get("cached_completion_tokens", 0)
    ex_live_calls = llm_provider.usage.get("calls", 0)
    ex_cache_hits = llm_provider.usage.get("cache_hits", 0)
    ex_live_cost = calculate_cost_usd(llm_provider.name, llm_provider.model, ex_live_p, ex_live_c)
    ex_cached_cost = calculate_cost_usd(llm_provider.name, llm_provider.model, ex_cached_p, ex_cached_c)
    ex_status = "ran" if ex_live_calls > 0 else ("cached" if ex_cache_hits > 0 else "failed")
    meta_stages = {
        "extraction": {
            "status": ex_status,
            "reason": "live API calls executed" if ex_status == "ran" else ("all responses loaded from on-disk cache" if ex_status == "cached" else "no responses"),
            "live_calls": ex_live_calls,
            "cache_hits": ex_cache_hits,
            "tokens": {
                "prompt_tokens": ex_live_p + ex_cached_p,
                "completion_tokens": ex_live_c + ex_cached_c,
                "total_tokens": ex_live_p + ex_cached_p + ex_live_c + ex_cached_c,
            },
            "cost": format_stage_cost(ex_live_cost, ex_cached_cost, ex_live_calls, ex_cache_hits),
            "live_cost_usd": round(ex_live_cost, 4),
            "cached_cost_usd": round(ex_cached_cost, 4),
            "wall_time_s": round(time.time() - t_start, 2),
        }
    }
    for s_name, s_rep in stage_reports.items():
        if isinstance(s_rep, dict) and "status" in s_rep:
            meta_stages[s_name] = s_rep

    meta = {
        "generated_at": generated_at,
        "git_commit": _git_commit(),
        "show": show_context.get("show_title"),
        "input_dir": input_dir,
        "episodes": len(episodes),
        "beats": total_beats,
        "extractor": {"provider": llm_provider.name, "model": llm_provider.model},
        "auditor": {
            "provider": "panel" if audit_panel else audit_provider_obj.name,
            "model": stage_reports["audit_panel"].get("judges", ["panel"]) if audit_panel else audit_provider_obj.model,
            "method": "llm" if (audit_panel or audit_provider_obj.is_live) else "rules",
        },
        "gemini_model_discovered": discovered_gemini_model,
        "allow_self_audit": allow_self_audit,
        "empty_episodes": {
            "count": len(empty_eps),
            "episodes": empty_eps,
        },
        "composites_enabled": composites,
        "stages_enabled": stages_enabled,
        "scoring_weights": effective_weights,
        "stage_reports": stage_reports,
        "stages": meta_stages,
        "counts": {
            "single_candidates": len(single_candidates),
            "composites": len(composite_list),
            "valid": len(valid),
            "after_dedup": len(deduped),
            "ranked": len(final_ranked),
            "audit_passed": n_pass,
            "audit_failed": n_fail,
            "audit_errors": n_err,
            "not_audited": n_not_audited,
            "tier_1": tier_1_c,
            "tier_2": tier_2_c,
            "tier_3": tier_3_c,
            "ranked_audit_passed": sum(1 for c in final_ranked if c.quality_audit and c.quality_audit.passed),
        },
        "rejected_by_validation": dict(extractor.drop_reasons),
        "constraint_violations": dict(violations),
        "extraction_failures": {str(k): v for k, v in sorted(extractor.failures.items())},
        "usage": usage,
        "wall_seconds": round(time.time() - t_start, 1),
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in final_ranked], f, indent=2, ensure_ascii=False)
    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in sorted(deduped, key=lambda c: -c.scores.composite_score)], f, indent=2, ensure_ascii=False)
    with open(rejected_path, "w", encoding="utf-8") as f:
        json.dump({"near_misses_reported_by_model": extractor.near_misses,
                   "proposals_rejected_by_validation": extractor.dropped}, f, indent=2, ensure_ascii=False)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    render_markdown_report(final_ranked, output_md, show_context, meta)
    print(f"\n✓ {output_json}\n✓ {output_md}\n✓ {pool_path}  ({len(deduped)} candidates)\n✓ {rejected_path}\n✓ {meta_path}")

    print("\n" + "=" * 70 + "\nTOP PROMOS SUMMARY:\n" + "=" * 70)
    for cand in final_ranked[:5]:
        eps = ", ".join(f"Ep {e}" for e in cand.episodes)
        segs = ", ".join(f"{s.start} -> {s.end}" for s in cand.segments)
        verdict = "PASS" if (cand.quality_audit and cand.quality_audit.passed) else "FAIL"
        print(f"Rank {cand.rank} | {cand.hook.type} | score {cand.effective_score} (raw {cand.scores.composite_score}) | audit {verdict} | {eps} | {cand.total_duration:.1f}s [{segs}]")
        print(f"  Hook: \"{cand.hook.quote[:75]}\"")
        print(f"  Cliffhanger: \"{cand.cliffhanger.quote[:75]}\"\n")

    if extractor.failures or n_err:
        print(f"WARNING: {len(extractor.failures)} episode(s) failed extraction and {n_err} candidate(s) are unaudited. "
              f"Results are incomplete; see {meta_path}.")
        run_pipeline.exit_code = 1
    return final_ranked


run_pipeline.exit_code = 0


def render_markdown_report(promos: List[PromoCandidate], filepath: str, context: Dict[str, Any], meta: Dict[str, Any]):
    ex, au = meta["extractor"], meta["auditor"]
    live = au["method"] == "llm"
    md = [
        "# Kuku Promo Finder - Ranked Promos",
        f"**Show:** {context.get('show_title')}  ",
        f"**Generated:** {meta['generated_at']} (commit {meta.get('git_commit') or 'n/a'})  ",
        f"**Extractor:** {ex['provider']} / {ex['model']}  ",
        f"**Auditor:** {au['provider']} / {au['model']} ({'LLM reads the clip screenplay' if live else 'rule lint only'})  ",
        f"**Stages:** {', '.join(meta.get('stages_enabled', []))}  ",
        f"**Promos listed:** {len(promos)} of {meta['counts']['after_dedup']} candidates "
        f"({meta['counts']['audit_passed']} passed audit, {meta['counts']['audit_failed']} failed, {meta['counts']['audit_errors']} unaudited)\n",
    ]
    if not live:
        md += ["> **SMOKE-TEST OUTPUT.** Produced by the offline keyword engine. The audit below is a rule lint, "
               "not a quality judgement. Run with an API key for LLM-judged results.\n"]
    if meta["extraction_failures"]:
        md += [f"> **INCOMPLETE:** extraction failed for episodes {', '.join(meta['extraction_failures'])}.\n"]
    md += [
        "---",
        "\n## Hard rules enforced in code (see `src/validation.py`)",
        "- Total duration 20-60s",
        "- Hook beat starts within 3s of the opening cut; stakes legible in 3s",
        "- Every cut is on a real beat edge; hook and cliffhanger quotes exist verbatim in the screenplay",
        "- Audit-passing promos rank above audit-failing ones; repeated hook types/episodes are penalised\n",
        "---",
        "\n## Ranked Promos\n",
    ]
    for p in promos:
        eps_str = ", ".join(f"Episode {e}" for e in p.episodes)
        segs_str = ", ".join(f"[{s.start} → {s.end}] ({s.duration:.1f}s)" for s in p.segments)
        a = p.quality_audit
        verdict = ("PASS" if a.passed else "FAIL") if (a and a.method != "error") else "UNAUDITED"
        flaw = f" - flaw: {a.flaw_type}" if (a and a.flaw_type) else ""
        risks = "; ".join(a.risks) if (a and a.risks) else "none listed"
        penalties = []
        if p.scores.diversity_penalty < 1.0:
            penalties.append(f"diversity x{p.scores.diversity_penalty}")
        if p.scores.audit_multiplier < 1.0:
            penalties.append(f"audit x{p.scores.audit_multiplier}")
        pen = f" ({', '.join(penalties)})" if penalties else ""
        conv_str = f" | conversion intent: {p.conversion_intent}/10" if p.conversion_intent is not None else ""
        payoff_str = f"- **Payoff Location:** `{p.payoff_location}`\n" if p.payoff_location and p.payoff_location != "unknown" else ""
        tier_str = f"- **Audit Tier:** Tier {p.audit_tier}\n" if getattr(p, "audit_tier", None) else ""
        trim_str = f"- **Trimmed to Cliffhanger:** Yes (-{p.seconds_removed}s)\n" if getattr(p, "trimmed_from_end", False) else ""
        verdicts_md = ""
        if getattr(p, "judge_verdicts", None):
            v_lines = []
            for jv in p.judge_verdicts:
                v_res = "PASS" if jv.get("pass") else f"FAIL ({jv.get('flaw_type') or 'unspecified'})"
                v_reason = jv.get("one_line_reason", "")
                v_lines.append(f"> - **{jv.get('judge', 'Judge')} ({jv.get('model', '')}):** {v_res} - {v_reason}")
            verdicts_md = "\n".join(v_lines) + "\n"

        md += [
            f"### Rank {p.rank}: {p.hook.name} ({p.promo_type.replace('_', ' ')})",
            f"- **Episode(s):** {eps_str}",
            f"- **Segments:** {segs_str} | **Total:** {p.total_duration:.1f}s",
            f"- **Score:** {p.effective_score} / 10 (raw {p.scores.composite_score}){pen}{conv_str}",
            f"- **Components:** hook {p.scores.hook_strength}, cliffhanger {p.scores.cliffhanger_strength}, payoff withheld {p.scores.payoff_withheld}, injustice {p.scores.injustice_tension}, clarity {p.scores.standalone_clarity}",
            f"{payoff_str}{tier_str}{trim_str}"
            f"- **Hook ({p.hook.type}):** `{p.hook.timestamp}` - *\"{p.hook.quote}\"*",
            f"- **Cliffhanger ({p.cliffhanger.type}):** `{p.cliffhanger.timestamp}` - *\"{p.cliffhanger.quote}\"*",
            f"  - *Withheld:* {p.cliffhanger.withheld_payoff}",
            f"- **Why it works:** {p.why_it_works}",
            f"\n> **Audit ({a.method if a else 'none'}): {verdict}{flaw}.** {a.critique if a else ''}",
            f"{verdicts_md}"
            f">\n> **Risks:** {risks}\n",
            "---\n",
        ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def resolve_args(args) -> Dict[str, str]:
    """Resolves show config and output paths; refuses the one dangerous default combination."""
    custom_input = os.path.normpath(args.input_dir) != os.path.normpath(DEFAULT_INPUT_DIR)
    if args.context:
        context = args.context
    elif args.show:
        context = os.path.join("config", "shows", f"{args.show}.yaml")
    elif custom_input:
        raise PipelineError(
            "A custom --input-dir needs its own show profile: pass --show <name> "
            "(config/shows/<name>.yaml, see config/shows/_template.yaml) or --context <file>. "
            "Refusing to run with another show's premise and characters.")
    else:
        context = os.path.join("config", "shows", f"{DEFAULT_SHOW}.yaml")
    if not os.path.exists(context):
        if getattr(args, "auto_profile", False):
            # When --auto-profile is active, permit starting with generated draft profile
            slug = args.show or (os.path.splitext(os.path.basename(args.context))[0] if args.context else "generated")
            context = os.path.join("config", "shows", f"{slug}.generated.yaml")
        else:
            raise PipelineError(f"Show profile not found: {context}")

    slug = os.path.splitext(os.path.basename(context))[0]
    out_dir = args.output_dir or ("outputs" if slug == DEFAULT_SHOW else os.path.join("outputs", slug))
    return {
        "context": context,
        "output_json": args.output_json or os.path.join(out_dir, "promos.json"),
        "output_md": args.output_md or os.path.join(out_dir, "PROMOS.md"),
    }


def main():
    parser = argparse.ArgumentParser(description="Find the best promo clips in microdrama screenplays.")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="Directory with screenplay .txt files")
    parser.add_argument("--taxonomy", default="config/taxonomy.yaml", help="Path to taxonomy YAML")
    parser.add_argument("--show", default=None, help="Show profile name in config/shows/ (default: broken_soldier)")
    parser.add_argument("--context", default=None, help="Explicit path to a show profile YAML (overrides --show)")
    parser.add_argument("--output-dir", default=None, help="Output folder (default: outputs/, or outputs/<show>/ for other shows)")
    parser.add_argument("--output-json", default=None, help="Path to write JSON output")
    parser.add_argument("--output-md", default=None, help="Path to write Markdown output")
    parser.add_argument("--provider", default="openai", help="gemini | openai | anthropic | heuristic (default: openai)")
    parser.add_argument("--model", default="gpt-6-luna", help="Model for extraction (default: gpt-6-luna)")
    parser.add_argument("--audit-provider", default=None, help="Provider for the auditor (default: gemini)")
    parser.add_argument("--audit-model", default=None, help="Model for the auditor (default: discovered gemini flash model)")
    parser.add_argument("--allow-self-audit", action="store_true", help="Allow pipeline to run when extractor model is the sole auditor")
    parser.add_argument("--audit-top-n", type=int, default=None, help="Audit only the N best candidates by weighted score; rest marked not audited")
    parser.add_argument("--top-k", type=int, default=15, help="Number of promos to select")
    parser.add_argument("--composites", action="store_true", help="Enable EXPERIMENTAL cross-episode composites")
    parser.add_argument("--no-cache", action="store_true", help="Disable the on-disk LLM response cache (.cache/kuku)")
    parser.add_argument("--workers", type=int, default=8, help="Parallel LLM calls")
    parser.add_argument("--allow-empty", action="store_true", help="Write outputs even if no promo survives")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose debug logging")

    # New LLM stage flags
    parser.add_argument("--cold-read", action="store_true", help="Stage A: Run isolated cold-read evaluation on candidates")
    parser.add_argument("--use-cold-read-in-rank", action="store_true", help="Use Stage A stakes_are_clear score in final ranking")
    parser.add_argument("--audit-panel", nargs="?", const="default", default=None, help="Stage B: Run dual-judge audit panel (default: openai:gpt-6-luna and Gemini flash)")
    parser.add_argument("--rerank", action="store_true", help="Stage C: Run listwise reranking twice and blend with weighted score")
    parser.add_argument("--auto-profile", action="store_true", help="Stage D: Generate draft show profile in config/shows/<show>.generated.yaml")
    parser.add_argument("--consolidate-taxonomy", action="store_true", help="Stage E: Cluster new tags into config/taxonomy.suggested.yaml")
    parser.add_argument("--recheck-empty", action="store_true", help="Stage F: Recheck empty episodes with relaxed prompt")
    parser.add_argument("--export-csv", nargs="?", const="default", default=None, help="Stage 5: Export ranked promos to CSV (one row per segment). Optional custom path.")
    parser.add_argument("--scoring-weights", default=None, help="Weights override as JSON (e.g. '{\"hook\":0.35}') or key=value pairs (e.g. 'hook=0.35,cliffhanger=0.25')")

    args = parser.parse_args()

    scoring_weights = None
    if args.scoring_weights:
        raw_sw = args.scoring_weights.strip()
        if raw_sw.startswith("{"):
            try:
                scoring_weights = json.loads(raw_sw)
            except json.JSONDecodeError as e:
                print(f"\nERROR: Malformed --scoring-weights JSON: {e}", file=sys.stderr)
                sys.exit(2)
        else:
            try:
                scoring_weights = {}
                for part in raw_sw.split(","):
                    if not part.strip():
                        continue
                    k, v = part.split("=", 1)
                    scoring_weights[k.strip()] = float(v.strip())
            except Exception as e:
                print(f"\nERROR: Malformed --scoring-weights: {e}. Expected JSON or key=value pairs (e.g. 'hook=0.35,cliffhanger=0.25')", file=sys.stderr)
                sys.exit(2)

    try:
        paths = resolve_args(args)
        run_pipeline(
            input_dir=args.input_dir,
            taxonomy_path=args.taxonomy,
            context_path=paths["context"],
            output_json=paths["output_json"],
            output_md=paths["output_md"],
            provider=args.provider,
            model=args.model,
            audit_provider=args.audit_provider,
            audit_model=args.audit_model,
            allow_self_audit=args.allow_self_audit,
            audit_top_n=args.audit_top_n,
            top_k=args.top_k,
            verbose=args.verbose,
            composites=args.composites,
            use_cache=not args.no_cache,
            workers=args.workers,
            allow_empty=args.allow_empty,
            cold_read=args.cold_read,
            use_cold_read_in_rank=args.use_cold_read_in_rank,
            audit_panel=args.audit_panel,
            rerank=args.rerank,
            auto_profile=args.auto_profile,
            consolidate_taxonomy=args.consolidate_taxonomy,
            recheck_empty=args.recheck_empty,
            export_csv=args.export_csv,
            scoring_weights=scoring_weights,
        )
    except (PipelineError, ProviderConfigError, FileNotFoundError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(getattr(e, "code", 2))
    sys.exit(run_pipeline.exit_code)


if __name__ == "__main__":
    main()
