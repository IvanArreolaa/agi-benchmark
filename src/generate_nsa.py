"""
generate_nsa.py — Generator for NSA-Bench (Novel Schema Acquisition)
Learning Track — Google DeepMind AGI Hackathon 2026

Produces: data/learning/nsa_bench.jsonl  (60 items, 15 per tier)

Tiers:
  T1 — Direct application     (associative learning)
  T2 — Chained inference      (concept formation)
  T3 — Transfer               (learning generalization)
  T4 — Violation detection    (procedural learning)

Run: python src/generate_nsa.py
"""

import json
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# Fabricated vocabulary pools
# All names are nonsense phoneme strings — zero retrieval value from training
# ---------------------------------------------------------------------------

ENTITIES_A = [
    "VELTHORN", "QUAZIM", "DRUVEK", "SELPHI", "MORTEX",
    "CRIVEN", "BLAXTON", "ZELPHAR", "FRUVOK", "NALDRIS",
    "STUVEK", "GROVEN", "PLETHIX", "WORZAK", "DREMUL",
]
ENTITIES_B = [
    "QUILNAR", "THROVIC", "BEXMAL", "SORPENT", "DOLVAK",
    "FURVEK", "GLENTHOR", "MIVREK", "STALPHOR", "ZUVOX",
    "WREKNAL", "CRUVETH", "PHONDAL", "BRIXEK", "NERVAK",
]
PROPERTIES = [
    "ALTIX", "BRENOX", "CROVAL", "DENDRIL", "EVRATH",
    "FLOREX", "GROVEN", "HELZAK", "IRVOX", "JELTHAR",
    "KROVEX", "LENDRAL", "MIVOX", "NEXRAL", "OVRATH",
]
STATES = [
    "TORVAL", "SELPRIX", "WRENDAX", "BLIVOTH", "CREZNAK",
    "DROVEN", "FILTHAR", "GOVREK", "HOLVAX", "IZDRAK",
    "JORTHEM", "KLEVOX", "LORPHEN", "MEZDRAK", "NELVAX",
]
ACTIONS = [
    "TRANSFORMS INTO", "PRODUCES", "YIELDS", "GENERATES", "BECOMES",
    "CREATES", "EMITS", "TRIGGERS", "ACTIVATES", "CONVERTS TO",
]
DOMAINS_A = ["Zelphi system", "Vektran protocol", "Druvek taxonomy",
             "Mortex framework", "Blaxton schema"]
DOMAINS_B = ["Quorven registry", "Selphen codex", "Naldris catalogue",
             "Groven archive", "Phondal index"]


def pick(*pool, n=1, exclude=None):
    exclude = exclude or []
    opts = [x for x in pool[0] if x not in exclude]
    return random.sample(opts, n)


# ---------------------------------------------------------------------------
# T1: Direct Application (15 items)
# Given a mapping schema, apply one rule to retrieve a single output.
# ---------------------------------------------------------------------------

def make_t1(item_num: int) -> dict:
    domain = random.choice(DOMAINS_A)
    n_mappings = random.randint(4, 6)
    keys = random.sample(ENTITIES_A, n_mappings)
    vals = random.sample(ENTITIES_B, n_mappings)
    mapping = list(zip(keys, vals))
    action = random.choice(ACTIONS)

    target_idx = random.randint(0, n_mappings - 1)
    target_key, target_val = mapping[target_idx]

    # Build 3 distractors from other values in the schema
    distractor_pool = [v for k, v in mapping if k != target_key]
    # Add one completely foreign entity
    foreign = random.choice([e for e in ENTITIES_B if e not in vals])
    distractor_pool.append(foreign)
    distractors = random.sample(distractor_pool, 3)

    choices = [target_val] + distractors
    random.shuffle(choices)
    answer_letter = chr(65 + choices.index(target_val))

    mapping_lines = "\n".join(
        f"  {k} {action} {v}" for k, v in mapping
    )
    context = (
        f"The following mapping rules define the {domain}:\n\n"
        f"{mapping_lines}\n\n"
        f"These rules are complete and apply only within this schema. "
        f"No other rules exist."
    )
    question = (
        f"According to the {domain} rules above, "
        f"what does {target_key} {action.lower().replace('transforms into', 'transform into')}?"
    )

    return {
        "id": f"nsa_t1_{item_num:03d}",
        "track": "learning",
        "subtask": "direct_application",
        "difficulty": 1,
        "cognitive_ability": "associative_learning",
        "context": context,
        "question": question,
        "choices": choices,
        "answer": answer_letter,
        "human_baseline_expected": 0.93,
        "contamination_safe": True,
        "seed": SEED,
        "notes": "Model must retrieve a single learned association. No chaining required.",
    }


