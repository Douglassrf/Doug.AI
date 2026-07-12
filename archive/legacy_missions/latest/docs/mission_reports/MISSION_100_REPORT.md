# Mission 100 — Decision Replay Engine

## Status: COMPLETE

## Module
`doug_os/discovery/decision_replay_engine.py`

## Description
Records deep-copies of all system states at decision time (DecisionSnapshot) and allows replaying those states through any callable decision function to detect outcome differences. Computes structural diffs and a confidence score.

## Tests
`doug_os/tests/discovery/test_decision_replay_engine.py` — 12 tests, all passing.

Key cases:
- create_snapshot stores deepcopy — original mutation doesn't affect snapshot
- get_snapshot roundtrip
- replay invokes decision_function with snapshot states
- replay with missing snapshot → ValueError
- _compare_results detects new / removed / changed keys
- confidence 1.0 with no differences, decreases with more diffs
- to_dict serializes ReplayResult and DecisionSnapshot
