"""
scoring.py — Scoring, analysis, and report generation for AGI Benchmark Suite

Produces the model comparison tables and cognitive profiles needed for the submission.
"""

import json
import math
from pathlib import Path
from utils import load_jsonl, save_json


def load_results(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def accuracy_with_ci(hits: list[bool], confidence: float = 0.95) -> tuple[float, float, float]:
    """
    Wilson score interval for binomial proportion.
    More reliable than normal approximation for small n.
    Returns (accuracy, lower, upper).
    """
    n = len(hits)
    if n == 0:
        return 0.0, 0.0, 0.0
    p = sum(hits) / n
    z = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denominator
    return p, max(0, center - margin), min(1, center + margin)


def compare_models(result_paths: list[str]) -> dict:
    """
    Load multiple result files and produce a comparative summary table.

    Args:
        result_paths: List of paths to JSON result files from eval.py

    Returns:
        Dict with per-model, per-subtask breakdown
    """
    comparison = {}

    for path in result_paths:
        data = load_results(path)
        model = data["model"]
        results = data["results"]

        model_entry = {
            "model": model,
            "overall": {},
            "by_subtask": {},
            "by_difficulty": {},
            "prepotent_error_rate": 0.0,
        }

        # Overall accuracy with CI
        hits = [r["hit"] for r in results]
        acc, lo, hi = accuracy_with_ci(hits)
        model_entry["overall"] = {
            "accuracy": acc,
            "ci_lower": lo,
            "ci_upper": hi,
            "n": len(hits),
        }

        # By subtask
        subtask_hits: dict[str, list[bool]] = {}
        prepotent_hits: dict[str, list[bool]] = {}
        for r in results:
            st = r.get("subtask", "unknown")
            subtask_hits.setdefault(st, []).append(r["hit"])
            if r.get("prepotent_error") is not None:
                prepotent_hits.setdefault(st, []).append(r.get("prepotent_error", False))

        for st, hits_st in subtask_hits.items():
            acc, lo, hi = accuracy_with_ci(hits_st)
            model_entry["by_subtask"][st] = {
                "accuracy": acc,
                "ci_lower": lo,
                "ci_upper": hi,
                "n": len(hits_st),
            }
            if st in prepotent_hits:
                pe_rate = sum(prepotent_hits[st]) / len(prepotent_hits[st])
                model_entry["by_subtask"][st]["prepotent_error_rate"] = pe_rate

        # By difficulty
        diff_hits: dict[str, list[bool]] = {}
        for r in results:
            d = str(r.get("difficulty", "unknown"))
            diff_hits.setdefault(d, []).append(r["hit"])
        for d, hits_d in diff_hits.items():
            acc, lo, hi = accuracy_with_ci(hits_d)
            model_entry["by_difficulty"][d] = {
                "accuracy": acc,
                "ci_lower": lo,
                "ci_upper": hi,
                "n": len(hits_d),
            }

        # Overall prepotent error rate
        all_prepotent = [r.get("prepotent_error", False) for r in results
                         if r.get("prepotent_error") is not None]
        if all_prepotent:
            model_entry["prepotent_error_rate"] = sum(all_prepotent) / len(all_prepotent)

        comparison[model] = model_entry

    return comparison


def print_comparison_table(comparison: dict):
    """Print a readable comparison table to stdout."""
    models = list(comparison.keys())
    print("\n" + "="*70)
    print("MODEL COMPARISON — Overall Accuracy")
    print("="*70)
    print(f"{'Model':<45} {'Accuracy':>10} {'95% CI':>18} {'N':>6}")
    print("-"*70)
    for model, data in comparison.items():
        short = model.replace("claude-", "").replace("-20251001", "")
        acc = data["overall"]["accuracy"]
        lo = data["overall"]["ci_lower"]
        hi = data["overall"]["ci_upper"]
        n = data["overall"]["n"]
        print(f"{short:<45} {acc:>10.1%} [{lo:.1%}, {hi:.1%}] {n:>6}")

    print("\n" + "="*70)
    print("BY SUBTASK")
    print("="*70)
    all_subtasks = sorted(set(
        st for data in comparison.values()
        for st in data["by_subtask"]
    ))
    header = f"{'Subtask':<28}" + "".join(
        f"{m.replace('claude-','').replace('-20251001','')[:12]:>14}"
        for m in models
    )
    print(header)
    print("-"*70)
    for st in all_subtasks:
        row = f"{st:<28}"
        for model in models:
            acc = comparison[model]["by_subtask"].get(st, {}).get("accuracy", None)
            row += f"{'N/A':>14}" if acc is None else f"{acc:>14.1%}"
        print(row)

    print("\n" + "="*70)
    print("BY DIFFICULTY TIER")
    print("="*70)
    all_diffs = sorted(set(
        d for data in comparison.values()
        for d in data["by_difficulty"]
    ))
    header = f"{'Difficulty':<28}" + "".join(
        f"{m.replace('claude-','').replace('-20251001','')[:12]:>14}"
        for m in models
    )
    print(header)
    print("-"*70)
    for d in all_diffs:
        row = f"{'Tier ' + str(d):<28}"
        for model in models:
            acc = comparison[model]["by_difficulty"].get(d, {}).get("accuracy", None)
            row += f"{'N/A':>14}" if acc is None else f"{acc:>14.1%}"
        print(row)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scoring.py results/file1.json results/file2.json ...")
        sys.exit(1)

    comparison = compare_models(sys.argv[1:])
    print_comparison_table(comparison)

    output_path = "results/comparison.json"
    save_json(comparison, output_path)
    print(f"\nFull comparison saved to: {output_path}")