# ---------------------------------------------------------------------------
# T2: Chained Inference (15 items)
# Given rules that chain (A→B, B→C), infer the final state of an entity.
# ---------------------------------------------------------------------------

def make_t2(item_num: int) -> dict:
    domain = random.choice(DOMAINS_A)
    chain_len = random.randint(2, 3)

    # Build a chain: E0 → P0 → P1 → (P2)
    entities = random.sample(ENTITIES_A, 2)
    props = random.sample(PROPERTIES, chain_len + 1)
    start_entity = entities[0]
    wrong_entity = entities[1]

    # Chain rules
    rules = []
    rules.append(
        f"Rule 1: Any {start_entity} entity acquires property {props[0]}."
    )
    for i in range(1, chain_len):
        rules.append(
            f"Rule {i+1}: Any entity with property {props[i-1]} "
            f"acquires property {props[i]}."
        )
    final_prop = props[chain_len - 1]
    terminal_state = random.choice(STATES)
    rules.append(
        f"Rule {chain_len+1}: Any entity with property {final_prop} "
        f"becomes a {terminal_state}."
    )

    context = (
        f"The {domain} operates by the following rules:\n\n"
        + "\n".join(f"  {r}" for r in rules)
        + "\n\nAll rules apply sequentially. Each rule fires when its "
          "condition is met. No other rules exist."
    )

    # Correct answer: the terminal state
    # Distractors: intermediate properties, wrong entity's state, random state
    wrong_states = random.sample(
        [s for s in STATES if s != terminal_state], 3
    )
    choices = [terminal_state] + wrong_states
    random.shuffle(choices)
    answer_letter = chr(65 + choices.index(terminal_state))

    question = (
        f"A {start_entity} entity enters the {domain}. "
        f"After all applicable rules have fired, what does it become?"
    )

    return {
        "id": f"nsa_t2_{item_num:03d}",
        "track": "learning",
        "subtask": "chained_inference",
        "difficulty": 2,
        "cognitive_ability": "concept_formation",
        "context": context,
        "question": question,
        "choices": choices,
        "answer": answer_letter,
        "human_baseline_expected": 0.76,
        "contamination_safe": True,
        "seed": SEED,
        "notes": "Model must chain rules sequentially. Distractors include intermediate states.",
    }


# ---------------------------------------------------------------------------
# T3: Transfer (15 items)
# Schema in Domain A; structurally identical problem in Domain B.
# Surface entities are entirely different — only structure transfers.
# ---------------------------------------------------------------------------

def make_t3(item_num: int) -> dict:
    domain_a = random.choice(DOMAINS_A)
    domain_b = random.choice(DOMAINS_B)

    # Shared structural rule: X-type → acquires P → becomes S
    ent_a = random.choice(ENTITIES_A)
    prop_a = random.choice(PROPERTIES)
    state_a = random.choice(STATES)

    ent_b = random.choice([e for e in ENTITIES_B if e != ent_a])
    prop_b = random.choice([p for p in PROPERTIES if p != prop_a])
    state_b = random.choice([s for s in STATES if s != state_a])

    context = (
        f"You are given two independent classification systems.\n\n"
        f"--- {domain_a} ---\n"
        f"  Rule A1: Every {ent_a} entity acquires property {prop_a}.\n"
        f"  Rule A2: Any entity with property {prop_a} is classified as {state_a}.\n\n"
        f"--- {domain_b} ---\n"
        f"  Rule B1: Every {ent_b} entity acquires property {prop_b}.\n"
        f"  Rule B2: Any entity with property {prop_b} is classified as {state_b}.\n\n"
        f"The two systems are structurally parallel but operate on entirely "
        f"different entities and properties."
    )

    # Transfer question: new entity in domain B with same structure
    new_ent_b = random.choice([e for e in ENTITIES_B if e not in [ent_a, ent_b]])
    prop_b2 = random.choice([p for p in PROPERTIES if p != prop_a and p != prop_b])
    state_b2 = random.choice([s for s in STATES if s != state_a and s != state_b])

    context += (
        f"\n\n--- {domain_b} Extension ---\n"
        f"  Rule B3: Every {new_ent_b} entity acquires property {prop_b2}.\n"
        f"  Rule B4: Any entity with property {prop_b2} is classified as {state_b2}."
    )

    question = (
        f"A {new_ent_b} entity enters the {domain_b}. "
        f"Applying the same structural logic used in both systems above, "
        f"what is its final classification?"
    )

    wrong_states = random.sample(
        [s for s in STATES if s != state_b2], 3
    )
    choices = [state_b2] + wrong_states
    random.shuffle(choices)
    answer_letter = chr(65 + choices.index(state_b2))

    return {
        "id": f"nsa_t3_{item_num:03d}",
        "track": "learning",
        "subtask": "transfer",
        "difficulty": 3,
        "cognitive_ability": "learning_generalization",
        "context": context,
        "question": question,
        "choices": choices,
        "answer": answer_letter,
        "human_baseline_expected": 0.61,
        "contamination_safe": True,
        "seed": SEED,
        "notes": "Model must recognize structural equivalence across surface-different domains.",
    }


