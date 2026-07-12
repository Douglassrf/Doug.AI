"""Probability engine for experiences (Missão 25).

This module introduces the `ProbabilityEngine`, which consumes
experiences stored in an `ExperienceStore` and derives simple
statistics such as the probability de vitória (win probability), the
number of vezes a situação ocorreu (recurrence) e um nível de confiança.
Essas métricas ajudam a transformar o histórico de operações em um
indicador quantitativo utilizado por camadas superiores.

The engine is deliberately straightforward: it counts wins vs.
losses and scales a confidence factor with the number of samples.  In
missões futuras o algoritmo poderá ser aprimorado com distribuições
bayesianas, ponderações temporalmente decrescentes ou outros modelos.
"""

from __future__ import annotations

from typing import Dict, List

from .experience_store import ExperienceStore


class ProbabilityEngine:
    """Compute probabilities and confidence from recorded experiences.

    Parameters
    ----------
    store : ExperienceStore
        An instance of `ExperienceStore` from which to retrieve
        experiences.  The engine does not mutate the store.
    """

    def __init__(self, store: ExperienceStore) -> None:
        self.store = store

    def estimate(self, context: Dict) -> Dict[str, float | int | str]:
        """Estimate win probability and confidence for a given context.

        Parameters
        ----------
        context : dict
            The context describing the current market situation.

        Returns
        -------
        dict
            A dictionary containing:

            - ``win_probability`` (float): proportion of past experiences
              with this context that resulted in ``"WIN"``.  0.0 if no
              data.
            - ``recurrence`` (int): number of past experiences matching
              this context.
            - ``confidence`` (float): a simple confidence score based on
              sample size, scaled between 0 and 1.  It uses the formula
              ``min(1.0, recurrence / 10)``; thus, 10 or more samples
              yields confidence 1.0.
            - ``recommendation`` (str): a suggested outcome based on the
              win probability: ``"WIN"`` if >=0.6, ``"LOSS"`` if <=0.4
              and ``"UNSURE"`` otherwise.
        """
        experiences: List[Dict] = self.store.similar(context)
        total = len(experiences)
        if total == 0:
            return {
                "win_probability": 0.0,
                "recurrence": 0,
                "confidence": 0.0,
                "recommendation": "UNSURE",
            }
        wins = sum(1 for e in experiences if e.get("result") == "WIN")
        win_prob = wins / total
        # Confidence grows with sample size, saturating at 1.0 at 10 samples
        confidence = min(1.0, total / 10.0)
        # Recommendation logic
        if win_prob >= 0.6:
            rec = "WIN"
        elif win_prob <= 0.4:
            rec = "LOSS"
        else:
            rec = "UNSURE"
        return {
            "win_probability": round(win_prob, 4),
            "recurrence": total,
            "confidence": round(confidence, 4),
            "recommendation": rec,
        }