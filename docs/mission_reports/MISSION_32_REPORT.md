# Missão 32 – Liquidity Risk Engine

## Objetivo

Implementar um mecanismo capaz de mapear riscos de liquidez, classificando eventos de mercado em diferentes níveis (vacuum, stress, collapse) e ajustando um indicador de confiança conforme o risco.  A liquidez é um fator crítico para a execução de ordens e a estabilidade do mercado; portanto, a identificação de situações de baixa liquidez permite acionar freios de segurança e reduzir a exposição.

## Implementação

* **Classe `LiquidityRiskEngine`** – Criada em `doug_os/engines/liquidity_risk_engine.py`, esta classe possui parâmetros configuráveis como `ideal_depth` e `ideal_volume` (valores considerados saudáveis), e três limiares (`vacuum_threshold`, `stress_threshold`, `collapse_threshold`).  O método `evaluate(event)` recebe um dicionário com `order_book_depth` e `daily_volume`, normaliza esses valores em relação aos ideais e calcula uma pontuação de risco de 0 a 1 (quanto maior, pior a liquidez).
* **Classificação de risco** – A pontuação de risco determina a categoria:
  - **collapse** quando ≥ 0,8 – indica liquidez extremamente comprometida;
  - **stress** quando ≥ 0,5 – liquidez ruim que pode prejudicar a execução de ordens;
  - **vacuum** quando ≥ 0,3 – mercado com baixa liquidez mas sem colapso iminente;
  - **normal** abaixo de 0,3 – liquidez aceitável.

  Além da categoria, o método retorna um `confidence_adjustment` calculado como `1 − liquidity_risk`, permitindo reduzir a confiança de outros engines ou servos quando a liquidez está deteriorada.
* **Exportação Pública** – `doug_os/engines/__init__.py` foi atualizado para expor o `LiquidityRiskEngine`, permitindo importação direta.

## Testes

* Criado `tests/test_liquidity_risk_engine.py` com quatro cenários:
  1. **Colapso**: profundidade e volume muito baixos geram pontuação ≥ 0,8 e categoria `collapse` com ajuste de confiança ≤ 0,2.
  2. **Stress**: valores moderadamente baixos produzem pontuação entre 0,5 e 0,8 e categoria `stress`.
  3. **Vacuum**: valores levemente abaixo do ideal resultam em pontuação entre 0,3 e 0,5 e categoria `vacuum`.
  4. **Normal**: valores próximos aos ideais resultam em pontuação < 0,3, categoria `normal` e ajuste de confiança alto.

  Todos os testes passaram, demonstrando que o engine classifica corretamente os eventos e calcula os ajustes de confiança adequadamente.

## Atualização da Memória

* **`CURRENT_STATE.md`** foi atualizado para “após Missão 32”.  Inclui uma subseção *Liquidity Risk Engine* descrevendo o motor e removeu a missão 32 da lista de próximos passos.
* **`MISSION_HISTORY.md`** contém agora uma seção para a Missão 32 com detalhes da implementação e dos testes.
* **`ROADMAP.md`** marca a Missão 32 como concluída e resume a funcionalidade do novo engine.
* **`OPEN_ISSUES.md`** registra que a questão “Riscos de liquidez” foi resolvida, já que o `LiquidityRiskEngine` foi implementado.

## Resultado

A Missão 32 introduziu um motor simples e transparente para avaliação de liquidez, permitindo detectar vacuums, stress e colapsos de liquidez e ajustar a confiança de forma proporcional ao risco.  Esta camada complementa a defesa contra manipulação e risco implementada nas missões anteriores.  Todos os testes (46 no total) passam com cobertura global acima de 86 %.