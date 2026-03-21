"""
eval.py — Main evaluation harness for AGI Benchmark Suite

Usage:
    python src/eval.py --dataset data/learning/nsa_bench.jsonl \
                       --model claude-haiku-4-5-20251001 \
                       --output results/nsa_haiku.json

    python src/eval.py --dataset data/executive_functions/oap_bench.jsonl \
                       --model claude-sonnet-4-6 \
                       --output results/oap_sonnet.json
"""

import argparse
import time
from tqdm import tqdm
import anthropic

from utils import get_api_key, load_jsonl, save_json, extract_choice, MODELS


SYSTEM_PROMPT = (
    "You are a participant in a cognitive evaluation. "
    "Read each item carefully and respond with only your answer choice (A, B, C, or D). "
    "Do not explain your reasoning unless asked."
)


def format_prompt(item: dict) -> str:
    """Build the user-facing prompt from a task item."""
    parts = []

    if item.get("context"):
        parts.append(f"--- Context ---\n{item['context'].strip()}\n")

    parts.append(f"--- Question ---\n{item['question'].strip()}\n")

    choices = item.get("choices", [])
    if choices:
        for i, choice in enumerate(choices):
            label = chr(65 + i)  # A, B, C, D
            parts.append(f"{label}) {choice}")

    parts.append("\nRespond with only the letter of your answer (A, B, C, or D).")
    return "\n".join(parts)


def query_model(client: anthropic.Anthropic, model: str, prompt: str, retries: int = 3) -> str:
    """Query the model with retry logic on rate limit errors."""
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=16,  # Single-letter answer; small token budget reduces cost
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"  Rate limit hit, waiting {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"  API error on attempt {attempt + 1}: {e}")
            time.sleep(1)
    return "ERROR"


def run_evaluation(dataset_path: str, model: str, output_path: str, delay: float = 0.3):
    """
    Run a full benchmark evaluation.

    Args:
        dataset_path: Path to JSONL benchmark file
        model: Anthropic model string (e.g. 'claude-haiku-4-5-20251001')
        output_path: Path to write JSON results
        delay: Seconds between API calls (avoid rate limits)
    """
    client = anthropic.Anthropic(api_key=get_api_key())
    tasks = load_jsonl(dataset_path)

    print(f"\nRunning evaluation")
    print(f"  Dataset : {dataset_path}  ({len(tasks)} items)")
    print(f"  Model   : {model}")
    print(f"  Output  : {output_path}\n")

    results = []
    for item in tqdm(tasks, desc="Evaluating"):
        valid_choices = [chr(65 + i) for i in range(len(item.get("choices", [])))]
        prompt = format_prompt(item)
        raw_response = query_model(client, model, prompt)
        predicted = extract_choice(raw_response, valid_choices)
        correct = item["answer"].upper()
        hit = predicted == correct

        result = {
            "id": item["id"],
            "track": item.get("track"),
            "subtask": item.get("subtask"),
            "difficulty": item.get("difficulty"),
            "correct_answer": correct,
            "predicted": predicted,
            "raw_response": raw_response,
            "hit": hit,
            "prepotent_error": False,  # populated below if applicable
        }

        # Flag prepotent errors for Executive Functions items
        # predicted is a letter (A/B/C/D); resolve it to the actual choice value
        # then compare against the stored prepotent_response string
        if item.get("prepotent_response") and not hit and predicted is not None:
            predicted_value = item["choices"][ord(predicted) - 65]
            result["prepotent_error"] = (
                predicted_value.upper() == item["prepotent_response"].upper()
            )

        results.append(result)
        time.sleep(delay)

    summary = compute_summary(results, model, dataset_path)
    output = {"model": model, "dataset": dataset_path, "summary": summary, "results": results}
    save_json(output, output_path)

    print(f"\n=== Results ===")
    print(f"  Overall accuracy: {summary['overall_accuracy']:.1%}  ({summary['n_correct']}/{summary['n_total']})")
    print(f"  Results saved to: {output_path}")

    return output


def compute_summary(results: list[dict], model: str, dataset: str) -> dict:
    """Compute summary statistics broken down by subtask and difficulty."""
    n_total = len(results)
    n_correct = sum(r["hit"] for r in results)
    overall_accuracy = n_correct / n_total if n_total else 0

    # By subtask
    by_subtask = {}
    for r in results:
        st = r.get("subtask", "unknown")
        by_subtask.setdefault(st, {"n": 0, "correct": 0, "prepotent_errors": 0})
        by_subtask[st]["n"] += 1
        by_subtask[st]["correct"] += int(r["hit"])
        by_subtask[st]["prepotent_errors"] += int(r.get("prepotent_error", False))

    for st in by_subtask:
        d = by_subtask[st]
        d["accuracy"] = d["correct"] / d["n"] if d["n"] else 0

    # By difficulty
    by_difficulty = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        by_difficulty.setdefault(diff, {"n": 0, "correct": 0})
        by_difficulty[diff]["n"] += 1
        by_difficulty[diff]["correct"] += int(r["hit"])

    for diff in by_difficulty:
        d = by_difficulty[diff]
        d["accuracy"] = d["correct"] / d["n"] if d["n"] else 0

    return {
        "model": model,
        "dataset": dataset,
        "n_total": n_total,
        "n_correct": n_correct,
        "overall_accuracy": overall_accuracy,
        "by_subtask": by_subtask,
        "by_difficulty": by_difficulty,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AGI Benchmark evaluation")
    parser.add_argument("--dataset", required=True, help="Path to JSONL benchmark file")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001",
                        help="Anthropic model string (default: haiku)")
    parser.add_argument("--output", required=True, help="Path to write JSON results")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Seconds between API calls (default: 0.3)")
    args = parser.parse_args()

    # Resolve model alias if provided
    model = MODELS.get(args.model, args.model)
    run_evaluation(args.dataset, model, args.output, args.delay)
