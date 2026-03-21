# Concept Document: AGI Cognitive Benchmark Suite

**Tracks:** Learning · Executive Functions
**Authors:** Ivan Garibay (City of Dallas / UTSA) · Claude (Anthropic)
**Submission Deadline:** April 16, 2026

---

## Problem Statement

The DeepMind Cognitive Taxonomy (Burnell et al., 2026) identifies Learning and Executive Functions as two of the five cognitive domains with the largest evaluation gaps. Existing benchmarks fail these domains in a consistent way: they test *the appearance* of the ability rather than the ability itself.

For **Learning**, the gap is that most benchmarks measure retrieval from training data, not genuine in-context knowledge acquisition. A model that has memorized the training corpus can score well on any benchmark whose content could plausibly appear in pretraining — regardless of whether it can actually *learn* anything new.

For **Executive Functions**, the gap is that most benchmarks test whether a model can *do* something, not whether it can *inhibit doing the wrong thing*. Inhibitory control — suppressing the habitual, high-probability response in favor of a context-correct one — is precisely what current benchmarks leave unmeasured.

Both benchmarks in this suite are designed to be structurally unsolvable by retrieval or statistical pattern-matching alone.

---

## Benchmark 1: NSA-Bench (Novel Schema Acquisition)

### Cognitive sub-abilities targeted
From DeepMind taxonomy (Section 7.4):
- **Concept formation** — induction of category structure from examples
- **Associative learning** — linking novel stimuli to novel responses
- **Procedural learning** — acquiring rule-based operational sequences
- **Learning generalization** — transferring acquired schema to new cases

### Core design principle
Each task item presents a fabricated knowledge system — an invented taxonomy, a synthetic rule grammar, or a procedurally generated logical calculus — that does not and cannot exist in any model's training data. The model must acquire and apply this system purely from in-context information.

### Task structure (four difficulty tiers)

| Tier | Sub-ability | Description |
|---|---|---|
| T1: Direct application | Associative learning | Given schema, apply one rule to one input |
| T2: Inference | Concept formation | Given schema, chain two rules to reach a conclusion |
| T3: Transfer | Learning generalization | Given schema + novel scenario, identify applicable rules |
| T4: Correction | Procedural learning | Given schema + introduced contradiction, identify the violation |

### Why this is contamination-safe
Schemas are procedurally generated using a fixed random seed. Novel entity names, rule structures, and relational vocabularies are synthetic. No item can be answered by retrieval because the knowledge system is defined only within the context window of that item.

---

## Benchmark 2: OAP-Bench (Override and Plan)

### Cognitive sub-abilities targeted
From DeepMind taxonomy (Section 7.8):
- **Inhibitory control** — suppressing prepotent (dominant, automatic) responses
- **Cognitive flexibility** — shifting between task rules or mental sets
- **Working memory** — maintaining goal state under distraction
- **Planning** — sequencing actions across multiple steps toward a goal

### Core design principle
Each task is designed so that the most statistically likely response — the one a model would produce by completing the pattern — is explicitly wrong. Correct performance requires detecting that the habitual response is invalid and generating a context-appropriate override.

### Task structure (three subtask types)

| Type | Sub-ability | Description |
|---|---|---|
| Rule Reversal | Inhibitory control | Instructions explicitly invert a well-practiced mapping (e.g., semantic opposites, reversed sorting) |
| Task Switching | Cognitive flexibility | Mid-sequence rule change; model must detect switch and apply new rule without perseverating |
| Loaded Working Memory | Working memory + inhibition | Maintain a goal state while processing distractor content; respond to goal, not distractor |

### Why this measures what it claims
These tasks are adapted from validated cognitive psychology paradigms (Stroop, WCST, n-back variants) translated into language form. The scoring penalizes "close but wrong" answers that reflect partial inhibition failure — not just binary hit/miss.

---

## Evaluation Protocol

Both benchmarks follow the DeepMind three-stage protocol:
1. AI evaluation on held-out task items (stratified by subtask and difficulty)
2. Human baseline anchoring via published norms from the source cognitive paradigms
3. Model cognitive profiles showing performance relative to the human distribution

### Models evaluated
Claude Haiku 4.5, Claude Sonnet 4.6, Claude Opus 4.6 — three capability tiers within a single model family, enabling controlled analysis of how these cognitive sub-abilities scale with model size and capability.

---

## Expected Contribution

This submission contributes:
1. Two fully specified, contamination-safe benchmark datasets (JSONL format)
2. A reproducible evaluation harness with deterministic scoring
3. Empirical cognitive profiles for three Claude model tiers
4. Theoretical grounding in cognitive psychology literature for each task type
5. A methodology for fabricated-world learning benchmarks that other researchers can extend
