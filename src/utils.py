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
    Returns None if no valid choice is found.
    """
    text = text.strip().upper()
    # Try first character
    if text and text[0] in valid_choices:
        return text[0]
    # Try to find a letter in parentheses or after common patterns
    import re
    patterns = [
        r'\b([A-D])\)',        # A) B) C) D)
        r'\b([A-D])\.',        # A. B. C. D.
        r'answer is ([A-D])',  # "answer is A"
        r'answer: ([A-D])',    # "answer: A"
        r'\b([A-D])\b',        # standalone letter
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1).upper() in valid_choices:
            return match.group(1).upper()
    return None


MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
}
