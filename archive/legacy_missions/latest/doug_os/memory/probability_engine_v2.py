"""Probability engine v2 (Missão 35).

Esta implementação avança o motor de probabilidade introduzido na
Missão 25 adicionando recorrência temporal, confiança histórica, contexto
de regime e aprendizado por cenário.  A ideia central é atribuir maior
peso às experiências mais recentes e às experiências com o mesmo
regime do contexto atual, refletindo que eventos recentes e
condicionalmente relevantes devem influenciar mais as decisões.

O motor utiliza a ordem de inserção no banco (campo ``id``) como
proxy para o tempo.  Pesos lineares crescentes são aplicados às
experiências conforme a sua posição; ou seja, a experiência mais
antiga tem peso 1, a próxima peso 2, etc.  Se for fornecido um
``regime`` ao estimador, experiências com regime igual recebem um
fator multiplicativo (1.5) no seu peso.  A probabilidade de vitória
peso ponderada é calculada como soma(peso * resultado) / soma(pesos).
Recorrência ponderada é a soma de pesos.  A confiança histórica é
calculada como min(1.0, recorrência_ponderada / 5.0), saturando em 1
com cinco ou mais experiências ponderadas.  A recomendação segue
limiares 0.55 e 0.45 para ``WIN`` e ``LOSS`` respectivamente.

Em futuras versões poderá ser incorporada uma decaimento exponencial
baseado em timestamps reais ou modelos bayesianos mais sofisticados.
"""

from __future__ import annotations

from typing import Dict, Optional

from .experience_store import ExperienceStore


class ProbabilityEngineV2:
    """Calcula probabilidades ponderadas com recência e contexto de regime."""

    def __init__(self, store: ExperienceStore) -> None:
        self.store = store

    def estimate(self, context: Dict, regime: Optional[str] = None) -> Dict[str, float | int | str]:
        """Estimate win probability using weighted experiences.

        Parameters
        ----------
        context : dict
            Contexto atual utilizado para recuperar experiências similares.
        regime : str, optional
            Regime de mercado atual.  Experiências com o mesmo regime
            recebem peso adicional.

        Returns
        -------
        dict
            Dicionário contendo:
            - ``win_probability``: probabilidade ponderada de vitória.
            - ``recurrence``: recorrência ponderada (soma dos pesos).
            - ``confidence``: confiança histórica (recorrência_ponderada/5, saturada em 1).
            - ``recommendation``: ``WIN`` se probabilidade >=0.55, ``LOSS`` se <=0.45, ``UNSURE`` caso contrário.
        """
        # Recuperar todas as experiências com o mesmo contexto pattern
        # Ordenar por id (asc) para que a posição represente o tempo de inserção
        cur = self.store.conn.execute(
            "SELECT result, regime FROM experiences WHERE pattern_hash=? ORDER BY id ASC",
            (self.store._hash(context),),
        )
        rows = cur.fetchall()
        if not rows:
            return {
                "win_probability": 0.0,
                "recurrence": 0,
                "confidence": 0.0,
                "recommendation": "UNSURE",
            }

        total_weighted = 0.0
        win_weighted = 0.0
        for idx, (result, reg) in enumerate(rows, start=1):
            # Base weight increases linearly with position (recent events have greater idx)
            weight = float(idx)
            # Boost weight if regimes match (case insensitive)
            if regime and reg and regime.lower() == reg.lower():
                weight *= 1.5
            total_weighted += weight
            if result == "WIN":
                win_weighted += weight

        win_prob = win_weighted / total_weighted
        # Weighted recurrence
        recurrence = total_weighted
        # Historical confidence saturates after 5 weighted observations
        confidence = min(1.0, recurrence / 5.0)
        if win_prob >= 0.55:
            rec = "WIN"
        elif win_prob <= 0.45:
            rec = "LOSS"
        else:
            rec = "UNSURE"
        return {
            "win_probability": round(win_prob, 4),
            "recurrence": round(recurrence, 2),
            "confidence": round(confidence, 4),
            "recommendation": rec,
        }
