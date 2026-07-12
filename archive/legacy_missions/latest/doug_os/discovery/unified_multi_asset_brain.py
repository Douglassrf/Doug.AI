from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class UnifiedView:
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    global_risk_score: float = 0.0
    liquidity_score: float = 0.0
    regime: str = "unknown"
    asset_scores: Dict[str, float] = field(default_factory=dict)
    correlations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    recommendation: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "global_risk_score": self.global_risk_score,
            "liquidity_score": self.liquidity_score,
            "regime": self.regime,
            "asset_scores": self.asset_scores,
            "correlations": self.correlations,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
        }


class UnifiedMultiAssetBrain:
    _ASSET_CLASSES = ["crypto", "forex", "commodity", "bond", "equity", "stablecoin"]

    def __init__(self):
        self._views: List[UnifiedView] = []

    def integrate(self, market_data: Dict[str, Dict[str, Any]]) -> UnifiedView:
        asset_scores = self._calculate_asset_scores(market_data)
        correlations = self._calculate_correlations(market_data)
        risk_score = self._calculate_global_risk(asset_scores, correlations)
        liquidity_score = self._calculate_liquidity(market_data)
        regime = self._determine_regime(asset_scores, risk_score)
        recommendation = self._generate_recommendation(asset_scores, regime)
        confidence = self._calculate_confidence(asset_scores)
        view = UnifiedView(
            global_risk_score=risk_score, liquidity_score=liquidity_score,
            regime=regime, asset_scores=asset_scores, correlations=correlations,
            recommendation=recommendation, confidence=confidence,
        )
        self._views.append(view)
        return view

    def _calculate_asset_scores(self, data: Dict[str, Dict]) -> Dict[str, float]:
        scores = {}
        for ac in self._ASSET_CLASSES:
            if ac in data:
                d = data[ac]
                momentum = d.get("momentum", 0.5)
                volatility = d.get("volatility", 0.5)
                volume = d.get("volume", 0.5)
                scores[ac] = float(min(max(momentum * 0.4 + (1 - volatility) * 0.3 + volume * 0.3, 0.0), 1.0))
            else:
                scores[ac] = 0.5
        return scores

    def _calculate_correlations(self, data: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
        corr: Dict[str, Dict[str, float]] = {}
        for a in self._ASSET_CLASSES:
            corr[a] = {}
            for b in self._ASSET_CLASSES:
                corr[a][b] = 1.0 if a == b else (0.3 if (a in data and b in data) else 0.0)
        return corr

    def _calculate_global_risk(self, scores: Dict[str, float], correlations: Dict) -> float:
        avg_risk = float(np.mean([1 - s for s in scores.values()]))
        cross_corrs = [
            correlations[a][b]
            for a in correlations for b in correlations[a]
            if a != b
        ]
        corr_penalty = float(np.mean(cross_corrs)) * 0.3 if cross_corrs else 0.0
        return float(min(avg_risk + corr_penalty, 1.0))

    def _calculate_liquidity(self, data: Dict[str, Dict]) -> float:
        scores = [min(data[ac].get("volume", 0) / 1000, 1.0) for ac in self._ASSET_CLASSES if ac in data]
        return float(np.mean(scores)) if scores else 0.5

    def _determine_regime(self, scores: Dict[str, float], risk: float) -> str:
        if risk > 0.7: return "crisis"
        if risk > 0.5: return "high_risk"
        if risk < 0.3: return "low_risk"
        best = max(scores, key=scores.get)
        if scores[best] > 0.7: return f"{best}_dominant"
        return "neutral"

    def _generate_recommendation(self, scores: Dict[str, float], regime: str) -> str:
        if regime == "crisis": return "Reduce exposure. Focus on safe havens."
        if regime == "high_risk": return "Caution advised. Consider defensive positioning."
        if regime == "low_risk": return "Favorable environment. Consider risk-on assets."
        best = max(scores, key=scores.get)
        return f"Opportunity in {best}. Score: {scores[best]:.2f}"

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        std = float(np.std(list(scores.values())))
        return float(min(1 - min(std, 0.5), 1.0))
