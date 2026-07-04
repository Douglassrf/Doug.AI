from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class MacroData:
    timestamp: datetime
    gdp_growth: float = 0.0
    inflation: float = 0.0
    unemployment: float = 0.0
    interest_rate: float = 0.0
    pmi_manufacturing: float = 0.0
    pmi_services: float = 0.0
    consumer_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "gdp_growth": self.gdp_growth, "inflation": self.inflation,
            "unemployment": self.unemployment, "interest_rate": self.interest_rate,
            "pmi_manufacturing": self.pmi_manufacturing, "pmi_services": self.pmi_services,
            "consumer_confidence": self.consumer_confidence,
        }


@dataclass
class MacroPrediction:
    gdp_forecast: float = 0.0
    inflation_forecast: float = 0.0
    rate_forecast: float = 0.0
    confidence_index: float = 0.0
    regime_transition_score: float = 0.0
    predicted_regime: str = "stable"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gdp_forecast": self.gdp_forecast,
            "inflation_forecast": self.inflation_forecast,
            "rate_forecast": self.rate_forecast,
            "confidence_index": self.confidence_index,
            "regime_transition_score": self.regime_transition_score,
            "predicted_regime": self.predicted_regime,
            "created_at": self.created_at.isoformat(),
        }


class PredictiveMacroEngine:
    def __init__(self):
        self._history: List[MacroData] = []
        self._predictions: List[MacroPrediction] = []

    def predict(self, data: MacroData) -> MacroPrediction:
        self._history.append(data)
        prediction = MacroPrediction(
            gdp_forecast=self._forecast_gdp(data),
            inflation_forecast=self._forecast_inflation(data),
            rate_forecast=self._forecast_rates(data),
            confidence_index=self._calculate_confidence(data),
            regime_transition_score=self._calculate_regime_transition(data),
            predicted_regime=self._predict_regime(data),
        )
        self._predictions.append(prediction)
        return prediction

    def _forecast_gdp(self, data: MacroData) -> float:
        if len(self._history) < 3:
            return float(data.gdp_growth)
        trend = float(np.mean([d.gdp_growth for d in self._history[-3:]]))
        pmi_avg = (data.pmi_manufacturing + data.pmi_services) / 2
        if pmi_avg > 50:
            trend += (pmi_avg - 50) / 100
        return trend

    def _forecast_inflation(self, data: MacroData) -> float:
        if data.inflation == 0:
            return 2.0
        unemployment_gap = data.unemployment - 4.5
        inflation_adjust = -unemployment_gap * 0.2
        growth_adjust = data.gdp_growth * 0.1
        return float(max(data.inflation + inflation_adjust + growth_adjust, 0.0))

    def _forecast_rates(self, data: MacroData) -> float:
        base = data.interest_rate
        adj = (data.inflation - base) * 0.5 if data.inflation > base else 0.0
        if data.gdp_growth > 3:
            adj += 0.25
        return float(base + adj)

    def _calculate_confidence(self, data: MacroData) -> float:
        conf = 0.0
        if data.consumer_confidence > 0:
            conf += data.consumer_confidence / 100 * 0.4
        pmi_avg = (data.pmi_manufacturing + data.pmi_services) / 2
        if pmi_avg > 50:
            conf += (pmi_avg - 50) / 50 * 0.3
        if len(self._history) > 5:
            volatility = float(np.std([d.gdp_growth for d in self._history[-5:]]))
            conf += (1 - min(volatility, 1.0)) * 0.3
        return float(min(conf, 1.0))

    def _calculate_regime_transition(self, data: MacroData) -> float:
        if len(self._history) < 5:
            return 0.0
        recent = self._history[-5:]
        gdp_vol = float(np.std([d.gdp_growth for d in recent]))
        inf_vol = float(np.std([d.inflation for d in recent]))
        return float(min((gdp_vol + inf_vol) / 2, 1.0))

    def _predict_regime(self, data: MacroData) -> str:
        if data.gdp_growth > 2.5 and data.inflation < 3:
            return "expansion"
        if data.gdp_growth < 0:
            return "recession"
        if data.inflation > 4:
            return "inflationary"
        if data.unemployment > 6:
            return "stagnation"
        return "stable"
