import pytest
from doug_os.discovery.unified_multi_asset_brain import UnifiedView, UnifiedMultiAssetBrain


def test_integrate_empty_data_regime_not_crisis():
    brain = UnifiedMultiAssetBrain()
    result = brain.integrate({})
    assert result.regime != "crisis"


def test_high_scores_asset_above_threshold():
    brain = UnifiedMultiAssetBrain()
    data = {"crypto": {"momentum": 0.9, "volatility": 0.1, "volume": 0.9}}
    result = brain.integrate(data)
    assert result.asset_scores["crypto"] > 0.7


def test_high_risk_score_gives_crisis_or_high_risk():
    brain = UnifiedMultiAssetBrain()
    # All low-score assets create high risk
    data = {ac: {"momentum": 0.0, "volatility": 1.0, "volume": 0.0}
            for ac in ["crypto", "forex", "commodity", "bond", "equity", "stablecoin"]}
    result = brain.integrate(data)
    assert result.regime in ("crisis", "high_risk")


def test_low_risk_score_gives_low_risk_regime():
    brain = UnifiedMultiAssetBrain()
    # All high-score assets: low risk
    data = {ac: {"momentum": 1.0, "volatility": 0.0, "volume": 1.0}
            for ac in ["crypto", "forex", "commodity", "bond", "equity", "stablecoin"]}
    result = brain.integrate(data)
    assert result.regime == "low_risk"


def test_correlations_diagonal_is_one():
    brain = UnifiedMultiAssetBrain()
    result = brain.integrate({})
    for ac in brain._ASSET_CLASSES:
        assert result.correlations[ac][ac] == 1.0


def test_recommendation_changes_with_regime():
    brain = UnifiedMultiAssetBrain()
    # Crisis regime
    crisis_data = {ac: {"momentum": 0.0, "volatility": 1.0, "volume": 0.0}
                   for ac in ["crypto", "forex", "commodity", "bond", "equity", "stablecoin"]}
    crisis_result = brain.integrate(crisis_data)
    # Low risk regime
    low_data = {ac: {"momentum": 1.0, "volatility": 0.0, "volume": 1.0}
                for ac in ["crypto", "forex", "commodity", "bond", "equity", "stablecoin"]}
    low_result = brain.integrate(low_data)
    assert crisis_result.recommendation != low_result.recommendation


def test_to_dict_serializes_all_fields():
    brain = UnifiedMultiAssetBrain()
    result = brain.integrate({"equity": {"momentum": 0.6, "volatility": 0.3, "volume": 0.5}})
    d = result.to_dict()
    expected_keys = {
        "timestamp", "global_risk_score", "liquidity_score", "regime",
        "asset_scores", "correlations", "recommendation", "confidence",
    }
    assert expected_keys == set(d.keys())
    assert isinstance(d["asset_scores"], dict)
    assert isinstance(d["correlations"], dict)
    assert isinstance(d["timestamp"], str)
