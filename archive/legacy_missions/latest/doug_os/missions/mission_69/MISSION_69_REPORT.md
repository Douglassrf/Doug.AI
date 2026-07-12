# Mission 69 — Derivatives Gravity Engine

## Module
`doug_os/discovery/derivatives_gravity.py`

## Summary
Implements `DerivativesGravityEngine` that analyzes options/derivatives market data to compute a gravity index reflecting structural market pressure from open interest, gamma, delta, and put/call dynamics.

## Key Components
- **DerivativeData**: Dataclass with open_interest, gamma_exposure, delta_exposure, dealer_delta, options_volume, puts_calls_ratio.
- **GravityIndex**: Output with index [0,1], gravity_score, pressure_score, risk_level (low/medium/high/extreme), components dict.
- **DerivativesGravityEngine**: `analyze()` computes weighted gravity_score (OI 30%, gamma 25%, delta 25%, dealer 10%, vol 10%) and pressure_score ((put_call + gamma_pressure)/2). Index = average of both. Risk levels: >0.8 extreme, >0.6 high, >0.4 medium, else low.

## Tests (6 passing)
1. analyze returns GravityIndex with index in [0,1]
2. Max inputs produce index > 0.8 → risk_level "extreme"
3. Zero inputs produce index ≤ 0.4 → risk_level "low"
4. open_interest=500 → components["open_interest"] ≈ 0.5
5. index = (gravity_score + pressure_score) / 2
6. to_dict serializes all fields including created_at

## Status: PASSED
