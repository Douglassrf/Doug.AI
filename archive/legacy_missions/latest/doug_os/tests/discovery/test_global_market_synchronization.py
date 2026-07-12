import pytest
from doug_os.discovery.global_market_synchronization import (
    GlobalMarketSynchronization, MarketSnapshot, GlobalMarketState,
)

SNAP_DATA = {
    "forex": {"EURUSD": 1.08, "GBPUSD": 1.26},
    "crypto": {"BTC": 0.8, "ETH": 0.6},
    "commodities": {"GOLD": 0.7, "OIL": 0.5},
    "bonds": {"US10Y": 0.4, "DE10Y": 0.3},
    "indices": {"SP500": 0.75, "DAX": 0.65},
    "futures": {"ES": 0.7, "CL": 0.5},
    "etfs": {"SPY": 0.72, "GLD": 0.6},
    "macro": {"CPI": 0.5, "PMI": 0.6},
}


@pytest.fixture
def sync():
    return GlobalMarketSynchronization(seed=42)


def test_add_snapshot_returns_snapshot(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    assert isinstance(snap, MarketSnapshot)
    assert snap.id.startswith("ms_")


def test_snapshot_stores_markets(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    assert snap.forex == SNAP_DATA["forex"]
    assert snap.crypto == SNAP_DATA["crypto"]


def test_snapshot_calculates_correlations(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    assert len(snap.correlations) > 0


def test_correlation_self_is_one(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    for market, corrs in snap.correlations.items():
        assert corrs[market] == 1.0


def test_analyze_global_state_returns_state(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    state = sync.analyze_global_state(snap.id)
    assert isinstance(state, GlobalMarketState)
    assert state.snapshot_id == snap.id


def test_global_regime_is_known_value(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    state = sync.analyze_global_state(snap.id)
    assert state.global_regime in ("bull", "bear", "neutral", "high_risk", "crisis")


def test_scores_in_range(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    state = sync.analyze_global_state(snap.id)
    for score in (state.liquidity_score, state.risk_score, state.momentum_score):
        assert 0.0 <= score <= 1.0


def test_analyze_unknown_snapshot_raises(sync):
    with pytest.raises(ValueError):
        sync.analyze_global_state("nonexistent_id")


def test_get_global_state_returns_latest(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    sync.analyze_global_state(snap.id)
    assert sync.get_global_state() is not None


def test_get_global_state_before_analyze_returns_none(sync):
    assert sync.get_global_state() is None


def test_get_correlation_matrix_after_analyze(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    sync.analyze_global_state(snap.id)
    matrix = sync.get_correlation_matrix()
    assert isinstance(matrix, dict)
    assert len(matrix) > 0


def test_anomaly_detection_runs(sync):
    snap = sync.add_snapshot(SNAP_DATA)
    state = sync.analyze_global_state(snap.id)
    assert isinstance(state.anomaly_detected, bool)
