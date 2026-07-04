"""Continuous learning loop (Missão 27).

This module defines a simple learning loop that closes the feedback
cycle between execution and analysis.  It ties together the
ExperienceStore and ProbabilityEngine to record outcomes, evaluate
patterns and return recommendations based on historical performance.

The loop is intended to run after each trade or simulated decision.
While the current implementation only returns metrics and a suggested
recommendation, future missions could adjust engine weights or
configuration parameters automatically.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .experience_store import ExperienceStore
from .probability_engine import ProbabilityEngine


class LearningLoop:
    """Encapsulate the experience → memory → evaluation → adjustment pipeline.

    Parameters
    ----------
    store : ExperienceStore
        Persistent storage used to save new experiences.
    engine : ProbabilityEngine
        Engine used to evaluate probabilities from stored experiences.
    """

    def __init__(self, store: ExperienceStore, engine: ProbabilityEngine) -> None:
        self.store = store
        self.engine = engine

    def process_experience(
        self,
        context: Dict,
        regime: str,
        decision: str,
        result: str,
        pnl: float,
    ) -> Dict[str, float | int | str]:
        """Record an experience and compute updated metrics.

        This method represents one iteration of the learning loop.  It
        performs the following steps:

        1. **Experiência**: receives the context, regime, decision and
           outcome of a trade.
        2. **Memória**: stores the experience in the `ExperienceStore`.
        3. **Avaliação**: uses the `ProbabilityEngine` to compute
           probabilities and confidence for the given context.
        4. **Ajuste**: returns the metrics along with the original
           decision.  In future iterations this step may adjust
           parameters or suggest a new decision.

        Parameters
        ----------
        context : dict
            The market context describing the situation when the trade
            occurred.
        regime : str
            The market regime at the time of the decision.
        decision : str
            The decision taken (e.g., ``"BUY"``, ``"SELL"``, ``"HOLD"``).
        result : str
            Outcome of the decision (``"WIN"`` or ``"LOSS"``).
        pnl : float
            Profit or loss of the trade.

        Returns
        -------
        dict
            A dictionary of metrics as returned by `ProbabilityEngine.estimate`,
            with the addition of the `original_decision` for reference.
        """
        # Save the experience to memory
        self.store.save(context, regime, decision, result, pnl)
        # Evaluate probabilities based on updated memory
        metrics = self.engine.estimate(context)
        # Include original decision in output for reference
        metrics_with_decision = dict(metrics)
        metrics_with_decision["original_decision"] = decision
        return metrics_with_decision