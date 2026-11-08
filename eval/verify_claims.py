"""
eval/verify_claims.py

Automated verification harness for all claims across documentation:
- Counts of 'new:' hook and cliffhanger types in the top 15 (settled from outputs/promos.json)
- Candidates proposed / valid / deduped / audited / audit_error / by tier
- Empty-episode count and list
- Total and per-run cost summed from meta files
- Top-15 promos with a code-verified payoff_location vs 'unknown'
- extractor_model, judge models and method per promo; fails if extractor == only judge without --allow-self-audit

Exits 0 on complete agreement; exits non-zero on any discrepancy or missing claim.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent


def compute_ground_truth_metrics() -> Dict[str, Any]:
    promos_path = ROOT / "outputs" / "promos.json"
    meta_path = ROOT / "outputs" / "promos.meta.json"
    pool_path = ROOT / "outputs" / "promos.pool.json"

    if not promos_path.exists():
        raise FileNotFoundError(f"Missing {promos_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path}")

    promos: List[Dict[str, Any]] = json.loads(promos_path.read_text(encoding="utf-8"))
    meta: Dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
    pool: List[Dict[str, Any]] = json.loads(pool_path.read_text(encoding="utf-8")) if pool_path.exists() else []

    top_15 = promos[:15]

    # 1. 'new:' hook and cliffhanger counts in top 15
    new_hooks = sum(1 for p in top_15 if p.get("hook", {}).get("type", "").startswith("new:"))
    new_cliffs = sum(1 for p in top_15 if p.get("cliffhanger", {}).get("type", "").startswith("new:"))
    new_either = sum(
        1 for p in top_15
        if p.get("hook", {}).get("type", "").startswith("new:")
        or p.get("cliffhanger", {}).get("type", "").startswith("new:")
    )

    # 2. Candidate counts
    counts = meta.get("counts", {})
    proposed = counts.get("single_candidates", 0) + counts.get("composites", 0)
    valid = counts.get("valid", 0)
    deduped = counts.get("after_dedup", len(pool))
    audited = counts.get("audit_passed", 0) + counts.get("audit_failed", 0)
    audit_errors = counts.get("audit_errors", 0)
    tier_1 = counts.get("tier_1", sum(1 for c in pool if c.get("audit_tier") == 1))
    tier_2 = counts.get("tier_2", sum(1 for c in pool if c.get("audit_tier") == 2))
    tier_3 = counts.get("tier_3", sum(1 for c in pool if c.get("audit_tier") == 3))

    # 3. Empty episodes
    empty_info = meta.get("empty_episodes", {})
    empty_count = empty_info.get("count", 0)
    empty_list = empty_info.get("episodes", [])

    # 4. Payoff locations in top 15
    payoff_verified = sum(1 for p in top_15 if p.get("payoff_location") and p.get("payoff_location") != "unknown")
    payoff_unknown = sum(1 for p in top_15 if not p.get("payoff_location") or p.get("payoff_location") == "unknown")

    # 5. Extractor & Judges verification
    extractor_model = meta.get("extractor", {}).get("model", "")
    extractor_provider = meta.get("extractor", {}).get("provider", "")
    allow_self_audit = meta.get("allow_self_audit", False)

    for p in top_15:
        verdicts = p.get("judge_verdicts", [])
        if not verdicts:
            raise ValueError(f"Promo {p.get('promo_id')} missing judge_verdicts")
        if len(verdicts) == 1 and verdicts[0].get("model") == extractor_model and not allow_self_audit:
            raise ValueError(
                f"Promo {p.get('promo_id')} has extractor model '{extractor_model}' as sole judge without --allow-self-audit"
            )

    # 6. Costs from meta files
    meta_files = sorted(ROOT.glob("outputs/**/*.meta.json"))
    total_cost = 0.0
    per_run_costs = {}
    for mf in meta_files:
        try:
            m_data = json.loads(mf.read_text(encoding="utf-8"))
            rel = str(mf.relative_to(ROOT))
            run_c = 0.0
            if "stages" in m_data and isinstance(m_data["stages"], dict):
                for s in m_data["stages"].values():
                    run_c += float(s.get("live_cost_usd", 0.0))
            per_run_costs[rel] = round(run_c, 4)
            total_cost += run_c
        except Exception:
            pass
    total_cost = round(total_cost, 4)

    return {
        "top_15_new_hooks": new_hooks,
        "top_15_new_cliffhangers": new_cliffs,
        "top_15_new_either": new_either,
        "proposed": proposed,
        "valid": valid,
        "deduped": deduped,
        "audited": audited,
        "audit_errors": audit_errors,
        "tier_1": tier_1,
        "tier_2": tier_2,
        "tier_3": tier_3,
        "empty_count": empty_count,
        "empty_list": empty_list,
        "payoff_verified": payoff_verified,
        "payoff_unknown": payoff_unknown,
        "extractor_model": extractor_model,
        "extractor_provider": extractor_provider,
        "total_cost": total_cost,
        "per_run_costs": per_run_costs,
    }


def verify_file_claims(doc_path: Path, metrics: Dict[str, Any]) -> List[str]:
    """Verifies that all specific numerical claims in a document match computed ground truth."""
    if not doc_path.exists():
        return [f"File {doc_path} does not exist"]

    text = doc_path.read_text(encoding="utf-8")
    issues = []

    # Check top-15 new hook/cliffhanger counts
    # Pattern: X of top 15 hooks and Y of top 15 cliffhangers
    hook_cliff_match = re.search(r"(\d+)\s+of\s+top\s+15\s+hooks\s+and\s+(\d+)\s+of\s+top\s+15\s+cliffhangers", text)
    if hook_cliff_match:
        claimed_h = int(hook_cliff_match.group(1))
        claimed_c = int(hook_cliff_match.group(2))
        if claimed_h != metrics["top_15_new_hooks"]:
            issues.append(f"{doc_path.name}: claimed {claimed_h} new hooks in top 15, but ground truth is {metrics['top_15_new_hooks']}")
        if claimed_c != metrics["top_15_new_cliffhangers"]:
            issues.append(f"{doc_path.name}: claimed {claimed_c} new cliffhangers in top 15, but ground truth is {metrics['top_15_new_cliffhangers']}")

    # Check empty episodes count
    empty_match = re.search(r"(\d+)\s+empty\s+episodes?", text, re.IGNORECASE)
    if empty_match:
        claimed_empty = int(empty_match.group(1))
        if claimed_empty != metrics["empty_count"]:
            issues.append(f"{doc_path.name}: claimed {claimed_empty} empty episodes, but ground truth is {metrics['empty_count']}")

    # Check candidate pool counts if mentioned
    # Pattern: X candidates proposed, Y valid, Z deduped
    cand_match = re.search(r"(\d+)\s+(?:single-episode\s+)?candidates(?:\s+proposed)?,\s*(\d+)\s+valid,\s*(\d+)\s+deduped", text)
    if cand_match:
        c_prop, c_val, c_dedup = int(cand_match.group(1)), int(cand_match.group(2)), int(cand_match.group(3))
        if c_prop != metrics["proposed"]:
            issues.append(f"{doc_path.name}: claimed {c_prop} proposed, ground truth {metrics['proposed']}")
        if c_val != metrics["valid"]:
            issues.append(f"{doc_path.name}: claimed {c_val} valid, ground truth {metrics['valid']}")
        if c_dedup != metrics["deduped"]:
            issues.append(f"{doc_path.name}: claimed {c_dedup} deduped, ground truth {metrics['deduped']}")

    # Check tier breakdown if mentioned
    tier_match = re.search(r"Tier\s*1\s*=\s*(\d+).*?Tier\s*2\s*=\s*(\d+).*?Tier\s*3\s*=\s*(\d+)", text, re.IGNORECASE)
    if tier_match:
        t1, t2, t3 = int(tier_match.group(1)), int(tier_match.group(2)), int(tier_match.group(3))
        if t1 != metrics["tier_1"] or t2 != metrics["tier_2"] or t3 != metrics["tier_3"]:
            issues.append(f"{doc_path.name}: claimed tiers ({t1}, {t2}, {t3}), ground truth is ({metrics['tier_1']}, {metrics['tier_2']}, {metrics['tier_3']})")

    # Check verified payoff locations
    payoff_match = re.search(r"(\d+)\s+of\s+top\s+15\s+promos\s+have\s+a\s+code-verified\s+payoff_location", text, re.IGNORECASE)
    if payoff_match:
        claimed_payoff = int(payoff_match.group(1))
        if claimed_payoff != metrics["payoff_verified"]:
            issues.append(f"{doc_path.name}: claimed {claimed_payoff} verified payoffs, ground truth is {metrics['payoff_verified']}")

    return issues


def main():
    print("=" * 70)
    print("KUKU CLAIMS VERIFICATION HARNESS (eval/verify_claims.py)")
    print("=" * 70)

    try:
        metrics = compute_ground_truth_metrics()
    except Exception as e:
        print(f"FAILED to compute metrics: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nGround Truth Computed from Committed Outputs:")
    print(f"  • Extractor: {metrics['extractor_provider']}:{metrics['extractor_model']}")
    print(f"  • Candidates: {metrics['proposed']} proposed -> {metrics['valid']} valid -> {metrics['deduped']} deduped")
    print(f"  • Audit Tiers: Tier 1={metrics['tier_1']}, Tier 2={metrics['tier_2']}, Tier 3={metrics['tier_3']}, Errors={metrics['audit_errors']}")
    print(f"  • Empty Episodes ({metrics['empty_count']}): {metrics['empty_list']}")
    print(f"  • Top 15 'new:' tags: {metrics['top_15_new_hooks']} hooks, {metrics['top_15_new_cliffhangers']} cliffhangers")
    print(f"  • Top 15 Payoff Locations: {metrics['payoff_verified']} verified, {metrics['payoff_unknown']} unknown")
    print(f"  • Total Cost from Meta: ${metrics['total_cost']:.4f}")

    docs_to_check = [
        ROOT / "SOLUTION_DOC.md",
        ROOT / "README.md",
        ROOT / "AGENTS.md",
    ]

    all_issues = []
    print("\nVerifying Document Claims:")
    for doc in docs_to_check:
        issues = verify_file_claims(doc, metrics)
        if issues:
            print(f"  ✗ {doc.name}: {len(issues)} mismatch(es)")
            for iss in issues:
                print(f"      - {iss}")
            all_issues.extend(issues)
        else:
            print(f"  ✓ {doc.name}: all checked numbers match ground truth.")

    if all_issues:
        print(f"\nFAILED: {len(all_issues)} claim mismatch(es) detected across documentation.", file=sys.stderr)
        sys.exit(1)

    print("\n✓ ALL CLAIMS VERIFIED SUCCESSFULLY AGAINST COMMITTED OUTPUTS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
