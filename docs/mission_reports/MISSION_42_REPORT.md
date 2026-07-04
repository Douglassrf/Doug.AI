# MISSION 42 — Theory Generator

## Módulo
`doug_os/discovery/theory_generator.py`

## O que foi implementado
Gerador automático de teorias científicas baseado em variáveis target e preditoras,
com scoring multidimensional e rastreamento de novidade.

## Classes principais
- `GeneratedTheory`: teoria com hypothesis, mechanism, predictions, assumptions,
  testability_score, novelty_score, plausibility_score
- `TheoryGenerator`: gerador com métodos:
  - `generate_theories()`: gera N teorias com preditores selecionados aleatoriamente
  - `generate_single()`: gera uma teoria determinística (útil para testes)
  - `_calculate_novelty()`: calcula novidade via similaridade Jaccard com teorias existentes
  - `get_theory()`: recupera teoria por ID
  - `list_theories()`: lista todas as teorias geradas

## Destaques
- Seed configurável via `random.Random` para reprodutibilidade
- Novidade decresce automaticamente conforme teorias similares são geradas
- 8 mecanismos e 6 templates de suposições pré-definidos

## Testes
10 testes em `tests/discovery/test_theory_generator/test_theory_generator.py`
Todos passando.

## Commit
`531f563` — Missão 42 — Theory Generator
