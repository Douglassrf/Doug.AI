# Metodologia Professor DogEye — 100 pares rotativos

## Estrutura

| Dimensao | Valor |
|----------|-------|
| Pares Deriv | **100 todo dia** |
| Pares Binance | **100 todo dia** |
| Amostras | **5 por par** (~500/exchange, ~1000/dia) |
| Camadas | **10 layers** (L1 Fundacao -> L10 Omega) |
| Missoes | **331** catalogadas, ~33 por camada |
| Revisao | **Antes** de cada sessao: erros anteriores (memoria) |

## Fluxo por sessao

1. **REVISAO** — professor mostra piores pares/estrategias e erros recentes
2. **TREINO LOTE** — 12 simulacoes × 10 pares (Deriv + Binance)
3. **CAMADA** — 10 missoes da layer do dia (tip-to-tip mental)
4. **ROTACAO** — avanca para proximos 10 pares; a cada ciclo completo muda camada

## Comandos

```powershell
# Ver plano de hoje (sem treinar)
python scripts/dogeye_curriculum_training.py --plan-only

# Sessao completa (recomendado)
python scripts/dogeye_curriculum_training.py --samples-per-pair 12

# Treino diario agendado (07:00)
.\train_daily.ps1
```

## Arquivos

- `data/training/curriculum_state.json` — lote/camada atual
- `data/training/student_memory.json` — absorcao de conhecimento
- `data/training/reports/curriculum_*.json` — relatorio por sessao

## Meta semanal

- **7 dias** × 10 pares = percorrer ~70 pares variados
- **10 dias** = cobrir os 100 pares Deriv + 100 Binance
- Equipe deve **cair menos** nos mesmos erros (absorption rate sobe)
