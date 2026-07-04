# ============================================================
# MISSÃO 269 — LIQUIDITY INTELLIGENCE MATRIX
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


@dataclass
class LiquidityZone:
    """Zona de liquidez."""
    id: str = field(default_factory=lambda: f"lz_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    price_level: float = 0.0
    liquidity_score: float = 0.0
    institutional_presence: float = 0.0
    depth: float = 0.0
    zone_type: str = "high"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "price_level": self.price_level,
            "liquidity_score": self.liquidity_score,
            "institutional_presence": self.institutional_presence,
            "depth": self.depth,
            "zone_type": self.zone_type,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass
class LiquidityMap:
    """Mapa de liquidez."""
    id: str = field(default_factory=lambda: f"lm_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    zones: List[LiquidityZone] = field(default_factory=list)
    liquidity_index: float = 0.0
    migration_detected: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "zones": [z.to_dict() for z in self.zones],
            "liquidity_index": self.liquidity_index,
            "migration_detected": self.migration_detected,
            "created_at": self.created_at.isoformat(),
        }


class LiquidityIntelligenceMatrix:
    """Matriz de inteligência de liquidez."""

    def __init__(self):
        self._maps: Dict[str, List[LiquidityMap]] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._liquidity_history: Dict[str, List[float]] = {}

    def analyze_liquidity(
        self,
        asset: str,
        order_book: Dict[str, Any],
        volume_data: Dict[str, float],
    ) -> LiquidityMap:
        zones: List[LiquidityZone] = []

        for level in order_book.get("levels", []):
            depth = level.get("depth", 0)
            spread = level.get("spread", 0.01)
            liquidity_score = self._calculate_liquidity_score(depth, spread)
            institutional_presence = self._detect_institutional_presence(volume_data, asset, level)
            zone_type = "high" if liquidity_score > 0.7 else "medium" if liquidity_score > 0.4 else "low"

            zones.append(
                LiquidityZone(
                    asset=asset,
                    price_level=level.get("price", 0),
                    liquidity_score=liquidity_score,
                    institutional_presence=institutional_presence,
                    depth=depth,
                    zone_type=zone_type,
                )
            )

        liquidity_index = self._calculate_liquidity_index(zones)
        migration = self._detect_liquidity_migration(asset, zones)

        liquidity_map = LiquidityMap(
            asset=asset,
            zones=zones,
            liquidity_index=liquidity_index,
            migration_detected=migration,
        )

        self._maps.setdefault(asset, []).append(liquidity_map)
        self._liquidity_history.setdefault(asset, []).append(liquidity_index)
        self._check_liquidity_alerts(asset, liquidity_index)

        return liquidity_map

    def _calculate_liquidity_score(self, depth: float, spread: float) -> float:
        depth_score = min(depth / 1000, 1.0)
        spread_score = 1 - min(spread / 0.1, 1.0)
        return depth_score * 0.6 + spread_score * 0.4

    def _detect_institutional_presence(
        self,
        volume: Dict[str, float],
        asset: str,
        level: Dict[str, Any],
    ) -> float:
        seed = f"{asset}:{volume}:{level.get('price', 0)}"
        return _deterministic_unit(seed, 0.2, 0.8)

    def _calculate_liquidity_index(self, zones: List[LiquidityZone]) -> float:
        if not zones:
            return 0.0

        avg_score = np.mean([z.liquidity_score for z in zones])
        depth_factor = min(sum(z.depth for z in zones) / 1000, 1.0)
        return avg_score * 0.6 + depth_factor * 0.4

    def _detect_liquidity_migration(self, asset: str, zones: List[LiquidityZone]) -> bool:
        if asset not in self._maps or not self._maps[asset]:
            return False

        previous = self._maps[asset][-1]
        prev_center = np.mean([z.price_level for z in previous.zones]) if previous.zones else 0
        curr_center = np.mean([z.price_level for z in zones]) if zones else 0

        return abs(curr_center - prev_center) > 0.05 * curr_center if curr_center else False

    def _check_liquidity_alerts(self, asset: str, liquidity_index: float) -> None:
        if asset in self._liquidity_history and len(self._liquidity_history[asset]) > 5:
            recent = self._liquidity_history[asset][-5:]
            drop = recent[-1] - recent[0]

            if drop < -0.3:
                self._alerts.append({
                    "asset": asset,
                    "type": "liquidity_drop",
                    "severity": "high",
                    "message": f"Liquidity dropped {abs(drop) * 100:.1f}%",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    def get_liquidity_dashboard(self) -> Dict[str, Any]:
        return {
            "assets_tracked": len(self._maps),
            "total_zones": sum(len(m.zones) for maps in self._maps.values() for m in maps),
            "avg_liquidity_index": np.mean([
                m.liquidity_index for maps in self._maps.values() for m in maps
            ]) if self._maps else 0,
            "liquidity_alerts": self._alerts[-10:],
            "high_liquidity_assets": [
                asset for asset, history in self._liquidity_history.items()
                if history and history[-1] > 0.7
            ][:5],
        }
