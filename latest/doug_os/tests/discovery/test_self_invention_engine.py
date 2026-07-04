import pytest
from doug_os.discovery.self_invention_engine import CandidateIndicator, SelfInventionEngine


BASE_FORMULAS = ["RSI(14)", "MACD(12,26)", "EMA(20)"]


def test_generate_candidates_count():
    engine = SelfInventionEngine(seed=42)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=8)
    assert len(candidates) == 8


def test_generate_candidates_formula_not_empty():
    engine = SelfInventionEngine(seed=42)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=5)
    for c in candidates:
        assert c.formula != "", f"Candidate {c.id} has empty formula"


def test_evaluate_candidates_sets_scores():
    engine = SelfInventionEngine(seed=0)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=5)
    evaluated = engine.evaluate_candidates(candidates, baseline_score=0.5, market_data={})
    for c in evaluated:
        assert c.baseline_score == 0.5
        assert 0.0 <= c.current_score <= 1.0
        assert c.improvement == pytest.approx(c.current_score - c.baseline_score, abs=1e-9)


def test_evaluate_candidates_inactive_when_negative_improvement():
    engine = SelfInventionEngine(seed=1)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=10)
    # Force baseline high so some will be negative
    evaluated = engine.evaluate_candidates(candidates, baseline_score=0.9, market_data={})
    for c in evaluated:
        if c.improvement < 0:
            assert c.is_active is False


def test_evolve_generation_creates_children_with_higher_generation():
    engine = SelfInventionEngine(seed=7)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=6)
    engine.evaluate_candidates(candidates, baseline_score=0.3, market_data={})
    new_gen = engine.evolve_generation()
    assert len(new_gen) > 0
    for child in new_gen:
        assert child.generation > 0
        assert child.parent_id is not None


def test_get_best_indicators_sorted_desc():
    engine = SelfInventionEngine(seed=99)
    candidates = engine.generate_candidates(BASE_FORMULAS, n_candidates=10)
    engine.evaluate_candidates(candidates, baseline_score=0.4, market_data={})
    best = engine.get_best_indicators(n=5)
    improvements = [b.improvement for b in best]
    assert improvements == sorted(improvements, reverse=True)


def test_to_dict_serialization():
    ind = CandidateIndicator(name="TEST", formula="RSI(14)", parameters={"period": 14})
    d = ind.to_dict()
    assert d["name"] == "TEST"
    assert d["formula"] == "RSI(14)"
    assert "created_at" in d
    assert "last_updated" in d
    assert isinstance(d["is_active"], bool)
