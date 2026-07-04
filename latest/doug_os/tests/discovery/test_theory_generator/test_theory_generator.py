import pytest
from doug_os.discovery.theory_generator import TheoryGenerator, GeneratedTheory


@pytest.fixture
def generator():
    return TheoryGenerator(seed=42)


def test_generate_theories_returns_correct_count(generator):
    theories = generator.generate_theories(
        target="revenue", predictors=["price", "volume", "demand"], n=3
    )
    assert len(theories) == 3
    assert all(isinstance(t, GeneratedTheory) for t in theories)


def test_each_theory_has_non_empty_hypothesis(generator):
    theories = generator.generate_theories(
        target="growth", predictors=["investment", "innovation", "market_size"], n=5
    )
    for t in theories:
        assert t.hypothesis != ""
        assert "growth" in t.hypothesis


def test_testability_score_between_0_and_1(generator):
    theories = generator.generate_theories(
        target="profit", predictors=["cost", "revenue", "margin"], n=4
    )
    for t in theories:
        assert 0.0 <= t.testability_score <= 1.0


def test_novelty_score_between_0_and_1(generator):
    theories = generator.generate_theories(
        target="efficiency", predictors=["process", "automation", "skill"], n=4
    )
    for t in theories:
        assert 0.0 <= t.novelty_score <= 1.0


def test_generate_single_returns_theory(generator):
    theory = generator.generate_single(
        target="output", predictors=["input", "throughput", "quality"]
    )
    assert isinstance(theory, GeneratedTheory)
    assert "output" in theory.hypothesis
    assert theory.target == "output"
    assert len(theory.predictors) >= 1


def test_get_theory_by_id(generator):
    theory = generator.generate_single(
        target="sales", predictors=["marketing", "price"]
    )
    fetched = generator.get_theory(theory.id)
    assert fetched is theory


def test_get_theory_missing_returns_none(generator):
    assert generator.get_theory("nonexistent_id") is None


def test_theories_have_predictions(generator):
    theories = generator.generate_theories(
        target="performance", predictors=["training", "experience"], n=2
    )
    for t in theories:
        assert len(t.predictions) > 0


def test_theories_have_assumptions(generator):
    theories = generator.generate_theories(
        target="risk", predictors=["volatility", "exposure"], n=2
    )
    for t in theories:
        assert len(t.assumptions) > 0


def test_novelty_decreases_with_similar_theories(generator):
    # First theory should have high novelty (no prior theories)
    t1 = generator.generate_single(target="X", predictors=["A", "B"])
    # Generate many with same target — novelty should generally decrease
    theories = generator.generate_theories(target="X", predictors=["A", "B"], n=5)
    # At least some should have novelty < 1.0
    novelties = [t.novelty_score for t in theories]
    assert any(n < 1.0 for n in novelties)
