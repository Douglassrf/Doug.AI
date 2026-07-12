# MISSION 59 — CERTAINTY TRAP DETECTOR

## Status: COMPLETE

## Module
`doug_os/discovery/certainty_trap_detector.py`

## Description
Prevents hypotheses from being treated as absolute truths over time. Checks hypothesis age, number of distinct market regime changes, and whether the hypothesis has been reviewed recently (frozen). Raises severity levels when old, unreviewed hypotheses span multiple regime changes.

## Key Classes
- `CertaintyTrapAlert` — dataclass with age, frozen, regime_changes, severity fields + `to_dict()`
- `CertaintyTrapDetector` — `check()` evaluates a hypothesis; `get_stale_hypotheses()` returns IDs older than threshold

## Fix Applied
`self._alerts` correctly typed as `Dict[str, CertaintyTrapAlert]` (spec had ambiguous List annotation).

## Severity Logic
- age > 365 AND regime_changes > 3 AND frozen → critical
- age > 180 AND regime_changes > 2 AND frozen → high
- age > 90 AND regime_changes > 1 → medium
- age > 30 → low

## Tests
6 tests, all passing.
