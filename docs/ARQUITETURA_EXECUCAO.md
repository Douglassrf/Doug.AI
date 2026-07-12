# Arquitetura de Execução — Fonte Única de Verdade

## Fluxo real de produção

As 7 tarefas do Windows Task Scheduler (`DougAI_Autocycle_Diario`, `DougAI_Torre_Controle`,
`DougAI_Treino_Diario/Semanal/Mensal`, `DougAI_Edge_Training`, `DougAI_Noticias_3h`) chamam
exclusivamente scripts em `scripts/`, que importam só das pastas abaixo, todas na raiz do
repositório. Isto é o Doug.AI em produção — não há mais nenhum outro caminho de execução.

- `scripts/` — pontos de entrada (um `.py` por tarefa agendada).
- `core/` — orquestrador único da Torre de Controle (`core/orchestrator.py`).
- `training/` — motor de backtest, treino contínuo, currículo, gate de confiança,
  ledger de paper trading, detecção de regime.
- `integrations/` — clientes reais Binance (`binance_apprentice.py`) e Deriv
  (`deriv_demo.py`, `deriv_bridge.py`), e o `money_guard.py`.
- `dashboard/` — painel Streamlit de observação (não faz parte do ciclo automático).
- `src/app/` — camada auxiliar usada pelo dashboard (config Deriv, cliente HTTP).

`missions/` (arquivos soltos `mission_*.py` e as pastas de relatório sem `doug_os/`) continua
na raiz porque tem duas dependências vivas confirmadas: `training/curriculum.py` escaneia
essa pasta em runtime para montar o catálogo de missões, e `scripts/tip_to_tip_training.py`
importa `missions.mission_301`/`missions.mission_299` diretamente (parte do benchmark de
certificação manual, ligado aos gates descritos em `docs/DERIV_API_SETUP.md`).

## `archive/legacy_missions/`

Contém código histórico confirmado como não referenciado por nenhum dos itens acima:

- as 12 cópias duplicadas `mission_XX/doug_os/` (snapshots incrementais do mesmo projeto
  `doug_os`, cada uma um pouco mais completa que a anterior — a versão mais avançada era
  `latest/doug_os/`, também arquivada);
- `latest/` completa (só era usada por um probe opcional do dashboard,
  `dashboard/preflight_bridge.py`, que já degrada para dados demo quando a pasta não existe —
  comportamento inalterado, por design: "bridge must never crash dashboard");
- `fase_omega_final/` e `fase_xxii_cognitive_trading_loop/` (fases antigas, sem nenhum import
  vivo).

Essas 4 árvores eram a causa de ~133 dos ~145 erros de coleção do `pytest` (colisão de nome de
módulo `doug_os.tests.*` entre as 12 cópias, e `ModuleNotFoundError` por falta de pythonpath em
`latest/doug_os/tests/`). Resolvido pelo `git mv` + `pytest.ini` (`testpaths`, `norecursedirs`).

**Regra**: `archive/` não deve receber código novo nem ser importado por nada em produção. Se
algum dia for necessário reviver algo de lá, mova o arquivo específico de volta para a árvore
viva e adicione um teste — não importe direto de dentro de `archive/`.

**Atualização — as outras 6 pastas `fase_*` foram auditadas e arquivadas depois.**
`fase_final_trading_operating_system`, `fase_xvi_alpha_generation`,
`fase_xvii_predictive_intelligence`, `fase_xviii_quantum_trading_intelligence`,
`fase_xix_meta_cognitive_trading` e `fase_xxi_evolutionary_trading_intelligence` (60
missões, 258-317) foram lidas integralmente numa auditoria posterior: zero import vivo
confirmado, e o que tinha matemática real por trás (não fachada estatística via hash
determinístico) foi extraído e reimplementado do zero para os dados reais do projeto —
`training/strategy_trend.py` (de mission_309) e `training/trade_efficiency.py` (de
mission_262), ambos validados por simulação walk-forward antes de integrar. Os outros 10
candidatos avaliados (268, 316, 292, 290, 260, 270, 278, 279, 310, 314) e os 4 "gates de
certificação" (300, 303, 306, 317) foram rejeitados com justificativa concreta — a maior
parte porque `training/stats_validation.py` (DSR) já é estatisticamente mais rigoroso do
que o que essas missões ofereciam. As 6 pastas foram movidas para
`archive/legacy_missions/` (mesmo tratamento das outras 4 árvores acima).
