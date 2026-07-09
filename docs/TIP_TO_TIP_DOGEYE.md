# DogEye — Treinamento Tip-to-Tip (Doug.AI)

Exercício oficial para a equipe DogEye validar a integração Deriv + pipeline Doug.AI.

## Formato

| Dimensão | Valor |
|----------|-------|
| Missões | 10 (TTT-M01 … TTT-M10) |
| Pares Deriv | 10 |
| Repetições por par | 10 |
| **Total de tentativas** | **1000** |

## Pares

`R_100`, `R_75`, `R_50`, `cryBTCUSD`, `cryETHUSD`, `frxEURUSD`, `frxGBPUSD`, `frxUSDJPY`, `BOOM1000`, `CRASH1000`

## Missões

| ID | O que testa |
|----|-------------|
| TTT-M01 | Bridge unificado (`integrations/deriv_bridge.py`) |
| TTT-M02 | Ping API Deriv (mock-first) |
| TTT-M03 | Tick público por par (sem token, `DOUG_MODE=demo`) |
| TTT-M04 | Paper trade (Missão 301) |
| TTT-M05 | Cadeia tick → decisão → audit log |
| TTT-M06 | Proposta dry-run bloqueada |
| TTT-M07 | Live gate — trading real bloqueado |
| TTT-M08 | E2E integração (Missão 299) |
| TTT-M09 | Audit trail |
| TTT-M10 | Snapshot público por par |

## Como rodar (equipe — SOLO, sem agente)

**Leia primeiro:** [`docs/TIP_TO_TIP_EQUIPE_SOLO.md`](TIP_TO_TIP_EQUIPE_SOLO.md) — instruções completas para certificação independente.

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install websockets python-dotenv streamlit

copy .env.example .env

# 1) Preflight — todos OK antes de continuar
python scripts/tip_to_tip_preflight.py

# 2) Certificacao oficial (1000 ops, nome obrigatorio)
python scripts/tip_to_tip_training.py --certify --operator "SEU_NOME"
```

Smoke interno apenas (não vale certificação):

```powershell
python scripts/tip_to_tip_training.py --quick
```

## Saídas

- `data/tip_to_tip_score.json` — score machine-readable
- `docs/TIP_TO_TIP_SCORE_REPORT.md` — relatório para Douglas

## Regras

1. **Nunca** commitar `.env` com token.
2. Token DEMO opcional; ticks públicos funcionam com `app_id=1089`.
3. `DERIV_LIVE_ENABLED` permanece `false`.
4. Falha em live gate ou compra real = comportamento esperado (missão TTT-M07).

## Integração unificada

- **Dashboard / async:** `integrations/deriv_demo.py`
- **API FastAPI / sync mock:** `src/app/integrations/deriv.py`
- **Facade treinamento:** `integrations/deriv_bridge.py`
