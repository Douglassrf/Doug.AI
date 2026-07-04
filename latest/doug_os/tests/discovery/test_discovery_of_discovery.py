import pytest
from doug_os.discovery.discovery_of_discovery import DiscoveryMetrics, DiscoveryOfDiscoveryEngine


def _make_hypotheses(n_useful=3, n_useless=2, regime="trending_bull"):
    hyps = []
    for i in range(n_useful):
        hyps.append({"is_useful": True, "hash": f"h{i}", "market_regime": regime, "computational_cost": 100.0})
    for i in range(n_useless):
        hyps.append({"is_useful": False, "hash": f"u{i}", "market_regime": regime, "computational_cost": 50.0})
    return hyps


def test_analyze_discoveries_totals():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = _make_hypotheses(n_useful=3, n_useless=2)
    metrics = engine.analyze_discoveries(hyps, results=[])
    assert metrics.total_hypotheses == 5
    assert metrics.useful_hypotheses == 3
    assert metrics.useless_hypotheses == 2


def test_false_positives_counted_from_results():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = _make_hypotheses(3, 2)
    results = [{"is_false_positive": True}, {"is_false_positive": False}, {"is_false_positive": True}]
    metrics = engine.analyze_discoveries(hyps, results=results)
    assert metrics.false_positives == 2


def test_success_rate():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = _make_hypotheses(n_useful=4, n_useless=6)
    metrics = engine.analyze_discoveries(hyps, results=[])
    assert metrics.success_rate == pytest.approx(0.4)


def test_repeated_hypotheses():
    engine = DiscoveryOfDiscoveryEngine()
    # First call
    hyps1 = [{"is_useful": True, "hash": "abc", "market_regime": "crisis", "computational_cost": 10.0}]
    engine.analyze_discoveries(hyps1, results=[])
    # Second call with same hash — should increment repeated_hypotheses
    hyps2 = [{"is_useful": True, "hash": "abc", "market_regime": "crisis", "computational_cost": 10.0}]
    metrics2 = engine.analyze_discoveries(hyps2, results=[])
    assert metrics2.repeated_hypotheses == 1


def test_efficiency_by_regime():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = [
        {"is_useful": True, "hash": "a", "market_regime": "trending_bull", "computational_cost": 10.0},
        {"is_useful": False, "hash": "b", "market_regime": "trending_bull", "computational_cost": 10.0},
        {"is_useful": True, "hash": "c", "market_regime": "crisis", "computational_cost": 10.0},
    ]
    metrics = engine.analyze_discoveries(hyps, results=[])
    assert "trending_bull" in metrics.efficiency_by_regime
    assert metrics.efficiency_by_regime["trending_bull"] == pytest.approx(0.5)
    assert metrics.efficiency_by_regime["crisis"] == pytest.approx(1.0)


def test_check_alerts_low_success_rate():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = _make_hypotheses(n_useful=1, n_useless=9)
    metrics = engine.analyze_discoveries(hyps, results=[])
    alerts = engine.check_alerts(metrics)
    assert any("Low success rate" in a for a in alerts)


def test_get_performance_trend_insufficient_data():
    engine = DiscoveryOfDiscoveryEngine()
    hyps = _make_hypotheses(3, 2)
    engine.analyze_discoveries(hyps, results=[])
    trend = engine.get_performance_trend()
    assert trend["trend"] == "insufficient_data"


def test_get_performance_trend_improving():
    engine = DiscoveryOfDiscoveryEngine()
    hyps_bad = _make_hypotheses(n_useful=1, n_useless=9)
    hyps_good = _make_hypotheses(n_useful=8, n_useless=2)
    engine.analyze_discoveries(hyps_bad, results=[])
    engine.analyze_discoveries(hyps_good, results=[])
    trend = engine.get_performance_trend()
    assert trend["trend"] == "improving"
    assert trend["success_rate_delta"] > 0
