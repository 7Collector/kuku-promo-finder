"""
Main execution pipeline for Kuku Promo Finder.
Parses screenplays, generates candidate promos, reranks for diversity, and runs quality auditing.
"""

import os
import json
import argparse
import yaml
from typing import List, Dict, Any

from src.parser import parse_all_episodes
from src.taxonomy import Taxonomy
from src.providers.factory import get_llm_provider
from src.extractor import PromoExtractor
from src.composite import CompositePromoBuilder
from src.ranker import PromoRanker
from src.auditor import PromoAuditor
from src.models import PromoCandidate
from src.utils.logging import setup_logger, logger


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_pipeline(
    input_dir: str,
    taxonomy_path: str,
    context_path: str,
    output_json: str,
    output_md: str,
    provider: str = None,
    model: str = None,
    top_k: int = 15,
    verbose: bool = False,
) -> List[PromoCandidate]:
    setup_logger(verbose=verbose)
    print("=" * 70)
    print("KUKU PROMO FINDER - MICRODRAMA VIRAL CLIP PIPELINE")
    print("=" * 70)

    # 1. Load Configurations
    print(f"\n[1/5] Loading taxonomy from {taxonomy_path} and context from {context_path}...")
    taxonomy = Taxonomy(taxonomy_path)
    show_context = load_yaml(context_path)
    print(f"  • Hook types registered: {len(taxonomy.hooks)}")
    print(f"  • Cliffhanger types registered: {len(taxonomy.cliffhangers)}")
    print(f"  • Show title: {show_context.get('show_title')}")

    # 2. Parse Screenplays
    print(f"\n[2/5] Parsing screenplays from: {input_dir}...")
    episodes = parse_all_episodes(input_dir)
    print(f"  • Successfully parsed {len(episodes)} episodes.")
    total_beats = sum(len(ep.all_beats) for ep in episodes)
    print(f"  • Total dramatic beats extracted: {total_beats}")

    # 3. Candidate Extraction
    print(f"\n[3/5] Extracting promo candidates (Single-Episode & Composites)...")
    llm_provider = get_llm_provider(provider_name=provider, model_name=model)
    print(f"  • Active Engine / Provider: {llm_provider.name} (Model: {llm_provider.model})")

    extractor = PromoExtractor(taxonomy=taxonomy, llm_provider=llm_provider)
    single_candidates: List[PromoCandidate] = []

    prev_summary = ""
    for ep in episodes:
        cands = extractor.extract_candidates_for_episode(
            episode=ep,
            show_context=show_context,
            prev_episode_summary=prev_summary,
            max_candidates=2,
        )
        single_candidates.extend(cands)
        prev_summary = f"Ep {ep.episode_number}: {ep.logline}"

    print(f"  • Generated {len(single_candidates)} single-episode candidate windows.")

    # Cross-episode composites (dynamic and show-agnostic)
    composite_builder = CompositePromoBuilder(taxonomy=taxonomy)
    composites = composite_builder.build_cross_episode_composites(
        episodes=episodes,
        single_candidates=single_candidates,
        max_composites=2,
    )
    print(f"  • Created {len(composites)} cross-episode composite promos.")

    all_candidates = single_candidates + composites

    # 4. Scoring, Constraint Enforcement & Diversity Reranking
    print(f"\n[4/5] Scoring, physical constraint checking, and MMR diversity reranking...")
    ranker = PromoRanker(taxonomy=taxonomy)

    valid_candidates = []
    for cand in all_candidates:
        ranker.score_candidate(cand)
        if ranker.validate_constraints(cand):
            valid_candidates.append(cand)

    print(f"  • {len(valid_candidates)} candidates passed physical constraints (20-60s, hook <= 3.5s).")

    deduped = ranker.deduplicate(valid_candidates, overlap_threshold=0.35)
    print(f"  • {len(deduped)} candidates remain after deduplication.")

    final_ranked = ranker.rerank_for_diversity(deduped, top_k=top_k)
    print(f"  • Selected top {len(final_ranked)} promos balanced across hook types.")

    # 5. Adversarial Quality Auditing
    print(f"\n[5/5] Running adversarial quality checks (Resolution leaks, context deficits, visual dependencies)...")
    auditor = PromoAuditor(llm_provider=llm_provider, show_context=show_context)
    for cand in final_ranked:
        cand.quality_audit = auditor.audit_candidate(cand)

    # 6. Save Outputs
    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(output_md) or ".", exist_ok=True)

    # JSON export
    raw_data = [cand.to_dict() for cand in final_ranked]
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2)
    print(f"\n✓ Saved raw JSON output to: {output_json}")

    # Markdown export
    render_markdown_report(final_ranked, output_md, show_context)
    print(f"✓ Saved formatted Markdown report to: {output_md}")

    print("\n" + "=" * 70)
    print("TOP PROMOS SUMMARY:")
    print("=" * 70)
    for cand in final_ranked[:5]:
        eps = ", ".join(f"Ep {e}" for e in cand.episodes)
        segs = ", ".join(f"{s.start} -> {s.end}" for s in cand.segments)
        print(f"Rank {cand.rank} | {cand.hook.type.upper()} | Eff Score: {cand.effective_score} (Raw: {cand.scores.composite_score}) | {eps} | {cand.total_duration:.1f}s [{segs}]")
        print(f"  Hook: \"{cand.hook.quote[:75]}\"")
        print(f"  Cliffhanger: \"{cand.cliffhanger.quote[:75]}\"")
        print(f"  Why it works: {cand.why_it_works[:80]}...\n")

    return final_ranked


