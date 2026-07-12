# Doug.AI v1.0 — AI Trading Operating System

**Constitutional Trading** — 332 missions across phased evolution (missions 01–37 snapshots + fase XVI–XXII + omega final).

> **Disclaimer:** Doug.AI is research and educational software. It does **not** provide financial advice. All trading is paper/shadow mode by default — no real money, no live exchange orders. Use at your own risk.


## Quickstart

```bash
# Clone and enter the repo
git clone https://github.com/Douglassrf/doug-ai.git
cd doug-ai

# Create virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt

# Run tests (official suite — see docs/ARQUITETURA_EXECUCAO.md)
pytest -q
```

Fluxo de produção real e regras de arquitetura: [`docs/ARQUITETURA_EXECUCAO.md`](docs/ARQUITETURA_EXECUCAO.md).
Código histórico das missões antigas (snapshots duplicados, sem uso em produção) foi movido
para `archive/legacy_missions/` — não é importado por nada vivo e não deve receber código novo.

## Dashboard (local — recomendado no Windows)

Operations dashboard (Streamlit) — monitor paper/shadow trades, 10 constitutional layers, audit log, and settings panel.

**Requisitos:** Python 3.11+, virtualenv e deps do dashboard.

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
python -m venv .venv
.\.venv\Scripts\pip install -r requirements-dashboard.txt
.\run_dashboard.ps1
```

Alternativa (CMD): `run_dashboard.cmd`

Abra **http://localhost:8501** no navegador.

O script define `PYTHONPATH` na raiz do projeto (necessário para `from dashboard...`) e ativa modo paper/demo.

## Dashboard Docker (opcional)

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) running on your machine.

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
docker compose up --build
```

Open **http://localhost:8501** in your browser.

| Path | Purpose |
|------|---------|
| `dashboard/app.py` | Streamlit UI (Overview, Layers, Operations, **Deriv Demo**, Settings, Council) |
| `integrations/deriv_demo.py` | Cliente WebSocket Deriv — **somente conta demo** |
| `data/audit_log.jsonl` | Volume-mounted operations log |
| `data/settings.json` | Volume-mounted dashboard settings |
| `data/deriv_status.json` | Último snapshot Deriv (saldo, ticks, candles) |
| `scripts/run_preflight_demo.py` | Optional CLI demo log generator |
| `scripts/test_deriv_demo.py` | Teste de conexão Deriv demo |

Detached mode: `docker compose up -d --build` · Stop: `docker compose down`

Worker Deriv opcional (refresh automático a cada 60s):

```powershell
docker compose --profile deriv up -d --build
```

Optional demo feed (outside Docker):

```powershell
python scripts/run_preflight_demo.py --once
python scripts/run_preflight_demo.py --interval 15
```

## Deriv Demo Setup (conta virtual — sem dinheiro real)

> Guia completo (demo → live): [`docs/DERIV_API_SETUP.md`](docs/DERIV_API_SETUP.md)

