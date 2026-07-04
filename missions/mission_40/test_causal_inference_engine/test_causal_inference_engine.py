import pytest
from doug_os.discovery.causal_inference_engine import (
    AdvancedCausalInferenceEngine,
    CausalGraph,
    CausalRelationship,
    CausalInferenceResult,
)


@pytest.fixture
def engine():
    return AdvancedCausalInferenceEngine()


@pytest.fixture
def engine_with_dag(engine):
    variables = ["A", "M", "B", "C"]
    relationships = [
        ("A", "M", 0.7),
        ("M", "B", 0.6),
        ("A", "C", 0.5),
        ("C", "B", 0.4),
    ]
    engine.build_dag(variables, relationships)
    return engine


def test_build_dag_returns_causal_graph(engine):
    variables = ["X", "Y", "Z"]
    relationships = [("X", "Y", 0.8), ("Y", "Z", 0.6)]
    graph = engine.build_dag(variables, relationships)
    assert isinstance(graph, CausalGraph)
    assert "X" in graph.nodes
    assert "Y" in graph.nodes
    assert "Z" in graph.nodes
    assert len(graph.edges) == 2
    assert graph.edges[0].strength == 0.8
    assert graph.edges[1].strength == 0.6


def test_detect_confounders_finds_intermediate_nodes(engine_with_dag):
    confounders = engine_with_dag.detect_confounders("A", "B")
    assert len(confounders) > 0
    assert "M" in confounders or "C" in confounders


def test_detect_confounders_empty_when_no_path(engine):
    engine.build_dag(["X", "Y"], [])
    confounders = engine.detect_confounders("X", "Y")
    assert confounders == []


def test_check_backdoor_true_with_confounders(engine_with_dag):
    assert engine_with_dag.check_backdoor("A", "B") is True


def test_check_backdoor_false_no_confounders(engine):
    engine.build_dag(["X", "Y"], [("X", "Y", 0.5)])
    assert engine.check_backdoor("X", "Y") is False


def test_check_frontdoor_true_with_mediators(engine_with_dag):
    assert engine_with_dag.check_frontdoor("A", "B") is True


def test_check_frontdoor_false_direct_only(engine):
    engine.build_dag(["X", "Y"], [("X", "Y", 0.5)])
    assert engine.check_frontdoor("X", "Y") is False


def test_do_calculus_adjusted_by_confounders(engine_with_dag):
    data = {"direct_effect": 0.5, "conf_M": 0.8, "conf_C": 0.6}
    effect = engine_with_dag.do_calculus("A", "B", data)
    # Should be less than 0.5 due to confounder adjustment
    assert effect < 0.5
    assert effect > 0.0


def test_infer_causality_positive(engine_with_dag):
    data = {
        "direct_effect": 0.5,
        "conf_M": 0.1,
        "conf_C": 0.1,
        "p_value": 0.01,
        "effect_size": 0.6,
    }
    result = engine_with_dag.infer_causality("A", "B", data)
    assert isinstance(result, CausalInferenceResult)
    assert result.is_causal is True
    assert result.confidence > 0.0
    assert result.relationship_type in (CausalRelationship.DIRECT, CausalRelationship.INDIRECT)


def test_infer_causality_negative_high_pvalue(engine_with_dag):
    data = {
        "direct_effect": 0.5,
        "conf_M": 0.1,
        "p_value": 0.9,
        "effect_size": 0.1,
    }
    result = engine_with_dag.infer_causality("A", "B", data)
    assert result.is_causal is False
    assert "Not statistically significant" in result.alternative_explanations


def test_infer_causality_negative_small_effect(engine_with_dag):
    data = {
        "direct_effect": 0.05,
        "p_value": 0.01,
        "effect_size": 0.05,
    }
    result = engine_with_dag.infer_causality("A", "B", data)
    assert result.is_causal is False
    assert "Effect size too small" in result.alternative_explanations


def test_counterfactual_analysis(engine_with_dag):
    data = {"direct_effect": 0.3, "baseline": 100.0, "uncertainty": 0.1}
    intervention = {"effect_multiplier": 2.0}
    cf = engine_with_dag.counterfactual_analysis("A", "B", data, intervention)
    assert "baseline" in cf
    assert "counterfactual" in cf
    assert "difference" in cf
    assert cf["baseline"] == 100.0
    assert cf["counterfactual"] != cf["baseline"]
    assert abs(cf["difference"] - (cf["counterfactual"] - cf["baseline"])) < 1e-9


def test_get_graph_returns_none_before_build(engine):
    assert engine.get_graph() is None


def test_get_graph_returns_graph_after_build(engine):
    engine.build_dag(["A", "B"], [("A", "B", 0.5)])
    assert engine.get_graph() is not None
