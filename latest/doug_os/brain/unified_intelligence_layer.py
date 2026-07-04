"""Unified Intelligence Layer (Missão 37).

Esta camada consolida todas as inteligências do Doug.OS – técnicas,
on‑chain, macroeconômica, notícias, memória e aprendizado – e define
o fluxo completo de decisão conforme especificado no roteiro: sinais
dos servos → Intelligence Council → Brian Supreme → DougBrain →
Shadow Executor.  A implementação aqui integra servos assíncronos,
combina seus sinais via o `IntelligenceCouncil`, revisa o resultado
com `BrianSupremeV1` e retorna um pacote contendo a decisão final e
os diagnósticos do supervisor.

A classe `UnifiedIntelligenceLayer` pode ser estendida nas próximas
missões para incorporar ajustes automáticos a partir do loop de
aprendizado, integração com experiência de probabilidade v2 e
inserção automática de experiências no `ExperienceStore`.
"""

from __future__ import annotations

import asyncio
from typing import Iterable, Dict, Any, Tuple, List

from doug_os.core.doug_bus import DougBus
from doug_os.core.intelligence_council import IntelligenceCouncil
from doug_os.brian.brian_supreme_v1 import BrianSupremeV1
from doug_os.core.intent_vector import IntentVector


class UnifiedIntelligenceLayer:
    """Aggregate servos and produce final decisions with supervisory feedback."""

    def __init__(self, servos: Iterable[Any], supervisor: BrianSupremeV1 | None = None) -> None:
        self.servos = list(servos)
        self.bus = DougBus()
        self.council = IntelligenceCouncil()
        self.supervisor = supervisor or BrianSupremeV1()

    async def process_event(self, market_event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a market event through all layers and return the result.

        Parameters
        ----------
        market_event : dict
            Arbitrary event to be passed to all servos.  Each servo
            extracts the fields of interest.

        Returns
        -------
        dict
            Structure containing the cycle id, raw vectors, council
            decision and supervisor feedback.
        """
        cycle_id, vectors = await self.bus.collect(self.servos, market_event)
        # Determine final decision via the intelligence council
        council_decision = self.council.decide(vectors, cycle_id=cycle_id)
        # Supervisor analyses the raw signals (IntentVectors) for inconsistencies
        supervisor_feedback = self.supervisor.review(vectors)
        return {
            "cycle_id": cycle_id,
            "vectors": [v.to_dict() for v in vectors],
            "decision": council_decision,
            "supervisor": supervisor_feedback,
        }
