# Mission 71 — Stablecoin Macro Rotation

## Module
`doug_os/discovery/stablecoin_rotation.py`

## Summary
Implements `StablecoinMacroRotation` that tracks USDT/USDC supply flows and derives macro rotation signals including pressure index, trend, and alert level.

## Key Components
- **StablecoinFlow**: Dataclass with usdt_supply, usdc_supply, exchange_balance, net_flow, rotation_index.
- **StablecoinAnalysis**: Output with total_supply, usdt_share, usdc_share, exchange_ratio, pressure_index [-1,1], trend (neutral/increasing/decreasing), alert (green/yellow/red).
- **StablecoinMacroRotation**: Rolling window (default 30). `update()` computes shares, pressure (net_flow/total*10 clamped), trend via np.mean of last 5 net_flows, alert from abs(pressure) thresholds (>0.8 red, >0.5 yellow).

## Tests (6 passing)
1. update returns StablecoinAnalysis instance
2. usdt_share + usdc_share ≈ 1.0
3. pressure_index clamped to [-1, 1] even with extreme net_flow
4. alert "red" when net_flow causes |pressure| > 0.8
5. trend "increasing" after 5+ data points with net_flow=5.0
6. to_dict serializes all 8 fields correctly

## Status: PASSED
