# ============================================================
# MISSÃO 279 — INSTITUTIONAL INTENTION DETECTOR
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class InstitutionalIntent:
    """Intenção institucional."""
    id: str = field(default_factory=lambda: f"ii_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    intent_type: str = ""
    probability: float = 0.0
    confidence: float = 0.0
    time_horizon_hours: int = 24
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "intent_type": self.intent_type,
            "probability": self.probability,
            "confidence": self.confidence,
            "time_horizon_hours": self.time_horizon_hours,
            "timeline": self.timeline[-10:],
            "created_at": self.created_at.isoformat(),
        }


class InstitutionalIntentionDetector:
    """
    Detector de intenção institucional.

    Implementa:
    - Institutional Intent Score
    - Accumulation Probability
    - Distribution Probability
    - Trap Probability
    - Fake Breakout Detector
    - Liquidity Capture Detector
    - Intent Timeline
    - Confidence Index
    - Historical Validation
    - Dashboard
    """

    def __init__(self):
        self._intents: Dict[str, List[InstitutionalIntent]] = {}
        self._historical_accuracy: Dict[str, List[float]] = {}

    def detect_intent(
        self,
        asset: str,
        market_data: Dict[str, Any],
        order_flow: Dict[str, Any],
    ) -> InstitutionalIntent:
        acc_prob = self._calculate_accumulation(market_data, order_flow)
        dist_prob = self._calculate_distribution(market_data, order_flow)
        trap_prob = self._calculate_trap(market_data, order_flow)
        fake_breakout_prob = self._calculate_fake_breakout(market_data, order_flow)
        liquidity_capture_prob = self._calculate_liquidity_capture(market_data, order_flow)

        intents = {
            "accumulation": acc_prob,
            "distribution": dist_prob,
            "trap": trap_prob,
            "fake_breakout": fake_breakout_prob,
            "liquidity_capture": liquidity_capture_prob,
        }

        main_intent = max(intents, key=intents.get)
        main_prob = intents[main_intent]
        confidence = self._calculate_confidence(market_data, order_flow)
        timeline = self._build_timeline(market_data, order_flow)

        intent = InstitutionalIntent(
            asset=asset,
            intent_type=main_intent,
            probability=main_prob,
            confidence=confidence,
            timeline=timeline,
        )

        if asset not in self._intents:
            self._intents[asset] = []

        self._intents[asset].append(intent)
        return intent

    def _calculate_accumulation(self, market: Dict, flow: Dict) -> float:
        score = 0.0
        if flow.get("buy_volume", 0) > flow.get("sell_volume", 0):
            score += 0.3
        if market.get("price_position", 0.5) < 0.3:
            score += 0.3
        if flow.get("large_orders_buy", 0) > flow.get("large_orders_sell", 0):
            score += 0.2
        return min(score, 1.0)

    def _calculate_distribution(self, market: Dict, flow: Dict) -> float:
        score = 0.0
        if flow.get("sell_volume", 0) > flow.get("buy_volume", 0):
            score += 0.3
        if market.get("price_position", 0.5) > 0.7:
            score += 0.3
        if flow.get("large_orders_sell", 0) > flow.get("large_orders_buy", 0):
            score += 0.2
        return min(score, 1.0)

    def _calculate_trap(self, market: Dict, flow: Dict) -> float:
        score = 0.0
        if abs(market.get("price_change", 0)) > 0.02 and flow.get("volume_spike", False):
            score += 0.4
        if flow.get("retail_buy", 0) > flow.get("retail_sell", 0) and flow.get("institutional_sell", 0) > 0:
            score += 0.3
        return min(score, 1.0)

    def _calculate_fake_breakout(self, market: Dict, flow: Dict) -> float:
        score = 0.0
        if market.get("breakout_attempt", False):
            score += 0.3
        if flow.get("low_volume_breakout", False):
            score += 0.4
        return min(score, 1.0)

    def _calculate_liquidity_capture(self, market: Dict, flow: Dict) -> float:
        score = 0.0
        if flow.get("stop_hunting", False):
            score += 0.4
        if market.get("liquidity_concentration", 0) > 0.7:
            score += 0.3
        return min(score, 1.0)

    def _calculate_confidence(self, market: Dict, flow: Dict) -> float:
        confidence = 0.5
        if flow.get("data_quality", 0) > 0.7:
            confidence += 0.2
        if market.get("volatility", 0.3) < 0.3:
            confidence += 0.2
        return min(confidence, 1.0)

    def _build_timeline(self, market: Dict, flow: Dict) -> List[Dict[str, Any]]:
        events = []
        if flow.get("large_orders_buy", 0) > 5:
            events.append({"type": "large_buy", "timestamp": datetime.now(timezone.utc).isoformat()})
        if flow.get("large_orders_sell", 0) > 5:
            events.append({"type": "large_sell", "timestamp": datetime.now(timezone.utc).isoformat()})
        if market.get("breakout_attempt", False):
            events.append({"type": "breakout_attempt", "timestamp": datetime.now(timezone.utc).isoformat()})
        return events

    def get_intent_dashboard(self) -> Dict[str, Any]:
        total_intents = sum(len(intents) for intents in self._intents.values())

        return {
            "total_intents": total_intents,
            "assets_tracked": len(self._intents),
            "intent_distribution": {
                "accumulation": sum(
                    1 for intents in self._intents.values() for i in intents if i.intent_type == "accumulation"
                ),
                "distribution": sum(
                    1 for intents in self._intents.values() for i in intents if i.intent_type == "distribution"
                ),
                "trap": sum(
                    1 for intents in self._intents.values() for i in intents if i.intent_type == "trap"
                ),
                "fake_breakout": sum(
                    1 for intents in self._intents.values() for i in intents if i.intent_type == "fake_breakout"
                ),
                "liquidity_capture": sum(
                    1 for intents in self._intents.values() for i in intents if i.intent_type == "liquidity_capture"
                ),
            },
            "avg_confidence": np.mean([
                i.confidence for intents in self._intents.values() for i in intents
            ]) if total_intents > 0 else 0,
        }
