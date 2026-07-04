# MISSION 63 — INTERNAL MARKET

## Status: COMPLETE

## Module
`doug_os/discovery/internal_market.py`

## Description
Internal market where models compete for trust and symbolic capital. Each correct directional prediction earns 5% of current capital; wrong predictions lose 3%. Win rate is tracked and combined with capital to compute a score. Models are ranked by score.

## Key Classes
- `ModelRanking` — dataclass with symbolic_capital, win_rate, score, accuracy_history (capped at 100) + `to_dict()` (exposes last 10 accuracy entries)
- `InternalMarket` — `register_model()`, `trade()`, `get_ranking()`, `get_best_model()`

## Capital Formula
- Correct: `capital += capital * 0.05`
- Wrong: `capital -= capital * 0.03` (floor: 10.0)
- Score: `win_rate * capital / 100`

## Tests
7 tests, all passing.
