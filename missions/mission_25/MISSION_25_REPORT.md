# Missão 25 – Experience Probability Engine

## Contexto

Com a memória de mercado expandida na Missão 24, o Doug.OS passou a registrar contextos completos, regimes, decisões e resultados das operações.  O próximo passo lógico é **converter esse histórico em informações quantitativas** que auxiliem a tomada de decisão.  A Missão 25 estabelece um mecanismo simples de cálculo de probabilidades com base nas experiências armazenadas.

## Implementação

### Classe `ProbabilityEngine`

Foi introduzido o módulo `doug_os/memory/probability_engine.py`, contendo a classe `ProbabilityEngine`.  Este engine recebe uma instância de `ExperienceStore` e fornece o método `estimate(context)` que:

1. Recupera todas as experiências previamente salvas com o mesmo hash de contexto (via `ExperienceStore.similar`).
2. Calcula a **probabilidade de vitória** dividindo o número de experiências com `result == "WIN"` pelo total de experiências.
3. Calcula a **recorrência** como o número total de experiências encontradas.
4. Determina um nível de **confiança** simples usando a fórmula `min(1.0, recorrência / 10)`, de modo que 10 ou mais experiências saturam em confiança máxima.
5. Gera uma **recomendação** com base na probabilidade: `WIN` se ≥ 0,6, `LOSS` se ≤ 0,4 e `UNSURE` caso contrário.

O método retorna um dicionário com as métricas calculadas:

```python
{
    "win_probability": 0.6667,
    "recurrence": 3,
    "confidence": 0.3,
    "recommendation": "WIN",
}
```

Esse design é intencionalmente simples, mas prepara o terreno para algoritmos mais sofisticados (e.g., Bayes, decaimento temporal) em futuras missões.

### Testes

O arquivo `tests/test_probability_engine.py` contempla dois cenários:

1. **Nenhuma experiência registrada:** ao estimar probabilidades para um contexto inexistente, o engine retorna zero para probabilidade, recorrência e confiança, e a recomendação `UNSURE`.
2. **Experiências registradas:** três experiências (duas vitórias e uma derrota) são salvas para o mesmo contexto; a estimativa resulta em probabilidade de vitória ≈0,6667, recorrência 3, confiança 0,3 e recomendação `WIN`.  Os testes confirmam esses valores.

### Atualizações de documentação

* **`MISSION_HISTORY.md`** – adicionada seção detalhando a Missão 25.
* **`CURRENT_STATE.md`** – a subseção “Memória e Aprendizado” inclui o `ProbabilityEngine`.
* **`ROADMAP.md`** – a linha referente à Missão 25 foi marcada como **Concluída**.

## Resultado

O Doug.OS agora não apenas grava experiências completas, mas também consegue **extrair estatísticas úteis** dessas experiências.  A probabilidade de vitória, recorrência e confiança permitirão que futuros servos e engines ajustem comportamentos com base em evidências históricas.  Essa capacidade estatística é um passo essencial para o sistema de aprendizagem contínua planejado para a Missão 27.