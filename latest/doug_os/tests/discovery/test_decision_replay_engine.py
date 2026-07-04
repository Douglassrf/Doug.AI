import pytest
from doug_os.discovery.decision_replay_engine import DecisionReplayEngine, DecisionSnapshot, ReplayResult


def make_engine():
    return DecisionReplayEngine()


def make_snapshot(engine, decision_id="dec_001"):
    return engine.create_snapshot(
        decision_id=decision_id,
        market_state={"price": 100.0, "volume": 1000},
        internal_state={"bias": "bullish"},
        weights={"signal": 0.7},
        council_state={"vote": "buy"},
        risk_state={"drawdown": 0.05},
        dougbrain_state={"confidence": 0.8},
    )


def test_create_snapshot_deepcopy():
    eng = make_engine()
    market = {"price": 100.0}
    snap = eng.create_snapshot("d1", market, {}, {}, {}, {}, {})
    market["price"] = 999.0  # mutate original
    assert snap.market_state["price"] == 100.0  # snapshot unaffected


def test_get_snapshot_returns_correct():
    eng = make_engine()
    snap = make_snapshot(eng)
    result = eng.get_snapshot(snap.id)
    assert result is snap


def test_get_snapshot_missing_returns_none():
    eng = make_engine()
    assert eng.get_snapshot("missing") is None


def test_replay_calls_decision_function():
    eng = make_engine()
    snap = make_snapshot(eng)
    called_with = {}

    def mock_fn(market_state, internal_state, weights, council_state, risk_state, dougbrain_state, **kw):
        called_with.update({"market_state": market_state, "weights": weights})
        return {"action": "buy"}

    result = eng.replay(snap.id, mock_fn)
    assert called_with["market_state"] == {"price": 100.0, "volume": 1000}
    assert result.replayed_result == {"action": "buy"}
    assert result.decision_id == "dec_001"


def test_replay_missing_snapshot_raises():
    eng = make_engine()
    with pytest.raises(ValueError):
        eng.replay("nonexistent", lambda **kw: {})


def test_compare_results_new_key():
    eng = make_engine()
    diff = eng._compare_results({}, {"score": 0.9})
    assert "score" in diff
    assert diff["score"]["status"] == "new"


def test_compare_results_removed_key():
    eng = make_engine()
    diff = eng._compare_results({"score": 0.9}, {})
    assert diff["score"]["status"] == "removed"


def test_compare_results_changed_key():
    eng = make_engine()
    diff = eng._compare_results({"score": 0.5}, {"score": 0.9})
    assert diff["score"]["status"] == "changed"
    assert diff["score"]["diff"] == pytest.approx(0.4)


def test_confidence_no_differences():
    eng = make_engine()
    assert eng._calculate_confidence({}) == 1.0


def test_confidence_decreases_with_differences():
    eng = make_engine()
    diff_5 = {"a": {}, "b": {}, "c": {}, "d": {}, "e": {}}
    conf5 = eng._calculate_confidence(diff_5)
    diff_1 = {"a": {}}
    conf1 = eng._calculate_confidence(diff_1)
    assert conf5 < conf1
    assert conf5 >= 0.0


def test_to_dict_all_fields():
    eng = make_engine()
    snap = make_snapshot(eng)
    result = eng.replay(snap.id, lambda **kw: {"x": 1}, original_result={"x": 2})
    d = result.to_dict()
    for key in ["decision_id", "original_result", "replayed_result", "differences", "confidence", "created_at"]:
        assert key in d


def test_snapshot_to_dict():
    eng = make_engine()
    snap = make_snapshot(eng)
    d = snap.to_dict()
    for key in ["id", "decision_id", "timestamp", "market_state", "internal_state",
                "weights", "council_state", "risk_state", "dougbrain_state"]:
        assert key in d
