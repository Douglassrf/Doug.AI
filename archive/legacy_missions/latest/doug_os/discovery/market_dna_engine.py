from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class MarketDNA:
    id: str = field(default_factory=lambda: f"dna_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    behavioral_signature: Dict[str, float] = field(default_factory=dict)
    volatility_dna: Dict[str, float] = field(default_factory=dict)
    liquidity_dna: Dict[str, float] = field(default_factory=dict)
    institutional_dna: Dict[str, float] = field(default_factory=dict)
    news_sensitivity: Dict[str, float] = field(default_factory=dict)
    macro_dna: Dict[str, float] = field(default_factory=dict)
    whale_dna: Dict[str, float] = field(default_factory=dict)
    cycle_dna: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "asset": self.asset,
            "behavioral_signature": self.behavioral_signature,
            "volatility_dna": self.volatility_dna,
            "liquidity_dna": self.liquidity_dna,
            "institutional_dna": self.institutional_dna,
            "news_sensitivity": self.news_sensitivity,
            "macro_dna": self.macro_dna,
            "whale_dna": self.whale_dna,
            "cycle_dna": self.cycle_dna,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class DNADriftResult:
    asset: str = ""
    drift_score: float = 0.0
    components: Dict[str, float] = field(default_factory=dict)
    alert_level: str = "green"
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset": self.asset, "drift_score": self.drift_score,
            "components": self.components, "alert_level": self.alert_level,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class MarketDNAEngine:
    _REQUIRED = ["momentum", "historical_vol", "spread", "volume",
                 "institutional_presence", "price_reaction", "rate_sensitivity"]

    def __init__(self):
        self._dnas: Dict[str, MarketDNA] = {}
        self._drift_history: List[DNADriftResult] = []

    def build_dna(self, asset: str, data: Dict[str, Any]) -> MarketDNA:
        dna = MarketDNA(
            asset=asset,
            behavioral_signature=self._extract_behavioral(data),
            volatility_dna=self._extract_volatility(data),
            liquidity_dna=self._extract_liquidity(data),
            institutional_dna=self._extract_institutional(data),
            news_sensitivity=self._extract_news_sensitivity(data),
            macro_dna=self._extract_macro(data),
            whale_dna=self._extract_whale(data),
            cycle_dna=self._extract_cycle(data),
        )
        dna.confidence = self._calculate_confidence(data)
        self._dnas[asset] = dna
        return dna

    def _extract_behavioral(self, d: Dict) -> Dict[str, float]:
        return {"momentum": d.get("momentum", 0.5), "mean_reversion": d.get("mean_reversion", 0.5),
                "trend_following": d.get("trend_following", 0.5),
                "volatility_clustering": d.get("volatility_clustering", 0.5)}

    def _extract_volatility(self, d: Dict) -> Dict[str, float]:
        return {"historical_vol": d.get("historical_vol", 0.3), "implied_vol": d.get("implied_vol", 0.3),
                "volatility_skew": d.get("volatility_skew", 0.0), "volatility_term": d.get("volatility_term", 0.0)}

    def _extract_liquidity(self, d: Dict) -> Dict[str, float]:
        return {"spread": d.get("spread", 0.5), "depth": d.get("depth", 0.5),
                "volume": d.get("volume", 0.5), "turnover": d.get("turnover", 0.5)}

    def _extract_institutional(self, d: Dict) -> Dict[str, float]:
        return {"institutional_presence": d.get("institutional_presence", 0.3),
                "flow_pattern": d.get("flow_pattern", 0.5),
                "execution_style": d.get("execution_style", 0.5),
                "positioning": d.get("positioning", 0.5)}

    def _extract_news_sensitivity(self, d: Dict) -> Dict[str, float]:
        return {"price_reaction": d.get("price_reaction", 0.5),
                "volume_reaction": d.get("volume_reaction", 0.5),
                "speed_of_absorption": d.get("speed_of_absorption", 0.5),
                "sentiment_dependency": d.get("sentiment_dependency", 0.5)}

    def _extract_macro(self, d: Dict) -> Dict[str, float]:
        return {"rate_sensitivity": d.get("rate_sensitivity", 0.3),
                "inflation_sensitivity": d.get("inflation_sensitivity", 0.3),
                "growth_sensitivity": d.get("growth_sensitivity", 0.3),
                "liquidity_sensitivity": d.get("liquidity_sensitivity", 0.3)}

    def _extract_whale(self, d: Dict) -> Dict[str, float]:
        return {"whale_presence": d.get("whale_presence", 0.3),
                "concentration": d.get("concentration", 0.3),
                "distribution_pattern": d.get("distribution_pattern", 0.5),
                "accumulation_behavior": d.get("accumulation_behavior", 0.5)}

    def _extract_cycle(self, d: Dict) -> Dict[str, float]:
        return {"cycle_amplitude": d.get("cycle_amplitude", 0.5),
                "cycle_frequency": d.get("cycle_frequency", 0.5),
                "cycle_phase": d.get("cycle_phase", 0.5),
                "cycle_stability": d.get("cycle_stability", 0.5)}

    def _calculate_confidence(self, data: Dict) -> float:
        present = sum(1 for f in self._REQUIRED if f in data)
        return min(present / len(self._REQUIRED) * 0.5 + 0.5, 1.0)

    def detect_drift(self, asset: str, new_data: Dict[str, Any]) -> DNADriftResult:
        if asset not in self._dnas:
            return DNADriftResult(asset=asset, alert_level="green",
                                  recommendation="No baseline DNA available")
        current = self._dnas[asset]
        components: Dict[str, float] = {}
        total_drift = 0.0
        dna_fields = [
            ("behavioral_signature", current.behavioral_signature),
            ("volatility_dna", current.volatility_dna),
            ("liquidity_dna", current.liquidity_dna),
            ("institutional_dna", current.institutional_dna),
            ("news_sensitivity", current.news_sensitivity),
            ("macro_dna", current.macro_dna),
            ("whale_dna", current.whale_dna),
            ("cycle_dna", current.cycle_dna),
        ]
        for field_name, dna_dict in dna_fields:
            drifts = [abs(cv - new_data[k]) / (cv + 0.01)
                      for k, cv in dna_dict.items() if k in new_data]
            if drifts:
                avg = sum(drifts) / len(drifts)
                components[field_name] = avg
                total_drift += avg
        drift_score = total_drift / len(components) if components else 0.0
        if drift_score > 0.5:
            level, rec = "red", "Significant DNA drift detected. Asset behavior has changed substantially."
        elif drift_score > 0.3:
            level, rec = "yellow", "Moderate DNA drift detected. Monitor closely."
        else:
            level, rec = "green", "DNA stable. No significant drift detected."
        result = DNADriftResult(asset=asset, drift_score=drift_score, components=components,
                                alert_level=level, recommendation=rec)
        self._drift_history.append(result)
        return result

    def get_dna(self, asset: str) -> Optional[MarketDNA]:
        return self._dnas.get(asset)

    def get_drift_history(self, asset: str) -> List[DNADriftResult]:
        return [d for d in self._drift_history if d.asset == asset]
