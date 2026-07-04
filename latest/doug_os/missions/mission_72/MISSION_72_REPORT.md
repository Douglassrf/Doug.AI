# Mission 72 — Energy Cost Model BTC

## Module
`doug_os/discovery/energy_cost_btc.py`

## Summary
Implements `EnergyCostModelBTC` that estimates Bitcoin mining production cost from hash rate, difficulty, and electricity price, and derives miner capitulation index, hash rate trend, and difficulty phase.

## Key Components
- **MiningMetrics**: Dataclass with hash_rate (EH/s), difficulty, block_time, electricity_cost ($/kWh), miner_revenue.
- **EnergyCostResult**: Output with production_cost, market_price, cost_gap, miner_capitulation_index [0,1], hash_rate_trend (stable/increasing/decreasing), difficulty_phase (normal/increasing/decreasing).
- **EnergyCostModelBTC**: `_estimate_production_cost()` uses 30 J/TH efficiency, computes energy cost per second and BTC earned per second from difficulty. `_calculate_capitulation()` = max(-profit_margin/2, 0). Trends use 5-point slope for hash rate and 3-point avg change for difficulty.

## Tests (7 passing)
1. analyze returns EnergyCostResult instance
2. hash_rate=0 → production_cost=0
3. electricity_cost=0 → production_cost=0
4. market_price > production_cost → miner_capitulation_index = 0
5. market_price << production_cost → capitulation > 0
6. 5 ascending hash_rate points → hash_rate_trend "increasing"
7. 3 ascending difficulty points → difficulty_phase "increasing"
8. to_dict serializes all 7 fields correctly

## Status: PASSED
