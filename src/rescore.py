"""
rescore.py — Re-apply prepotent error detection to existing results files.

Use this when eval.py logic is fixed but you don't want to re-run API calls.

Usage:
    python src/rescore.py results/oap_haiku.json
    python src/rescore.py results/oap_sonnet.json
"""

import sys
import json
from pathlib import Path


def rescore(path: str):
    with open(path) as f:
        data = json.load(f)

    # Load original dataset to get choices and prepotent_response per item
    dataset_path = data["dataset"]
    items_by_id = {}
    with open(dataset_path) as f:
        for line in f:
            item = json.loads(line.strip())
            items_by_id[item["id"]] = item

    fixed = 0
    prepotent_count = 0

    for result in data["results"]:
        item = items_by_id.get(result["id"])
        if not item:
            continue

        prepotent_response = item.get("prepotent_response")
        predicted_letter = result.get("predicted")
        hit = result.get("hit", False)

        if prepotent_response and not hit and predicted_letter:
            try:
                idx = ord(predicted_letter.upper()) - 65
                predicted_value = item["choices"][idx]
                is_prepotent = predicted_value.upper() == prepotent_response.upper()
            except (IndexError, TypeError):
                is_prepotent = False

            if result.get("prepotent_error") != is_prepotent:
                result["prepotent_error"] = is_prepotent
                fixed += 1
            if is_prepotent:
                prepotent_count += 1

    # Recompute prepotent_error_rate in summary by_subtask
    subtask_prepotent: dict[str, list] = {}
    for result in data["results"]:
        st = result.get("subtask", "unknown")
        if result.get("prepotent_error") is not None and not result["hit"]:
            subtask_prepotent.setdefault(st, []).append(result["prepotent_error"])

    for st, flags in subtask_prepotent.items():
        if st in data["summary"]["by_subtask"]:
            rate = sum(flags) / len(flags) if flags else 0.0
            data["summary"]["by_subtask"][st]["prepotent_error_rate"] = rate

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Rescored: {path}")
    print(f"  Fixed {fixed} prepotent_error flags")
    print(f"  Total prepotent errors detected: {prepotent_count}")

    # Print updated breakdown
    print("\n=== Updated prepotent error rates by subtask ===")
    for st, d in data["summary"]["by_subtask"].items():
        pe = d.get("prepotent_error_rate")
        if pe is not None:
            misses = d["n"] - d["correct"]
            print(f"  {st:<30} accuracy={d['accuracy']:.1%}  prepotent_error_rate={pe:.1%}  (of {misses} misses)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/rescore.py results/oap_haiku.json")
        sys.exit(1)
    for path in sys.argv[1:]:
        rescore(path)
