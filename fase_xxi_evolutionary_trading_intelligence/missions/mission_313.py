# ============================================================
# MISSÃO 313 — COMPETITIVE ALPHA ANALYZER
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AlphaAnalysis:
    """Análise de Alpha."""

    id: str = field(default_factory=lambda: f"aa_{uuid.uuid4().hex[:12]}")
    alpha_id: str = ""
    persistence_score: float = 0.0
    saturation_score: float = 0.0
    competition_score: float = 0.0
    edge_score: float = 0.0
    opportunity_decay: float = 0.0
    alpha_lifetime_remaining: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alpha_id": self.alpha_id,
            "persistence_score": self.persistence_score,
            "saturation_score": self.saturation_score,
            "competition_score": self.competition_score,
            "edge_score": self.edge_score,
            "opportunity_decay": self.opportunity_decay,
            "alpha_lifetime_remaining": self.alpha_lifetime_remaining,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class CompetitiveAlphaAnalyzer:
    """
    Analisador competitivo de Alpha.

    Implementa:
    - Alpha Persistence
    - Alpha Saturation
    - Alpha Competition
    - Edge Score
    - Opportunity Decay
    - Competitor Pressure
    - Alpha Lifetime
    - Dashboard
    - Learning History
    - Recommendation Engine
    """

    def __init__(self):
        self._analyses: Dict[str, List[AlphaAnalysis]] = {}
        self._alpha_history: Dict[str, List[float]] = {}
        self._learning_history: List[Dict[str, Any]] = []

    def analyze_alpha(
        self,
        alpha_id: str,
        historical_returns: List[float],
        market_returns: List[float],
    ) -> AlphaAnalysis:
        """Analisa competitividade do Alpha."""
        persistence = self._calculate_persistence(historical_returns)
        saturation = self._calculate_saturation(alpha_id, historical_returns)
        competition = self._calculate_competition(historical_returns, market_returns)
        edge = self._calculate_edge_score(historical_returns, market_returns)
        decay = self._calculate_opportunity_decay(historical_returns)
        lifetime = self._estimate_alpha_lifetime(persistence, decay, saturation)
        recommendation = self._generate_recommendation(edge, saturation, competition, lifetime)

        analysis = AlphaAnalysis(
            alpha_id=alpha_id,
            persistence_score=persistence,
            saturation_score=saturation,
            competition_score=competition,
            edge_score=edge,
            opportunity_decay=decay,
            alpha_lifetime_remaining=lifetime,
            recommendation=recommendation,
        )

        if alpha_id not in self._analyses:
            self._analyses[alpha_id] = []
        self._analyses[alpha_id].append(analysis)

        if alpha_id not in self._alpha_history:
            self._alpha_history[alpha_id] = []
        self._alpha_history[alpha_id].extend(historical_returns[-5:])

        self._learning_history.append(
            {
                "alpha_id": alpha_id,
                "analysis_id": analysis.id,
                "edge_score": edge,
                "recommendation": recommendation,
                "timestamp": analysis.created_at.isoformat(),
            }
        )

        return analysis

    def _calculate_persistence(self, returns: List[float]) -> float:
        """Calcula persistência do alpha."""
        if len(returns) < 3:
            return 0.0

        mean_r = float(np.mean(returns))
        std_r = float(np.std(returns)) if len(returns) > 1 else 1.0

        if std_r == 0:
            return 1.0 if mean_r > 0 else 0.0

        sharpe_like = mean_r / std_r
        return min(max(sharpe_like * 0.5 + 0.5, 0.0), 1.0)

    def _calculate_saturation(self, alpha_id: str, returns: List[float]) -> float:
        """Calcula saturação do alpha."""
        history_len = len(self._alpha_history.get(alpha_id, [])) + len(returns)
        return min(history_len / 100.0, 1.0)

    def _calculate_competition(
        self, alpha_returns: List[float], market_returns: List[float]
    ) -> float:
        """Calcula pressão competitiva via correlação com o mercado."""
        if not alpha_returns or not market_returns:
            return 0.5

        min_len = min(len(alpha_returns), len(market_returns))
        corr = np.corrcoef(alpha_returns[-min_len:], market_returns[-min_len:])[0, 1]

        if np.isnan(corr):
            return 0.5

        return min(abs(float(corr)), 1.0)

    def _calculate_edge_score(
        self, alpha_returns: List[float], market_returns: List[float]
    ) -> float:
        """Calcula edge score relativo ao mercado."""
        if not alpha_returns:
            return 0.0

        excess = float(np.mean(alpha_returns))
        if market_returns:
            excess -= float(np.mean(market_returns))

        return min(max(excess * 10 + 0.5, 0.0), 1.0)

    def _calculate_opportunity_decay(self, returns: List[float]) -> float:
        """Calcula decaimento da oportunidade."""
        if len(returns) < 5:
            return 0.0

        recent = returns[-5:]
        older = returns[-10:-5] if len(returns) >= 10 else returns[:-5]

        if not older:
            return 0.0

        decay = max(0.0, float(np.mean(older)) - float(np.mean(recent)))
        return min(decay * 5, 1.0)

    def _estimate_alpha_lifetime(
        self, persistence: float, decay: float, saturation: float
    ) -> float:
        """Estima dias restantes de vida útil do alpha."""
        base = persistence * (1 - decay) * (1 - saturation)
        return min(max(base * 365, 0.0), 365.0)

    def _generate_recommendation(
        self,
        edge: float,
        saturation: float,
        competition: float,
        lifetime: float,
    ) -> str:
        """Gera recomendação operacional."""
        if edge > 0.6 and saturation < 0.5 and lifetime > 90:
            return "scale"
        if edge < 0.3 or lifetime < 30:
            return "retire"
        if saturation > 0.7 or competition > 0.8:
            return "monitor"
        return "maintain"

    def get_alpha_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de análises de alpha."""
        all_analyses = [a for analyses in self._analyses.values() for a in analyses]

        if not all_analyses:
            return {"status": "no_data"}

        recommendations: Dict[str, int] = {}
        for analysis in all_analyses:
            recommendations[analysis.recommendation] = (
                recommendations.get(analysis.recommendation, 0) + 1
            )

        return {
            "total_analyses": len(all_analyses),
            "alphas_tracked": len(self._analyses),
            "avg_edge_score": float(np.mean([a.edge_score for a in all_analyses])),
            "avg_persistence": float(np.mean([a.persistence_score for a in all_analyses])),
            "recommendation_distribution": recommendations,
            "learning_events": len(self._learning_history),
            "recent_analyses": [a.to_dict() for a in all_analyses[-5:]],
        }

    def get_learning_history(self, alpha_id: str | None = None) -> List[Dict[str, Any]]:
        """Retorna histórico de aprendizado."""
        if alpha_id is None:
            return self._learning_history[-20:]
        return [entry for entry in self._learning_history if entry["alpha_id"] == alpha_id]
