"""
Measure the ranker against YOUR hand-picked promos.

1. Before looking at any model output, write eval/ground_truth.json:
     [{"episode": 15, "start": "00:47.40", "end": "01:07.50", "note": "shove then Alexander charges"}, ...]
   Ground-truth criterion: "Would I pay to see what happens next", set by the user.
2. python eval/recall.py [outputs/promos.json] [--k 15] [--all-ablations]

A pick counts as found when a ranked promo in the same episode overlaps it by >= 50%
of the shorter interval. Prints recall and precision.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.timestamps import calculate_temporal_overlap, try_parse_timestamp


def hit(pick: Dict[str, Any], promo: Dict[str, Any]) -> bool:
    ps, pe = try_parse_timestamp(pick["start"]), try_parse_timestamp(pick["end"])
    if ps is None or pe is None:
        return False
    for seg in promo.get("segments", []):
        ep_val = seg.get("episode")
        if ep_val is None and promo.get("episodes"):
            ep_val = promo["episodes"][0]
        if ep_val != pick.get("episode"):
            continue
        s_sec = seg.get("start_seconds") or try_parse_timestamp(seg.get("start"))
        e_sec = seg.get("end_seconds") or try_parse_timestamp(seg.get("end"))
        if s_sec is None or e_sec is None:
            continue
        _, ratio = calculate_temporal_overlap(ps, pe, s_sec, e_sec)
        if ratio >= 0.5:
            return True
    return False


def evaluate_promos(truth: List[Dict[str, Any]], promos: List[Dict[str, Any]], label: str = "", k: int = 15):
    evaluated_promos = promos[:k] if k > 0 else promos
    found = [t for t in truth if any(hit(t, p) for p in evaluated_promos)]
    relevant = [p for p in evaluated_promos if any(hit(t, p) for t in truth)]
    rec = len(found) / max(1, len(truth))
    prec = len(relevant) / max(1, len(evaluated_promos))
    k_str = f"@{k}" if k > 0 else " (full pool)"
    print(f"\n[{label}] Picks: {len(truth)} | Recall{k_str}: {len(found)}/{len(truth)} ({rec:.1%}) | Precision{k_str}: {len(relevant)}/{len(evaluated_promos)} ({prec:.1%})")
    return {"recall": rec, "precision": prec, "found": len(found), "total": len(truth)}


def main():
    gt_path = Path(__file__).with_name("ground_truth.json")
    if not gt_path.exists():
        print(f"Notice: {gt_path} not found.")
        print("Ground truth has not been provided by the user. Claiming no recall anywhere (recall is unmeasured).")
        print("To measure recall: write your picks to eval/ground_truth.json with criterion 'would I pay to see what happens next'.")
        sys.exit(0)

    truth = json.loads(gt_path.read_text())
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 15

    # If --all-ablations is requested, scan outputs/ablations
    if "--all-ablations" in sys.argv:
        print("=" * 60)
        print("EVALUATING ALL ABLATIONS AGAINST GROUND TRUTH")
        print("=" * 60)
        # Full pool
        pool_path = Path("outputs/promos.pool.json")
        if pool_path.exists():
            evaluate_promos(truth, json.loads(pool_path.read_text()), label="Full Pool", k=0)

        # Baseline & ablations
        ablations_dir = Path("outputs/ablations")
        if ablations_dir.exists():
            for p in sorted(ablations_dir.iterdir()):
                promos_file = p / "promos.json"
                if promos_file.exists():
                    promos = json.loads(promos_file.read_text())
                    evaluate_promos(truth, promos, label=f"Ablation: {p.name}", k=k)
        return

    promos_path = args[0] if args and not args[0].isdigit() else "outputs/promos.json"
    p = Path(promos_path)
    if not p.exists():
        sys.exit(f"Promos file not found: {p}")
    promos = json.loads(p.read_text())
    evaluate_promos(truth, promos, label=p.name, k=k)


if __name__ == "__main__":
    main()
