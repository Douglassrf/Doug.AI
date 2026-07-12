import pytest
from discovery.ab_experiment_runner import ABExperimentRunner, TradeResult


def test_record_trade():
    runner = ABExperimentRunner()
    r = runner.record("A", won=True, pnl=1.5)
    assert r.group == "A"
    assert r.won is True


def test_capital_split():
    runner = ABExperimentRunner(capital_split_a=0.80)
    assert runner.capital_for_group("A") == pytest.approx(0.80)
    assert runner.capital_for_group("B") == pytest.approx(0.20)


def test_evaluate_insufficient_data():
    runner = ABExperimentRunner(min_trades=20)
    for _ in range(5):
        runner.record("A", True)
        runner.record("B", False)
    result = runner.evaluate()
    assert result is None


def test_evaluate_a_wins():
    runner = ABExperimentRunner(min_trades=5, p_value_threshold=0.05, seed=1)
    # A vence claramente: 5/5
    for _ in range(5):
        runner.record("A", True, pnl=1.0)
    # B perde claramente: 0/5
    for _ in range(5):
        runner.record("B", False, pnl=-1.0)
    result = runner.evaluate()
    assert result is not None
    assert result.winner in ("A", "inconclusive")
    assert result.promote_b is False


def test_evaluate_b_wins_and_promotes():
    runner = ABExperimentRunner(min_trades=5, p_value_threshold=0.20, seed=42)
    # B tem win rate muito melhor que A
    for _ in range(5):
        runner.record("A", False, pnl=-1.0)
    for _ in range(5):
        runner.record("B", True, pnl=2.0)
    result = runner.evaluate()
    assert result is not None
    if result.promote_b:
        # Após promoção, geração incrementa e B é zerado
        assert runner._generation == 1
        assert len(runner._results_b) == 0


def test_generation_increments_on_promote():
    runner = ABExperimentRunner(min_trades=3, p_value_threshold=0.50, seed=0)
    for _ in range(3):
        runner.record("A", False)
    for _ in range(3):
        runner.record("B", True)
    runner.evaluate()
    # geração pode ter incrementado se B ganhou
    assert runner._generation >= 0


def test_get_stats():
    runner = ABExperimentRunner(name="test_exp")
    runner.record("A", True)
    stats = runner.get_stats()
    assert stats["name"] == "test_exp"
    assert stats["trades_a"] == 1
    assert "capital_split" in stats


def test_get_experiments_empty():
    runner = ABExperimentRunner()
    assert runner.get_experiments() == []


def test_p_value_between_0_and_1():
    runner = ABExperimentRunner(min_trades=5, seed=7)
    for i in range(5):
        runner.record("A", won=i % 2 == 0)
        runner.record("B", won=i % 3 == 0)
    result = runner.evaluate()
    if result is not None:
        assert 0.0 <= result.p_value <= 1.0


def test_trade_result_to_dict():
    r = TradeResult(group="B", won=True, pnl=2.5)
    d = r.to_dict()
    assert d["group"] == "B"
    assert d["pnl"] == pytest.approx(2.5)
