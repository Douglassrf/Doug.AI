# Missão 24 – Market Memory v2

## Contexto

Até a Missão 23, o Doug.OS possuía uma implementação simplificada do módulo de memória (`ExperienceProbabilityEngine`) que apenas contava quantas vezes uma determinada situação de mercado havia ocorrido.  Não havia registro dos regimes, decisões ou resultados associados a cada contexto, o que limitava a análise histórica e a possibilidade de aprendizado.  A missão 24 propôs criar uma **memória de mercado de segunda geração** capaz de armazenar eventos completos (contexto, regime, decisão, resultado e PnL) e recuperar padrões semelhantes para uso posterior.

## Implementação

### Nova classe `ExperienceStore`

Foi adicionada a classe `ExperienceStore` no arquivo `doug_os/memory/experience_store.py`.  Essa classe utiliza **SQLite** para persistir experiências completas e expõe os métodos `save()` e `similar()`:

* **`save(context, regime, decision, result, pnl)`**: insere um novo registro na tabela `experiences`.  Cada experiência recebe um hash SHA‑256 calculado a partir do contexto (JSON com chaves ordenadas) para identificar situações semelhantes.  Além do contexto, são armazenados o regime de mercado (``"bull"``, ``"bear"``, etc.), a decisão tomada (``"BUY"``, ``"SELL"``, ``"HOLD"``), o resultado (``"WIN"`` ou ``"LOSS"``) e o PnL.
* **`similar(context)`**: calcula o hash do contexto fornecido e retorna uma lista de experiências previamente salvas com o mesmo hash.  Cada item da lista inclui o contexto original, o regime, a decisão, o resultado e o PnL.

O banco de dados é criado automaticamente em `doug_os/logs/experience_store.db` (ou em qualquer caminho especificado) e a tabela `experiences` é criada se ainda não existir【463754646063017†L24-L33】.

### Testes

Criou‑se o arquivo `tests/test_market_memory.py` com um teste que:

1. Instancia a `ExperienceStore` com um banco temporário, salva uma experiência com um contexto simples, regime `bull`, decisão `BUY`, resultado `WIN` e PnL positivo.
2. Chama `similar()` com o mesmo contexto e verifica que a experiência retornada contém exatamente os valores salvos (contexto, regime, decisão, resultado, PnL).
3. Verifica que chamar `similar()` com um contexto não existente retorna uma lista vazia.

Os testes demonstram que a memória persiste corretamente os dados e permite recuperar experiências semelhantes.

### Atualizações de documentação

* **`MISSION_HISTORY.md`** – adicionou‑se uma nova seção para a Missão 24, descrevendo objetivo, ações e resultados.
* **`CURRENT_STATE.md`** – o cabeçalho passou a indicar que estamos após a Missão 24 e foi criada uma nova subseção de **Memória e Aprendizado**.  Essa subseção explica o funcionamento do `ExperienceStore` e sua importância para o aprendizado.
* **`ROADMAP.md`** – o item da Missão 24 foi marcado como **Concluído**.
* **`OPEN_ISSUES.md`** – a questão “Memória limitada” foi marcada como resolvida, pois a nova implementação registra regime, decisão, resultado e PnL.

## Resultado

A nova memória de mercado fornece uma base robusta para analisar experiências passadas e extrair padrões.  Ao armazenar o contexto completo junto com regime, decisão e resultado, o Doug.OS poderá, nas próximas missões, **calcular probabilidades** de sucesso, ajustar parâmetros e eventualmente **aprender** com o próprio histórico.  A Missão 25 aproveitará esses dados para implementar o motor de probabilidade.