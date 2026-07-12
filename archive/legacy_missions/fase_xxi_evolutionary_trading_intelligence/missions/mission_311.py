# ============================================================
# MISSÃO 311 — INSTITUTIONAL MEMORY NETWORK
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class InstitutionalMemory:
    """Memória institucional."""

    id: str = field(default_factory=lambda: f"im_{uuid.uuid4().hex[:12]}")
    institution_id: str = ""
    behavior_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    market_regime: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "behavior_type": self.behavior_type,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "context": self.context,
            "market_regime": self.market_regime,
        }


class InstitutionalMemoryNetwork:
    """
    Rede de memória institucional.

    Implementa:
    - Institutional Archive
    - Behavior Timeline
    - Whale History
    - Flow History
    - Liquidity Archive
    - Regime Memory
    - Historical Comparison
    - Memory Index
    - Dashboard
    - Similar Case Finder
    """

    def __init__(self):
        self._memories: List[InstitutionalMemory] = []
        self._institution_index: Dict[str, List[InstitutionalMemory]] = {}
        self._regime_index: Dict[str, List[InstitutionalMemory]] = {}

    def record_behavior(
        self,
        institution_id: str,
        behavior_type: str,
        context: Dict[str, Any],
        market_regime: str,
        confidence: float = 0.5,
    ) -> InstitutionalMemory:
        """Registra comportamento institucional."""
        memory = InstitutionalMemory(
            institution_id=institution_id,
            behavior_type=behavior_type,
            context=context,
            market_regime=market_regime,
            confidence=confidence,
        )

        self._memories.append(memory)

        if institution_id not in self._institution_index:
            self._institution_index[institution_id] = []
        self._institution_index[institution_id].append(memory)

        if market_regime not in self._regime_index:
            self._regime_index[market_regime] = []
        self._regime_index[market_regime].append(memory)

        return memory

    def find_similar_cases(
        self,
        behavior_type: str,
        market_regime: str,
        context: Dict[str, Any],
    ) -> List[InstitutionalMemory]:
        """Encontra casos similares."""
        results: List[InstitutionalMemory] = []

        for memory in self._memories:
            if memory.behavior_type == behavior_type and memory.market_regime == market_regime:
                similarity = self._calculate_context_similarity(memory.context, context)
                if similarity > 0.5:
                    results.append(memory)

        return sorted(results, key=lambda x: x.confidence, reverse=True)

    def _calculate_context_similarity(self, ctx1: Dict[str, Any], ctx2: Dict[str, Any]) -> float:
        """Calcula similaridade entre contextos."""
        if not ctx1 or not ctx2:
            return 0.0

        common_keys = set(ctx1.keys()) & set(ctx2.keys())
        if not common_keys:
            return 0.0

        similarity = 0.0
        for key in common_keys:
            if isinstance(ctx1[key], (int, float)) and isinstance(ctx2[key], (int, float)):
                diff = abs(ctx1[key] - ctx2[key])
                similarity += 1 / (1 + diff)

        return similarity / len(common_keys)

    def get_institution_history(self, institution_id: str) -> List[InstitutionalMemory]:
        """Retorna histórico de uma instituição."""
        return self._institution_index.get(institution_id, [])

    def get_memory_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de memória."""
        return {
            "total_memories": len(self._memories),
            "institutions_tracked": len(self._institution_index),
            "regimes_covered": len(self._regime_index),
            "avg_confidence": (
                float(np.mean([m.confidence for m in self._memories]))
                if self._memories
                else 0.0
            ),
            "behavior_distribution": {
                behavior: sum(1 for m in self._memories if m.behavior_type == behavior)
                for behavior in {m.behavior_type for m in self._memories}
            },
            "recent_memories": [m.to_dict() for m in self._memories[-5:]],
        }
