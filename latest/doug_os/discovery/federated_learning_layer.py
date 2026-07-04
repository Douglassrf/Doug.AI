from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ModelUpdate:
    id: str = field(default_factory=lambda: f"mu_{uuid.uuid4().hex[:12]}")
    node_id: str = ""
    model_version: str = ""
    weights: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    privacy_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "model_version": self.model_version,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
            "privacy_score": self.privacy_score,
        }


@dataclass
class FederatedModel:
    id: str = field(default_factory=lambda: f"fm_{uuid.uuid4().hex[:12]}")
    name: str = ""
    version: str = "1.0.0"
    global_weights: Dict[str, Any] = field(default_factory=dict)
    local_updates: List[ModelUpdate] = field(default_factory=list)
    aggregation_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_aggregated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "aggregation_count": self.aggregation_count,
            "created_at": self.created_at.isoformat(),
            "last_aggregated": self.last_aggregated.isoformat() if self.last_aggregated else None,
        }


class FederatedLearningLayer:
    """Camada de aprendizado federado — aggregação segura, privacidade, versionamento."""

    def __init__(self, privacy_threshold: float = 0.7) -> None:
        self._models: Dict[str, FederatedModel] = {}
        self._updates: List[ModelUpdate] = []
        self._privacy_threshold = privacy_threshold

    def create_model(self, name: str, initial_weights: Dict[str, Any]) -> FederatedModel:
        model = FederatedModel(name=name, global_weights=initial_weights)
        self._models[model.id] = model
        return model

    def submit_update(
        self,
        model_id: str,
        node_id: str,
        local_weights: Dict[str, Any],
        metrics: Dict[str, float],
        privacy_score: float = 0.0,
    ) -> ModelUpdate:
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        if privacy_score < self._privacy_threshold:
            raise ValueError(f"Privacy score {privacy_score:.2f} below threshold {self._privacy_threshold:.2f}")

        update = ModelUpdate(
            node_id=node_id,
            model_version=model.version,
            weights=local_weights,
            metrics=metrics,
            privacy_score=privacy_score,
        )
        model.local_updates.append(update)
        self._updates.append(update)
        return update

    def aggregate(self, model_id: str) -> Dict[str, Any]:
        model = self._models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        if not model.local_updates:
            return {"status": "no_updates"}

        aggregated: Dict[str, Any] = {}
        for update in model.local_updates:
            for key, val in update.weights.items():
                aggregated.setdefault(key, []).append(val)

        averaged: Dict[str, Any] = {}
        for key, values in aggregated.items():
            numeric = [v for v in values if isinstance(v, (int, float))]
            averaged[key] = sum(numeric) / len(numeric) if numeric else values[0]

        model.global_weights = averaged
        model.aggregation_count += 1
        model.last_aggregated = datetime.now(timezone.utc)
        model.version = f"{model.version.split('.')[0]}.{model.aggregation_count}"
        model.local_updates.clear()

        return {
            "status": "success",
            "aggregated_weights": averaged,
            "aggregation_count": model.aggregation_count,
        }

    def get_model_metrics(self, model_id: str) -> Dict[str, Any]:
        model = self._models.get(model_id)
        if not model:
            return {}
        all_metrics: Dict[str, List[float]] = {}
        for update in model.local_updates:
            for k, v in update.metrics.items():
                all_metrics.setdefault(k, []).append(v)
        return {
            "model_id": model_id,
            "version": model.version,
            "total_updates": len(model.local_updates),
            "aggregation_count": model.aggregation_count,
            "avg_metrics": {k: sum(v) / len(v) for k, v in all_metrics.items() if v},
        }
