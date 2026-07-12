"""Teste de integração — Missão 39: Scientific Method Core completo."""
import pytest
from doug_os.discovery.scientific_method.protocol import ScientificProtocol, EvidenceLevel
from doug_os.discovery.scientific_method.hypothesis_validator import HypothesisValidator
from doug_os.discovery.scientific_method.experiment_protocol import ExperimentProtocol, ExperimentDesign
from doug_os.discovery.scientific_method.scientific_score import ScientificScoreCalculator
from doug_os.discovery.scientific_method.causal_inference import CausalInferenceEngine
from doug_os.discovery.scientific_method.dag_builder import DAGBuilder, DAGNode, DAGEdge
from doug_os.discovery.scientific_method.counterfactual import CounterfactualEngine


def test_scientific_method_full_pipeline():
    # 1. Formular protocolo
    protocol = ScientificProtocol(
        hypothesis_id="hyp_m39_001",
        question="Does volatility cause increased trading volume?",
        hypothesis_formulation=(
            "If market volatility increases between sessions, "
            "then trading volume will increase significantly within the same period"
        ),
        null_hypothesis="Volatility has no effect on trading volume",
        alternative_hypothesis="Higher volatility increases trading volume",
        independent_variables=["volatility"],
        dependent_variables=["trading_volume"],
        control_variables=["time_of_day", "market_cap"],
        success_criteria={"effect_size": 0.2, "p_value": 0.05},
        rejection_criteria={"p_value": 0.1},
    )
    assert protocol.is_valid()

    # 2. Validar hipótese
    validator = HypothesisValidator()
    val_result = validator.validate(protocol.hypothesis_formulation)
    assert val_result.valid
    assert val_result.score > 0.5

    # 3. Definir protocolo de experimento
    exp_protocol = ExperimentProtocol(
        scientific_protocol_id=protocol.id,
        design=ExperimentDesign.A_B_TESTING,
        sample_size=500,
        iterations=100,
        confidence_level=0.95,
        primary_metric="trading_volume",
        secondary_metrics=["bid_ask_spread", "order_depth"],
    )
    assert exp_protocol.is_valid()

    # 4. Construir DAG causal
    builder = DAGBuilder()
    for name, ntype in [
        ("volatility", "treatment"),
        ("fear_index", "confounder"),
        ("trading_volume", "outcome"),
    ]:
        builder.add_node(DAGNode(name, node_type=ntype))
    builder.add_edge(DAGEdge("volatility", "fear_index"))
    builder.add_edge(DAGEdge("volatility", "trading_volume"))
    builder.add_edge(DAGEdge("fear_index", "trading_volume"))

    # 5. Inferência causal
    causal_engine = CausalInferenceEngine()
    causal_engine.build_dag(
        variables=["volatility", "fear_index", "trading_volume"],
        relationships=[
            ("volatility", "fear_index"),
            ("volatility", "trading_volume"),
            ("fear_index", "trading_volume"),
        ],
    )
    causal_engine.detect_confounders("volatility", "trading_volume")
    causal_result = causal_engine.infer_causality(
        "volatility", "trading_volume",
        data={"effect_size": 0.45, "p_value": 0.02},
    )
    assert causal_result.is_causal

    # 6. Score científico
    calculator = ScientificScoreCalculator()
    score = calculator.calculate(
        protocol_data=protocol.to_dict(),
        results={
            "effect_size": 0.45,
            "p_value": 0.02,
            "confidence_level": 0.95,
            "sample_size": 500,
            "repetitions": 5,
            "consistency": 0.9,
            "variance": 0.08,
            "stress_tests_passed": 4,
            "sensitivity": 0.85,
            "conditions_tested": 4,
            "novel_combination": True,
            "contribution": "Causal link vol → volume",
        },
    )
    assert score.overall_score > 0.6

    # 7. Análise contrafactual
    cf_engine = CounterfactualEngine()
    cf_result = cf_engine.analyze(
        historical_data={"outcome": 1_000_000.0, "variance": 0.1},
        intervention={"description": "volatility spike +50%", "effect_multiplier": 1.45},
    )
    assert cf_result.expected_outcome > 1_000_000.0
    assert cf_result.confidence > 0.5

    # 8. Promover evidência
    protocol.promote_evidence(EvidenceLevel.CAUSAL)
    assert protocol.evidence_level == EvidenceLevel.CAUSAL
