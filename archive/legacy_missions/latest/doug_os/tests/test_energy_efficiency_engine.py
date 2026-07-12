import pytest
from discovery.energy_efficiency_engine import EnergyEfficiencyEngine, EnergyProfile


def test_measure_idle():
    eng = EnergyEfficiencyEngine(idle_threshold=30.0)
    profile = eng.measure_energy(cpu_percent=10.0, memory_percent=20.0)
    assert profile.workload_pattern == "idle"
    assert eng._idle_mode is True


def test_measure_heavy():
    eng = EnergyEfficiencyEngine(heavy_threshold=60.0)
    profile = eng.measure_energy(cpu_percent=80.0, memory_percent=50.0)
    assert profile.workload_pattern == "heavy"
    assert eng._heavy_task_window is True


def test_measure_normal():
    eng = EnergyEfficiencyEngine(idle_threshold=20.0, heavy_threshold=70.0)
    profile = eng.measure_energy(cpu_percent=40.0, memory_percent=30.0)
    assert profile.workload_pattern == "normal"


def test_energy_calculation():
    eng = EnergyEfficiencyEngine()
    profile = eng.measure_energy(cpu_percent=100.0, memory_percent=100.0)
    assert profile.cpu_energy == pytest.approx(50.0)
    assert profile.memory_energy == pytest.approx(20.0)
    assert profile.total_energy == pytest.approx(70.0)


def test_efficiency_score_zero_load():
    eng = EnergyEfficiencyEngine()
    profile = eng.measure_energy(cpu_percent=0.0, memory_percent=0.0)
    assert profile.efficiency_score == pytest.approx(1.0)


def test_schedule_workload_idle():
    eng = EnergyEfficiencyEngine(idle_threshold=50.0)
    eng.measure_energy(cpu_percent=10.0, memory_percent=5.0)
    result = eng.schedule_workload("background")
    assert result["scheduled"] is True
    assert result["efficiency_impact"] >= 0.8


def test_schedule_workload_heavy():
    eng = EnergyEfficiencyEngine(heavy_threshold=60.0)
    eng.measure_energy(cpu_percent=80.0, memory_percent=50.0)
    result = eng.schedule_workload("heavy")
    assert result["scheduled"] is True


def test_get_efficiency_metrics_empty():
    eng = EnergyEfficiencyEngine()
    m = eng.get_efficiency_metrics()
    assert m == {"status": "no_data"}


def test_get_efficiency_metrics():
    eng = EnergyEfficiencyEngine()
    eng.measure_energy(cpu_percent=20.0, memory_percent=30.0)
    eng.measure_energy(cpu_percent=10.0, memory_percent=10.0)
    m = eng.get_efficiency_metrics()
    assert "avg_efficiency" in m
    assert 0.0 <= m["avg_efficiency"] <= 1.0


def test_get_energy_dashboard():
    eng = EnergyEfficiencyEngine()
    eng.measure_energy(cpu_percent=30.0, memory_percent=20.0)
    dash = eng.get_energy_dashboard()
    assert "current_profile" in dash
    assert dash["current_profile"] is not None
