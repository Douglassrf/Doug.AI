# MISSION 41 — Monte Carlo Adaptive Lab

## Módulo
`doug_os/discovery/monte_carlo_lab.py`

## O que foi implementado
Laboratório Monte Carlo adaptativo com convergência automática, bootstrap
estatístico e stress test em múltiplos cenários.

## Classes principais
- `MonteCarloResult`: resultado completo com mean, median, std, CIs (90/95/99),
  bootstrap_estimates, stress_results, robustness_score, variance_score,
  failure_probability
- `MonteCarloAdaptiveLab`: laboratório com métodos:
  - `run_simulation()`: executa com convergência adaptativa
  - `_bootstrap()`: 500 amostras bootstrap
  - `_stress_test()`: 6 cenários (normal, high_volatility, extreme, low_liquidity, crash, recovery)
  - `get_result()`: recupera resultado por ID

## Destaques
- Convergência para antes do limite de iterações quando modelo estabiliza
- Seed configurável para reprodutibilidade
- Threshold de falha customizável por parâmetro

## Testes
9 testes em `tests/discovery/test_monte_carlo_lab/test_monte_carlo_lab.py`
Todos passando.

## Commit
`651203b` — Missão 41 — Monte Carlo Adaptive Lab
