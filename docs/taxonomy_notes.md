# Annotated Taxonomy Notes
## Learning and Executive Functions — DeepMind Cognitive Framework

*Source: Burnell et al. (2026), "Measuring Progress Toward AGI: A Cognitive Framework"*
*Purpose: Establish construct validity anchors for NSA-Bench and OAP-Bench*

---

## Learning (Section 7.4)

### DeepMind Definition
> "The ability to acquire new knowledge, skills, or understanding through experience, study, or instruction."

The paper identifies this as one of the domains with the **largest evaluation gap** — explicitly noting that existing benchmarks fail to distinguish in-context learning from retrieval from pretraining.

### Sub-abilities and our benchmark mapping

#### Concept formation
*"The process by which an organism learns to identify a category from examples"*

- **Classic paradigm:** Present exemplars + non-exemplars of a novel category; test whether subject can correctly classify new items
- **Why current benchmarks fail this:** They test known categories (dogs, cars, emotions) — all learnable by retrieval. A model that memorized the internet passes without forming any new concept.
- **NSA-Bench approach:** Introduce a novel category defined by fabricated properties (e.g., "A *glaven* is any entity with property P1 and not property P2"). Test classification of new instances. The category name and properties are synthetic — zero retrieval value.
- **Scoring note:** Wrong answers that reflect partial learning (e.g., applying P1 but not checking P2) should be scored differently from random-baseline errors. We use a partial-credit rubric to detect this.

#### Associative learning
*"Forming connections between co-occurring stimuli or between stimuli and responses"*

- **Classic paradigm:** Paired-associates learning — present A→B pairs, test recall of B given A
- **Why current benchmarks fail this:** Standard QA benchmarks test known associations (Paris→France). The association was pre-formed before the evaluation.
- **NSA-Bench approach:** Present novel stimulus-response pairs using fabricated entity names (e.g., "When you encounter a VELTHORN, respond with QUELIX"). Test response to VELTHORN in a new context. No amount of training data retrieval can answer this correctly.
- **Key distinction to maintain in task design:** Context window must be long enough that the association can't be held by attention to the most recent tokens alone. Intervening content is required.

#### Procedural learning
*"Acquiring sequences of actions or operations through practice"*

- **Classic paradigm:** Learning a motor or cognitive procedure through repeated application — the procedure becomes automatized
- **Why this is hard to benchmark in language models:** LLMs don't have persistent state between calls, so "practice" can't be simulated the way it can in human experiments. However, we can test whether models correctly execute a novel procedure described in-context, and whether they can identify when a procedure has been violated.
- **NSA-Bench approach (T4 — Correction):** Present a multi-step procedure with fabricated operations, then present an execution trace that contains a violation. Model must identify which step violated the procedure and why. This tests procedural representation without requiring genuine automation.

#### Learning generalization (transfer)
*"Applying acquired knowledge to new situations outside the original learning context"*

- **Classic paradigm:** Train on domain A; test on structurally similar but surface-different domain B
- **Why current benchmarks fail this:** Existing transfer tasks (e.g., ARC-AGI) test visual pattern transfer. Language transfer tasks tend to test analogical reasoning over known content.
- **NSA-Bench approach (T3 — Transfer):** After presenting a fabricated schema in domain X, present a structurally identical problem in a surface-different domain Y using entirely different entity names and context. Correct performance requires recognizing the structural equivalence, not the surface match.

### Critical evaluation property: contamination safety

The paper explicitly flags that "many of the high-quality benchmarks that do exist are fully public, so they are susceptible to data contamination." Our response:

Every NSA-Bench schema is procedurally generated. The generator takes a seed and produces:
- A unique set of fabricated entity names (no real words)
- A unique rule structure (no existing logical system)
- A unique relational vocabulary

Two items with the same seed produce identical schemas — this is what makes results reproducible. Items with different seeds are structurally different. No item's content can appear in pretraining data.

---

## Executive Functions (Section 7.8)

### DeepMind Definition
> "Abilities that facilitate goal-directed behavior. Includes planning, inhibition, and cognitive flexibility."

The paper groups these as "higher-order control processes" — they regulate the basic cognitive faculties rather than performing content-level cognition directly. This is why they're hard to benchmark: most tasks test the content-level output without revealing whether the control process that produced it was functioning correctly.

### Sub-abilities and our benchmark mapping

#### Inhibitory control
*"The ability to suppress prepotent responses — automatic, dominant, or habitual reactions — in favor of context-appropriate behavior"*

