import pytest
from doug_os.discovery.scientific_method.causal_inference import CausalInferenceEngine


@pytest.fixture
def engine():
    return CausalInferenceEngine()


def test_dag_building(engine):
    engine.build_dag(
        variables=["A", "B", "C"],
        relationships=[("A", "B"), ("B", "C")],
    )
    assert "A" in engine._dag
    assert engine._dag.has_edge("A", "B")


def test_confounder_detection(engine):
    engine.build_dag(
        variables=["treatment", "confounder", "outcome"],
        relationships=[
            ("treatment", "confounder"),
            ("treatment", "outcome"),
            ("confounder", "outcome"),
        ],
    )
    confounders = engine.detect_confounders("treatment", "outcome")
    assert "confounder" in confounders


def test_causal_inference_positive(engine):
    engine.build_dag(
        variables=["vol", "mediator", "volume"],
        relationships=[("vol", "mediator"), ("vol", "volume"), ("mediator", "volume")],
    )
    engine.detect_confounders("vol", "volume")
    result = engine.infer_causality(
        "vol", "volume",
        data={"effect_size": 0.4, "p_value": 0.01},
    )
    assert result.is_causal is True
    assert result.confidence > 0.5


def test_causal_inference_negative_high_pvalue(engine):
    engine.build_dag(
        variables=["A", "M", "B"],
        relationships=[("A", "M"), ("A", "B"), ("M", "B")],
    )
    engine.detect_confounders("A", "B")
    result = engine.infer_causality(
        "A", "B",
        data={"effect_size": 0.05, "p_value": 0.5},
    )
    assert result.is_causal is False
    assert len(result.alternative_explanations) > 0
