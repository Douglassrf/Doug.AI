# Missão 39 — Scientific Method Core

## Objetivo
Implementar método científico formal como camada de validação de descobertas do DOUG OS, garantindo que nenhuma hipótese seja aceita sem evidência rigorosa.

## Ações executadas

### Módulos criados (`discovery/scientific_method/`)
| Arquivo | Responsabilidade |
|---|---|
| `protocol.py` | `ScientificProtocol` + `EvidenceLevel` (ordenação inteira) + `ScientificStatus` |
| `hypothesis_validator.py` | Validação por falsificabilidade, testabilidade e especificidade |
| `experiment_protocol.py` | `ExperimentProtocol` com 8 designs (A/B, Monte Carlo, Factorial, etc.) |
| `scientific_score.py` | `ScientificScoreCalculator` — score ponderado em 5 dimensões |
| `causal_inference.py` | `CausalInferenceEngine` — DAG + critério backdoor (correlação ≠ causalidade) |
| `dag_builder.py` | `DAGBuilder` — construção de DAGs com validação de acyclicidade em tempo real |
| `counterfactual.py` | `CounterfactualEngine` — análise "e se" sobre dados históricos |

### Correções aplicadas ao spec original
- `EvidenceLevel` com valores inteiros (1–6) em vez de strings — permite comparação ordinal em `promote_evidence()`
- `field(default_factory=list)` adicionado onde faltava o import em `ScientificScore`
- Algoritmo `detect_confounders()` corrigido: detecta nós em caminhos indiretos (len > 2), não apenas nós repetidos em múltiplos caminhos

## Testes
- **34 testes, 34 passando, 0 falhas**
- Cobertura: protocol, validator, experiment, score, causal, dag, counterfactual, integração end-to-end

## Resultado
✅ 34/34 testes passando  
✅ Commit: `8f14dd5`  
✅ Integração completa via teste de pipeline (volatilidade → volume causal)  
✅ Arquivado em `missions/mission_39/`
