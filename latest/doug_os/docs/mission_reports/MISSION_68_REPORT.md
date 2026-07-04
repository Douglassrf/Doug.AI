# Mission 68 — Macro Liquidity Flow Engine

## Module
`doug_os/discovery/macro_liquidity_flow.py`

## Summary
Implements `MacroLiquidityFlowEngine` that ingests `LiquidityData` snapshots and produces `LiquidityScore` objects tracking global crypto liquidity conditions.

## Key Components
- **LiquidityData**: Dataclass holding global_liquidity, central_bank_balance, market_cap, volume_24h, stablecoin_supply, exchange_reserves.
- **LiquidityScore**: Output with score [0,1], pressure_index [-1,1], cycle_phase, trend, alert_level (green/yellow/red), components dict.
- **MacroLiquidityFlowEngine**: Rolling window engine (deque maxlen=30) with methods: `update()`, `_detect_cycle()` (expansion/contraction/neutral via MA5 vs MA10), `_calculate_trend()` (slope over 5 points), `_determine_alert()`, `get_heatmap()`.

## Tests (7 passing)
1. update returns LiquidityScore with score in [0,1]
2. alert_level "red" when all inputs are zero (score < 0.3)
3. alert_level "green" with high-score, low-pressure inputs
4. _detect_cycle returns "expansion" when recent MA > long MA * 1.02
5. _calculate_trend returns "increasing" with 5 ascending data points
6. get_heatmap returns dict with global_liquidity, trend, pressure keys
7. to_dict serializes all LiquidityScore fields correctly

## Status: PASSED
