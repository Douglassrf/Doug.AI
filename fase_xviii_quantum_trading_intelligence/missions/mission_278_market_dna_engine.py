# ============================================================
# MISSÃO 278 — MARKET DNA ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AssetDNA:
    """DNA de um ativo."""
    id: str = field(default_factory=lambda: f"dna_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    behavioral_fingerprint: Dict[str, float] = field(default_factory=dict)
    volatility_signature: Dict[str, float] = field(default_factory=dict)
    liquidity_signature: Dict[str, float] = field(default_factory=dict)
    momentum_signature: Dict[str, float] = field(default_factory=dict)
    session_signature: Dict[str, float] = field(default_factory=dict)
    market_personality: str = ""
    dna_evolution: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "behavioral_fingerprint": self.behavioral_fingerprint,
            "volatility_signature": self.volatility_signature,
            "liquidity_signature": self.liquidity_signature,
            "momentum_signature": self.momentum_signature,
            "session_signature": self.session_signature,
            "market_personality": self.market_personality,
            "dna_evolution": self.dna_evolution[-10:],
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MarketDNAEngine:
    """
    Motor de DNA de mercado.

    Implementa:
    - Asset DNA Profile
    - Behavioral Fingerprint
    - Volatility Signature
    - Liquidity Signature
    - Momentum Signature
    - Session Signature
    - Market Personality Index
    - DNA Evolution Tracker
    - DNA Comparison
    - DNA Dashboard
    """

    def __init__(self):
        self._dnas: Dict[str, AssetDNA] = {}
        self._personality_types = [
            "trend_follower",
            "mean_reverter",
            "range_trader",
            "breakout_trader",
            "scalper",
        ]

    def build_dna(self, asset: str, market_data: Dict[str, Any]) -> AssetDNA:
        """Constrói DNA do ativo."""
        behavioral = self._extract_behavioral(market_data)
        volatility = self._extract_volatility(market_data)
        liquidity = self._extract_liquidity(market_data)
        momentum = self._extract_momentum(market_data)
        session = self._extract_session(market_data)
        personality = self._determine_personality(behavioral, volatility)
        confidence = self._calculate_confidence(market_data)

        dna = AssetDNA(
            asset=asset,
            behavioral_fingerprint=behavioral,
            volatility_signature=volatility,
            liquidity_signature=liquidity,
            momentum_signature=momentum,
            session_signature=session,
            market_personality=personality,
            confidence=confidence,
        )

        if asset in self._dnas:
            previous = self._dnas[asset]
            dna.dna_evolution = previous.dna_evolution + [{
                "previous_personality": previous.market_personality,
                "new_personality": personality,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }]

        self._dnas[asset] = dna
        return dna

    def _extract_behavioral(self, data: Dict) -> Dict[str, float]:
        return {
            "trend_consistency": data.get("trend_consistency", 0.5),
            "mean_reversion": data.get("mean_reversion", 0.5),
            "volatility_clustering": data.get("volatility_clustering", 0.5),
            "serial_correlation": data.get("serial_correlation", 0.5),
        }

    def _extract_volatility(self, data: Dict) -> Dict[str, float]:
        return {
            "historical_vol": data.get("historical_vol", 0.3),
            "implied_vol": data.get("implied_vol", 0.3),
            "vol_skew": data.get("vol_skew", 0.0),
            "vol_term": data.get("vol_term", 0.0),
        }

    def _extract_liquidity(self, data: Dict) -> Dict[str, float]:
        return {
            "spread": data.get("spread", 0.5),
            "depth": data.get("depth", 0.5),
            "volume": data.get("volume", 0.5),
            "turnover": data.get("turnover", 0.5),
        }

    def _extract_momentum(self, data: Dict) -> Dict[str, float]:
        return {
            "short_term": data.get("momentum_short", 0.5),
            "medium_term": data.get("momentum_medium", 0.5),
            "long_term": data.get("momentum_long", 0.5),
            "momentum_persistence": data.get("momentum_persistence", 0.5),
        }

    def _extract_session(self, data: Dict) -> Dict[str, float]:
        return {
            "asian_session": data.get("asian_volume", 0.3),
            "european_session": data.get("european_volume", 0.4),
            "american_session": data.get("american_volume", 0.5),
        }

    def _determine_personality(self, behavioral: Dict, volatility: Dict) -> str:
        trend_score = behavioral.get("trend_consistency", 0.5)
        mean_reversion = behavioral.get("mean_reversion", 0.5)
        vol = volatility.get("historical_vol", 0.3)

        if trend_score > 0.7 and vol > 0.3:
            return "trend_follower"
        if mean_reversion > 0.7 and vol < 0.4:
            return "mean_reverter"
        if vol > 0.5:
            return "breakout_trader"
        if vol < 0.2:
            return "range_trader"
        return "scalper"

    def _calculate_confidence(self, data: Dict) -> float:
        required_fields = [
            "trend_consistency",
            "historical_vol",
            "spread",
            "volume",
            "momentum_short",
        ]
        present = sum(1 for f in required_fields if f in data)
        return min(present / len(required_fields) * 0.8 + 0.2, 1.0)

    def compare_dna(self, asset1: str, asset2: str) -> Dict[str, Any]:
        dna1 = self._dnas.get(asset1)
        dna2 = self._dnas.get(asset2)

        if not dna1 or not dna2:
            return {"error": "One or both assets not found"}

        similarity: Dict[str, float] = {}
        total_score = 0.0
        count = 0

        for key in [
            "behavioral_fingerprint",
            "volatility_signature",
            "liquidity_signature",
            "momentum_signature",
        ]:
            sig1 = getattr(dna1, key, {})
            sig2 = getattr(dna2, key, {})

            if sig1 and sig2:
                common_keys = set(sig1.keys()) & set(sig2.keys())
                if common_keys:
                    diff = sum(abs(sig1[k] - sig2[k]) for k in common_keys)
                    similarity[key] = 1 - min(diff / len(common_keys), 1.0)
                    total_score += similarity[key]
                    count += 1

        similarity["overall"] = total_score / count if count > 0 else 0.5

        return {
            "asset1": asset1,
            "asset2": asset2,
            "similarity": similarity,
            "personality_match": dna1.market_personality == dna2.market_personality,
        }

    def get_dna_dashboard(self) -> Dict[str, Any]:
        return {
            "assets_tracked": len(self._dnas),
            "personality_distribution": {
                p: sum(1 for dna in self._dnas.values() if dna.market_personality == p)
                for p in self._personality_types
            },
            "avg_confidence": np.mean([dna.confidence for dna in self._dnas.values()]) if self._dnas else 0,
            "dnas": {asset: dna.to_dict() for asset, dna in list(self._dnas.items())[:5]},
        }
