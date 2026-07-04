from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class OrderRoute:
    id: str = field(default_factory=lambda: f"route_{uuid.uuid4().hex[:12]}")
    exchange: str = ""
    priority: int = 0
    estimated_fill_time: float = 0.0
    estimated_slippage: float = 0.0
    liquidity_score: float = 0.0
    cost_score: float = 0.0
    reliability: float = 0.0
    route_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "exchange": self.exchange,
            "priority": self.priority,
            "estimated_fill_time": self.estimated_fill_time,
            "estimated_slippage": self.estimated_slippage,
            "liquidity_score": self.liquidity_score,
            "cost_score": self.cost_score,
            "reliability": self.reliability,
            "route_score": self.route_score,
        }


@dataclass
class RoutingDecision:
    id: str = field(default_factory=lambda: f"rd_{uuid.uuid4().hex[:12]}")
    order_id: str = ""
    selected_route: OrderRoute = field(default_factory=OrderRoute)
    alternatives: List[OrderRoute] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "selected_route": self.selected_route.to_dict(),
            "alternatives": [r.to_dict() for r in self.alternatives],
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat(),
        }


class IntelligentOrderRoutingEngine:
    def __init__(self):
        self._routes: List[OrderRoute] = []
        self._decisions: List[RoutingDecision] = []
        self._exchange_metrics: Dict[str, Dict[str, float]] = {}

    def add_exchange_metrics(
        self,
        exchange: str,
        liquidity: float,
        cost: float,
        reliability: float,
        avg_fill_time: float,
    ) -> None:
        self._exchange_metrics[exchange] = {
            "liquidity": liquidity,
            "cost": cost,
            "reliability": reliability,
            "avg_fill_time": avg_fill_time,
        }

    def generate_routes(
        self, order_size: float, order_type: str, market: str
    ) -> List[OrderRoute]:
        routes: List[OrderRoute] = []
        for exchange, m in self._exchange_metrics.items():
            liq = m["liquidity"]
            cost_score = 1.0 - m["cost"]
            rel = m["reliability"]
            fill_time = m["avg_fill_time"] * (1.0 + order_size / 1000.0)
            slippage = (1.0 - liq) * order_size * 0.01
            score = liq * 0.3 + cost_score * 0.3 + rel * 0.25 + (1.0 / (1.0 + fill_time)) * 0.15
            r = OrderRoute(
                exchange=exchange,
                estimated_fill_time=fill_time,
                estimated_slippage=slippage,
                liquidity_score=liq,
                cost_score=cost_score,
                reliability=rel,
                route_score=score,
            )
            routes.append(r)
            self._routes.append(r)
        routes.sort(key=lambda x: x.route_score, reverse=True)
        for i, r in enumerate(routes):
            r.priority = i + 1
        return routes

    def select_route(
        self,
        order_id: str,
        routes: List[OrderRoute],
        preference: str = "balanced",
    ) -> RoutingDecision:
        if not routes:
            return RoutingDecision(order_id=order_id, reasoning="No routes available")
        adjusted: List[OrderRoute] = []
        for r in routes:
            s = r.route_score
            if preference == "fast":
                s = r.route_score * 0.7 + (1.0 / (1.0 + r.estimated_fill_time)) * 0.3
            elif preference == "cheap":
                s = r.route_score * 0.7 + r.cost_score * 0.3
            elif preference == "reliable":
                s = r.route_score * 0.7 + r.reliability * 0.3
            adjusted.append(
                OrderRoute(
                    id=r.id, exchange=r.exchange, priority=r.priority,
                    estimated_fill_time=r.estimated_fill_time,
                    estimated_slippage=r.estimated_slippage,
                    liquidity_score=r.liquidity_score,
                    cost_score=r.cost_score, reliability=r.reliability, route_score=s,
                )
            )
        adjusted.sort(key=lambda x: x.route_score, reverse=True)
        sel = adjusted[0]
        conf = (
            sel.route_score / (sel.route_score + adjusted[1].route_score)
            if len(adjusted) > 1
            else sel.route_score
        )
        reasoning = (
            f"Selected {sel.exchange} for order {order_id} with score {sel.route_score:.2f}. "
            f"Preference: {preference}. Fill time: {sel.estimated_fill_time:.2f}s, "
            f"Slippage: {sel.estimated_slippage:.4f}"
        )
        d = RoutingDecision(
            order_id=order_id, selected_route=sel,
            alternatives=adjusted[1:4], confidence=conf, reasoning=reasoning,
        )
        self._decisions.append(d)
        return d

    def get_route_metrics(self, exchange: str) -> Optional[Dict[str, float]]:
        return self._exchange_metrics.get(exchange)

    def get_routing_summary(self) -> Dict[str, Any]:
        if not self._decisions:
            return {"status": "no_data"}
        counts: Dict[str, int] = {}
        for d in self._decisions:
            counts[d.selected_route.exchange] = counts.get(d.selected_route.exchange, 0) + 1
        return {
            "total_routes": len(self._routes),
            "total_decisions": len(self._decisions),
            "exchange_usage": counts,
            "avg_confidence": float(np.mean([d.confidence for d in self._decisions])),
            "top_exchange": max(counts, key=counts.get) if counts else None,
        }
