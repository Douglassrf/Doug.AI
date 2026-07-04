from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class Context:
    id: str = field(default_factory=lambda: f"ctx_{__import__('uuid').uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    market: Dict[str, Any] = field(default_factory=dict)
    macro: Dict[str, Any] = field(default_factory=dict)
    temporal: Dict[str, Any] = field(default_factory=dict)
    portfolio: Dict[str, Any] = field(default_factory=dict)
    risk: Dict[str, Any] = field(default_factory=dict)
    news: Dict[str, Any] = field(default_factory=dict)
    behavioral: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    relevance_score: float = 0.5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "timestamp": self.timestamp.isoformat(),
            "market": self.market, "macro": self.macro, "temporal": self.temporal,
            "portfolio": self.portfolio, "risk": self.risk, "news": self.news,
            "behavioral": self.behavioral, "confidence": self.confidence,
            "relevance_score": self.relevance_score, "created_at": self.created_at.isoformat(),
        }


class ContextAwarenessEngine:
    def __init__(self):
        self._contexts: List[Context] = []
        self._current_context: Optional[Context] = None

    def build_context(self, market_data: Dict, macro_data: Dict, temporal_data: Dict,
                      portfolio_data: Dict, risk_data: Dict, news_data: Dict,
                      behavioral_data: Dict) -> Context:
        all_data = {"market": market_data, "macro": macro_data, "temporal": temporal_data,
                    "portfolio": portfolio_data, "risk": risk_data, "news": news_data,
                    "behavioral": behavioral_data}
        ctx = Context(
            market=market_data, macro=macro_data, temporal=temporal_data,
            portfolio=portfolio_data, risk=risk_data, news=news_data,
            behavioral=behavioral_data,
            confidence=self._calculate_confidence(all_data),
            relevance_score=self._calculate_relevance(
                {"market": market_data, "macro": macro_data, "temporal": temporal_data}),
        )
        self._contexts.append(ctx)
        self._current_context = ctx
        return ctx

    def _calculate_confidence(self, data: Dict[str, Dict]) -> float:
        scores = []
        for v in data.values():
            if isinstance(v, dict):
                nums = [x for x in v.values() if isinstance(x, (int, float))]
                if nums: scores.append(float(np.mean(nums)))
        return float(min(np.mean(scores), 1.0)) if scores else 0.5

    def _calculate_relevance(self, data: Dict[str, Dict]) -> float:
        rel = 0.5
        if data.get("market"): rel += 0.2
        if data.get("macro"): rel += 0.2
        if data.get("temporal"): rel += 0.1
        return min(rel, 1.0)

    def get_current_context(self) -> Optional[Context]:
        return self._current_context

    def get_contexts_in_range(self, start: datetime, end: datetime) -> List[Context]:
        return [c for c in self._contexts if start <= c.timestamp <= end]

    def get_context_summary(self) -> Dict[str, Any]:
        if not self._current_context:
            return {"status": "no_context"}
        ctx = self._current_context
        return {
            "market_regime": ctx.market.get("regime", "unknown"),
            "macro_regime": ctx.macro.get("regime", "unknown"),
            "risk_level": ctx.risk.get("level", "unknown"),
            "temporal_horizon": ctx.temporal.get("horizon", "unknown"),
            "confidence": ctx.confidence,
            "relevance": ctx.relevance_score,
        }
