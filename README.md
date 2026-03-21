# AGI Cognitive Benchmark Suite
### Submission for: Measuring Progress Toward AGI — Cognitive Abilities (Kaggle / Google DeepMind, 2026)
**Tracks:** Learning · Executive Functions

---

## Overview

This repository contains two benchmark suites designed for the Google DeepMind / Kaggle hackathon on measuring cognitive abilities in frontier AI systems. Both benchmarks are grounded in the DeepMind Cognitive Taxonomy (Burnell et al., 2026) and are designed to isolate specific sub-abilities where the evaluation gap is largest.

| Benchmark | Track | Core Construct |
|---|---|---|
| **NSA-Bench** (Novel Schema Acquisition) | Learning | In-context acquisition of novel structured knowledge |
| **OAP-Bench** (Override and Plan) | Executive Functions | Inhibitory control, cognitive flexibility, working memory |

Both benchmarks are:
- **Contamination-safe** — task items use fabricated or procedurally generated content that cannot exist in training data
- **Human-baseline anchored** — difficulty tiers calibrated to expected human performance
- **Fully reproducible** — fixed seeds, deterministic scoring, version-locked dependencies

---

## Repository Structure

```
agi-benchmark/
├── data/
│   ├── learning/             # NSA-Bench dataset (JSONL)
│   └── executive_functions/  # OAP-Bench dataset (JSONL)
├── src/
│   ├── eval.py               # Main evaluation harness
│   ├── scoring.py            # Scoring logic and metrics
│   ├── generate_tasks.py     # Task generation scripts
│   └── utils.py              # Shared utilities
├── results/                  # Model evaluation outputs
├── docs/
│   ├── concept.md            # Benchmark concept document
│   ├── taxonomy_notes.md     # Annotated DeepMind taxonomy analysis
│   ├── nsa_bench_spec.md     # NSA-Bench full specification
│   └── oap_bench_spec.md     # OAP-Bench full specification
├── tests/                    # Unit tests for scoring and parsing
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/agi-benchmark.git
cd agi-benchmark
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 3. Run Learning benchmark
python src/eval.py \
  --dataset data/learning/nsa_bench.jsonl \
  --model claude-haiku-4-5-20251001 \
  --output results/nsa_haiku.json

# 4. Run Executive Functions benchmark
python src/eval.py \
  --dataset data/executive_functions/oap_bench.jsonl \
  --model claude-haiku-4-5-20251001 \
  --output results/oap_haiku.json
```

---

## Models Evaluated

| Model | API String | Tier |
|---|---|---|
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast / lightweight |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Mid-range |
| Claude Opus 4.6 | `claude-opus-4-6` | Frontier |

Running all three models on both benchmarks reveals capability scaling across a single model family — a clean controlled comparison.

---

## Citation

If you use this benchmark, please cite:
```
Burnell, R. et al. (2026). Measuring Progress Toward AGI: A Cognitive Framework.
Google DeepMind. https://deepmind.google/
```

---

## License

MIT — benchmark datasets and evaluation code are freely available for research use.
