"""Testes básicos — Missões 278-287 (Fase XVIII Quantum Trading Intelligence)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_278_market_dna_engine import MarketDNAEngine, AssetDNA
from mission_279_institutional_intention_detector import (
    InstitutionalIntentionDetector,
    InstitutionalIntent,
)
from mission_280_adaptive_alpha_laboratory import AdaptiveAlphaLaboratory, AlphaCandidate
from mission_281_capital_preservation_ai import CapitalPreservationAI, CapitalHealth
from mission_282_precision_entry_engine import PrecisionEntryEngine, EntryDecision
from mission_283_precision_exit_engine import PrecisionExitEngine, ExitDecision
from mission_284_quantum_trade_orchestrator import QuantumTradeOrchestrator, TradePlan
from mission_285_adaptive_position_sizer import AdaptivePositionSizer, PositionSizeRecommendation
from mission_286_quantum_risk_fusion_engine import QuantumRiskFusionEngine, FusedRiskProfile
from mission_287_quantum_trading_intelligence_hub import (
    QuantumTradingIntelligenceHub,
    QuantumTradingSnapshot,
)


@pytest.mark.parametrize(
    "cls",
    [
        AssetDNA,
        InstitutionalIntent,
        AlphaCandidate,
        CapitalHealth,
        EntryDecision,
        ExitDecision,
        TradePlan,
        PositionSizeRecommendation,
        FusedRiskProfile,
        QuantumTradingSnapshot,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_278_market_dna_engine():
    engine = MarketDNAEngine()
    dna = engine.build_dna(
        "EURUSD",
        {
            "trend_consistency": 0.8,
            "mean_reversion": 0.2,
            "historical_vol": 0.35,
            "spread": 0.1,
            "volume": 0.9,
            "momentum_short": 0.7,
        },
    )
    assert dna.asset == "EURUSD"
    assert dna.market_personality == "trend_follower"
    assert engine.get_dna_dashboard()["assets_tracked"] == 1


def test_mission_279_institutional_intention_detector():
    detector = InstitutionalIntentionDetector()
    intent = detector.detect_intent(
        "BTCUSD",
        {"price_position": 0.2, "volatility": 0.25},
        {"buy_volume": 1000, "sell_volume": 400, "large_orders_buy": 6, "data_quality": 0.8},
    )
    assert intent.asset == "BTCUSD"
    assert detector.get_intent_dashboard()["total_intents"] == 1


def test_mission_280_adaptive_alpha_laboratory():
    lab = AdaptiveAlphaLaboratory()
    perf = [0.01, -0.005, 0.02, 0.015, -0.01] * 5
    parent = lab.submit_alpha("momentum_rsi", "RSI momentum", "RSI(14)", perf)
    child = lab.mutate_alpha(parent.id)
    assert child.id != parent.id
    assert child.parent_ids == [parent.id]
    child2 = lab.mutate_alpha(parent.id)
    assert child2.formula == child.formula
    assert lab.get_alpha_dashboard()["total_alphas"] == 3


def test_mission_281_capital_preservation_ai():
    ai = CapitalPreservationAI(max_drawdown=0.2)
    health = ai.monitor_capital(100000, 20000, [100000, 98000, 95000, 96000])
    assert health.total_capital == 100000
    assert ai.get_capital_dashboard()["health_score"] == health.health_score


def test_mission_282_precision_entry_engine():
    engine = PrecisionEntryEngine()
    decision = engine.evaluate_entry(
        "EURUSD",
        1.1050,
        {"liquidity": 0.8, "timing_score": 0.7, "institutional_score": 0.75, "regime_score": 0.8, "volatility": 0.3},
        {"liquidity": True, "timing": True, "institutional": True, "regime": True},
    )
    assert decision.asset == "EURUSD"
    assert decision.final_decision == "GO"
    assert isinstance(engine._decisions, list)
    assert engine.get_entry_dashboard()["total_decisions"] == 1


def test_mission_283_precision_exit_engine():
    engine = PrecisionExitEngine()
    decision = engine.evaluate_exit("EURUSD", 1.1100, {"profit_pct": 0.04, "duration_minutes": 90})
    assert decision.asset == "EURUSD"
    assert engine.get_exit_dashboard()["total_decisions"] == 1


def test_mission_284_quantum_trade_orchestrator():
    orchestrator = QuantumTradeOrchestrator()
    plan = orchestrator.orchestrate(
        "EURUSD",
        {"direction": "long", "price": 1.10, "go": True},
        {"price": 1.12},
        size=2.0,
    )
    assert plan.asset == "EURUSD"
    assert orchestrator.get_orchestrator_dashboard()["total_plans"] == 1


def test_mission_285_adaptive_position_sizer():
    sizer = AdaptivePositionSizer()
    rec = sizer.calculate_size("EURUSD", 100000, {"volatility": 0.25, "confidence": 0.8})
    assert rec.asset == "EURUSD"
    assert rec.recommended_size > 0
    assert sizer.get_sizer_dashboard()["recommendations"] == 1


def test_mission_286_quantum_risk_fusion_engine():
    engine = QuantumRiskFusionEngine()
    profile = engine.fuse_risk("EURUSD", {"capital_risk": 0.3, "market_risk": 0.4, "execution_risk": 0.2})
    assert profile.asset == "EURUSD"
    assert engine.get_risk_dashboard()["profiles"] == 1


def test_mission_287_quantum_trading_intelligence_hub():
    hub = QuantumTradingIntelligenceHub()
    snapshot = hub.aggregate({"market_dna": {"assets_tracked": 1}, "entry": {"total_decisions": 2}})
    assert snapshot.market_dna["assets_tracked"] == 1
    assert hub.get_hub_dashboard()["snapshots"] == 1
