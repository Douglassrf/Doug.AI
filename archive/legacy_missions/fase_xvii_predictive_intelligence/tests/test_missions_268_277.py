"""Testes básicos — Missões 268-277 (Fase XVII Predictive Intelligence Architecture)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_268_predictive_market_state_engine import (
    PredictiveMarketStateEngine,
    MarketStatePrediction,
    StateTransitionMatrix,
)
from mission_269_liquidity_intelligence_matrix import (
    LiquidityIntelligenceMatrix,
    LiquidityZone,
    LiquidityMap,
)
from mission_270_institutional_behavior_predictor import (
    InstitutionalBehaviorPredictor,
    InstitutionalPrediction,
)
from mission_271_adaptive_volatility_forecast import (
    AdaptiveVolatilityForecast,
    VolatilityForecast,
)
from mission_272_market_energy_engine import MarketEnergyEngine, EnergyIndex
from mission_273_predictive_signal_fusion_engine import (
    PredictiveSignalFusionEngine,
    FusedSignal,
)
from mission_274_regime_transition_alert_engine import (
    RegimeTransitionAlertEngine,
    RegimeAlert,
)
from mission_275_forecast_validation_engine import (
    ForecastValidationEngine,
    ValidationReport,
)
from mission_276_predictive_risk_mapper import PredictiveRiskMapper, RiskMapEntry
from mission_277_predictive_intelligence_hub import (
    PredictiveIntelligenceHub,
    PredictiveIntelligenceSnapshot,
)


@pytest.mark.parametrize(
    "cls",
    [
        MarketStatePrediction,
        StateTransitionMatrix,
        LiquidityZone,
        LiquidityMap,
        InstitutionalPrediction,
        VolatilityForecast,
        EnergyIndex,
        FusedSignal,
        RegimeAlert,
        ValidationReport,
        RiskMapEntry,
        PredictiveIntelligenceSnapshot,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_268_predictive_market_state_engine():
    engine = PredictiveMarketStateEngine()
    for regime in ["trending_bull", "ranging", "trending_bull"]:
        engine.update_regime_history(regime)
    pred = engine.predict_next_state(
        "trending_bull",
        {"volatility": 0.25, "liquidity": 0.7},
    )
    assert pred.id.startswith("msp_")
    dashboard = engine.get_predictive_dashboard()
    assert dashboard["total_predictions"] == 1


def test_mission_269_liquidity_intelligence_matrix():
    matrix = LiquidityIntelligenceMatrix()
    liquidity_map = matrix.analyze_liquidity(
        "EURUSD",
        {"levels": [{"price": 1.10, "depth": 500, "spread": 0.01}]},
        {"large_volume": 1000},
    )
    assert liquidity_map.asset == "EURUSD"
    assert matrix.get_liquidity_dashboard()["assets_tracked"] == 1


def test_mission_270_institutional_behavior_predictor():
    predictor = InstitutionalBehaviorPredictor()
    pred = predictor.predict_behavior(
        "BTCUSD",
        {"accumulation_score": 0.6, "distribution_score": 0.2, "data_quality": 0.8},
        {"volatility": 0.25, "trend": "bullish"},
    )
    assert pred.asset == "BTCUSD"
    assert predictor.get_forecast_dashboard()["total_predictions"] == 1


def test_mission_271_adaptive_volatility_forecast():
    forecaster = AdaptiveVolatilityForecast()
    prices = [100 + i * 0.5 + (i % 3) * 0.2 for i in range(30)]
    forecast = forecaster.forecast_volatility("EURUSD", prices, implied_vol=0.25)
    assert forecast.asset == "EURUSD"
    assert forecaster.get_forecast_dashboard()["total_forecasts"] == 1


def test_mission_272_market_energy_engine():
    engine = MarketEnergyEngine()
    index = engine.calculate_energy(
        "EURUSD",
        {"momentum": 0.5, "trend_strength": 0.6, "buy_pressure": 0.7, "sell_pressure": 0.4},
    )
    assert index.asset == "EURUSD"
    assert engine.get_energy_dashboard()["assets_tracked"] == 1


def test_mission_273_predictive_signal_fusion_engine():
    fusion = PredictiveSignalFusionEngine()
    signal = fusion.fuse("EURUSD", [
        {"direction": "bullish", "strength": 0.7, "confidence": 0.8},
        {"direction": "bullish", "strength": 0.6, "confidence": 0.7},
    ])
    assert signal.asset == "EURUSD"
    assert fusion.get_fusion_dashboard()["signals_fused"] == 1


def test_mission_274_regime_transition_alert_engine():
    alerts = RegimeTransitionAlertEngine()
    alert = alerts.evaluate("EURUSD", "ranging", "trending_bull", 0.65)
    assert alert.asset == "EURUSD"
    assert alerts.get_alert_dashboard()["total_alerts"] == 1


def test_mission_275_forecast_validation_engine():
    validator = ForecastValidationEngine()
    report = validator.validate("vf_test", predicted=0.25, actual=0.22)
    assert report.forecast_id == "vf_test"
    assert validator.get_validation_dashboard()["validations"] == 1


def test_mission_276_predictive_risk_mapper():
    mapper = PredictiveRiskMapper()
    entry = mapper.map_risk("EURUSD", {"volatility": 0.4, "liquidity": 0.6, "transition_probability": 0.3})
    assert entry.asset == "EURUSD"
    assert mapper.get_risk_dashboard()["assets_tracked"] == 1


def test_mission_277_predictive_intelligence_hub():
    hub = PredictiveIntelligenceHub()
    snapshot = hub.aggregate({"market_state": {"total_predictions": 1}, "energy": {"assets_tracked": 2}})
    assert snapshot.market_state["total_predictions"] == 1
    assert hub.get_hub_dashboard()["snapshots"] == 1
