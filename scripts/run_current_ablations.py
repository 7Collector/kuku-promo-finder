import json
import os
import sys
import time
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.models import PromoCandidate
from src.parser import parse_all_episodes
from src.providers.factory import get_llm_provider
from src.ranker import PromoRanker
from src.stages import run_cold_read, run_rerank
from src.taxonomy import Taxonomy

def main():
    print("=" * 70)
    print("RUNNING ABLATIONS ON CURRENT POOL (Tier-1 candidates)")
    print("=" * 70)

    # 1. Load context, episodes, taxonomy, and current pool
    taxonomy_path = "config/taxonomy.yaml"
    context_path = "config/shows/broken_soldier.yaml"
    pool_path = "outputs/promos.pool.json"

    with open(context_path, "r", encoding="utf-8") as f:
        show_context = yaml.safe_load(f)

    taxonomy = Taxonomy(taxonomy_path, show_context_path=context_path)
    episodes = parse_all_episodes("assets/I Married a Broken Soldier. He was a Duke")
    episodes_by_num = {e.episode_number: e for e in episodes}

    with open(pool_path, "r", encoding="utf-8") as f:
        pool = [PromoCandidate.model_validate(c) for c in json.load(f)]

    tier1 = [c for c in pool if getattr(c, "audit_tier", None) == 1]
    tier1_sorted = sorted(tier1, key=lambda c: -c.scores.composite_score)
    print(f"Loaded {len(pool)} total candidates in pool.")
    print(f"Found {len(tier1)} Tier-1 candidates. Top 25 selected for rerank.")

    llm = get_llm_provider("openai", "gpt-6-luna", cache=True)

    # 2. Run Listwise Rerank over top 25 Tier-1 candidates
    print("\n--- Running Listwise Rerank on Current Tier-1 Candidates (cap 25) ---")
    rerank_cands = [PromoCandidate.model_validate(c.to_dict()) for c in tier1_sorted[:25]]
    rerank_report = run_rerank(
        candidates=rerank_cands,
        show_context=show_context,
        llm_provider=llm,
        max_cands=25,
    )
    print(f"Rerank report:")
    print(f"  • Top-10 overlap between Run 1 & Run 2: {rerank_report.get('overlap_between_runs'):.1%}")
    print(f"  • Top-10 overlap with weighted rank: {rerank_report.get('overlap_with_original'):.1%}")
    print(f"  • Kendall tau (Run 1 vs Run 2): {rerank_report.get('tau_between_runs')}")
    print(f"  • Kendall tau (Run 1 vs weighted): {rerank_report.get('tau_r1_vs_weighted')}")
    print(f"  • Kendall tau (Run 2 vs weighted): {rerank_report.get('tau_r2_vs_weighted')}")

    # Rank and save rerank ablation
    ranker = PromoRanker(taxonomy)
    rerank_ranked = ranker.rerank_for_diversity(rerank_cands, top_k=15)

    rerank_dir = Path("outputs/ablations/rerank")
    rerank_dir.mkdir(parents=True, exist_ok=True)
    with open(rerank_dir / "promos.json", "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in rerank_ranked], f, indent=2)
    with open(rerank_dir / "promos.pool.json", "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in rerank_cands], f, indent=2)

    meta_rerank = {
        "ablation_name": "rerank",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "show": show_context.get("show_title"),
        "counts": {
            "total_candidates": len(rerank_cands),
            "ranked": len(rerank_ranked),
            "tier_1": len(rerank_cands),
        },
        "stages": {
            "extraction": {"status": "reused", "reason": "reused from current 60-candidate pool", "live_calls": 0, "cache_hits": 0, "live_cost_usd": 0.0, "cached_cost_usd": 0.0},
            "rerank": {
                "status": rerank_report.get("status", "ran"),
                "reason": rerank_report.get("reason", "executed listwise rerank over tier-1 candidates"),
                "live_calls": rerank_report.get("live_calls", 0),
                "cache_hits": rerank_report.get("cache_hits", 0),
                "live_cost_usd": rerank_report.get("live_cost_usd", 0.0),
                "cached_cost_usd": rerank_report.get("cached_cost_usd", 0.0),
                "wall_time_s": rerank_report.get("wall_time_s", 0.0),
            }
        },
        "rerank_report": {
            "candidates_reranked": len(rerank_cands),
            "overlap_between_runs": rerank_report.get("overlap_between_runs"),
            "overlap_with_original": rerank_report.get("overlap_with_original"),
            "tau_between_runs": rerank_report.get("tau_between_runs"),
            "tau_r1_vs_weighted": rerank_report.get("tau_r1_vs_weighted"),
            "tau_r2_vs_weighted": rerank_report.get("tau_r2_vs_weighted"),
            "run_1_top_10": rerank_report.get("run_1_top_10", []),
            "run_2_top_10": rerank_report.get("run_2_top_10", []),
        },
    }
    with open(rerank_dir / "promos.meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_rerank, f, indent=2)
    print("✓ Saved rerank ablation files.")

    # 3. Run Cold-Read over all 26 Tier-1 candidates
    print("\n--- Running Cold-Read on Current Tier-1 Candidates (26) ---")
    cold_cands = [PromoCandidate.model_validate(c.to_dict()) for c in tier1_sorted]
    cold_report = run_cold_read(
        candidates=cold_cands,
        episodes_by_num=episodes_by_num,
        llm_provider=llm,
        use_in_rank=False,
        workers=8,
    )
    print(f"Cold-read report:")
    print(f"  • Correlation with standalone_clarity: r = {cold_report.get('correlation')}")
    print(f"  • Disagreements (|diff| >= 2.0): {cold_report.get('disagreements_count')}/{len(cold_cands)}")

    cold_ranked = ranker.rerank_for_diversity(cold_cands, top_k=15)
    cold_dir = Path("outputs/ablations/cold_read")
    cold_dir.mkdir(parents=True, exist_ok=True)
    with open(cold_dir / "promos.json", "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in cold_ranked], f, indent=2)
    with open(cold_dir / "promos.pool.json", "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in cold_cands], f, indent=2)

    meta_cold = {
        "ablation_name": "cold_read",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "show": show_context.get("show_title"),
        "counts": {
            "total_candidates": len(cold_cands),
            "ranked": len(cold_ranked),
            "tier_1": len(cold_cands),
        },
        "stages": {
            "extraction": {"status": "reused", "reason": "reused from current 60-candidate pool", "live_calls": 0, "cache_hits": 0, "live_cost_usd": 0.0, "cached_cost_usd": 0.0},
            "cold_read": {
                "status": cold_report.get("status", "ran"),
                "reason": cold_report.get("reason", "blind evaluation of clip screenplay text"),
                "live_calls": cold_report.get("live_calls", 0),
                "cache_hits": cold_report.get("cache_hits", 0),
                "live_cost_usd": cold_report.get("live_cost_usd", 0.0),
                "cached_cost_usd": cold_report.get("cached_cost_usd", 0.0),
                "wall_time_s": cold_report.get("wall_time_s", 0.0),
            }
        },
        "cold_read_report": {
            "candidates_evaluated": len(cold_cands),
            "correlation": cold_report.get("correlation"),
            "disagreements_count": cold_report.get("disagreements_count"),
            "disagreements": cold_report.get("disagreements", []),
        },
    }
    with open(cold_dir / "promos.meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_cold, f, indent=2)
    print("✓ Saved cold-read ablation files.")

if __name__ == "__main__":
    main()