Integração MVP com a [Deriv WebSocket API](https://api.deriv.com/) para **treino e simulação** em conta demo. O código **recusa** tokens de conta real (`is_virtual` / loginid `VRT*`).

### 1. Criar token na Deriv (conta DEMO)

1. Acesse [home.deriv.com/dashboard/home](https://home.deriv.com/dashboard/home) e faça login.
2. No seletor de conta (canto superior), escolha **Conta demo** (saldo virtual, ex.: USD 10.000).
3. Vá em **Configurações da conta** → **API token** → **Criar novo token**.
4. Marque os escopos **Read** e **Trade** (apenas na demo — nunca use token de conta real aqui).
5. Copie o token gerado (ele só aparece uma vez).

Opcional: registre um `app_id` em [api.deriv.com](https://api.deriv.com/) ou use o público de testes `1089`.

### 2. Configurar Doug.AI

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
copy .env.example .env
# Edite .env e cole: DERIV_API_TOKEN=seu_token_demo_aqui
```

Instale deps do dashboard (fora do Docker):

```powershell
pip install -r requirements-dashboard.txt
python scripts/test_deriv_demo.py
```

Saída esperada (com token válido demo):

```
🔗 Conectando Deriv demo (app_id=1089)...
✅ Conta DEMO: VRTCxxxxx | Saldo: 10000.00 USD
   Tick R_100: ...
   Tick cryBTCUSD: ...
✅ Teste concluído — status salvo em data/deriv_status.json
```

### 3. Dashboard

```powershell
.\run_dashboard.ps1
```

Abra **http://localhost:8501** → menu lateral **Deriv Demo**. Mostra status, saldo demo, ticks, candles e sinais paper locais (sem ordens reais na Deriv).

O token pode ficar em `.env` (recomendado, gitignored) ou em `data/settings.json` via painel — **nunca commite** o arquivo `.env`.

### Segurança

| Regra | Implementação |
|-------|----------------|
| Só conta demo | `authorize` → valida `is_virtual` / prefixo `VRT` |
| Sem ordens reais | Apenas leitura de saldo/ticks/candles + sinais paper locais |
| Token do usuário | Variável `DERIV_API_TOKEN` — nunca no repositório |

---

# DOUG.AI (Doug.OS)

Doug.OS é um sistema de inteligência/decisão para trading (Forex, metais preciosos e
criptomoedas) construído em Python, organizado em torno de um núcleo de orquestração de
sinais ("núcleo seguro") que evolui através de "missões" incrementais.

## Arquitetura central (com base no código e relatórios encontrados)

- **DougBus** — barramento de eventos que orquestra a chamada aos "servos" (módulos de
  sinal) e propaga um `cycle_id` por ciclo de decisão.
- **IntentVector** — estrutura padronizada de saída de cada servo (sinal, força, contexto).
- **IntelligenceCouncil** — agrega os `IntentVector` de todos os servos, aplica pesos
  dinâmicos (Dynamic Weighting) e o regime de mercado corrente para produzir uma decisão
  final (BUY/SELL/HOLD) com score de confiança.
- **RegimeDetector** — classifica o regime de mercado (NORMAL, TRENDING, VOLATILE,
  MANIPULATED, CHAOTIC, SYSTEMIC_RISK, WHITE_NOISE) usado para ponderar os sinais.
- **Risk Empire / Risk servo** — veto de risco com prioridade sobre as demais decisões.
- **Shadow Executor** — execução simulada (modo seguro, sem ordens reais, sem conexão a
  exchange real).
- **AuditLog** — log auditável (JSONL) de cada ciclo de decisão, pesos aplicados e
  resultado.
- **Servos** (plugáveis via DougBus) — market, news/psychology, on-chain, macro econômico,
  risk empire, evolution/research, entre outros. Cada servo emite um `IntentVector`.
- **Conectores de dados** (`connectors/`) — camada somente leitura (mock de preços,
  ForexConnector, CryptoConnector) registrada na Data Connector Layer.
- **Memória / Aprendizado** (`memory/`) — `ExperienceStore` (SQLite) persiste contexto,
  regime, decisão, resultado e PnL; `ProbabilityEngine` calcula probabilidade de
  vitória/confiança a partir do histórico; `LearningLoop` expõe gravação/consulta de
  estatísticas; Darwin Engine e Digital Twin para evolução/simulação.
- **Inteligência on-chain** (`onchain/`) — WhaleDetector, ExchangeFlowTracker,
  StablecoinTracker, WalletMonitor, OnChainEventRegistry, WhaleMirrorEngine,
  StablecoinFlowEngine, MarketIntegrityV2Engine, LiquidityRiskEngine.
- **Brian** (`brian/` / `brain/`) — camada de supervisão/raciocínio (Brian Supreme),
  revisando inconsistências e produzindo explicações antes da decisão final.
- **Unified Intelligence Layer (Missão 37)** — consolida todas as camadas (técnica,
  on-chain, macro, notícias, memória) em um fluxo único, com supervisão do Brian Supreme V1
  antes de a decisão chegar ao executor.

O projeto é deliberadamente "modo seguro" em todas as fases recuperadas: não opera dinheiro
real, não conecta a exchanges reais para ordens, e roda apenas em paper/shadow trading.

## Missões recuperadas

Faixa numérica coberta: **missões 01 a 37**, com as seguintes lacunas/observações:

- **Missão 18** e **Missão 22** são mencionadas no `MISSION_HISTORY.md` mas não possuem
  `MISSION_XX_REPORT.md` nem snapshot de código isolado em nenhum dos zips (incluindo os
  aninhados) — o trabalho dessas missões está incorporado ao snapshot acumulado seguinte
  (M19 e M23, respectivamente). Nada foi fabricado para preencher essas lacunas.
- **Missões 02–17** não têm pasta individual por missão nos zips originais — existem dois
  snapshots combinados cobrindo sub-intervalos desse período: um do pacote "Roadmap Produção
  V21" (missões 02–11) e outro do pacote "Execução Contínua" (missões 02–17, estado mais
  avançado dentro desse intervalo).

| Missão(ões) | Conteúdo disponível em `missions/` |
|---|---|
| 01 (Fase 1 — Núcleo Seguro) | snapshot completo de `doug_os/` |
| 02 (Decision Cycle Engine) | snapshot completo de `doug_os/` + README específico |
| 02–11 (`mission_02_11_roadmap_v21`) | snapshot combinado de `doug_os/` (Roadmap Produção V21) |
| 02–17 (`mission_02_17_combined`) | snapshot combinado de `doug_os/` (Execução Contínua), sem separação por missão individual |
| 19, 20, 21, 23 | snapshot de `doug_os/` + `MISSION_XX_REPORT.md` |
| 24, 25, 26, 27 | apenas `MISSION_XX_REPORT.md` (código incorporado ao acumulado, sem snapshot isolado nos zips) |
| 28, 29, 30, 31 | snapshot de `doug_os/` + `MISSION_XX_REPORT.md` |
| 32, 33, 34, 35, 36 | apenas `MISSION_XX_REPORT.md` (sem snapshot isolado nos zips) |
| 37 | apenas `MISSION_37_REPORT.md` em `missions/mission_37/` — o snapshot de código correspondente (estado final acumulado) está em `latest/`, não duplicado dentro de `missions/` |

Os três arquivos `DOUG_OS_M28_M37_CONSOLIDADO*.zip` (`DOUG_OS_M28_M37_CONSOLIDADO.zip`,
`DOUG_OS_M28_M37_CONSOLIDADO (1).zip`, `DOUG_OS_M28_M37_CONSOLIDADO (2).zip`) foram
verificados via MD5/SHA e são **idênticos byte a byte**. Apenas a cópia sem sufixo foi
extraída e usada; as outras duas foram ignoradas.

## Estrutura de pastas

```
DOUG.AI/
├── README.md                        (este arquivo)
├── missions/
│   ├── mission_01/                  Fase 1 — Núcleo Seguro (snapshot completo)
│   ├── mission_02/                  Decision Cycle Engine (snapshot completo + README)
│   ├── mission_02_11_roadmap_v21/   snapshot combinado de doug_os/ (Missões 02–11)
│   ├── mission_02_17_combined/      snapshot combinado de doug_os/ (Missões 02–17)
│   ├── mission_19/ … mission_21/    snapshot doug_os/ + MISSION_XX_REPORT.md
│   ├── mission_23/                  snapshot doug_os/ + MISSION_23_REPORT.md
│   ├── mission_24/ … mission_27/    apenas MISSION_XX_REPORT.md
│   ├── mission_28/ … mission_31/    snapshot doug_os/ + MISSION_XX_REPORT.md
│   ├── mission_32/ … mission_36/    apenas MISSION_XX_REPORT.md
│   └── mission_37/                  apenas MISSION_37_REPORT.md (snapshot em latest/)
├── latest/
│   └── doug_os/                     snapshot mais avançado/acumulado do projeto
│                                     (estado pós-Missão 37, extraído da raiz de
│                                     DOUG_OS_M28_M37_CONSOLIDADO.zip)
└── docs/
    ├── CURRENT_STATE.md
    ├── MISSION_HISTORY.md
    ├── OPEN_ISSUES.md
    ├── ROADMAP.md
    ├── BLOCK02_COMPLETION_REPORT.md
    ├── BLOCK03_COMPLETION_REPORT.md
    ├── PROJECT_STATUS__M28_M37_doug_os.md
    ├── MISSION_02_DECISION_CYCLE_ENGINE.md
    ├── README__fase1.md             (idêntico ao README de mission_02, mantido uma vez)
    ├── README__missoes_02_17.md
    ├── STATUS__missoes_02_17.md
    ├── README__roadmap_v21.md
    ├── RELATORIO_ROADMAP_PRODUCAO_V21.md
    └── mission_reports/
        └── MISSION_19_REPORT.md … MISSION_37_REPORT.md   (cópia consolidada de todos
                                                             os relatórios de missão
                                                             encontrados em um único lugar)
```

- **`missions/mission_XX/`** — contém o snapshot de código `doug_os/` daquela missão
  (quando um snapshot isolado existia em algum zip) e/ou o `MISSION_XX_REPORT.md`
  correspondente. Missões sem snapshot próprio têm apenas o relatório — isso é fiel ao que
  estava disponível nos zips, nada foi inventado.
- **`latest/doug_os/`** — cópia do snapshot mais avançado do projeto (170 arquivos, o maior
  conjunto entre todos os snapshots extraídos), correspondente ao estado acumulado após a
  Missão 37, extraído do nível raiz (não aninhado) de `DOUG_OS_M28_M37_CONSOLIDADO.zip`.
- **`docs/`** — todos os documentos de status/roadmap/histórico/relatório (`*.md`)
  encontrados nos pacotes, deduplicados por conteúdo. Quando dois pacotes tinham um arquivo
  de mesmo nome com conteúdo diferente, ambas as versões foram mantidas, com o pacote de
  origem como sufixo do nome (ex.: `README__fase1.md`, `README__roadmap_v21.md`). Quando o
  conteúdo era idêntico, apenas uma cópia foi mantida.

## Origem dos dados

Reconstruído a partir de 8 arquivos zip em `Downloads` (3 deles cópias idênticas de
`DOUG_OS_M28_M37_CONSOLIDADO.zip`, das quais só uma foi usada), alguns contendo zips
aninhados (até 3 níveis de profundidade) que foram extraídos recursivamente:

- `DOUG_OS_FASE_1_NUCLEO_SEGURO.zip`
- `DOUG_OS_M18_M27_CONSOLIDADO.zip` (continha zips de M19, M20, M21, M23 aninhados)
- `DOUG_OS_M28_M37_CONSOLIDADO.zip` (continha o M18_M27 consolidado aninhado, que por sua
  vez continha M19/M20/M21/M23, além de M28, M29, M30 e M31 aninhados separadamente; os
  relatórios de M24–M27 e M32–M37 estavam soltos na raiz deste zip, sem snapshot de código
  próprio)
- `DOUG_OS_MISSOES_02_17_EXECUCAO_CONTINUA.zip`
- `DOUG_OS_MISSAO_02_DECISION_CYCLE_ENGINE.zip`
- `DOUG_OS_ROADMAP_PRODUCAO_V21_MISSOES_02_11.zip` (documento de roadmap; seu conteúdo foi
  incorporado em `docs/`, não como uma pasta de missão própria, pois é um relatório de
  planejamento e não um snapshot de código distinto)

Os arquivos zip originais permanecem intactos em `Downloads` e não foram modificados. A
pasta temporária de extração (`_extraction_tmp`) foi removida ao final do processo.
