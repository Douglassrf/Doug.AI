import pytest
from discovery.formal_decision_verification import FormalDecisionVerification, DecisionVerification


def test_verify_safe_decision():
    fdv = FormalDecisionVerification()
    decision = {"id": "d1", "risk_amount": 1.0, "capital": 100.0, "risk_score": 0.3}
    v = fdv.verify_decision(decision)
    assert v.verified is True
    assert v.capital_check_passed is True
    assert v.risk_veto_triggered is False


def test_capital_preservation_breach():
    fdv = FormalDecisionVerification()
    decision = {"id": "d2", "risk_amount": 5.0, "capital": 100.0, "risk_score": 0.2}
    v = fdv.verify_decision(decision)
    assert v.capital_check_passed is False
    assert v.verified is False


def test_risk_veto_triggered():
    fdv = FormalDecisionVerification()
    decision = {"id": "d3", "risk_amount": 0.5, "capital": 100.0, "risk_score": 0.9}
    v = fdv.verify_decision(decision)
    assert v.risk_veto_triggered is True
    assert v.verified is False


def test_register_invariant_passes():
    fdv = FormalDecisionVerification()
    fdv.register_invariant("positive_size", lambda d: d.get("size", 0) > 0)
    v = fdv.verify_decision({"id": "x", "size": 100, "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    assert "positive_size" in v.invariants_passed


def test_register_invariant_fails():
    fdv = FormalDecisionVerification()
    fdv.register_invariant("positive_size", lambda d: d.get("size", 0) > 0)
    v = fdv.verify_decision({"id": "y", "size": -1, "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    assert "positive_size" in v.invariants_failed
    assert v.verified is False


def test_register_safety_rule():
    fdv = FormalDecisionVerification()
    fdv.register_safety_rule(lambda d: d.get("approved", False))
    v = fdv.verify_decision({"id": "z", "approved": False, "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    assert len(v.safety_violations) > 0
    assert v.verified is False


def test_safety_rule_passes():
    fdv = FormalDecisionVerification()
    fdv.register_safety_rule(lambda d: d.get("approved", False))
    v = fdv.verify_decision({"id": "q", "approved": True, "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    assert v.safety_violations == []


def test_get_verification():
    fdv = FormalDecisionVerification()
    v = fdv.verify_decision({"id": "a", "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    fetched = fdv.get_verification(v.id)
    assert fetched is not None
    assert fetched.id == v.id


def test_get_all_verifications():
    fdv = FormalDecisionVerification()
    fdv.verify_decision({"risk_amount": 1, "capital": 100, "risk_score": 0.1})
    fdv.verify_decision({"risk_amount": 2, "capital": 100, "risk_score": 0.1})
    assert len(fdv.get_all_verifications()) == 2


def test_verification_to_dict():
    fdv = FormalDecisionVerification()
    v = fdv.verify_decision({"id": "abc", "risk_amount": 1, "capital": 100, "risk_score": 0.1})
    d = v.to_dict()
    assert "verified" in d
    assert "capital_check_passed" in d
