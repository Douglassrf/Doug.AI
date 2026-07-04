import pytest
from discovery.defensive_mode_controller import (
    DefensiveModeController, SCENARIO_STRESS, SCENARIO_LATERAL,
    SCENARIO_TRENDING, SCENARIO_NORMAL,
)


def test_detect_stress_vix():
    c = DefensiveModeController()
    s = c.detect_scenario({"vix": 35.0, "range_pct": 1.0, "momentum_sigma": 0.0, "volatility": 0.01})
    assert s.name == SCENARIO_STRESS


def test_detect_stress_volatility():
    c = DefensiveModeController()
    s = c.detect_scenario({"vix": 5.0, "volatility": 0.05})
    assert s.name == SCENARIO_STRESS


def test_detect_lateral():
    c = DefensiveModeController()
    s = c.detect_scenario({"vix": 10.0, "range_pct": 0.003, "momentum_sigma": 0.5, "volatility": 0.01})
    assert s.name == SCENARIO_LATERAL


def test_detect_trending():
    c = DefensiveModeController()
    s = c.detect_scenario({"vix": 15.0, "range_pct": 1.0, "momentum_sigma": 2.5, "volatility": 0.02})
    assert s.name == SCENARIO_TRENDING


def test_detect_normal():
    c = DefensiveModeController()
    s = c.detect_scenario({"vix": 15.0, "range_pct": 1.0, "momentum_sigma": 0.5, "volatility": 0.01})
    assert s.name == SCENARIO_NORMAL


def test_apply_stress_config():
    c = DefensiveModeController()
    cfg = c.apply({"vix": 40.0, "range_pct": 1.0, "momentum_sigma": 0.0, "volatility": 0.02})
    assert cfg.scenario == SCENARIO_STRESS
    assert cfg.stop_loss_pct == 0.5
    assert cfg.max_position_size == 0.25
    assert cfg.active_agents == ["RiskAgent"]


def test_apply_trending_config():
    c = DefensiveModeController()
    cfg = c.apply({"vix": 15.0, "range_pct": 1.0, "momentum_sigma": 3.0, "volatility": 0.02})
    assert cfg.scenario == SCENARIO_TRENDING
    assert cfg.max_position_size == 1.0


def test_is_agent_active_stress():
    c = DefensiveModeController()
    c.apply({"vix": 40.0, "volatility": 0.05})
    assert c.is_agent_active("RiskAgent") is True
    assert c.is_agent_active("MarketAgent") is False


def test_custom_config():
    c = DefensiveModeController()
    c.register_custom_config("CUSTOM", 0.3, 0.10, ["RiskAgent"], 1, "my config")
    cfg = c.apply_scenario("CUSTOM")
    assert cfg.stop_loss_pct == 0.3
    assert cfg.max_position_size == 0.10


def test_get_stats():
    c = DefensiveModeController()
    c.apply({"vix": 5.0, "range_pct": 1.0, "momentum_sigma": 0.0, "volatility": 0.01})
    c.apply({"vix": 40.0, "range_pct": 1.0, "momentum_sigma": 0.0, "volatility": 0.01})
    stats = c.get_stats()
    assert stats["total_switches"] == 2
    assert "by_scenario" in stats
