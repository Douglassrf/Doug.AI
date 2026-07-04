# ============================================================
# MISSÃO 325 — OMEGA MEMORY CONSOLIDATION
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class PhaseMemory:
    """Memória consolidada de uma fase."""

    id: str = field(default_factory=lambda: f"pm_{uuid.uuid4().hex[:12]}")
    phase: str = ""
    mission_range: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "phase": self.phase,
            "mission_range": self.mission_range,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MemoryLink:
    """Link entre memórias de fases."""

    id: str = field(default_factory=lambda: f"ml_{uuid.uuid4().hex[:12]}")
    source_phase: str = ""
    target_phase: str = ""
    link_type: str = ""
    strength: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_phase": self.source_phase,
            "target_phase": self.target_phase,
            "link_type": self.link_type,
            "strength": self.strength,
            "created_at": self.created_at.isoformat(),
        }


class OmegaMemoryConsolidation:
    """
    Consolida memórias de todas as fases em índice unificado.

    Implementa busca, timeline e cross-phase linking.
    """

    def __init__(self):
        self._memories: Dict[str, PhaseMemory] = {}
        self._phase_index: Dict[str, List[str]] = {}
        self._links: List[MemoryLink] = []
        self._timeline: List[Dict[str, Any]] = []

    def register_phase_memory(
        self,
        phase: str,
        mission_range: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> PhaseMemory:
        """Registra memória de uma fase."""
        memory = PhaseMemory(
            phase=phase,
            mission_range=mission_range,
            content=content,
            tags=tags or [],
        )
        self._memories[memory.id] = memory

        if phase not in self._phase_index:
            self._phase_index[phase] = []
        self._phase_index[phase].append(memory.id)

        self._timeline.append(
            {
                "event": "memory_registered",
                "phase": phase,
                "memory_id": memory.id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return memory

    def search(self, query: str) -> List[PhaseMemory]:
        """Busca no índice de memórias."""
        query_lower = query.lower()
        results: List[tuple[PhaseMemory, float]] = []

        for memory in self._memories.values():
            score = 0.0
            if query_lower in memory.phase.lower():
                score += 0.4
            if query_lower in memory.mission_range.lower():
                score += 0.3
            if query_lower in str(memory.content).lower():
                score += 0.2
            if any(query_lower in tag.lower() for tag in memory.tags):
                score += 0.1

            if score > 0:
                results.append((memory, score))

        results.sort(key=lambda item: item[1], reverse=True)
        return [memory for memory, _ in results]

    def link_phases(
        self,
        source_phase: str,
        target_phase: str,
        link_type: str = "evolution",
        strength: float = 0.5,
    ) -> MemoryLink:
        """Cria link entre fases."""
        link = MemoryLink(
            source_phase=source_phase,
            target_phase=target_phase,
            link_type=link_type,
            strength=strength,
        )
        self._links.append(link)

        self._timeline.append(
            {
                "event": "phase_linked",
                "source": source_phase,
                "target": target_phase,
                "link_type": link_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return link

    def get_cross_phase_links(self, phase: str) -> List[MemoryLink]:
        """Retorna links de uma fase."""
        return [
            link
            for link in self._links
            if link.source_phase == phase or link.target_phase == phase
        ]

    def get_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna timeline de consolidação."""
        return self._timeline[-limit:]

    def get_memory_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de memória."""
        return {
            "total_memories": len(self._memories),
            "phases_indexed": len(self._phase_index),
            "total_links": len(self._links),
            "timeline_events": len(self._timeline),
            "phases": list(self._phase_index.keys()),
        }
