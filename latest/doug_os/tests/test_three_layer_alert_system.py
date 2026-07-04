import pytest
from discovery.three_layer_alert_system import ThreeLayerAlertSystem, AlertDecision


def _signal(ev=0.80, ag=0.75, risk=1.5):
    return {"evidence_score": ev, "agreement_score": ag, "risk_pct": risk}


def test_all_layers_pass():
    sys = ThreeLayerAlertSystem()
    d = sys.evaluate(_signal(0.80, 0.75, 1.5))
    assert d.approved is True
    assert d.blocked_at_layer == 0
    assert len(d.layers) == 3


def test_block_at_layer1():
    sys = ThreeLayerAlertSystem(evidence_threshold=0.75)
    d = sys.evaluate(_signal(ev=0.60))
    assert d.approved is False
    assert d.blocked_at_layer == 1
    assert len(d.layers) == 1


def test_block_at_layer2():
    sys = ThreeLayerAlertSystem(consensus_threshold=0.70)
    d = sys.evaluate(_signal(ev=0.80, ag=0.50))
    assert d.approved is False
    assert d.blocked_at_layer == 2


def test_block_at_layer3():
    sys = ThreeLayerAlertSystem(max_risk_pct=2.0)
    d = sys.evaluate(_signal(ev=0.80, ag=0.75, risk=3.5))
    assert d.approved is False
    assert d.blocked_at_layer == 3


def test_boundary_evidence_exact():
    sys = ThreeLayerAlertSystem(evidence_threshold=0.75)
    d = sys.evaluate(_signal(ev=0.75))
    assert d.layers[0].passed is True


def test_boundary_consensus_exact():
    sys = ThreeLayerAlertSystem(consensus_threshold=0.70)
    d = sys.evaluate(_signal(ag=0.70))
    assert d.layers[1].passed is True


def test_get_stats():
    sys = ThreeLayerAlertSystem()
    sys.evaluate(_signal(0.80, 0.75, 1.5))
    sys.evaluate(_signal(0.50, 0.75, 1.5))
    stats = sys.get_stats()
    assert stats["total"] == 2
    assert stats["approved"] == 1
    assert stats["blocked"] == 1


def test_history():
    sys = ThreeLayerAlertSystem()
    sys.evaluate(_signal())
    history = sys.get_history()
    assert len(history) == 1
    assert "approved" in history[0]


def test_approved_only_filter():
    sys = ThreeLayerAlertSystem()
    sys.evaluate(_signal())
    sys.evaluate(_signal(ev=0.10))
    history = sys.get_history(approved_only=True)
    assert all(h["approved"] for h in history)


def test_to_dict_complete():
    sys = ThreeLayerAlertSystem()
    d = sys.evaluate(_signal())
    dd = d.to_dict()
    assert "layers" in dd
    assert "blocked_at_layer" in dd
    assert len(dd["layers"]) == 3
