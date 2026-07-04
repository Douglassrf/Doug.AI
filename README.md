# Doug.AI v1.0 — AI Trading Operating System

**Constitutional Trading** — 331 missions across phased evolution (missions 01–37 snapshots + fase XVI–XXI + omega final).

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

# Run tests (primary suite — latest snapshot)
cd latest/doug_os
pytest -q
```

Phase-specific tests live under `fase_*/` (e.g. `fase_omega_final/`). Each phase has its own `requirements.txt` if you need isolated runs.

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
