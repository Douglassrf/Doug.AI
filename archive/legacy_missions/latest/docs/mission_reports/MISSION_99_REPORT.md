# Mission 99 — Decision DNA Engine

## Status: COMPLETE

## Module
`doug_os/discovery/decision_dna_engine.py`

## Description
Captures the full reasoning fingerprint of a decision: evidence, hypotheses, module weights, market regime, confidence, risk, explanation, reasoning chain, and a SHA-256 audit hash. Supports lookup by DNA id or decision_id, outcome updates, and text search.

## Tests
`doug_os/tests/discovery/test_decision_dna_engine.py` — 10 tests, all passing.

Key cases:
- audit_hash generated on creation, 16 hex chars
- get_dna / get_dna_by_decision roundtrips
- update_outcome persists outcome dict
- search_dna matches by explanation text
- to_dict includes all fields with outcome=None
