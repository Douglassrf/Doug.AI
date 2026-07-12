from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class ModelRanking:
    model_id: str
    model_name: str
    score: float = 0.0
    symbolic_capital: float = 100.0
    win_rate: float = 0.0
    accuracy_history: List[float] = field(default_factory=list)
    regime_performance: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id, "model_name": self.model_name,
            "score": self.score, "symbolic_capital": self.symbolic_capital,
            "win_rate": self.win_rate, "accuracy_history": self.accuracy_history[-10:],
            "regime_performance": self.regime_performance,
            "last_updated": self.last_updated.isoformat(),
        }


class InternalMarket:
    """Mercado interno onde modelos competem por confiança e capital simbólico."""

    def __init__(self):
        self._models: Dict[str, ModelRanking] = {}
        self._trade_history: List[Dict[str, Any]] = []

    def register_model(self, model_id: str, model_name: str) -> ModelRanking:
        m = ModelRanking(model_id=model_id, model_name=model_name)
        self._models[model_id] = m
        return m

    def trade(self, model_id: str, prediction: Dict[str, Any], actual: Dict[str, Any]) -> float:
        model = self._models.get(model_id)
        if not model: return 0.0
        correct = self._check_prediction(prediction, actual)
        model.accuracy_history.append(1.0 if correct else 0.0)
        if len(model.accuracy_history) > 100:
            model.accuracy_history = model.accuracy_history[-100:]
        model.win_rate = sum(model.accuracy_history) / len(model.accuracy_history)
        capital_change = model.symbolic_capital * (0.05 if correct else -0.03)
        model.symbolic_capital = max(model.symbolic_capital + capital_change, 10.0)
        model.score = model.win_rate * model.symbolic_capital / 100.0
        model.last_updated = datetime.now(timezone.utc)
        self._trade_history.append({
            "model_id": model_id, "correct": correct,
            "capital_change": capital_change,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return model.symbolic_capital

    def _check_prediction(self, prediction: Dict, actual: Dict) -> bool:
        pd_, ad_ = prediction.get("direction", 0), actual.get("direction", 0)
        if pd_ == 0 or ad_ == 0: return False
        return (pd_ > 0 and ad_ > 0) or (pd_ < 0 and ad_ < 0)

    def get_ranking(self) -> List[ModelRanking]:
        return sorted(self._models.values(), key=lambda m: m.score, reverse=True)

    def get_best_model(self) -> Optional[ModelRanking]:
        r = self.get_ranking()
        return r[0] if r else None
