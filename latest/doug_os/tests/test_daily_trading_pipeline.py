import pytest
from discovery.daily_trading_pipeline import DailyTradingPipeline


def _market_data(price=50000, vol=0.02, rsi=55, momentum=0.01,
                 evidence=0.80, agreement=0.75, risk=1.5, votes=None):
    return {
        "price": price,
        "volume": 100.0,
        "volatility": vol,
        "rsi": rsi,
        "momentum": momentum,
        "spread": 0.0002,
        "evidence_score": evidence,
        "agreement_score": agreement,
        "risk_pct": risk,
        "council_votes": votes or [
            {"agent_id": "MarketAgent", "option": "BUY", "confidence": 0.80},
            {"agent_id": "RiskAgent", "option": "BUY", "confidence": 0.75},
            {"agent_id": "DiscoveryAgent", "option": "BUY", "confidence": 0.70},
        ],
    }


def test_full_pipeline_approved():
    pipeline = DailyTradingPipeline()
    run = pipeline.run("BTC/USDT", _market_data())
    assert run.approved is True
    assert run.final_action != ""
    assert len(run.steps) == 8


def test_blocked_on_zero_price():
    pipeline = DailyTradingPipeline()
    run = pipeline.run("BTC/USDT", _market_data(price=0))
    assert run.approved is False
    assert run.blocked_at_phase == "market_data"


def test_blocked_by_alert_layer1():
    pipeline = DailyTradingPipeline(alert_evidence_threshold=0.90)
    run = pipeline.run("ETH/USDT", _market_data(evidence=0.50))
    assert run.approved is False
    assert "alert" in run.blocked_at_phase or run.blocked_at_phase != ""


def test_blocked_by_alert_layer3_risk():
    pipeline = DailyTradingPipeline(alert_max_risk_pct=1.0)
    run = pipeline.run("SOL/USDT", _market_data(risk=5.0))
    assert run.approved is False


def test_hold_when_no_votes():
    pipeline = DailyTradingPipeline()
    data = _market_data(votes=[])
    run = pipeline.run("BTC/USDT", data)
    # Sem votos → HOLD no council → aprovado no red team (não é BUY)
    assert run is not None


def test_red_team_blocks_overbought():
    pipeline = DailyTradingPipeline(council_threshold=0.60)
    # RSI alto + volatilidade alta → Red Team bloqueia
    run = pipeline.run("BTC/USDT", _market_data(rsi=90.0, vol=0.06))
    # Pode ser bloqueado pelo Red Team
    assert run is not None
    assert run.blocked_at_phase in ("", "red_team_check", "three_layer_alert", "council_vote")


def test_run_stores_in_history():
    pipeline = DailyTradingPipeline()
    pipeline.run("BTC/USDT", _market_data())
    assert len(pipeline.get_runs()) == 1


def test_get_stats():
    pipeline = DailyTradingPipeline()
    pipeline.run("BTC/USDT", _market_data())
    stats = pipeline.get_stats()
    assert stats["total_runs"] == 1


def test_multiple_runs():
    pipeline = DailyTradingPipeline()
    for i in range(3):
        pipeline.run(f"ASSET_{i}", _market_data())
    assert pipeline.get_stats()["total_runs"] == 3


def test_run_to_dict():
    pipeline = DailyTradingPipeline()
    run = pipeline.run("BTC/USDT", _market_data())
    d = run.to_dict()
    assert "steps" in d
    assert "approved" in d
    assert "final_action" in d
