"""
Main execution pipeline for Kuku Promo Finder.
Parses screenplays, generates candidate promos, reranks for diversity, and runs quality auditing.
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
from src.providers.factory import get_llm_provider, ProviderConfigError
from src.validation import check_candidate
from src.extractor import PromoExtractor
from src.composite import CompositePromoBuilder
from src.ranker import PromoRanker
from src.auditor import PromoAuditor
from src.models import PromoCandidate
from src.utils.logging import setup_logger, logger


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
    top_k: int = 15,
    verbose: bool = False,
    composites: bool = False,
    use_cache: bool = True,
    workers: int = 8,
    allow_empty: bool = False,
) -> List[PromoCandidate]:
    setup_logger(verbose=verbose)
    t_start = time.time()
    print("=" * 70)
    print("KUKU PROMO FINDER - MICRODRAMA VIRAL CLIP PIPELINE")
    print("=" * 70)

    # 1. Configuration
    print(f"\n[1/6] Loading taxonomy from {taxonomy_path} and show context from {context_path}...")
    taxonomy = Taxonomy(taxonomy_path, show_context_path=context_path)
    show_context = load_yaml(context_path)
    print(f"  • Hook types: {len(taxonomy.hooks)}, cliffhanger types: {len(taxonomy.cliffhangers)}")
    print(f"  • Show: {show_context.get('show_title')}")

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

    # 3. Extraction
    print(f"\n[3/6] Extracting promo candidates...")
    llm_provider = get_llm_provider(provider_name=provider, model_name=model, cache=use_cache)
    print(f"  • Extractor: {llm_provider.name} (model: {llm_provider.model})")
    if not llm_provider.is_live:
        print("  • NOTE: offline keyword engine. Output is a smoke test, not LLM-judged.")
    extractor = PromoExtractor(taxonomy=taxonomy, llm_provider=llm_provider)

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
        ranker.score_candidate(cand)
        errs = check_candidate(cand, episodes_by_num)
        if errs or not ranker.validate_constraints(cand):
            for e in errs or ["constraint check failed"]:
                violations[e.split(" in Ep")[0]] += 1
            continue
        valid.append(cand)
    print(f"  • {len(valid)}/{len(all_candidates)} candidates satisfy every hard constraint.")
    deduped = ranker.deduplicate(valid, overlap_threshold=0.35)
    print(f"  • {len(deduped)} remain after de-duplication.")

    # 5. Audit
    audit_provider_obj = llm_provider
    if audit_provider or audit_model:
        audit_provider_obj = get_llm_provider(provider_name=audit_provider or llm_provider.name,
                                              model_name=audit_model, cache=use_cache)
    print(f"\n[5/6] Auditing {len(deduped)} candidates ({audit_provider_obj.name}, model {audit_provider_obj.model})...")
    if audit_provider_obj.is_live and audit_provider_obj.name == llm_provider.name and audit_provider_obj.model == llm_provider.model:
        print("  • NOTE: the extractor model grades its own picks. Use --audit-model for an independent judge.")
    auditor = PromoAuditor(llm_provider=audit_provider_obj, show_context=show_context, episodes=episodes, taxonomy=taxonomy)

    def audit_cand(cand):
        cand.quality_audit = auditor.audit_candidate(cand)
        return cand

    _run_parallel(audit_cand, deduped, workers if audit_provider_obj.is_live else 1)
    n_pass = sum(1 for c in deduped if c.quality_audit.passed)
    n_err = sum(1 for c in deduped if c.quality_audit.method == "error")
    n_fail = len(deduped) - n_pass - n_err
    label = "passed" if audit_provider_obj.is_live else "passed rule lint (not a quality judgement)"
    print(f"  • {n_pass} {label}, {n_fail} failed, {n_err} unaudited (audit error).")

    # 6. Rank
    print(f"\n[6/6] Ranking (audit-passing first, diversity-penalised)...")
    final_ranked = ranker.rerank_for_diversity(deduped, top_k=top_k)
    print(f"  • Selected top {len(final_ranked)}.")
    if not final_ranked and not allow_empty:
        raise PipelineError("No promos survived the hard constraints; existing outputs were left untouched "
                            "(use --allow-empty to write an empty result).", code=3)

    # Outputs
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pool_path, meta_path, rejected_path = (_sibling(output_json, s) for s in (".pool.json", ".meta.json", ".rejected.json"))
    for path in (output_json, output_md, pool_path, meta_path, rejected_path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if audit_provider_obj is llm_provider:
        usage = {"extractor_and_auditor_combined": llm_provider.usage}  # one provider object serves both
    else:
        usage = {"extractor": llm_provider.usage, "auditor": audit_provider_obj.usage}
    meta = {
        "generated_at": generated_at,
        "git_commit": _git_commit(),
        "show": show_context.get("show_title"),
        "input_dir": input_dir,
        "episodes": len(episodes),
        "beats": total_beats,
        "extractor": {"provider": llm_provider.name, "model": llm_provider.model},
        "auditor": {"provider": audit_provider_obj.name, "model": audit_provider_obj.model,
                    "method": "llm" if audit_provider_obj.is_live else "rules"},
        "composites_enabled": composites,
        "counts": {
            "single_candidates": len(single_candidates), "composites": len(composite_list),
            "valid": len(valid), "after_dedup": len(deduped), "ranked": len(final_ranked),
            "audit_passed": n_pass, "audit_failed": n_fail, "audit_errors": n_err,
            "ranked_audit_passed": sum(1 for c in final_ranked if c.quality_audit.passed),
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
        verdict = "PASS" if cand.quality_audit.passed else "FAIL"
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
        "- Hook beat starts within 3s of the opening cut",
        "- Every cut is on a real beat edge; hook and cliffhanger quotes exist verbatim in the screenplay",
        "- Audit-passing promos rank above audit-failing ones; repeated hook types/episodes are penalised\n",
        "---",
        "\n## Ranked Promos\n",
    ]
    for p in promos:
        eps_str = ", ".join(f"Episode {e}" for e in p.episodes)
        segs_str = ", ".join(f"[{s.start} → {s.end}] ({s.duration:.1f}s)" for s in p.segments)
        a = p.quality_audit
        verdict = ("PASS" if a.passed else "FAIL") if a.method != "error" else "UNAUDITED"
        flaw = f" - flaw: {a.flaw_type}" if a.flaw_type else ""
        risks = "; ".join(a.risks) if a.risks else "none listed"
        penalties = []
        if p.scores.diversity_penalty < 1.0:
            penalties.append(f"diversity x{p.scores.diversity_penalty}")
        if p.scores.audit_multiplier < 1.0:
            penalties.append(f"audit x{p.scores.audit_multiplier}")
        pen = f" ({', '.join(penalties)})" if penalties else ""
        md += [
            f"### Rank {p.rank}: {p.hook.name} ({p.promo_type.replace('_', ' ')})",
            f"- **Episode(s):** {eps_str}",
            f"- **Segments:** {segs_str} | **Total:** {p.total_duration:.1f}s",
            f"- **Score:** {p.effective_score} / 10 (raw {p.scores.composite_score}){pen}",
            f"- **Components:** hook {p.scores.hook_strength}, injustice {p.scores.injustice_tension}, cliffhanger {p.scores.cliffhanger_strength}, clarity {p.scores.standalone_clarity}, payoff withheld {p.scores.payoff_withheld}",
            f"- **Hook ({p.hook.type}):** `{p.hook.timestamp}` - *\"{p.hook.quote}\"*",
            f"- **Cliffhanger ({p.cliffhanger.type}):** `{p.cliffhanger.timestamp}` - *\"{p.cliffhanger.quote}\"*",
            f"  - *Withheld:* {p.cliffhanger.withheld_payoff}",
            f"- **Why it works:** {p.why_it_works}",
            f"\n> **Audit ({a.method}): {verdict}{flaw}.** {a.critique}",
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
    parser.add_argument("--provider", default=None, help="gemini | openai | anthropic | heuristic (default: first with an API key, else heuristic)")
    parser.add_argument("--model", default=None, help="Model for extraction (e.g. gemini-3.8-flash, gpt-6-luna, claude-sonnet-5-5)")
    parser.add_argument("--audit-provider", default=None, help="Provider for the auditor (default: same as extractor)")
    parser.add_argument("--audit-model", default=None, help="Model for the auditor (use a different model for an independent judge)")
    parser.add_argument("--top-k", type=int, default=15, help="Number of promos to select")
    parser.add_argument("--composites", action="store_true", help="Enable EXPERIMENTAL cross-episode composites")
    parser.add_argument("--no-cache", action="store_true", help="Disable the on-disk LLM response cache (.cache/kuku)")
    parser.add_argument("--workers", type=int, default=8, help="Parallel LLM calls")
    parser.add_argument("--allow-empty", action="store_true", help="Write outputs even if no promo survives")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose debug logging")
    args = parser.parse_args()

    try:
        paths = resolve_args(args)
        run_pipeline(
            input_dir=args.input_dir, taxonomy_path=args.taxonomy, context_path=paths["context"],
            output_json=paths["output_json"], output_md=paths["output_md"],
            provider=args.provider, model=args.model,
            audit_provider=args.audit_provider, audit_model=args.audit_model,
            top_k=args.top_k, verbose=args.verbose, composites=args.composites,
            use_cache=not args.no_cache, workers=args.workers, allow_empty=args.allow_empty,
        )
    except (PipelineError, ProviderConfigError, FileNotFoundError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(getattr(e, "code", 2))
    sys.exit(run_pipeline.exit_code)


if __name__ == "__main__":
    main()
