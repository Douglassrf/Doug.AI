# Mission 70 — Options Pain Engine

## Module
`doug_os/discovery/options_pain.py`

## Summary
Implements `OptionsPainEngine` that calculates max pain price, gamma walls, and expiration pressure from calls/puts option data.

## Key Components
- **OptionCluster**: Dataclass for individual option position (strike, open_interest, gamma, delta, type).
- **OptionsPainResult**: Output with max_pain_price, current_price, pain_gap, gamma_walls (up to 5 strikes), clusters, expiration_pressure.
- **OptionsPainEngine**: `calculate_pain(calls, puts, current_price)` creates sorted OptionCluster list, finds max OI strike as max_pain, detects top-5 gamma concentration strikes as walls, calculates ATM OI ratio as expiration_pressure.

## Tests (6 passing)
1. calculate_pain returns OptionsPainResult instance
2. max_pain_price = strike with highest aggregated open_interest
3. pain_gap = abs(current_price - max_pain_price)
4. gamma_walls returns up to 5 strikes ordered by descending gamma
5. expiration_pressure = OI in [0.95, 1.05] / total OI
6. to_dict serializes all fields correctly

## Status: PASSED
