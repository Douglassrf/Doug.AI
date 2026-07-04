# MISSION 44 — Impossibility Detector

## Módulo
`doug_os/discovery/impossibility_detector.py`

## O que foi implementado
Firewall lógico-científico que verifica hipóteses em 4 camadas de impossibilidade.
Bloqueia hipóteses que violam princípios fundamentais.

## Classes principais
- `ImpossibilityCheck`: resultado com is_impossible, reason, confidence, violations,
  suggestions, veto
- `ImpossibilityDetector`: detector com métodos:
  - `check()`: verifica hipótese em todas as 4 camadas
  - `_logical_check()`: detecta contradições em pares (increase/decrease, buy/sell, etc.)
  - `_statistical_check()`: verifica variância negativa, correlação > |1|, probabilidade fora de [0,1]
  - `_probabilistic_check()`: soma de probs exclusivas > 1, guaranteed_return > 100%
  - `_known_impossibility_check()`: verifica 5 impossibilidades conhecidas

## Regras de decisão
- `is_impossible = True` quando >= 2 violações
- `veto = True` quando >= 3 violações
- `confidence = 1 - n_violations / (n_violations + 1)`

## Testes
13 testes em `tests/discovery/test_impossibility_detector/test_impossibility_detector.py`
Todos passando.

## Commit
`455a64b` — Missão 44 — Impossibility Detector
