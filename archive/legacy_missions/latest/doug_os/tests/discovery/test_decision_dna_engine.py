import pytest
from doug_os.discovery.decision_dna_engine import DecisionDNAEngine, DecisionDNA


def make_engine():
    return DecisionDNAEngine()


def make_dna(engine, decision_id="dec_001", explanation="buy signal"):
    return engine.create_dna(
        decision_id=decision_id,
        evidence=[{"type": "price", "value": "above MA"}],
        hypotheses=[{"h": "bullish"}],
        modules=["module_a"],
        market_regime="bull",
        score=0.8,
        confidence=0.75,
        risk_score=0.2,
        weights={"module_a": 0.6},
        explanation=explanation,
        reasoning_chain=["step1", "step2"],
    )


def test_create_dna_audit_hash_not_empty():
    eng = make_engine()
    dna = make_dna(eng)
    assert dna.audit_hash != ""
    assert len(dna.audit_hash) == 16


def test_audit_hash_is_hex():
    eng = make_engine()
    dna = make_dna(eng)
    int(dna.audit_hash, 16)  # raises ValueError if not hex


def test_get_dna_returns_correct():
    eng = make_engine()
    dna = make_dna(eng)
    retrieved = eng.get_dna(dna.id)
    assert retrieved is dna


def test_get_dna_missing_returns_none():
    eng = make_engine()
    assert eng.get_dna("nonexistent") is None


def test_get_dna_by_decision():
    eng = make_engine()
    dna = make_dna(eng, decision_id="dec_999")
    result = eng.get_dna_by_decision("dec_999")
    assert result is dna


def test_get_dna_by_decision_missing_returns_none():
    eng = make_engine()
    assert eng.get_dna_by_decision("nope") is None


def test_update_outcome():
    eng = make_engine()
    dna = make_dna(eng)
    assert dna.outcome is None
    eng.update_outcome(dna.id, {"pnl": 0.05, "status": "win"})
    assert dna.outcome == {"pnl": 0.05, "status": "win"}


def test_update_outcome_missing_id_noop():
    eng = make_engine()
    eng.update_outcome("missing", {"pnl": 1.0})  # should not raise


def test_search_dna_by_explanation():
    eng = make_engine()
    dna1 = make_dna(eng, explanation="strong buy signal detected")
    dna2 = make_dna(eng, explanation="sell pressure increasing")
    results = eng.search_dna("buy")
    ids = [r["dna"]["id"] for r in results]
    assert dna1.id in ids
    assert dna2.id not in ids


def test_to_dict_all_fields():
    eng = make_engine()
    dna = make_dna(eng)
    d = dna.to_dict()
    for key in ["id", "decision_id", "evidence", "hypotheses", "modules",
                "market_regime", "timestamp", "score", "confidence", "risk_score",
                "weights", "explanation", "reasoning_chain", "audit_hash",
                "created_at", "outcome"]:
        assert key in d
    assert d["outcome"] is None
