import pytest
from doug_os.discovery.cognitive_pattern_evolution import (
    CognitivePatternEvolution, CognitivePattern,
)


@pytest.fixture
def evo():
    e = CognitivePatternEvolution(population_size=10, seed=42)
    for i in range(5):
        e.create_pattern(
            name=f"pattern_{i}",
            description=f"desc {i}",
            pattern_data={"a": float(i), "b": float(i * 2)},
            confidence=0.5 + i * 0.1,
        )
    return e


def test_create_pattern_returns_pattern(evo):
    p = evo.create_pattern("test", "desc", {"x": 1.0}, 0.7)
    assert isinstance(p, CognitivePattern)
    assert p.id in evo._patterns


def test_evolve_generation_increments_generation(evo):
    assert evo._generation == 0
    evo.evolve_generation()
    assert evo._generation == 1


def test_evolve_produces_new_patterns(evo):
    initial = len(evo._patterns)
    evo.evolve_generation()
    assert len(evo._patterns) >= initial


def test_fitness_calculated_after_evolve(evo):
    evo.evolve_generation()
    for p in evo._patterns.values():
        if p.generation == 0:
            assert p.fitness > 0.0


def test_get_top_patterns_sorted(evo):
    evo.evolve_generation()
    top = evo.get_top_patterns(3)
    assert len(top) <= 3
    fitnesses = [p.fitness for p in top]
    assert fitnesses == sorted(fitnesses, reverse=True)


def test_retire_pattern(evo):
    pid = list(evo._patterns.keys())[0]
    assert evo.retire_pattern(pid) is True
    assert evo._patterns[pid].active is False


def test_retire_nonexistent_returns_false(evo):
    assert evo.retire_pattern("ghost_id") is False


def test_fitness_history_grows(evo):
    evo.evolve_generation()
    evo.evolve_generation()
    assert len(evo._fitness_history) == 2


def test_get_pattern_dashboard(evo):
    evo.evolve_generation()
    dash = evo.get_pattern_dashboard()
    assert "total_patterns" in dash
    assert "avg_fitness" in dash
    assert "fitness_history" in dash


def test_retired_not_in_active_count(evo):
    pid = list(evo._patterns.keys())[0]
    evo.retire_pattern(pid)
    dash = evo.get_pattern_dashboard()
    assert dash["retired_patterns"] >= 1
    assert dash["active_patterns"] < dash["total_patterns"]
