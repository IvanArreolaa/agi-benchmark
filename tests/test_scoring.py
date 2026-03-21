"""
tests/test_scoring.py — Unit tests for scoring and utility functions

Run with: pytest tests/
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import extract_choice, item_hash
from scoring import accuracy_with_ci


# --- extract_choice tests ---

def test_extract_choice_plain_letter():
    assert extract_choice("A", ["A", "B", "C", "D"]) == "A"

def test_extract_choice_lowercase():
    assert extract_choice("b", ["A", "B", "C", "D"]) == "B"

def test_extract_choice_with_paren():
    assert extract_choice("The answer is C)", ["A", "B", "C", "D"]) == "C"

def test_extract_choice_natural_language():
    assert extract_choice("I believe the answer is D.", ["A", "B", "C", "D"]) == "D"

def test_extract_choice_no_valid():
    assert extract_choice("I don't know", ["A", "B", "C", "D"]) is None

def test_extract_choice_invalid_letter():
    assert extract_choice("E", ["A", "B", "C", "D"]) is None

def test_extract_choice_verbose_because():
    assert extract_choice(
        "The answer is B because the passage clearly states the count is 5.",
        ["A", "B", "C", "D"]
    ) == "B"

def test_extract_choice_verbose_choose():
    assert extract_choice("I would choose C as the correct answer.", ["A", "B", "C", "D"]) == "C"

def test_extract_choice_end_of_string():
    assert extract_choice("After careful reading, I select D", ["A", "B", "C", "D"]) == "D"

def test_extract_choice_with_explanation_first():
    assert extract_choice(
        "Looking at the options carefully: A is wrong, B is wrong, C is correct.",
        ["A", "B", "C", "D"]
    ) == "C"


# --- accuracy_with_ci tests ---

def test_accuracy_perfect():
    acc, lo, hi = accuracy_with_ci([True] * 100)
    assert abs(acc - 1.0) < 1e-9
    assert hi <= 1.0
    assert lo > 0.9

def test_accuracy_zero():
    acc, lo, hi = accuracy_with_ci([False] * 50)
    assert acc == 0.0

def test_accuracy_half():
    acc, lo, hi = accuracy_with_ci([True, False] * 50)
    assert abs(acc - 0.5) < 0.01
    assert lo < 0.5 < hi

def test_accuracy_empty():
    acc, lo, hi = accuracy_with_ci([])
    assert acc == 0.0

def test_ci_bounds_in_range():
    for n in [10, 50, 200]:
        hits = [True] * (n // 2) + [False] * (n // 2)
        acc, lo, hi = accuracy_with_ci(hits)
        assert 0.0 <= lo <= acc <= hi <= 1.0


# --- item_hash tests ---

def test_item_hash_deterministic():
    item = {"id": "test_001", "question": "What is X?", "answer": "A"}
    assert item_hash(item) == item_hash(item)

def test_item_hash_different_items():
    item1 = {"id": "001", "question": "Q1"}
    item2 = {"id": "002", "question": "Q2"}
    assert item_hash(item1) != item_hash(item2)

def test_item_hash_order_invariant():
    item1 = {"a": 1, "b": 2}
    item2 = {"b": 2, "a": 1}
    assert item_hash(item1) == item_hash(item2)
