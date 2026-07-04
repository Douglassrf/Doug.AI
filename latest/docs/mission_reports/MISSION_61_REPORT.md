# MISSION 61 — DOUBT ENGINE

## Status: COMPLETE

## Module
`doug_os/discovery/doubt_engine.py`

## Description
Healthy doubt engine that challenges hypotheses before any promotion. Generates critical questions from templates, identifies evidence gaps (sample size, reproducibility, independent validation, peer review), and builds adversarial arguments against overconfident or complex hypotheses.

## Key Classes
- `DoubtAnalysis` — dataclass with critical_questions, doubt_score, evidence_gaps, adversarial_arguments + `to_dict()`
- `DoubtEngine` — `analyze()` runs full doubt pipeline; `get_high_doubt_recommendations()` filters by threshold

## Fix Applied
Corrected syntax bug: `f"doubt_{uuid.uuid4().hex[:12]}"` (spec had unbalanced quotes).

## Doubt Score Formula
`score = n_gaps * 0.1 + n_adversarial * 0.1 + (0.3 if quality < 0.5)`

## Tests
6 tests, all passing.
