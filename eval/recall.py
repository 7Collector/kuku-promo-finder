"""
Measure the ranker against YOUR hand-picked promos.

1. Before looking at any model output, write eval/ground_truth.json:
     [{"episode": 15, "start": "00:47.40", "end": "01:07.50", "note": "shove then Alexander charges"}, ...]
   Commit it before running the pipeline so the measurement is blind.
2. python eval/recall.py [outputs/promos.json] [--k 10]

A pick counts as found when a ranked promo in the same episode overlaps it by >= 50%
of the shorter interval. Prints recall@k and precision@k.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.timestamps import calculate_temporal_overlap, try_parse_timestamp


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 10
    promos_path = args[0] if args and not args[0].isdigit() else "outputs/promos.json"
    gt_path = Path(__file__).with_name("ground_truth.json")
    if not gt_path.exists():
        sys.exit(f"{gt_path} not found. Hand-pick promos first (see this file's docstring).")
    truth = json.loads(gt_path.read_text())
    promos = json.loads(Path(promos_path).read_text())[:k]

    def hit(pick, promo):
        ps, pe = try_parse_timestamp(pick["start"]), try_parse_timestamp(pick["end"])
        for seg in promo["segments"]:
            if seg.get("episode", promo["episodes"][0]) != pick["episode"]:
                continue
            if calculate_temporal_overlap(ps, pe, seg["start_seconds"], seg["end_seconds"])[1] >= 0.5:
                return True
        return False

    found = [t for t in truth if any(hit(t, p) for p in promos)]
    relevant = [p for p in promos if any(hit(t, p) for t in truth)]
    print(f"picks: {len(truth)}  recall@{k}: {len(found)}/{len(truth)} = {len(found) / len(truth):.0%}")
    print(f"precision@{k}: {len(relevant)}/{len(promos)} = {len(relevant) / max(1, len(promos)):.0%}")
    for t in truth:
        print(("  FOUND  " if t in found else "  MISSED ") + f"Ep {t['episode']} {t['start']}-{t['end']} {t.get('note', '')}")


if __name__ == "__main__":
    main()
