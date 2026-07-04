# ============================================================
# MISSÃO 259 — MARKET OPPORTUNITY RADAR
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class OpportunitySignal:
    """Sinal de oportunidade."""
    id: str = field(default_factory=lambda: f"os_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    type: str = ""
    strength: float = 0.0
    confidence: float = 0.0
    timeframe: str = "short"
    score: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "type": self.type,
            "strength": self.strength,
            "confidence": self.confidence,
            "timeframe": self.timeframe,
            "score": self.score,
            "detected_at": self.detected_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass
class OpportunityHeatMap:
    """Heatmap de oportunidades."""
    id: str = field(default_factory=lambda: f"ohm_{uuid.uuid4().hex[:12]}")
    signals: List[OpportunitySignal] = field(default_factory=list)
    top_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "signals": [s.to_dict() for s in self.signals],
            "top_opportunities": self.top_opportunities,
            "created_at": self.created_at.isoformat(),
        }


class MarketOpportunityRadar:
    """Radar de oportunidades de mercado."""

    def __init__(self):
        self._signals: List[OpportunitySignal] = []
        self._heatmaps: List[OpportunityHeatMap] = []
        self._asset_scores: Dict[str, float] = {}

    def scan_opportunities(self, market_data: Dict[str, Any]) -> List[OpportunitySignal]:
        signals: List[OpportunitySignal] = []
        for detector in (
            self._detect_liquidity_opportunity,
            self._detect_momentum_opportunity,
            self._detect_volatility_opportunity,
            self._detect_institutional_opportunity,
            self._detect_macro_opportunity,
        ):
            opp = detector(market_data)
            if opp:
                signals.append(opp)

        for signal in signals:
            signal.score = self._calculate_opportunity_score(signal)

        self._signals.extend(signals)
        return signals

    def _detect_liquidity_opportunity(self, data: Dict) -> Optional[OpportunitySignal]:
        spread = data.get("spread", 0.1)
        depth = data.get("depth", 0.5)
        if spread < 0.05 and depth > 0.7:
            return OpportunitySignal(
                asset=data.get("asset", "unknown"),
                type="liquidity",
                strength=0.8,
                confidence=0.7,
                timeframe="short",
            )
        return None

    def _detect_momentum_opportunity(self, data: Dict) -> Optional[OpportunitySignal]:
        momentum = data.get("momentum", 0.0)
        trend = data.get("trend_strength", 0.0)
        if abs(momentum) > 0.3 and trend > 0.5:
            return OpportunitySignal(
                asset=data.get("asset", "unknown"),
                type="momentum",
                strength=abs(momentum),
                confidence=trend,
                timeframe="medium",
            )
        return None

    def _detect_volatility_opportunity(self, data: Dict) -> Optional[OpportunitySignal]:
        volatility = data.get("volatility", 0.0)
        if volatility > 0.4:
            return OpportunitySignal(
                asset=data.get("asset", "unknown"),
                type="volatility",
                strength=volatility,
                confidence=0.6,
                timeframe="short",
            )
        return None

    def _detect_institutional_opportunity(self, data: Dict) -> Optional[OpportunitySignal]:
        large_orders = data.get("large_orders", 0)
        institutional_flow = data.get("institutional_flow", 0.0)
        if large_orders > 10 and abs(institutional_flow) > 0.2:
            return OpportunitySignal(
                asset=data.get("asset", "unknown"),
                type="institutional",
                strength=abs(institutional_flow),
                confidence=0.7,
                timeframe="medium",
            )
        return None

    def _detect_macro_opportunity(self, data: Dict) -> Optional[OpportunitySignal]:
        macro_score = data.get("macro_score", 0.0)
        if abs(macro_score) > 0.6:
            return OpportunitySignal(
                asset=data.get("asset", "unknown"),
                type="macro",
                strength=abs(macro_score),
                confidence=0.65,
                timeframe="long",
            )
        return None

    def _calculate_opportunity_score(self, signal: OpportunitySignal) -> float:
        return signal.strength * 0.5 + signal.confidence * 0.3 + 0.2

    def generate_heatmap(self) -> OpportunityHeatMap:
        recent = [
            s for s in self._signals
            if (datetime.now(timezone.utc) - s.detected_at).total_seconds() < 3600
        ]
        top_opps = []
        for signal_type in ["liquidity", "momentum", "volatility", "institutional", "macro"]:
            type_signals = [s for s in recent if s.type == signal_type]
            if type_signals:
                best = max(type_signals, key=lambda x: x.score)
                top_opps.append(best.to_dict())

        heatmap = OpportunityHeatMap(signals=recent[-20:], top_opportunities=top_opps)
        self._heatmaps.append(heatmap)
        return heatmap

    def get_radar_dashboard(self) -> Dict[str, Any]:
        recent = [
            s for s in self._signals
            if (datetime.now(timezone.utc) - s.detected_at).total_seconds() < 3600
        ]
        return {
            "total_signals": len(self._signals),
            "recent_signals": len(recent),
            "by_type": {
                "liquidity": sum(1 for s in recent if s.type == "liquidity"),
                "momentum": sum(1 for s in recent if s.type == "momentum"),
                "volatility": sum(1 for s in recent if s.type == "volatility"),
                "institutional": sum(1 for s in recent if s.type == "institutional"),
                "macro": sum(1 for s in recent if s.type == "macro"),
            },
            "avg_score": np.mean([s.score for s in recent]) if recent else 0,
            "top_opportunity": max(recent, key=lambda x: x.score).to_dict() if recent else None,
        }
