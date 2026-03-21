"""
utils.py — Shared utilities for AGI Benchmark Suite
"""

import os
import json
import random
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found. Copy .env.example to .env and add your key."
        )
    return key


def load_jsonl(path: str) -> list[dict]:
    items = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def save_jsonl(items: list[dict], path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def save_json(data: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)


def item_hash(item: dict) -> str:
    """Deterministic hash of a task item for deduplication."""
    canonical = json.dumps(item, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


def extract_choice(text: str, valid_choices: list[str]) -> str | None:
    """
    Extract a single-letter answer choice from model output.
    Handles terse responses ("A") and verbose responses ("The answer is A because...").
    Returns None if no valid choice is found.
    """
    import re
    text = text.strip()
    upper = text.upper()

    # 1. First character is a valid letter followed by whitespace/punctuation end
    # (not the start of a word like "After" or "Before")
    import re
    if upper and upper[0] in valid_choices:
        # Only accept if followed by punctuation, whitespace, or end of string
        if len(upper) == 1 or upper[1] in ' \t\n.,;:)]-':
            return upper[0]

    # 2. High-confidence patterns first (explicit answer markers)
    high_conf = [
        r'(?:answer|choice|option|select|pick)\s*(?:is|:|=)\s*\(?([A-D])\)?',
        r'^\s*\(?([A-D])\)?[\s\.\)\:]',   # starts with (A) or A. or A:
        r'\b([A-D])\)\s',                  # "A) " mid-text
        r'\bthe\s+answer\s+is\s+([A-D])\b',
        r'\bcorrect\s+(?:answer|choice|option)\s+is\s+([A-D])\b',
        r'\bi\s+(?:would\s+)?(?:choose|select|pick|answer)\s+([A-D])\b',
        r'\bmy\s+answer\s+is\s+([A-D])\b',
        r'\bselect\s+([A-D])\b',
        r'\bchoose\s+([A-D])\b',
    ]
    for pattern in high_conf:
        match = re.search(pattern, upper, re.IGNORECASE)
        if match and match.group(1).upper() in valid_choices:
            return match.group(1).upper()

    # 3. Letter followed by closing punctuation or end of string
    match = re.search(r'\b([A-D])[\.!\?]?\s*$', upper)
    if match and match.group(1) in valid_choices:
        return match.group(1)

    # 4. Standalone letter anywhere (last resort — take the last match)
    matches = re.findall(r'\b([A-D])\b', upper)
    valid_matches = [m for m in matches if m in valid_choices]
    if valid_matches:
        return valid_matches[-1]

    return None


MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}
