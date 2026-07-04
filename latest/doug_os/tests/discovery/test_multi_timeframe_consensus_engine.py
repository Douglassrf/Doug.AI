import pytest
from datetime import datetime, timezone
from doug_os.discovery.multi_timeframe_consensus_engine import (
    MultiTimeframeConsensusEngine, TimeframeSignal, Timeframe, SignalType, ConsensusResult,
)


@pytest.fixture
def engine():
    return MultiTimeframeConsensusEngine()


def _sig(tf: Timeframe, sig: SignalType, strength: float = 0.7) -> TimeframeSignal:
    return TimeframeSignal(timeframe=tf, signal=sig, strength=strength, confidence=0.8)


def test_add_signal_stores_in_correct_timeframe(engine):
    s = _sig(Timeframe.H1, SignalType.BUY)
    engine.add_signal(s)
    assert len(engine._signals[Timeframe.H1]) == 1


def test_add_signal_cap_at_100(engine):
    for _ in range(105):
        engine.add_signal(_sig(Timeframe.M1, SignalType.NEUTRAL))
    assert len(engine._signals[Timeframe.M1]) == 100


def test_get_consensus_no_signals_returns_neutral(engine):
    result = engine.get_consensus()
    assert result.final_signal == SignalType.NEUTRAL
    assert result.final_strength == 0.0


def test_get_consensus_all_buy_returns_buy(engine):
    for tf in [Timeframe.H1, Timeframe.H4, Timeframe.D1]:
        engine.add_signal(_sig(tf, SignalType.BUY, 0.8))
    result = engine.get_consensus()
    assert result.final_signal == SignalType.BUY
    assert result.final_strength > 0.0


def test_get_consensus_divergence_detected(engine):
    engine.add_signal(_sig(Timeframe.H1, SignalType.BUY, 0.9))
    engine.add_signal(_sig(Timeframe.D1, SignalType.SELL, 0.9))
    result = engine.get_consensus()
    assert len(result.divergences) > 0


def test_consensus_score_between_0_and_1(engine):
    engine.add_signal(_sig(Timeframe.H1, SignalType.BUY))
    engine.add_signal(_sig(Timeframe.H4, SignalType.SELL))
    result = engine.get_consensus()
    assert 0.0 <= result.consensus_score <= 1.0


def test_get_temporal_summary_no_data_returns_no_data(engine):
    summary = engine.get_temporal_summary()
    assert summary[Timeframe.H1.value]["signal"] == "no_data"


def test_get_temporal_summary_with_signal(engine):
    engine.add_signal(_sig(Timeframe.D1, SignalType.STRONG_BUY, 0.9))
    summary = engine.get_temporal_summary()
    assert summary[Timeframe.D1.value]["signal"] == SignalType.STRONG_BUY.value


def test_get_consensus_history_limit(engine):
    for _ in range(5):
        engine.add_signal(_sig(Timeframe.H1, SignalType.BUY))
        engine.get_consensus()
    history = engine.get_consensus_history(limit=3)
    assert len(history) == 3


def test_votes_keys_are_strings(engine):
    engine.add_signal(_sig(Timeframe.H1, SignalType.BUY))
    result = engine.get_consensus()
    for key in result.votes:
        assert isinstance(key, str)


def test_to_dict_final_signal_is_string(engine):
    engine.add_signal(_sig(Timeframe.H4, SignalType.STRONG_BUY))
    result = engine.get_consensus()
    d = result.to_dict()
    assert isinstance(d["final_signal"], str)
    assert d["final_signal"] == SignalType.STRONG_BUY.value


def test_recommendation_not_empty(engine):
    engine.add_signal(_sig(Timeframe.H1, SignalType.BUY, 0.9))
    result = engine.get_consensus()
    assert len(result.recommendation) > 0
