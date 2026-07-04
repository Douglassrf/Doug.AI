from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class ModelPrediction:
    id: str = field(default_factory=lambda: f"mp_{uuid.uuid4().hex[:12]}")
    model_id: str = ""
    prediction: Any = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "model_id": self.model_id,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConsensusResult:
    id: str = field(default_factory=lambda: f"cr_{uuid.uuid4().hex[:12]}")
    predictions: List[ModelPrediction] = field(default_factory=list)
    consensus_value: Any = None
    consensus_confidence: float = 0.0
    agreement_score: float = 0.0
    method: str = "weighted_average"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "consensus_value": self.consensus_value,
            "consensus_confidence": self.consensus_confidence,
            "agreement_score": self.agreement_score,
            "method": self.method,
            "num_models": len(self.predictions),
            "timestamp": self.timestamp.isoformat(),
        }


class MultiModelConsensusEngine:
    """Motor de consenso multi-modelo — agrega previsões com ponderação por confiança."""

    def __init__(self, min_models: int = 2, confidence_threshold: float = 0.5) -> None:
        self._models: Dict[str, Dict[str, Any]] = {}
        self._results: List[ConsensusResult] = []
        self._min_models = min_models
        self._confidence_threshold = confidence_threshold

    def register_model(self, name: str, weight: float = 1.0, model_type: str = "general") -> str:
        model_id = f"model_{uuid.uuid4().hex[:8]}"
        self._models[model_id] = {"name": name, "weight": weight, "type": model_type}
        return model_id

    def submit_prediction(
        self,
        model_id: str,
        prediction: Any,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelPrediction:
        if model_id not in self._models:
            raise ValueError(f"Model {model_id} not registered")
        pred = ModelPrediction(
            model_id=model_id,
            prediction=prediction,
            confidence=confidence,
            metadata=metadata or {},
        )
        return pred

    def compute_consensus(self, predictions: List[ModelPrediction], method: str = "weighted_average") -> ConsensusResult:
        valid = [p for p in predictions if p.confidence >= self._confidence_threshold]
        if len(valid) < self._min_models:
            return ConsensusResult(
                predictions=predictions,
                consensus_value=None,
                consensus_confidence=0.0,
                agreement_score=0.0,
                method=method,
            )

        if method == "weighted_average":
            numeric = [p for p in valid if isinstance(p.prediction, (int, float))]
            if numeric:
                weights = np.array([
                    self._models.get(p.model_id, {}).get("weight", 1.0) * p.confidence
                    for p in numeric
                ])
                values = np.array([float(p.prediction) for p in numeric])
                total_w = weights.sum()
                consensus_val = float((weights * values).sum() / total_w) if total_w > 0 else 0.0
            else:
                votes: Dict[Any, float] = {}
                for p in valid:
                    w = self._models.get(p.model_id, {}).get("weight", 1.0) * p.confidence
                    votes[p.prediction] = votes.get(p.prediction, 0.0) + w
                consensus_val = max(votes, key=lambda k: votes[k])

            avg_confidence = float(np.mean([p.confidence for p in valid]))
            unique_preds = len({p.prediction for p in valid})
            agreement = 1.0 - (unique_preds - 1) / max(len(valid), 1)

        else:
            raise ValueError(f"Unknown method: {method}")

        result = ConsensusResult(
            predictions=predictions,
            consensus_value=consensus_val,
            consensus_confidence=avg_confidence,
            agreement_score=max(0.0, min(1.0, agreement)),
            method=method,
        )
        self._results.append(result)
        return result

    def get_consensus_metrics(self) -> Dict[str, Any]:
        if not self._results:
            return {"status": "no_results"}
        return {
            "total_rounds": len(self._results),
            "avg_confidence": sum(r.consensus_confidence for r in self._results) / len(self._results),
            "avg_agreement": sum(r.agreement_score for r in self._results) / len(self._results),
            "registered_models": len(self._models),
        }
