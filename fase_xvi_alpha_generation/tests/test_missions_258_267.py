"""Testes básicos — Missões 258-267 (Fase XVI Alpha Generation Intelligence)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_258_alpha_discovery_engine import AlphaDiscoveryEngine, AlphaSignature, AlphaDiscoveryResult
from mission_259_market_opportunity_radar import MarketOpportunityRadar, OpportunitySignal, OpportunityHeatMap
from mission_260_institutional_footprint_analyzer import InstitutionalFootprintAnalyzer, InstitutionalFootprint
from mission_261_adaptive_market_timing import AdaptiveMarketTiming, TimingSignal
from mission_262_trade_efficiency_analyzer import TradeEfficiencyAnalyzer, TradeEfficiency, ImprovementSuggestion
from mission_263_alpha_portfolio_composer import AlphaPortfolioComposer, AlphaAllocation
from mission_264_alpha_decay_monitor import AlphaDecayMonitor, AlphaDecayReport
from mission_265_alpha_correlation_engine import AlphaCorrelationEngine, CorrelationPair
from mission_266_alpha_execution_optimizer import AlphaExecutionOptimizer, ExecutionPlan
from mission_267_alpha_intelligence_hub import AlphaIntelligenceHub, AlphaIntelligenceSnapshot


@pytest.mark.parametrize(
    "cls",
    [
        AlphaSignature,
        AlphaDiscoveryResult,
        OpportunitySignal,
        OpportunityHeatMap,
        InstitutionalFootprint,
        TimingSignal,
        TradeEfficiency,
        ImprovementSuggestion,
        AlphaAllocation,
        AlphaDecayReport,
        CorrelationPair,
        ExecutionPlan,
        AlphaIntelligenceSnapshot,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_258_alpha_discovery_engine():
    engine = AlphaDiscoveryEngine()
    alpha = engine.discover_alpha(
        name="momentum_rsi",
        description="RSI momentum",
        formula="rsi_crossover",
        performance_data=[0.01, -0.005, 0.02, 0.015, -0.01] * 5,
    )
    assert alpha.id.startswith("alpha_")
    dashboard = engine.get_alpha_dashboard()
    assert dashboard["total_alphas"] == 1


def test_mission_259_market_opportunity_radar():
    radar = MarketOpportunityRadar()
    signals = radar.scan_opportunities({
        "asset": "EURUSD",
        "spread": 0.02,
        "depth": 0.8,
        "momentum": 0.5,
        "trend_strength": 0.6,
    })
    assert isinstance(signals, list)
    heatmap = radar.generate_heatmap()
    assert isinstance(heatmap, OpportunityHeatMap)


def test_mission_260_institutional_footprint_analyzer():
    analyzer = InstitutionalFootprintAnalyzer()
    fp = analyzer.analyze_footprint("BTCUSD", {"volume": 1000}, {"large": 5})
    assert fp.asset == "BTCUSD"
    assert analyzer.get_institutional_dashboard()["assets_tracked"] == 1


def test_mission_261_adaptive_market_timing():
    timing = AdaptiveMarketTiming()
    entry = timing.calculate_entry_timing("EURUSD", {"regime": "trending_bull", "volatility": 0.3, "liquidity": 0.7})
    exit_sig = timing.calculate_exit_timing("EURUSD", {"profit": 0.03, "duration_minutes": 90})
    assert entry.action == "entry"
    assert exit_sig.action == "exit"
    assert isinstance(timing._signals, list)


def test_mission_262_trade_efficiency_analyzer():
    analyzer = TradeEfficiencyAnalyzer()
    result = analyzer.analyze_trade(
        "t1",
        {"price": 100, "optimal_price": 99, "timing_score": 0.8, "price_vs_signal": 0.01},
        {"price": 105, "optimal_price": 106, "hit_target": True, "timing_score": 0.7, "profit_pct": 0.05, "max_profit_pct": 0.06},
        {"delay_ms": 50, "slippage_bps": 3},
    )
    assert result.trade_id == "t1"
    assert analyzer.get_efficiency_dashboard()["trades_analyzed"] == 1


def test_mission_263_alpha_portfolio_composer():
    composer = AlphaPortfolioComposer()
    allocations = composer.compose([{"id": "a1", "score": 0.8}, {"id": "a2", "score": 0.4}])
    assert len(allocations) == 2
    assert composer.get_portfolio_dashboard()["allocations"] == 2


def test_mission_264_alpha_decay_monitor():
    monitor = AlphaDecayMonitor()
    report = monitor.evaluate("a1", decay_rate=0.2, lifetime_days=30)
    assert report.alpha_id == "a1"
    assert monitor.get_decay_dashboard()["alphas_monitored"] == 1


def test_mission_265_alpha_correlation_engine():
    engine = AlphaCorrelationEngine()
    pairs = engine.compute_matrix({"a1": [0.1, 0.2, 0.3], "a2": [0.1, 0.15, 0.25]})
    assert len(pairs) == 1
    assert engine.get_correlation_dashboard()["pairs"] == 1


def test_mission_266_alpha_execution_optimizer():
    optimizer = AlphaExecutionOptimizer()
    plan = optimizer.optimize("a1", "EURUSD", size=10, liquidity=0.5)
    assert plan.alpha_id == "a1"
    assert optimizer.get_execution_dashboard()["plans"] == 1


def test_mission_267_alpha_intelligence_hub():
    hub = AlphaIntelligenceHub()
    snapshot = hub.aggregate({"discovery": {"total_alphas": 1}, "timing": {"total_signals": 2}})
    assert snapshot.discovery["total_alphas"] == 1
    assert hub.get_hub_dashboard()["snapshots"] == 1
