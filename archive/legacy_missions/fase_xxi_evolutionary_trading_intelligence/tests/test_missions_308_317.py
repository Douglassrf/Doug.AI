"""Testes — Missões 308-317 (Fase XXI Evolutionary Trading Intelligence)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_308 import MarketEvolutionEngine, MarketEvolutionReport
from mission_309 import StrategyLifecycleManager, StrategyLifecycle, LifecycleStage
from mission_310 import GlobalPatternIntelligence, UniversalPattern
from mission_311 import InstitutionalMemoryNetwork, InstitutionalMemory
from mission_312 import PredictiveLiquidityEngine, LiquidityPrediction
from mission_313 import CompetitiveAlphaAnalyzer, AlphaAnalysis
from mission_314 import AdaptiveStrategyMutationEngine, MutationCandidate
from mission_315 import EcosystemIntelligenceOrchestrator, EcosystemReport
from mission_316 import EvolutionaryLearningLoop, LearningCycle
from mission_317 import FaseXXICertificationGate, CertificationReport


@pytest.mark.parametrize(
    "cls",
    [
        MarketEvolutionReport,
        StrategyLifecycle,
        UniversalPattern,
        InstitutionalMemory,
        LiquidityPrediction,
        AlphaAnalysis,
        MutationCandidate,
        EcosystemReport,
        LearningCycle,
        CertificationReport,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_308_market_evolution_engine():
    engine = MarketEvolutionEngine()
    historical = {
        "volatility": 0.3,
        "liquidity": 0.5,
        "regime": "trending",
        "behavioral": {
            "trend_consistency": 0.5,
            "mean_reversion": 0.4,
            "volatility_clustering": 0.3,
        },
        "institutional": {"presence": 0.4},
    }
    current = {
        "volatility": 0.3,
        "liquidity": 0.5,
        "regime": "ranging",
        "behavioral": {
            "trend_consistency": 0.9,
            "mean_reversion": 0.1,
            "volatility_clustering": 0.8,
        },
        "institutional": {"presence": 0.8},
    }

    report = engine.analyze_evolution(current, historical)
    assert report.regime_mutation is True
    assert report.behavioral_drift > 0.3
    assert engine.get_evolution_dashboard()["total_reports"] == 1


def test_mission_309_strategy_lifecycle_transitions():
    manager = StrategyLifecycleManager()
    manager.register_strategy("momentum_v1")

    for i in range(25):
        manager.update_performance("momentum_v1", 0.01 + i * 0.015)

    assert manager.get_lifecycle_status("momentum_v1")["stage"] == LifecycleStage.GROWTH

    for _ in range(15):
        manager.update_performance("momentum_v1", 0.40)

    assert manager.get_lifecycle_status("momentum_v1")["stage"] == LifecycleStage.MATURITY

    for i in range(15):
        manager.update_performance("momentum_v1", 0.40 - i * 0.02)

    stage = manager.get_lifecycle_status("momentum_v1")["stage"]
    assert stage in (LifecycleStage.DECLINE, LifecycleStage.RETIRED)
    assert manager.get_lifecycle_dashboard()["total_strategies"] == 1


def test_mission_310_global_pattern_intelligence():
    intel = GlobalPatternIntelligence()
    pattern = intel.discover_pattern(
        "vol_compression",
        "Volatility compression breakout",
        {"features": ["vol", "range", "volume"]},
        ["EURUSD", "GBPUSD", "USDJPY"],
    )
    assert pattern.name == "vol_compression"
    assert pattern.confidence > 0.3

    similar = intel.find_similar_patterns({"features": ["vol"]}, threshold=0.5)
    assert len(similar) >= 1

    clusters = intel.cluster_patterns(k=2)
    assert len(clusters) >= 1
    assert intel.get_pattern_dashboard()["total_patterns"] == 1


def test_mission_310_deterministic_market_check():
    intel = GlobalPatternIntelligence()
    data = {"features": ["a", "b"]}
    first = intel._check_pattern_in_market(data, "EURUSD")
    second = intel._check_pattern_in_market(data, "EURUSD")
    assert first == second


def test_mission_311_institutional_memory_network():
    network = InstitutionalMemoryNetwork()
    memory = network.record_behavior(
        "whale_001",
        "accumulation",
        {"volume_ratio": 2.5, "price_impact": 0.01},
        "trending",
        confidence=0.85,
    )
    assert memory.institution_id == "whale_001"
    assert len(network.get_institution_history("whale_001")) == 1

    network.record_behavior(
        "whale_002",
        "accumulation",
        {"volume_ratio": 2.4, "price_impact": 0.012},
        "trending",
        confidence=0.7,
    )
    similar = network.find_similar_cases(
        "accumulation",
        "trending",
        {"volume_ratio": 2.45, "price_impact": 0.011},
    )
    assert len(similar) >= 1
    assert network.get_memory_dashboard()["total_memories"] == 2


def test_mission_312_predictive_liquidity_engine():
    engine = PredictiveLiquidityEngine()
    pred1 = engine.predict_liquidity(
        "BTCUSD",
        0.75,
        {"levels": [1, 2, 3], "depth": 0.8},
        {"average": 5000, "trend": 0.1, "data_quality": 0.9},
    )
    assert pred1.asset == "BTCUSD"
    assert pred1.confidence >= 0.7

    pred2 = engine.predict_liquidity(
        "BTCUSD",
        0.76,
        {"levels": [1, 2, 3], "depth": 0.8},
        {"average": 5000, "trend": 0.1, "data_quality": 0.9},
    )
    assert pred1.stop_cluster_density == pred2.stop_cluster_density
    assert engine.get_liquidity_dashboard()["total_predictions"] == 2


def test_mission_313_competitive_alpha_analyzer():
    analyzer = CompetitiveAlphaAnalyzer()
    alpha_returns = [0.02, 0.015, 0.01, 0.025, 0.018] * 4
    market_returns = [0.005, 0.003, 0.004, 0.006, 0.002] * 4

    analysis = analyzer.analyze_alpha("alpha_momentum", alpha_returns, market_returns)
    assert analysis.alpha_id == "alpha_momentum"
    assert analysis.edge_score > 0.5
    assert analysis.recommendation in ("scale", "maintain", "monitor", "retire")
    assert len(analyzer.get_learning_history("alpha_momentum")) == 1
    assert analyzer.get_alpha_dashboard()["total_analyses"] == 1


def test_mission_314_adaptive_strategy_mutation_engine():
    engine = AdaptiveStrategyMutationEngine()
    signals = {"evolution_score": 0.7, "regime": "trending", "risk_tolerance": 0.5}
    candidates = engine.generate_mutations("strat_001", signals, count=3)
    assert len(candidates) == 3

    best = engine.select_best("strat_001", candidates)
    assert best is not None
    assert best.fitness_score > 0

    previous = engine.rollback("strat_001")
    assert previous is None
    assert engine.get_mutation_dashboard()["total_candidates"] == 3


def test_mission_315_ecosystem_orchestrator():
    orchestrator = EcosystemIntelligenceOrchestrator()
    report = orchestrator.aggregate(
        {
            "evolution": {"total_reports": 5, "evolution_score": 0.6},
            "lifecycle": {"total_strategies": 3},
            "patterns": {"total_patterns": 2},
            "memory": {"total_memories": 10},
            "liquidity": {"total_predictions": 4},
            "alpha": {"total_analyses": 2, "avg_edge_score": 0.65},
            "mutations": {"total_candidates": 6, "avg_fitness": 0.55},
        }
    )
    assert report.ecosystem_health > 0
    assert orchestrator.get_ecosystem_dashboard()["reports"] == 1


def test_mission_316_evolutionary_learning_loop():
    loop = EvolutionaryLearningLoop()
    cycle = loop.integrate_feedback(
        {"evolution_score": 0.65},
        {"accuracy": 0.8, "stability": 0.7, "performance": 0.75},
    )
    assert cycle.model_version >= 1
    assert len(cycle.updates_applied) >= 1
    assert loop.get_learning_dashboard()["total_cycles"] == 1


def test_mission_317_certification_gate():
    gate = FaseXXICertificationGate()
    report = gate.evaluate(
        {
            "evolution": {"total_reports": 1},
            "lifecycle": {"total_strategies": 1},
            "patterns": {"total_patterns": 1},
            "memory": {"total_memories": 1},
            "liquidity": {"total_predictions": 1},
            "alpha": {"total_analyses": 1},
            "mutations": {"total_candidates": 1},
            "ecosystem_health": 0.65,
            "learning": {"total_cycles": 1},
        }
    )
    assert report.verdict == "GO"
    assert report.score >= 0.75
    assert gate.get_certification_dashboard()["latest_verdict"] == "GO"


def test_full_phase_integration():
    evolution_engine = MarketEvolutionEngine()
    lifecycle_manager = StrategyLifecycleManager()
    pattern_intel = GlobalPatternIntelligence()
    memory_network = InstitutionalMemoryNetwork()
    liquidity_engine = PredictiveLiquidityEngine()
    alpha_analyzer = CompetitiveAlphaAnalyzer()
    mutation_engine = AdaptiveStrategyMutationEngine()
    orchestrator = EcosystemIntelligenceOrchestrator()
    learning_loop = EvolutionaryLearningLoop()
    certification_gate = FaseXXICertificationGate()

    evolution_engine.analyze_evolution(
        {"regime": "volatile", "volatility": 0.5, "liquidity": 0.6},
        {"regime": "calm", "volatility": 0.2, "liquidity": 0.8},
    )
    lifecycle_manager.register_strategy("evo_strat_1")
    lifecycle_manager.update_performance("evo_strat_1", 0.02)
    pattern_intel.discover_pattern("p1", "desc", {"features": ["x"]}, ["EURUSD", "GBPUSD"])
    memory_network.record_behavior("inst1", "trap", {"x": 1}, "volatile")
    liquidity_engine.predict_liquidity("EURUSD", 0.8, {"depth": 0.9}, {"data_quality": 0.9})
    alpha_analyzer.analyze_alpha("a1", [0.01, 0.02], [0.005, 0.004])
    mutation_engine.generate_mutations("evo_strat_1", {"evolution_score": 0.6, "risk_tolerance": 0.5})

    ecosystem_report = orchestrator.aggregate(
        {
            "evolution": evolution_engine.get_evolution_dashboard(),
            "lifecycle": lifecycle_manager.get_lifecycle_dashboard(),
            "patterns": pattern_intel.get_pattern_dashboard(),
            "memory": memory_network.get_memory_dashboard(),
            "liquidity": liquidity_engine.get_liquidity_dashboard(),
            "alpha": alpha_analyzer.get_alpha_dashboard(),
            "mutations": mutation_engine.get_mutation_dashboard(),
        }
    )
    learning_loop.integrate_feedback(
        {"evolution_score": ecosystem_report.ecosystem_health},
        {"accuracy": 0.7, "stability": 0.6, "performance": 0.65},
    )

    cert_data = {
        **orchestrator.get_ecosystem_dashboard()["latest"],
        "learning": learning_loop.get_learning_dashboard(),
    }
    certification = certification_gate.evaluate(cert_data)
    assert certification.verdict in ("GO", "NO-GO")
