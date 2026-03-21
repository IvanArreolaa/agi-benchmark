"""
rerun_none.py — Re-run only items where predicted=None in an existing results file.

Use this after fixing extract_choice to avoid re-running the full benchmark.

Usage:
    python src/rerun_none.py results/oap_sonnet.json
    python src/rerun_none.py results/nsa_sonnet.json
"""

import sys
import json
import time
import anthropic
from tqdm import tqdm

# Add src to path
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils import get_api_key, load_jsonl, save_json, extract_choice
from eval import format_prompt, query_model, SYSTEM_PROMPT, compute_summary


def rerun_none(results_path: str, delay: float = 0.5):
    with open(results_path) as f:
        data = json.load(f)

    dataset_path = data["dataset"]
    model = data["model"]

    # Load dataset items by id
    items_by_id = {}
    for item in load_jsonl(dataset_path):
        items_by_id[item["id"]] = item

    # Find results where predicted is None
    none_results = [r for r in data["results"] if r["predicted"] is None]
    print(f"Found {len(none_results)} items with predicted=None in {results_path}")

    if not none_results:
        print("Nothing to re-run.")
        return

    client = anthropic.Anthropic(api_key=get_api_key())

    fixed = 0
    for result in tqdm(none_results, desc="Re-running"):
        item = items_by_id.get(result["id"])
        if not item:
            continue

        valid_choices = [chr(65 + i) for i in range(len(item.get("choices", [])))]
        prompt = format_prompt(item)
        raw_response = query_model(client, model, prompt)
        predicted = extract_choice(raw_response, valid_choices)
        correct = item["answer"].upper()
        hit = predicted == correct if predicted else False

        result["predicted"] = predicted
        result["raw_response"] = raw_response
        result["hit"] = hit

        # Re-apply prepotent error detection
        result["prepotent_error"] = False
        if item.get("prepotent_response") and not hit and predicted is not None:
            idx = ord(predicted) - 65
            try:
                predicted_value = item["choices"][idx]
                result["prepotent_error"] = (
                    predicted_value.upper() == item["prepotent_response"].upper()
                )
            except IndexError:
                pass

        if predicted is not None:
            fixed += 1

        time.sleep(delay)

    # Recompute summary
    data["summary"] = compute_summary(data["results"], model, dataset_path)
    save_json(data, results_path)

    still_none = sum(1 for r in data["results"] if r["predicted"] is None)
    print(f"\nFixed {fixed}/{len(none_results)} previously-None items")
    print(f"Still None after re-run: {still_none}")
    print(f"\n=== Updated summary ===")
    print(f"  Overall accuracy: {data['summary']['overall_accuracy']:.1%}  "
          f"({data['summary']['n_correct']}/{data['summary']['n_total']})")
    print(f"\n=== By subtask ===")
    for st, d in data["summary"]["by_subtask"].items():
        print(f"  {st:<30} {d['accuracy']:.1%}  ({d['correct']}/{d['n']})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/rerun_none.py results/oap_sonnet.json")
        sys.exit(1)
    for path in sys.argv[1:]:
        rerun_none(path)
