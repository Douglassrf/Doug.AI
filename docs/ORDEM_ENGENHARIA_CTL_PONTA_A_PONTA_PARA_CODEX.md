# Ordem de Engenharia — Doug.AI: Consolidação e Auto-Aprimoramento Ponta a Ponta

**De:** Douglas (dono do produto), redigido por Claude (revisão técnica sênior)
**Para:** Codex (execução)
**Data:** 2026-07-06
**Escopo:** Isto NÃO é "mais uma missão/fase". É uma ordem de consolidação — o objetivo é fazer o sistema que já existe funcionar de ponta a ponta, de forma íntegra, verificável e auto-aprimorável. Não crie mais uma pasta isolada (`fase_XXX/`, `mission_XXX/`). Trabalhe dentro do que já existe e conecte o que está solto.

---

## 0. Por que esta ordem existe

Auditoria (Claude, 2026-07-06) encontrou:

1. A pasta operacional real (onde os treinos diário/semanal rodam de verdade, via Agendador de Tarefas do Windows) **não é um repositório git**. Não há `.git` nela.
2. Dentro dela existe uma pasta `missions/` com **mais de 1000 arquivos**, onde cada "missão" (`mission_01`, `mission_02`, `mission_02_17_combined`, ...) é uma **cópia inteira duplicada** do código anterior, em vez de um histórico de versões (`git log`) sobre um único código-fonte. Isso é dívida técnica grave: nenhum agente (Codex, Claude, Cursor) tem um alvo único e vivo para integrar mudanças.
3. A PR #2 (`Add Phase XXII Cognitive Trading Loop`, mission_331.py) foi mergeada na `master` do GitHub **com o CI falhando** (`test (latest/doug_os)` — exit code 2). A descrição da PR só citou os testes do módulo novo isolado, não o suite completo que o CI roda.
4. Essa PR criou um sistema de "confiança"/validação (`CognitiveTradingLoop`, memória SQLite, teste estatístico, `protective_verdict`) **desconectado de tudo que já roda** — não fala com `training/coach.py`, `training/continuous_trainer.py` nem com o filtro de confiança já implementado e em produção (`training/confidence_gate.py`, integrado em `scripts/dogeye_curriculum_training.py`).
5. A parte de "evolução genética" do mission_331.py (`evolve_dna`) aplica uma mutação aleatória (`random.uniform(0.90, 1.10)`) em 3 parâmetros e decide "promover" o resultado usando um `fitness_results` que **não tem relação causal** com os parâmetros mutados — ou seja, não valida o filho antes de promovê-lo. Isso não é aprendizado real, é decoração com nome de peso.

Conclusão: o projeto não precisa de "mais uma fase brilhante". Precisa de consolidação, higiene de engenharia e uma base de validação real. É isso que esta ordem cobra.

---

## 1. Regras inegociáveis (não violar em nenhuma hipótese)

- **Paper trading / testnet / demo para sempre.** Nenhuma ordem real, nenhuma conta real, nenhum saque, nenhuma chave de produção. O próprio README do projeto já declara isso — mantenha.
- **Nenhuma API paga ou serviço de nuvem novo** sem autorização explícita do Douglas.
- **Nenhum número decorativo ou fabricado.** Todo resultado reportado (win rate, taxa de aprovação, nível de confiança) tem que vir de dado real computado, nunca hardcoded para "parecer bom".
- **Nenhuma PR mergeada com CI vermelho.** Se o CI falhar, a PR fica aberta até corrigir — sem exceção.
- **Nenhuma pasta nova de "fase" ou "missão" isolada.** Se precisar de um módulo novo, ele entra dentro da estrutura existente e é importado/usado por quem já roda o treino de verdade — não fica solto esperando alguém plugar depois.

---

## 2. Definição de "pronto" (Definition of Done)

Uma entrega só conta como "ponta a ponta" se, ao final:

1. O código roda **dentro do pipeline real** que o Agendador de Tarefas do Windows já executa (`train_daily.ps1` → `scripts/dogeye_curriculum_training.py`), não em um script/pasta paralela.
2. Existe **uma única** fonte de verdade para "o sistema deve confiar nesse sinal?" — não duas implementações concorrentes.
3. O CI está verde, com saída literal de terminal colada na PR (não só "passou").
4. A PR contém uma rodada de teste real do pipeline completo (`python scripts/dogeye_curriculum_training.py --samples-per-pair 1 --no-advance`, ou equivalente) com a saída colada — prova de integração, não só teste unitário isolado.
5. A documentação (README ou equivalente) reflete o estado real, não o estado aspiracional.

---

## 3. Fases de trabalho (nesta ordem — não pule etapa)

### Fase 0 — Reconciliar o código (bloqueante)

