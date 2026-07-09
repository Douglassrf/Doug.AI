# DogEye — Treino contínuo (semana inteira)

> **Douglas:** equipe deixa rodando 24/7 em demo. Sem agente. Objetivo: descobrir **qual estratégia funciona em qual cenário**.

---

## O que roda automaticamente

| Dimensão | Quantidade |
|----------|------------|
| Pares Deriv | **15** (sintéticos, crypto, forex, boom/crash) |
| Estratégias | **10** (ligadas às missões Doug.AI M259–M301) |
| Cenários detectados | trending_up, trending_down, ranging, high/low vol |
| Modo | **Paper / demo** — Deriv público, **sem live** |

A cada **~90 segundos** o sistema simula **~25 trades** aleatórios (par + estratégia), compara direção vs movimento do preço, grava score.

**Estimativa semana:** ~16.800 simulações se rodar 24h×7d.

---

## Comandos (equipe)

### 1. Ligar treino contínuo (deixem aberto a semana)

```powershell
cd C:\Users\SEU_USUARIO\Desktop\DOUG.AI
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt websockets python-dotenv
copy .env.example .env
.\run_continuous_training.ps1
```

### 2. Ver quem está ganhando (a qualquer momento)

```powershell
python scripts/dogeye_continuous_training.py --report
```

### 3. Um ciclo só (teste)

```powershell
python scripts/dogeye_continuous_training.py --once --samples 10
```

---

## O que estudar (como vida real)

Para **cada cenário**, vejam no `--report` qual combinação **estratégia + par** tem maior win rate:

| Cenário | Pergunta da equipe |
|---------|-------------------|
| `trending_up` | Qual estratégia surfou a tendência? |
| `trending_down` | Quem acertou sell? |
| `ranging` | Mean reversion ou range bound? |
| `high_volatility` | Vol guard ou meta blend? |
| `low_volatility` | Scalp ou capital shield? |

**Regra:** win rate só vale com **≥ 20 trades** na combinação — senão é sorte.

---

## Arquivos gerados

| Arquivo | Conteúdo |
|---------|----------|
| `data/training/sessions.jsonl` | Cada simulação (log completo) |
| `data/training/leaderboard.json` | Ranking estratégia × par × cenário |
| `data/training/continuous_state.json` | Último ciclo |

---

## Monitor ao vivo (opcional)

Terminal separado:

```powershell
.\run_live_ttt.ps1
# http://localhost:8502
```

Audit log também recebe eventos `continuous_training_cycle`.

---

## Estratégias × missões Doug.AI

| ID | Nome | Missão ref |
|----|------|------------|
| S01 | Momentum Pulse | M261 |
| S02 | Mean Reversion | M275 |
| S03 | Breakout Hunter | M259 |
| S04 | Trend Rider | M284 |
| S05 | Scalp Tick | M301 |
| S06 | Volatility Guard | M271 |
| S07 | RSI Proxy | M280 |
| S08 | Range Bound | M269 |
| S09 | Capital Shield | M281 |
| S10 | Meta Blend | M288 |

---

## Entrega semanal para Douglas (sexta-feira)

1. Print de `--report` (todos os cenários)
2. Top 3 combinações por cenário — **nome da estratégia + par + win rate**
3. Conclusão em 5 linhas: *“Em ranging usamos X; em trend usamos Y…”*
4. Confirmação: treino rodou em demo, `DERIV_LIVE_ENABLED=false`

---

## Proibido

- Live trading
- Token no GitHub
- Parar no primeiro dia — **mínimo 5 dias** de dados antes de concluir

**Treinem até ficarem bons. Sem agente.**
