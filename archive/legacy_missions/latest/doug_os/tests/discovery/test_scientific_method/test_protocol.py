import pytest
from doug_os.discovery.scientific_method.protocol import (
    ScientificProtocol, ScientificStatus, EvidenceLevel
)


def _valid_protocol(**kwargs) -> ScientificProtocol:
    defaults = dict(
        hypothesis_id="hyp_123",
        question="Does X affect Y?",
        hypothesis_formulation="If X increases, Y increases",
        null_hypothesis="X has no effect on Y",
        alternative_hypothesis="X affects Y",
        independent_variables=["X"],
        dependent_variables=["Y"],
        success_criteria={"effect_size": 0.2},
        rejection_criteria={"p_value": 0.1},
    )
    defaults.update(kwargs)
    return ScientificProtocol(**defaults)


def test_protocol_creation():
    p = _valid_protocol()
    assert p.hypothesis_id == "hyp_123"
    assert p.is_valid()
    assert p.status == ScientificStatus.FORMULATING


def test_protocol_invalid_missing_fields():
    p = ScientificProtocol()
    assert not p.is_valid()


def test_protocol_promote_evidence_advances():
    p = ScientificProtocol()
    assert p.evidence_level == EvidenceLevel.ANECDOTAL
    p.promote_evidence(EvidenceLevel.OBSERVATIONAL)
    assert p.evidence_level == EvidenceLevel.OBSERVATIONAL


def test_protocol_promote_evidence_does_not_retreat():
    p = ScientificProtocol()
    p.promote_evidence(EvidenceLevel.EXPERIMENTAL)
    p.promote_evidence(EvidenceLevel.ANECDOTAL)
    assert p.evidence_level == EvidenceLevel.EXPERIMENTAL


def test_protocol_to_dict_and_back():
    p = _valid_protocol()
    d = p.to_dict()
    p2 = ScientificProtocol.from_dict(d)
    assert p2.id == p.id
    assert p2.hypothesis_id == p.hypothesis_id
    assert p2.evidence_level == p.evidence_level
    assert p2.status == p.status


def test_protocol_id_is_unique():
    p1 = ScientificProtocol()
    p2 = ScientificProtocol()
    assert p1.id != p2.id
