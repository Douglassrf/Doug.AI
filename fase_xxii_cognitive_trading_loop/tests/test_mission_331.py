"""Testes — Missão 331 Cognitive Trading Loop."""

import sys
from pathlib import Path

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_331 import (
    CognitiveMemory,
    CognitiveTradeRecord,
    CognitiveTradingLoop,
    GeneticEvolutionReport,
    TradeValidationReport,
)


def test_dataclass_instantiation():
    for cls in [CognitiveTradeRecord, TradeValidationReport, GeneticEvolutionReport]:
        obj = cls()
        assert obj.id
        assert obj.to_dict()["id"] == obj.id


def test_memory_records_context_and_fetches_by_pair_strategy():
    memory = CognitiveMemory()
    record = memory.record_trade(
        strategy_id="rsi_alpha",
        pair="R_100",
        params={"rsi_period": 14, "band_width": 20, "stop_loss_pct": 1.0},
        result=1.25,
        market_context={"rsi": 31.0, "volatility": 0.18, "spread": 0.02},
        status="SIMULATION",
    )

    fetched = memory.fetch_recent("R_100", "rsi_alpha")
    assert fetched[0].id == record.id
    assert fetched[0].market_context["rsi"] == 31.0


def test_validate_trade_approves_only_with_similar_positive_significant_history():
    memory = CognitiveMemory()
    for index in range(30):
        memory.record_trade(
            "rsi_alpha",
            "R_100",
            {"rsi_period": 14, "band_width": 20, "stop_loss_pct": 1.0},
            1.0 if index < 26 else -0.2,
            {"rsi": 30.0 + (index % 3) * 0.2, "volatility": 0.20, "spread": 0.01},
        )

    loop = CognitiveTradingLoop(memory=memory, approval_threshold=0.72, min_samples=20)
    report = loop.validate_trade("rsi_alpha", "R_100", {"rsi": 30.1, "volatility": 0.20, "spread": 0.01})

    assert report.verdict == "APPROVED"
    assert report.probability >= 0.72
    assert loop.get_dashboard()["validations"] == 1


def test_validate_trade_standby_when_history_is_insufficient():
    loop = CognitiveTradingLoop(memory=CognitiveMemory(), min_samples=20)
    report = loop.validate_trade("rsi_alpha", "R_100", {"rsi": 30.1})

    assert report.verdict == "STANDBY"
    assert any("insuficiente" in reason for reason in report.reasons)


def test_evolve_dna_keeps_safety_limits_and_promotes_significant_positive_fitness():
    loop = CognitiveTradingLoop(memory=CognitiveMemory(), random_seed=7)
    report = loop.evolve_dna(
        {"rsi_period": 14, "band_width": 20, "stop_loss_pct": 1.0},
        [1.0] * 12 + [0.8] * 8,
    )

    assert report.promoted is True
    for key, value in report.child_params.items():
        lower, upper = loop.DNA_LIMITS[key]
        assert lower <= value <= upper


def test_protective_verdict_stops_after_recent_loss_cluster():
    memory = CognitiveMemory()
    for index in range(30):
        result = -1.0 if index >= 20 else 0.8
        memory.record_trade("rsi_alpha", "R_100", {}, result, {"rsi": 30.0})

    loop = CognitiveTradingLoop(memory=memory, min_samples=20)
    assert loop.protective_verdict("rsi_alpha", "R_100") == "PROTECTIVE_STOP"
