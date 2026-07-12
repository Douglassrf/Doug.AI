"""Testes básicos — Missões 288-297 (Fase XIX Meta-Cognitive Trading Intelligence)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_288_meta_cognition_engine import MetaCognitionEngine, CognitiveAudit
from mission_289_adaptive_bias_detector import AdaptiveBiasDetector, BiasReport
from mission_290_uncertainty_quantification_engine import (
    UncertaintyQuantificationEngine,
    UncertaintyProfile,
)
from mission_291_regime_adaptation_supervisor import (
    RegimeAdaptationSupervisor,
    RegimeTransition,
)
from mission_292_signal_reliability_engine import SignalReliabilityEngine, SignalReliability
from mission_293_strategic_opportunity_optimizer import (
    StrategicOpportunityOptimizer,
    StrategicOpportunity,
)
from mission_294_cognitive_decision_orchestrator import (
    CognitiveDecisionOrchestrator,
    CognitiveDecisionPlan,
)
from mission_295_meta_learning_feedback_engine import (
    MetaLearningFeedbackEngine,
    MetaLearningFeedback,
)
from mission_296_cognitive_risk_balancer import CognitiveRiskBalancer, CognitiveRiskBalance
from mission_297_meta_cognitive_trading_intelligence_hub import (
    MetaCognitiveTradingIntelligenceHub,
    MetaCognitiveTradingSnapshot,
)


@pytest.mark.parametrize(
    "cls",
    [
        CognitiveAudit,
        BiasReport,
        UncertaintyProfile,
        RegimeTransition,
        SignalReliability,
        StrategicOpportunity,
        CognitiveDecisionPlan,
        MetaLearningFeedback,
        CognitiveRiskBalance,
        MetaCognitiveTradingSnapshot,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_288_meta_cognition_engine():
    engine = MetaCognitionEngine()
    chain = [
        {"type": "premise", "premise": "trend increase"},
        {"type": "premise", "premise": "volume increase"},
        {"type": "conclusion", "conclusion": "buy"},
    ]
    audit = engine.audit_decision(
        "dec_001",
        chain,
        confidence=0.8,
        evidence={"quality": 0.9, "sample_size": 50},
    )
    assert audit.decision_id == "dec_001"
    assert engine.get_meta_dashboard()["total_audits"] == 1


def test_mission_289_adaptive_bias_detector():
    detector = AdaptiveBiasDetector()
    reports = detector.detect_biases(
        {
            "recent_weight": 0.85,
            "overfit_score": 0.95,
            "confirmation_ratio": 0.7,
        }
    )
    assert len(reports) >= 2
    assert any(r.severity == "critical" for r in reports)
    assert detector.get_bias_dashboard()["total_biases"] == len(reports)


def test_mission_290_uncertainty_quantification_engine():
    engine = UncertaintyQuantificationEngine()
    predictions = [0.01, 0.015, 0.012, 0.018, 0.011, 0.014]
    profile = engine.quantify_uncertainty("pred_001", predictions, [0.013, 0.014])
    assert profile.prediction_id == "pred_001"
    assert profile.reliability >= 0
    assert engine.get_uncertainty_dashboard()["total_profiles"] == 1


def test_mission_291_regime_adaptation_supervisor():
    supervisor = RegimeAdaptationSupervisor()
    supervisor.monitor_regime("trending_bull", {"volatility": 0.2})
    transition = supervisor.monitor_regime(
        "ranging",
        {"volatility": 0.35, "data_quality": 0.8},
    )
    assert transition.adaptation_needed is True
    assert supervisor.get_supervisor_dashboard()["total_transitions"] == 1


def test_mission_292_signal_reliability_engine():
    engine = SignalReliabilityEngine()
    reliability = engine.evaluate_signal("sig_001", 0.8, 0.75, 0.7, 0.85)
    assert reliability.signal_id == "sig_001"
    assert reliability.certification_status == "certified"
    assert engine.get_signal_dashboard()["total_signals"] == 1


def test_mission_293_strategic_opportunity_optimizer():
    optimizer = StrategicOpportunityOptimizer()
    candidates = [
        {"asset": "EURUSD", "direction": "long", "expected_return": 0.02, "risk": 0.2, "confidence": 0.8},
        {"asset": "BTCUSD", "direction": "long", "expected_return": 0.05, "risk": 0.4, "confidence": 0.7},
    ]
    opportunities = optimizer.optimize(candidates)
    assert len(opportunities) == 2
    assert opportunities[0].priority_rank == 1
    assert optimizer.get_optimizer_dashboard()["total_opportunities"] == 2


def test_mission_294_cognitive_decision_orchestrator():
    orchestrator = CognitiveDecisionOrchestrator()
    plan = orchestrator.orchestrate(
        "EURUSD",
        "buy",
        {
            "meta_audit_score": 0.8,
            "bias_clear": True,
            "uncertainty_ok": True,
            "signal_certified": True,
        },
    )
    assert plan.asset == "EURUSD"
    assert plan.status == "approved"
    assert orchestrator.get_orchestrator_dashboard()["total_plans"] == 1


def test_mission_295_meta_learning_feedback_engine():
    engine = MetaLearningFeedbackEngine()
    feedback = engine.record_feedback("dec_001", predicted_outcome=0.8, actual_outcome=0.75)
    assert feedback.decision_id == "dec_001"
    assert engine.get_learning_dashboard()["feedback_count"] == 1


def test_mission_296_cognitive_risk_balancer():
    balancer = CognitiveRiskBalancer()
    balance = balancer.balance(
        "portfolio_1",
        base_risk=0.5,
        cognitive_factors={"bias_score": 0.2, "uncertainty_score": 0.3, "reliability_score": 0.7},
    )
    assert balance.portfolio_id == "portfolio_1"
    assert balancer.get_risk_dashboard()["balances"] == 1


def test_mission_297_meta_cognitive_trading_intelligence_hub():
    hub = MetaCognitiveTradingIntelligenceHub()
    snapshot = hub.aggregate({"meta_cognition": {"total_audits": 1}, "bias": {"total_biases": 2}})
    assert snapshot.meta_cognition["total_audits"] == 1
    assert hub.get_hub_dashboard()["snapshots"] == 1