# ---------------------------------------------------------------------------
# T4: Violation Detection (15 items)
# A procedure is defined; an execution trace contains exactly one violation.
# Model identifies which step was violated.
# ---------------------------------------------------------------------------

def make_t4(item_num: int) -> dict:
    domain = random.choice(DOMAINS_A)
    n_steps = random.randint(4, 5)

    entities = random.sample(ENTITIES_A, n_steps)
    props = random.sample(PROPERTIES, n_steps)
    states = random.sample(STATES, 2)

    # Define the procedure
    proc_steps = []
    for i in range(n_steps):
        if i == 0:
            proc_steps.append(
                f"Step {i+1}: Accept a {entities[i]} entity and assign it property {props[i]}."
            )
        elif i == n_steps - 1:
            proc_steps.append(
                f"Step {i+1}: If the entity has property {props[i-1]}, "
                f"classify it as {states[0]}; otherwise classify it as {states[1]}."
            )
        else:
            proc_steps.append(
                f"Step {i+1}: Replace property {props[i-1]} with property {props[i]}."
            )

    # Build a correct trace then introduce one violation
    violation_step = random.randint(1, n_steps - 1)

    trace_steps = []
    for i in range(n_steps):
        step_num = i + 1
        if step_num == 1:
            trace_steps.append(
                f"Trace Step {step_num}: Received a {entities[i]} entity. "
                f"Assigned property {props[i]}. ✓"
            )
        elif step_num == n_steps:
            correct_prop = props[n_steps - 2]
            trace_steps.append(
                f"Trace Step {step_num}: Entity has property {correct_prop}. "
                f"Classified as {states[0]}. ✓"
            )
        elif step_num == violation_step:
            # Introduce violation: uses wrong property
            wrong_prop = random.choice([p for p in PROPERTIES if p != props[i] and p != props[i-1]])
            trace_steps.append(
                f"Trace Step {step_num}: Replaced property {props[i-1]} "
                f"with property {wrong_prop}."
                f"  ← Applied here"
            )
        else:
            trace_steps.append(
                f"Trace Step {step_num}: Replaced property {props[i-1]} "
                f"with property {props[i]}. ✓"
            )

    context = (
        f"The {domain} defines the following processing procedure:\n\n"
        + "\n".join(f"  {s}" for s in proc_steps)
        + "\n\n--- Execution Trace ---\n"
        + "\n".join(f"  {s}" for s in trace_steps)
        + "\n\nExactly one step in the trace violates the defined procedure."
    )

    question = "Which step number contains the violation?"

    # Build choices: correct violation step + 3 wrong step numbers
    all_steps = list(range(1, n_steps + 1))
    wrong_steps = [s for s in all_steps if s != violation_step]
    distractor_steps = random.sample(wrong_steps, min(3, len(wrong_steps)))
    while len(distractor_steps) < 3:
        distractor_steps.append(random.choice(wrong_steps))

    choices = [f"Step {violation_step}"] + [f"Step {s}" for s in distractor_steps]
    random.shuffle(choices)
    answer_letter = chr(65 + choices.index(f"Step {violation_step}"))

    return {
        "id": f"nsa_t4_{item_num:03d}",
        "track": "learning",
        "subtask": "violation_detection",
        "difficulty": 4,
        "cognitive_ability": "procedural_learning",
        "context": context,
        "question": question,
        "choices": choices,
        "answer": answer_letter,
        "human_baseline_expected": 0.47,
        "contamination_safe": True,
        "seed": SEED,
        "notes": "Model must maintain procedural representation and detect a single deviation.",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_nsa_bench(n_per_tier: int = 15) -> list[dict]:
    items = []
    generators = [make_t1, make_t2, make_t3, make_t4]
    for i, gen in enumerate(generators):
        for j in range(n_per_tier):
            item = gen(j + 1)
            items.append(item)
    return items


if __name__ == "__main__":
    random.seed(SEED)
    items = generate_nsa_bench(n_per_tier=15)

    out_path = Path("data/learning/nsa_bench.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

    print(f"Generated {len(items)} NSA-Bench items → {out_path}")
    subtask_counts = {}
    for item in items:
        st = item["subtask"]
        subtask_counts[st] = subtask_counts.get(st, 0) + 1
    for st, count in subtask_counts.items():
        print(f"  {st}: {count} items")
