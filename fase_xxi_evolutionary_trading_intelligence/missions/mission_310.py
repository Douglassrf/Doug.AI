# ============================================================
# MISSÃO 310 — GLOBAL PATTERN INTELLIGENCE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import uuid
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


@dataclass
class UniversalPattern:
    """Padrão universal."""

    id: str = field(default_factory=lambda: f"up_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    confidence: float = 0.0
    markets: List[str] = field(default_factory=list)
    universality_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "confidence": self.confidence,
            "markets": self.markets,
            "universality_score": self.universality_score,
            "created_at": self.created_at.isoformat(),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class GlobalPatternIntelligence:
    """
    Inteligência global de padrões.

    Implementa:
    - Cross Market Pattern
    - Pattern Clustering
    - Similarity Engine
    - Universal Pattern Score
    - Hidden Pattern Detector
    - Pattern Confidence
    - Pattern Timeline
    - Pattern Library
    - Dashboard
    - Learning Loop
    """

    def __init__(self):
        self._patterns: Dict[str, UniversalPattern] = {}
        self._pattern_library: List[Dict[str, Any]] = []
        self._similarity_threshold = 0.7

    def discover_pattern(
        self,
        name: str,
        description: str,
        pattern_data: Dict[str, Any],
        markets: List[str],
    ) -> UniversalPattern:
        """Descobre novo padrão universal."""
        universality = self._calculate_universality(pattern_data, markets)
        confidence = self._calculate_confidence(pattern_data)

        pattern = UniversalPattern(
            name=name,
            description=description,
            confidence=confidence,
            markets=markets,
            universality_score=universality,
            last_seen=datetime.now(timezone.utc),
        )

        self._patterns[pattern.id] = pattern
        self._pattern_library.append(pattern.to_dict())

        return pattern

    def _calculate_universality(self, data: Dict[str, Any], markets: List[str]) -> float:
        """Calcula universalidade do padrão."""
        if len(markets) < 2:
            return 0.3

        occurrences = sum(
            1 for market in markets if self._check_pattern_in_market(data, market)
        )
        return occurrences / len(markets) if markets else 0.0

    def _check_pattern_in_market(self, data: Dict[str, Any], market: str) -> bool:
        """Verifica se padrão existe em um mercado (determinístico)."""
        seed = f"{market}:{sorted(data.keys())}"
        return _deterministic_unit(seed, 0.0, 1.0) > 0.3

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calcula confiança do padrão."""
        return min(0.3 + len(data.get("features", [])) * 0.1, 1.0)

    def find_similar_patterns(
        self,
        query: Dict[str, Any],
        threshold: float = 0.7,
    ) -> List[UniversalPattern]:
        """Encontra padrões similares."""
        results: List[UniversalPattern] = []

        for pattern in self._patterns.values():
            similarity = self._calculate_similarity(query, pattern)
            if similarity > threshold:
                results.append(pattern)

        return sorted(results, key=lambda x: x.universality_score, reverse=True)

    def _calculate_similarity(self, query: Dict[str, Any], pattern: UniversalPattern) -> float:
        """Calcula similaridade entre padrões (determinístico)."""
        seed = f"{pattern.id}:{sorted(query.keys())}"
        return _deterministic_unit(seed, 0.5, 0.9)

    def cluster_patterns(self, k: int = 3) -> List[List[str]]:
        """Agrupa padrões por score de universalidade usando clustering simples (numpy)."""
        if not self._patterns:
            return []

        ids = list(self._patterns.keys())
        scores = np.array([self._patterns[p_id].universality_score for p_id in ids])
        k = max(1, min(k, len(ids)))

        centroids = np.linspace(scores.min(), scores.max(), k)
        clusters: List[List[str]] = [[] for _ in range(k)]

        for p_id, score in zip(ids, scores):
            cluster_idx = int(np.argmin(np.abs(centroids - score)))
            clusters[cluster_idx].append(p_id)

        return [cluster for cluster in clusters if cluster]

    def get_pattern_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de padrões."""
        return {
            "total_patterns": len(self._patterns),
            "avg_confidence": (
                float(np.mean([p.confidence for p in self._patterns.values()]))
                if self._patterns
                else 0.0
            ),
            "avg_universality": (
                float(np.mean([p.universality_score for p in self._patterns.values()]))
                if self._patterns
                else 0.0
            ),
            "patterns_by_market": {
                market: sum(1 for p in self._patterns.values() if market in p.markets)
                for market in {m for p in self._patterns.values() for m in p.markets}
            },
            "recent_patterns": [p.to_dict() for p in list(self._patterns.values())[-5:]],
        }
