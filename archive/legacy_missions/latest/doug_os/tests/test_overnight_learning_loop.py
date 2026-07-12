import pytest
from discovery.overnight_learning_loop import OvernightLearningLoop, DaySession


def _session(date="2026-07-04", won=7, lost=3, agents=None):
    s = DaySession(
        date=date,
        total_trades=won + lost,
        won_trades=won,
        lost_trades=lost,
        total_pnl=won * 1.5 - lost * 1.0,
        agent_outcomes=agents or {
            "MarketAgent":    {"win_rate": 0.70, "trades": 10},
            "RiskAgent":      {"win_rate": 0.90, "trades": 10},
            "DiscoveryAgent": {"win_rate": 0.40, "trades": 10},
        },
        patterns_tested=["RSI_reversal", "MA_cross", "VOL_breakout"],
        hypotheses_failed=["H1_volume_spike"],
    )
    return s


def test_run_overnight_returns_report():
    loop = OvernightLearningLoop()
    report = loop.run_overnight(_session())
    assert report is not None
    assert report.session_date == "2026-07-04"


def test_promotes_high_win_rate_agent():
    loop = OvernightLearningLoop(promote_threshold=0.65)
    loop.run_overnight(_session())
    report = loop._reports[-1]
    assert "RiskAgent" in report.agents_promoted


def test_penalizes_low_win_rate_agent():
    loop = OvernightLearningLoop(penalize_threshold=0.45)
    loop.run_overnight(_session())
    report = loop._reports[-1]
    assert "DiscoveryAgent" in report.agents_penalized


def test_weight_increases_after_promotion():
    loop = OvernightLearningLoop(promote_threshold=0.65)
    initial = loop.get_weight("RiskAgent")
    loop.run_overnight(_session())
    new = loop.get_weight("RiskAgent")
    assert new >= initial


def test_weight_decreases_after_penalty():
    loop = OvernightLearningLoop(penalize_threshold=0.45)
    loop._agent_weights["DiscoveryAgent"] = 0.70
    loop.run_overnight(_session())
    new = loop.get_weight("DiscoveryAgent")
    assert new <= 0.70


def test_scheduled_experiments():
    loop = OvernightLearningLoop()
    loop.run_overnight(_session())
    exps = loop.get_scheduled_experiments()
    assert "H1_volume_spike" in exps


def test_record_strategy_scores():
    loop = OvernightLearningLoop()
    loop.record_strategy_result("RSI_reversal", 0.85)
    loop.record_strategy_result("RSI_reversal", 0.75)
    loop.run_overnight(_session())
    report = loop._reports[-1]
    assert any(r["strategy"] == "RSI_reversal" for r in report.strategies_ranked)


def test_get_stats():
    loop = OvernightLearningLoop()
    loop.run_overnight(_session())
    stats = loop.get_stats()
    assert stats["total_sessions"] == 1
    assert stats["total_reports"] == 1


def test_weights_for_tomorrow():
    loop = OvernightLearningLoop()
    loop.run_overnight(_session())
    weights = loop.get_weights_for_tomorrow()
    assert isinstance(weights, dict)
    assert len(weights) > 0


def test_weight_bounds_respected():
    loop = OvernightLearningLoop(min_weight=0.10, max_weight=1.0)
    session = _session(agents={
        "A": {"win_rate": 1.0, "trades": 20},
        "B": {"win_rate": 0.0, "trades": 20},
    })
    for _ in range(20):
        loop.run_overnight(session)
    assert loop.get_weight("A") <= 1.0
    assert loop.get_weight("B") >= 0.10