Antes de qualquer coisa: descubra e documente a relação real entre o repositório GitHub `Douglassrf/Doug.AI` e a pasta operacional local (onde vive `training/coach.py`, `training/confidence_gate.py`, `training/continuous_trainer.py`, `training/strategies.py`, `scripts/dogeye_curriculum_training.py`, `training/pair_universe.py`). Se você (Codex) só tem acesso ao repositório remoto e não à pasta local, **diga isso explicitamente na PR** em vez de construir mais um módulo isolado sem saber se algo assim já existe. Se Douglas ainda não conectou os dois, esta fase termina aqui com uma nota clara pedindo essa conexão antes de prosseguir.

### Fase 1 — CI verde, de verdade

Investigue e corrija o motivo real do `test (latest/doug_os)` falhar com exit code 2 na PR #2. Não abra uma nova PR sem antes rodar o suite completo localmente e colar a saída literal. Se o problema for de import/colisão de nomes de teste entre `fase_xxii_cognitive_trading_loop/` e o resto do projeto, resolva isso — não ignore.

### Fase 2 — Um único motor de decisão (fim da duplicação)

Hoje existem três lógicas de "isso é confiável?" competindo: `training/coach.py` (remedial/XP), `training/confidence_gate.py` (limiar de confiança 90% sobre leaderboard, já em produção), e `CognitiveTradingLoop` do mission_331.py (memória SQLite + similaridade + teste estatístico + `protective_verdict`, isolado). Escolha o melhor de cada um e funda em **um único módulo**:

- Persistência: adotar SQLite (como no mission_331.py) em vez do JSON simples do leaderboard atual — mais robusto para histórico crescente.
- Gate de confiança: manter a exigência de amostra mínima + limiar real (`training/confidence_gate.py` já faz isso corretamente, sem lookahead).
- Segurança: manter `protective_verdict` (parar quando muitas perdas recentes) — é uma boa ideia do mission_331.py, vale preservar.
- Gamificação (XP, níveis, "Professor") pode continuar existindo como camada de relatório para humano, mas não pode ser a fonte de decisão real — a decisão real vem do motor de confiança unificado.
- Delete ou arquive o que ficar redundante. Não deixe os dois sistemas rodando em paralelo.

### Fase 3 — Motor de backtest histórico

Sem isso, nenhuma "melhoria" é verificável. Salvar localmente histórico real (Binance tem endpoint público gratuito de candles; Deriv já é usado via `ticks_history`) e rodar as estratégias contra esse histórico dividido em treino (ex. 70%) e teste (30%, nunca visto durante o ajuste). Todo resultado de "melhoria" reportado daqui pra frente tem que vir de teste fora da amostra.

### Fase 4 — Parâmetros aprendem de verdade

As estratégias em `training/strategies.py` têm limiares fixos no código (RSI 35/65, banda de 15 ticks, etc.). Transformar em parâmetros e ajustar via busca (grid search simples já basta, são poucos parâmetros) usando os dados da Fase 3, por par e cenário. Salvar a versão dos parâmetros tunados com data, para poder auditar/reverter. Corrigir a falha do `evolve_dna` do mission_331.py: a promoção de um parâmetro mutado só pode acontecer depois de validar o desempenho *desse mesmo* parâmetro contra dado real (Fase 3) — nunca contra um `fitness_results` desconectado.

### Fase 5 — Separar sintético de real

Os pares Deriv incluem índices sintéticos (`R_10`, `BOOM1000`, `1HZ100V`, etc.) que são aleatórios por design — nenhuma estratégia técnica tem vantagem estrutural neles. Separar esses pares dos pares reais (forex/cripto) em todos os relatórios, para não misturar sorte com sinal real.

---

## 4. O que NÃO fazer

- Não criar `fase_XXIII/`, `mission_332/` ou qualquer pasta nova isolada.
- Não duplicar o projeto inteiro como "snapshot" de progresso — isso é o que já causou a bagunça atual.
- Não mergear com CI vermelho.
- Não inventar métrica de sucesso sem dado real por trás.
- Não tocar em conta real, chave de produção, ordem ao vivo, ou qualquer fluxo de dinheiro de verdade.

---

## 5. Evidência exigida na entrega (sem exceção)

Colar na PR, literalmente:

1. Saída do `pytest` completo (não só o módulo novo), rodado 1x.
2. Saída de uma execução real do pipeline (`scripts/dogeye_curriculum_training.py --samples-per-pair 1 --no-advance`) mostrando o motor de decisão unificado em ação.
3. Confirmação do status do CI (link do Actions com "Status: Success").
4. Lista objetiva do que foi removido/consolidado (arquivos deletados ou fundidos), não só do que foi adicionado.

---

## 6. Meta de longo prazo (para dar contexto, não para prometer resultado)

O objetivo por trás disso tudo é que o Doug.AI acumule conhecimento real (memória de resultados validados), evolua parâmetros com base em evidência (não em nome bonito), e fique mais seletivo com o tempo — operando só quando o histórico real justificar. Isso é o caminho honesto para "amadurecer". Nenhuma etapa aqui promete um sistema perfeito ou infalível — promete um sistema que não mente sobre o que sabe.
