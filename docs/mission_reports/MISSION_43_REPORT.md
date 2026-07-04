# MISSION 43 — Theory Graveyard

## Módulo
`doug_os/discovery/theory_graveyard.py`

## O que foi implementado
Repositório de teorias falhas com análise de padrões, detecção de duplicatas
via hash SHA-256 e busca por similaridade Jaccard.

## Classes principais
- `BuriedTheory`: teoria enterrada com hypothesis, failure_reason, failure_category,
  similarity_hash (SHA-256 16 chars), burial_depth, lessons_learned, related_theories
- `TheoryGraveyard`: repositório com métodos:
  - `bury_theory()`: enterra teoria, classifica falha, gera hash e lições
  - `search_similar()`: busca por similaridade Jaccard com threshold customizável
  - `check_duplicate()`: verifica se hipótese idêntica já foi enterrada
  - `get_failure_patterns()`: retorna contagem por categoria de falha
  - `exhume()`: recupera teoria enterrada por ID
  - `list_buried()`: lista todas as teorias

## Destaques
- 5 categorias de falha: statistical, logical, empirical, causal, theoretical
- burial_depth aumenta para hipóteses repetidas
- Hash é normalizado (ordenado e lowercased) para detecção robusta

## Testes
12 testes em `tests/discovery/test_theory_graveyard/test_theory_graveyard.py`
Todos passando.

## Commit
`1fe8167` — Missão 43 — Theory Graveyard
