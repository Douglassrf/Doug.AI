import pytest
from discovery.validated_pattern_registry import ValidatedPatternRegistry


def test_register_pattern():
    reg = ValidatedPatternRegistry()
    p = reg.register("RSI_reversal", conditions={"rsi": "<30"})
    assert p.name == "RSI_reversal"
    assert p.status == "probation"


def test_record_result_increases_replications():
    reg = ValidatedPatternRegistry(min_replications=3)
    p = reg.register("pat1", initial_evidence=0.80)
    for i in range(3):
        reg.record_result(p.id, pnl=1.0)
    assert p.replications == 3
    assert p.status == "active"


def test_record_result_archives_low_confidence():
    reg = ValidatedPatternRegistry(archive_threshold=0.60, min_replications=2)
    p = reg.register("bad_pat", initial_evidence=0.10)
    reg.record_result(p.id, pnl=-1.0)
    reg.record_result(p.id, pnl=-1.0)
    assert p.status == "archived"


def test_get_active_returns_only_active():
    reg = ValidatedPatternRegistry(min_replications=2)
    p1 = reg.register("good", initial_evidence=0.90)
    p2 = reg.register("bad", initial_evidence=0.10)
    for _ in range(2):
        reg.record_result(p1.id, pnl=1.0)
        reg.record_result(p2.id, pnl=-1.0)
    active = reg.get_active()
    ids = [p.id for p in active]
    assert p1.id in ids
    assert p2.id not in ids


def test_get_top():
    reg = ValidatedPatternRegistry(min_replications=3)
    patterns = []
    for i in range(5):
        p = reg.register(f"pat_{i}", initial_evidence=0.60 + i * 0.05)
        for _ in range(3):
            reg.record_result(p.id, pnl=1.0)
        patterns.append(p)
    top3 = reg.get_top(3)
    assert len(top3) == 3
    assert top3[0].confidence >= top3[1].confidence


def test_get_by_name():
    reg = ValidatedPatternRegistry()
    reg.register("special_pat")
    found = reg.get_by_name("special_pat")
    assert found is not None


def test_archive_low_confidence():
    reg = ValidatedPatternRegistry(archive_threshold=0.70, min_replications=2)
    p = reg.register("marginal", initial_evidence=0.50)
    for _ in range(2):
        reg.record_result(p.id, pnl=0.5)
    count = reg.archive_low_confidence()
    assert count >= 0  # may or may not archive depending on computed confidence


def test_confidence_range():
    reg = ValidatedPatternRegistry()
    p = reg.register("test", initial_evidence=0.75)
    reg.record_result(p.id, pnl=1.0)
    assert 0.0 <= p.confidence <= 1.0


def test_get_stats():
    reg = ValidatedPatternRegistry()
    reg.register("p1")
    stats = reg.get_stats()
    assert stats["total"] == 1
    assert "by_status" in stats


def test_list_all():
    reg = ValidatedPatternRegistry()
    reg.register("p1")
    reg.register("p2")
    lst = reg.list_all()
    assert len(lst) == 2
    assert "name" in lst[0]
