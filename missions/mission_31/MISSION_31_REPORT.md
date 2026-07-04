# Missão 31 – Market Integrity V2

## Objetivo

Evoluir a camada de detecção de manipulações de mercado adicionando novos indicadores e consolidando uma pontuação agregada.  A versão anterior, presente no `ManipulationIntelligenceEngine`, já avaliava spoofing, wash trading, stop hunt e liquidez falsa.  A Missão 31 introduz um motor independente que considera especificamente **spoofing**, **armadilhas de liquidez**, **falsos rompimentos** e **wash trading**, sintetizando-os em uma classificação simples de risco.

## Implementação

* **Classe `MarketIntegrityV2Engine`** – Criada em `doug_os/engines/market_integrity_v2.py`, esta classe utiliza dataclasses para configurar pesos (por padrão, 0,25 para cada categoria) e limites de classificação (`threshold_high` = 0,6 e `threshold_warning` = 0,4).  O método `detect(event)` extrai as pontuações individuais de um dicionário de evento, normaliza‑as para o intervalo [0, 1], calcula uma média ponderada e converte o resultado para uma porcentagem.  A partir da pontuação normalizada, o engine classifica o evento em três categorias:
  - **dangerous**: quando a pontuação ≥ 0,6;
  - **warning**: quando a pontuação ≥ 0,4 e < 0,6;
  - **ok**: quando a pontuação < 0,4.

  O método retorna um dicionário com o score (em %), a classificação e os valores individuais de cada sinal de manipulação.  Pesos e thresholds podem ser personalizados na construção da classe para ajustes finos.
* **Exportação Pública** – O arquivo `doug_os/engines/__init__.py` foi atualizado para expor `MarketIntegrityV2Engine`, permitindo a importação simplificada.

## Testes

* Criado o arquivo `tests/test_market_integrity_v2.py` com quatro testes:
  1. **Risco alto**: pontuações de 0,8–0,9 resultam em classificação `dangerous` e score > 60.
  2. **Risco moderado**: pontuações em torno de 0,5 resultam em classificação `warning` com score entre 40 e 60.
  3. **Risco baixo**: pontuações abaixo de 0,2 resultam em classificação `ok` com score inferior a 40.
  4. **Configuração personalizada**: verifica que pesos e thresholds informados no construtor alteram a classificação conforme esperado.

  Todos os testes passaram, comprovando que a nova classe calcula corretamente a pontuação agregada e a classificação de risco.

## Atualização da Memória

* **`CURRENT_STATE.md`** foi atualizado para versão “após Missão 31”.  Uma nova subseção *Market Integrity V2* descreve o engine, enquanto a lista de próximos passos foi ajustada para iniciar na Missão 32.  O título foi atualizado e o progresso das missões reflete o avanço.
* **`MISSION_HISTORY.md`** recebeu uma nova entrada detalhando as etapas executadas nesta missão, as modificações de código e os testes realizados.
* **`ROADMAP.md`** foi atualizado: a linha referente à Missão 31 passou a indicar a conclusão da tarefa e resumir a funcionalidade do novo engine.
* **`OPEN_ISSUES.md`** marcou a questão “Evolução da camada de manipulação” como **Resolvida**, registrando que o motor foi implementado.

## Resultado

A Missão 31 adicionou um motor dedicado à integridade de mercado que sintetiza quatro indicadores de manipulação em uma classificação simples.  Esta implementação reforça a camada defensiva do Doug.OS, permitindo filtrar eventos de mercado com risco de manipulação antes que outras engines ou servos tomem decisões.  A arquitetura permanece modular, facilitando futuras extensões.  Todos os 42 testes (incluindo os novos) continuam passando, com cobertura de código acima de 85 %.