import pytest
from doug_os.discovery.scientific_validation_framework import (
    ScientificValidationFramework, ScientificDiscovery, ValidationResult,
)


@pytest.fixture
def fw():
    return ScientificValidationFramework()


def _make_discovery(fw, p_value=0.01, effect_size=0.5, sample_size=200, confidence=0.9, reps=3):
    d = fw.register_discovery(
        title="Test Discovery",
        description="A test hypothesis",
        hypothesis="H0: there is no effect",
        evidence=[{"source": "backtest", "strength": 0.8}],
    )
    d.p_value = p_value
    d.effect_size = effect_size
    d.sample_size = sample_size
    d.confidence = confidence
    d.replication_count = reps
    return d


def test_register_discovery_returns_discovery(fw):
    d = fw.register_discovery("T", "desc", "hyp", [])
    assert isinstance(d, ScientificDiscovery)
    assert d.id in fw._discoveries


def test_validate_strong_discovery_is_valid(fw):
    d = _make_discovery(fw)
    result = fw.validate(d.id)
    assert result.is_valid is True
    assert result.score > 0.6


def test_validate_weak_discovery_is_invalid(fw):
    d = _make_discovery(fw, p_value=0.5, effect_size=0.01, sample_size=5, confidence=0.1, reps=0)
    result = fw.validate(d.id)
    assert result.is_valid is False


def test_validate_unknown_raises(fw):
    with pytest.raises(ValueError):
        fw.validate("nonexistent_id")


def test_validated_discovery_added_to_queue(fw):
    d = _make_discovery(fw)
    fw.validate(d.id)
    assert d.id in fw.get_publication_queue()


def test_publish_validated_discovery(fw):
    d = _make_discovery(fw)
    fw.validate(d.id)
    assert fw.publish(d.id) is True
    assert d.status == "published"
    assert d.id not in fw.get_publication_queue()


def test_publish_unvalidated_returns_false(fw):
    d = fw.register_discovery("X", "desc", "hyp", [])
    assert fw.publish(d.id) is False


def test_validation_result_stored(fw):
    d = _make_discovery(fw)
    fw.validate(d.id)
    result = fw.get_validation_result(d.id)
    assert isinstance(result, ValidationResult)


def test_validation_confidence_in_range(fw):
    d = _make_discovery(fw)
    result = fw.validate(d.id)
    assert 0.0 <= result.confidence <= 1.0


def test_validation_result_has_reasons(fw):
    d = _make_discovery(fw, p_value=0.2, effect_size=0.05, sample_size=10)
    result = fw.validate(d.id)
    assert isinstance(result.reasons, list)


def test_get_all_discoveries(fw):
    fw.register_discovery("A", "d", "h", [])
    fw.register_discovery("B", "d", "h", [])
    assert len(fw.get_all_discoveries()) == 2


def test_validated_at_set_on_valid(fw):
    d = _make_discovery(fw)
    fw.validate(d.id)
    assert d.validated_at is not None