- **Classic paradigms:** Stroop task (name ink color, suppress reading), Go/No-Go, Stop Signal Task
- **The key insight for language models:** LLMs have extremely strong statistical priors — certain inputs reliably elicit certain outputs because that's what the training distribution contains. Inhibitory control measures whether the model can override those priors when explicitly instructed to.
- **OAP-Bench approach (Rule Reversal):** Present a rule that inverts a high-frequency mapping. For example: "For this task, when asked to name the opposite of a word, always give the synonym instead." Then ask: "What is the opposite of 'large'?" A model with intact inhibitory control says "big" (synonym, per the rule). A model with impaired inhibitory control says "small" (the prepotent response).
- **Scoring note:** This is one of the few places where wrong answers reveal more than right answers. We log whether errors are prepotent (the default response the rule is designed to suppress) or random. Prepotent errors are the diagnostic signal.

#### Cognitive flexibility
*"The ability to shift between mental sets, tasks, or rules — sometimes called task-switching or set-shifting"*

- **Classic paradigms:** Wisconsin Card Sorting Test (WCST), task-switching paradigms with alternating rule cues
- **Why current benchmarks fail this:** Most benchmarks present a single task type per item. Cognitive flexibility only appears under conditions where the rule changes mid-sequence and the subject must detect and adapt to the change.
- **OAP-Bench approach (Task Switching):** Present a sequence of items under Rule A, then introduce a cue signaling Rule B, then continue the sequence. Correct performance requires: (a) detecting the switch cue, (b) abandoning Rule A without perseveration, (c) applying Rule B correctly. We measure both the first item post-switch (most likely to fail) and subsequent items (recovery rate).
- **Key design constraint:** The switch cue must be unambiguous but not so loud that it trivializes the test. We use natural-language cues embedded in the item sequence ("From this point, use the new rule:...") rather than obvious formatting changes.

#### Working memory under load
*"Maintaining and manipulating information over short periods while performing concurrent cognitive operations"*

- **Classic paradigm:** n-back tasks, dual-task paradigms, distractor-interference paradigms
- **OAP-Bench approach (Loaded Working Memory):** Present a target goal state to maintain ("Your task is to track the count of the word 'red' in the following passage"). Then present a passage with highly salient distractor content designed to capture attention. Then test whether the model tracked the target (not the distractor). This differs from simple reading comprehension — the test is whether attention management worked correctly, not whether the model understood the text.

#### Planning
*"The ability to formulate and execute multi-step action sequences toward a goal, including anticipating consequences of actions"*

- **Classic paradigm:** Tower of Hanoi, route planning, multi-step problem-solving
- **In language model context:** Planning is the most benchmarked of the executive function sub-abilities (many chain-of-thought tasks measure this implicitly). We include a lightweight planning component in OAP-Bench but do not make it the primary focus — it is already better covered by existing benchmarks than the other three sub-abilities.

---

## On Human Baseline Anchoring

The DeepMind paper requires human baselines for a valid cognitive profile. Since we cannot run a demographic human study in 27 days, our approach is:

1. **Published norms**: Each task type (Stroop, WCST, n-back variants, concept formation) has decades of published human performance data. We map expected human performance ranges to our task difficulty tiers and cite the source literature.
2. **Difficulty calibration**: We calibrate task difficulty using these published norms so that Tier 1 items correspond to approximately 90%+ human accuracy, Tier 2 to ~75%, Tier 3 to ~55%, Tier 4 to ~35%.
3. **Transparent limitation**: We clearly state in the write-up that direct human baselines on our specific items were not collected, and explain why the published norms are a reasonable proxy. This is more honest than many competition submissions and judges will appreciate the methodological transparency.

---

## References

- Burnell, R. et al. (2026). Measuring Progress Toward AGI: A Cognitive Framework. Google DeepMind.
- Stroop, J.R. (1935). Studies of interference in serial verbal reactions. *Journal of Experimental Psychology*, 18(6), 643–662.
- Grant, D.A. & Berg, E. (1948). A behavioral analysis of degree of reinforcement on the Wisconsin Card Sorting Test. *Journal of Experimental Psychology*, 38, 404–411.
- Chollet, F. (2019). On the measure of intelligence. *arXiv:1911.01547*.
- Kovacs, K. & Conway, A.R.A. (2016). Process overlap theory: A unified account of the general factor of intelligence. *Psychological Inquiry*, 27(3), 151–177.
