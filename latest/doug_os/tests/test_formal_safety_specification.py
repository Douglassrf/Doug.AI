import pytest
from discovery.formal_safety_specification import FormalSafetySpecification, SafetyRule, SafetyVerificationResult


def test_register_rule():
    spec = FormalSafetySpecification()
    rule = spec.register_rule("no_short", lambda a: a.get("direction") != "short", severity="high")
    assert rule.name == "no_short"
    assert rule.severity == "high"


def test_verify_passes():
    spec = FormalSafetySpecification()
    spec.register_rule("positive_size", lambda a: a.get("size", 0) > 0)
    result = spec.verify_action({"size": 100})
    assert result.passed is True
    assert result.violated_rules == []


def test_verify_fails():
    spec = FormalSafetySpecification()
    spec.register_rule("positive_size", lambda a: a.get("size", 0) > 0)
    result = spec.verify_action({"size": -1})
    assert result.passed is False
    assert "positive_size" in result.violated_rules


def test_violation_count_incremented():
    spec = FormalSafetySpecification()
    rule = spec.register_rule("r", lambda a: False)
    spec.verify_action({})
    spec.verify_action({})
    assert rule.violation_count == 2


def test_critical_severity_blocks():
    spec = FormalSafetySpecification()
    spec.register_rule("no_margin", lambda a: not a.get("margin"), severity="critical")
    blocked = spec.is_action_blocked({"margin": True})
    assert blocked is True


def test_non_critical_violation():
    spec = FormalSafetySpecification()
    spec.register_rule("r", lambda a: False, severity="low")
    result = spec.verify_action({})
    assert result.severity == "low"
    assert not spec.is_action_blocked({})  # only blocks on critical


def test_multiple_rules():
    spec = FormalSafetySpecification()
    spec.register_rule("r1", lambda a: a.get("approved", False))
    spec.register_rule("r2", lambda a: a.get("size", 0) > 0)
    result = spec.verify_action({"approved": True, "size": 10})
    assert result.passed is True


def test_rule_exception_treated_as_failure():
    spec = FormalSafetySpecification()
    spec.register_rule("bad_rule", lambda a: 1 / 0)
    result = spec.verify_action({})
    assert result.passed is False


def test_get_safety_report():
    spec = FormalSafetySpecification()
    spec.register_rule("r", lambda a: False)
    spec.verify_action({})
    report = spec.get_safety_report()
    assert report["total_verifications"] == 1
    assert report["failed"] == 1
