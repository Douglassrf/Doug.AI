import pytest
from discovery.compute_cost_optimizer import ComputeCostOptimizer, ComputeCost, CostBudget


def test_record_cost():
    opt = ComputeCostOptimizer()
    cost = opt.record_cost("inference", cpu_cost=5.0, memory_cost=2.0, time_cost_ms=100.0)
    assert cost.operation == "inference"
    assert cost.cpu_cost == 5.0


def test_set_and_check_budget_ok():
    opt = ComputeCostOptimizer()
    opt.set_budget("inference", cpu=100.0, memory=50.0, time_ms=5000.0)
    opt.record_cost("inference", cpu_cost=10.0, memory_cost=5.0, time_cost_ms=100.0)
    assert opt.check_budget("inference") is True


def test_check_budget_exceeded():
    opt = ComputeCostOptimizer()
    opt.set_budget("inference", cpu=10.0, memory=10.0, time_ms=100.0)
    # Exhaust time budget completely
    opt.record_cost("inference", cpu_cost=2.0, memory_cost=2.0, time_cost_ms=150.0)
    assert opt.check_budget("inference") is False


def test_check_budget_unknown_operation():
    opt = ComputeCostOptimizer()
    assert opt.check_budget("unknown") is True


def test_enable_low_cost_mode():
    opt = ComputeCostOptimizer()
    opt.enable_low_cost_mode()
    assert opt._low_cost_mode is True


def test_disable_low_cost_mode():
    opt = ComputeCostOptimizer()
    opt.enable_low_cost_mode()
    opt.disable_low_cost_mode()
    assert opt._low_cost_mode is False


def test_get_cost_metrics():
    opt = ComputeCostOptimizer()
    opt.record_cost("train", cpu_cost=20.0, time_cost_ms=500.0)
    opt.record_cost("train", cpu_cost=30.0, time_cost_ms=700.0)
    m = opt.get_cost_metrics("train")
    assert m["count"] == 2
    assert m["total_cpu"] == pytest.approx(50.0)


def test_get_cost_dashboard():
    opt = ComputeCostOptimizer()
    opt.set_budget("op", cpu=100.0, memory=100.0, time_ms=1000.0)
    opt.record_cost("op", cpu_cost=5.0)
    dash = opt.get_cost_dashboard()
    assert "total_operations" in dash
    assert "budgets" in dash


def test_budget_remaining():
    opt = ComputeCostOptimizer()
    opt.set_budget("op", cpu=100.0, memory=50.0, time_ms=1000.0)
    opt.record_cost("op", cpu_cost=30.0, memory_cost=10.0)
    b = opt._budgets["op"]
    assert b.remaining_cpu == pytest.approx(70.0)
    assert b.remaining_memory == pytest.approx(40.0)
