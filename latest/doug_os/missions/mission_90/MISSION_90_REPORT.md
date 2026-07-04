# Mission 90 — Predictive Macro Engine

## Module
`doug_os/discovery/predictive_macro_engine.py`

## Classes
- `MacroData`: GDP, inflation, unemployment, interest_rate, PMI, consumer_confidence
- `MacroPrediction`: forecasts + regime + confidence
- `PredictiveMacroEngine`: `predict()` builds forecasts from history

## Key Logic
- GDP forecast: rolling mean of last 3 + PMI adjustment
- Inflation forecast: Phillips curve adjustment (unemployment gap)
- Rate forecast: Taylor-rule-inspired adjustment
- Regime: expansion / recession / inflationary / stagnation / stable
- Confidence: consumer confidence + PMI + GDP volatility

## Tests (7 passing)
1. gdp_growth > 2.5 + inflation < 3 → "expansion"
2. gdp_growth < 0 → "recession"
3. inflation > 4 → "inflationary"
4. inflation > interest_rate → rate_forecast > interest_rate
5. 3+ history → gdp_forecast uses mean of last 3
6. High consumer_confidence → confidence_index > 0
7. to_dict serializes all fields

## Commit
`452d77d` — Missao 90 - PREDICTIVE MACRO ENGINE
