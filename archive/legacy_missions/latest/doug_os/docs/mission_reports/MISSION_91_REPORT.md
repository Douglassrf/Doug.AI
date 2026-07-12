# Mission 91 — Unified Multi Asset Brain

## Module
`doug_os/discovery/unified_multi_asset_brain.py`

## Classes
- `UnifiedView`: dataclass with global_risk_score, liquidity, regime, asset_scores, correlations
- `UnifiedMultiAssetBrain`: `integrate()` processes multi-asset market_data dict

## Key Logic
- Asset score = momentum*0.4 + (1-volatility)*0.3 + volume*0.3
- Correlations: diagonal=1.0, cross-asset=0.3 (deterministic, no np.random)
- Global risk = mean(1-score) + correlation penalty
- Regime: crisis / high_risk / low_risk / {asset}_dominant / neutral
- Confidence based on score std deviation

## Tests (7 passing)
1. Empty data → regime != "crisis"
2. momentum=0.9, volatility=0.1, volume=0.9 → asset_score > 0.7
3. All low scores → regime in ("crisis", "high_risk")
4. All high scores → regime == "low_risk"
5. Diagonal correlations == 1.0
6. Recommendation differs between crisis and low_risk
7. to_dict serializes all fields

## Commit
`8135ace` — Missao 91 - UNIFIED MULTI ASSET BRAIN
