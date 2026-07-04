import pytest
from datetime import datetime, timezone
from doug_os.discovery.portfolio_intelligence import Position, PortfolioIntelligence, PortfolioIntelligenceLayer


def make_position(asset_id="A", asset_class="equity", value=100.0):
    return Position(asset_id=asset_id, asset_name=asset_id, asset_class=asset_class, value=value)


def test_empty_positions_returns_concentration_risk_one():
    layer = PortfolioIntelligenceLayer()
    result = layer.analyze([])
    assert result.concentration_risk == 1.0
    assert result.diversification_score == 0.0


def test_single_position_high_concentration():
    layer = PortfolioIntelligenceLayer()
    pos = make_position(value=1000.0)
    result = layer.analyze([pos])
    assert result.concentration_risk >= 1.0
    assert result.diversification_score == 0.0


def test_four_equal_positions_high_diversification():
    layer = PortfolioIntelligenceLayer()
    positions = [make_position(asset_id=str(i), value=250.0) for i in range(4)]
    result = layer.analyze(positions)
    assert result.diversification_score > 0.9


def test_weights_sum_to_one():
    layer = PortfolioIntelligenceLayer()
    positions = [
        make_position("A", value=300.0),
        make_position("B", value=400.0),
        make_position("C", value=300.0),
    ]
    layer.analyze(positions)
    total_weight = sum(p.weight for p in positions)
    assert abs(total_weight - 1.0) < 1e-9


def test_stress_score_higher_for_crypto_than_bond():
    layer = PortfolioIntelligenceLayer()
    crypto_positions = [make_position(asset_id="C", asset_class="crypto", value=1000.0)]
    bond_positions = [make_position(asset_id="B", asset_class="bond", value=1000.0)]
    crypto_result = layer.analyze(crypto_positions)
    bond_result = layer.analyze(bond_positions)
    assert crypto_result.stress_score > bond_result.stress_score


def test_entropy_positive_with_multiple_positions():
    layer = PortfolioIntelligenceLayer()
    positions = [make_position(asset_id=str(i), value=100.0 + i * 50) for i in range(4)]
    result = layer.analyze(positions)
    assert result.entropy > 0


def test_to_dict_serializes_correctly():
    layer = PortfolioIntelligenceLayer()
    positions = [make_position("X", value=500.0), make_position("Y", value=500.0)]
    result = layer.analyze(positions)
    d = result.to_dict()
    expected_keys = {
        "total_value", "diversification_score", "concentration_risk",
        "entropy", "correlation_risk", "stress_score", "recommendations", "created_at",
    }
    assert expected_keys == set(d.keys())
    assert d["total_value"] == 1000.0
    assert isinstance(d["recommendations"], list)
    assert isinstance(d["created_at"], str)