def render_markdown_report(promos: List[PromoCandidate], filepath: str, context: Dict[str, Any]):
    md_lines = [
        f"# Kuku Promo Finder — Official Ranked Promos",
        f"**Show:** {context.get('show_title')}  ",
        f"**Premise:** {context.get('premise')}  ",
        f"**Target Audience / Platform:** {context.get('target_platform')}  ",
        f"**Generated Promos Count:** {len(promos)}\n",
        "---",
        "\n## Executive Summary",
        "This document contains the top ranked promo acquisition ads for Instagram, TikTok, and YouTube Shorts.",
        "Every promo adheres to the following hard rules:",
        "- **20 to 60 seconds total duration**",
        "- **Opens on a high-stakes psychological hook** within the first 3 seconds ('blood boils' injustice, slap, contempt, or betrayal)",
        "- **Ends on a cliffhanger with withheld payoff** (cuts right before resolution or comeuppance)",
        "- **MMR Diversity Reranked** to ensure marketing campaign variety across hook archetypes.\n",
        "---",
        "\n## Ranked Promos\n"
    ]

    for p in promos:
        eps_str = ", ".join(f"Episode {e}" for e in p.episodes)
        segs_str = ", ".join(f"[{s.start} → {s.end}] ({s.duration:.1f}s)" for s in p.segments)

        audit_note = ""
        if p.quality_audit:
            risks_str = "; ".join(p.quality_audit.risks) if p.quality_audit.risks else "None detected"
            audit_note = (
                f"\n> **Quality Audit:** {p.quality_audit.critique}\n"
                f">\n"
                f"> **Identified Risks / Failure Flags:** {risks_str}\n"
            )

        penalty_note = f" (MMR Penalty Factor: {p.scores.diversity_penalty})" if p.scores.diversity_penalty < 1.0 else ""

        md_lines.append(f"### Rank {p.rank}: {p.hook.name} ({p.promo_type.replace('_', ' ').title()})")
        md_lines.append(f"- **Episode(s):** {eps_str}")
        md_lines.append(f"- **Segments:** {segs_str} | **Total Duration:** {p.total_duration:.1f}s")
        md_lines.append(f"- **Effective Rank Score:** **{p.effective_score} / 10** (Raw Composite: {p.scores.composite_score}){penalty_note}")
        md_lines.append(f"- **Score Breakdown:** Hook: {p.scores.hook_strength}, Injustice: {p.scores.injustice_tension}, Cliffhanger: {p.scores.cliffhanger_strength}, Clarity: {p.scores.standalone_clarity}, Payoff Withheld: {p.scores.payoff_withheld}")
        md_lines.append(f"- **Hook ({p.hook.type}):** `{p.hook.timestamp}` — *\"{p.hook.quote}\"*")
        md_lines.append(f"  - *Driver:* {p.hook.psychological_trigger}")
        md_lines.append(f"- **Cliffhanger ({p.cliffhanger.type}):** `{p.cliffhanger.timestamp}` — *\"{p.cliffhanger.quote}\"*")
        md_lines.append(f"  - *Withheld Payoff:* {p.cliffhanger.withheld_payoff}")
        md_lines.append(f"- **Why It Works for Cold Viewers:** {p.why_it_works}")
        if audit_note:
            md_lines.append(audit_note)
        md_lines.append("\n---\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def main():
    parser = argparse.ArgumentParser(description="Find best promos in microdrama screenplays.")
    parser.add_argument("--input-dir", default="assets/I Married a Broken Soldier. He was a Duke", help="Directory with screenplay txt files")
    parser.add_argument("--taxonomy", default="config/taxonomy.yaml", help="Path to taxonomy YAML")
    parser.add_argument("--context", default="config/show_context.yaml", help="Path to show context YAML")
    parser.add_argument("--output-json", default="outputs/promos.json", help="Path to write JSON output")
    parser.add_argument("--output-md", default="outputs/PROMOS.md", help="Path to write Markdown output")
    parser.add_argument("--provider", default=None, help="LLM provider (gemini, openai, anthropic, heuristic)")
    parser.add_argument("--model", default=None, help="Explicit model name (e.g. gemini-3.8-flash, gpt-6-luna, claude-sonnet-5-5)")
    parser.add_argument("--top-k", type=int, default=15, help="Number of promos to select")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()
    run_pipeline(
        input_dir=args.input_dir,
        taxonomy_path=args.taxonomy,
        context_path=args.context,
        output_json=args.output_json,
        output_md=args.output_md,
        provider=args.provider,
        model=args.model,
        top_k=args.top_k,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
