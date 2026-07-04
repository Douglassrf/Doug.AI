# Missão 35 – Experience Probability Engine V2

## Objetivo

Evoluir o motor probabilístico utilizado pelo Doug.OS para incorporar recorrência temporal, confiança histórica, contexto de regime e aprendizado por cenário. A versão anterior do motor atribuía o mesmo peso a todas as experiências, ignorando a recência e o regime de mercado no momento em que cada decisão foi tomada.

## Implementação

Para cumprir o objetivo, foi implementada a classe `ProbabilityEngineV2` em `doug_os/memory/probability_engine_v2.py`. Esse novo motor estende o `ProbabilityEngine` original e adiciona as seguintes melhorias:

* **Pesos por recência:** as experiências são ordenadas pelo campo `id` (que, por ser autoincremental na tabela SQLite, serve como proxy de tempo). Experiências mais recentes recebem pesos lineares crescentes, de modo que eventos recentes influenciam mais o resultado.
* **Multiplicador por regime:** se a experiência pertence ao mesmo regime atual (por exemplo, bull ou bear), seu peso é multiplicado por um fator (> 1) configurável. Isso destaca padrões que ocorrem em contextos de mercado semelhantes.
* **Probabilidade e recorrência ponderadas:** a probabilidade de vitória é calculada como a soma dos pesos de vitórias dividida pela soma de pesos de todas as experiências. A recorrência ponderada é a soma dos pesos. A confiança histórica é a recorrência dividida por 5, saturando em 1 para limitar o intervalo.
* **Recomendações com novos limiares:** a recomendação final (`WIN`, `LOSS` ou `UNSURE`) usa limiares de 0,55 e 0,45 para decidir entre vitória, derrota ou incerteza.

O módulo `doug_os/memory/__init__.py` foi atualizado para exportar a nova classe. Também foram acrescentadas entradas correspondentes no arquivo de configuração `config.py` para permitir ajustes futuros dos multiplicadores e limiares.

## Testes

O arquivo `tests/test_probability_engine_v2.py` foi criado para validar o novo comportamento. Os testes populam uma instância temporária do `ExperienceStore` com experiências ordenadas e regimes alternados. Em seguida, verificam que:

* a probabilidade de vitória calcula corretamente a soma ponderada das experiências;
* experiências recentes influenciam mais o resultado que experiências antigas;
* o multiplicador de regime ajusta a probabilidade para cima quando os contextos coincidem e para baixo quando diferem;
* a confiança histórica respeita o limite superior de 1.

Todos os testes passam, demonstrando que o motor de probabilidade considera recência e regime ao fazer recomendações.

## Atualizações de Documentação

Os documentos de estado (`CURRENT_STATE.md`) e de histórico (`MISSION_HISTORY.md`) foram atualizados para refletir a existência do motor de probabilidade V2, descrevendo as diferenças em relação à versão anterior e registrando esta missão como concluída. O `ROADMAP.md` marca a Missão 35 como concluída e o `OPEN_ISSUES.md` indica que a melhoria do motor de probabilidade está resolvida.

## Conclusão

A Missão 35 introduziu um mecanismo de probabilidade mais sofisticado, capaz de aprender com eventos recentes e ajustar sua confiança de acordo com o regime de mercado. Essa evolução prepara o terreno para decisões mais informadas no Doug.OS e suporta o aprendizado contínuo no loop de experiências.