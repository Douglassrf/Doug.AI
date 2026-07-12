"""Mission 335 — Capital Router: aloca capital nos Top-N ativos aprovados (Talent Show)."""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AssetOpportunity:
    """Score de oportunidade para um ativo."""
    id: str = field(default_factory=lambda: f"ao_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    cluster: str = "other"          # crypto | fx | commodities | equities | other
    confidence: float = 0.0
    regime_quality: float = 0.5
    historical_win_rate: float = 0.5
    liquidity_score: float = 1.0
    correlation_penalty: float = 0.0
    opportunity_score: float = 0.0
    action: str = "HOLD"
    allocated_fraction: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "cluster": self.cluster,
            "confidence": self.confidence,
            "regime_quality": self.regime_quality,
            "historical_win_rate": self.historical_win_rate,
            "liquidity_score": self.liquidity_score,
            "correlation_penalty": self.correlation_penalty,
            "opportunity_score": self.opportunity_score,
            "action": self.action,
            "allocated_fraction": self.allocated_fraction,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CapitalAllocation:
    """Alocação final de capital após o Talent Show."""
    id: str = field(default_factory=lambda: f"ca_{uuid.uuid4().hex[:12]}")
    top_assets: List[AssetOpportunity] = field(default_factory=list)
    rejected_assets: List[AssetOpportunity] = field(default_factory=list)
    total_slots: int = 3
    used_slots: int = 0
    daily_loss_used: float = 0.0        # R perdido no dia
    budget_ok: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "top_assets": [a.to_dict() for a in self.top_assets],
            "rejected_count": len(self.rejected_assets),
            "total_slots": self.total_slots,
            "used_slots": self.used_slots,
            "daily_loss_used": self.daily_loss_used,
            "budget_ok": self.budget_ok,
            "created_at": self.created_at.isoformat(),
        }


class CapitalRouter:
    """
    Talent Show de ativos: recebe N candidatos aprovados pelo Preflight + Red Team,
    calcula opportunity_score e aloca capital nos Top-K com restrições de cluster
    e orçamento diário de perdas.

    opportunity_score =
        confidence × regime_quality × historical_win_rate × liquidity_score
        × (1 - correlation_penalty)

    Regras:
    - Máx. max_per_cluster ativos do mesmo cluster entre os selecionados
    - Se daily_loss ≥ daily_loss_budget → slots subsequentes reduzidos 50%
    - Slot 0 perde 2R → slots 1,2 reduzem automaticamente
    """

    def __init__(
        self,
        top_k: int = 3,
        max_per_cluster: int = 2,
        daily_loss_budget_r: float = 4.0,
        seed: int = 42,
    ) -> None:
        self._top_k = top_k
        self._max_per_cluster = max_per_cluster
        self._daily_loss_budget_r = daily_loss_budget_r
        self._daily_loss_used: float = 0.0
        self._allocations: List[CapitalAllocation] = []
        self._win_rates: Dict[str, List[float]] = {}  # histórico por ativo
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ #
    #  Win Rate histórico                                                  #
    # ------------------------------------------------------------------ #

    def record_result(self, asset: str, won: bool) -> None:
        self._win_rates.setdefault(asset, []).append(1.0 if won else 0.0)

    def get_win_rate(self, asset: str) -> float:
        history = self._win_rates.get(asset, [])
        if not history:
            return 0.50  # prior neutro
        return float(np.mean(history[-50:]))  # últimos 50 trades

    def reset_daily_loss(self) -> None:
        self._daily_loss_used = 0.0

    def record_loss(self, r_value: float) -> None:
        self._daily_loss_used += abs(r_value)

    # ------------------------------------------------------------------ #
    #  Scoring                                                             #
    # ------------------------------------------------------------------ #

    def _compute_score(self, opp: AssetOpportunity) -> float:
        win_rate = self.get_win_rate(opp.asset)
        score = (
            opp.confidence
            * opp.regime_quality
            * win_rate
            * opp.liquidity_score
            * (1.0 - opp.correlation_penalty)
        )
        return float(min(1.0, max(0.0, score)))

    def _correlation_penalty(
        self, asset: str, cluster: str, selected: List[AssetOpportunity]
    ) -> float:
        """Penaliza se cluster já tem muitos ativos selecionados."""
        cluster_count = sum(1 for a in selected if a.cluster == cluster)
        if cluster_count == 0:
            return 0.0
        elif cluster_count == 1:
            return 0.20
        else:
            return 0.50

    # ------------------------------------------------------------------ #
    #  Main route                                                          #
    # ------------------------------------------------------------------ #

    def route(
        self,
        candidates: List[Dict[str, Any]],
    ) -> CapitalAllocation:
        """
        candidates: lista de dicts com chaves:
            asset, cluster, confidence, regime_quality, liquidity_score, action
        """
        if not candidates:
            alloc = CapitalAllocation(total_slots=self._top_k, used_slots=0)
            self._allocations.append(alloc)
            return alloc

        # Converte candidatos em AssetOpportunity
        opps: List[AssetOpportunity] = []
        for c in candidates:
            opp = AssetOpportunity(
                asset=c.get("asset", "UNKNOWN"),
                cluster=c.get("cluster", "other"),
                confidence=float(c.get("confidence", 0.5)),
                regime_quality=float(c.get("regime_quality", 0.5)),
                liquidity_score=float(c.get("liquidity_score", 1.0)),
                action=c.get("action", "HOLD"),
            )
            opps.append(opp)

        # Ordena por score preliminar (sem penalidade de correlação)
        for opp in opps:
            opp.opportunity_score = self._compute_score(opp)
        opps.sort(key=lambda o: o.opportunity_score, reverse=True)

        # Seleciona Top-K respeitando max_per_cluster
        selected: List[AssetOpportunity] = []
        rejected: List[AssetOpportunity] = []
        cluster_counts: Dict[str, int] = {}

        for opp in opps:
            if len(selected) >= self._top_k:
                rejected.append(opp)
                continue

            cluster = opp.cluster
            count = cluster_counts.get(cluster, 0)
            if count >= self._max_per_cluster:
                rejected.append(opp)
                continue

            # Recalcula com penalidade real de correlação
            opp.correlation_penalty = self._correlation_penalty(
                opp.asset, cluster, selected
            )
            opp.opportunity_score = self._compute_score(opp)

            selected.append(opp)
            cluster_counts[cluster] = count + 1

        # Calcula fração de capital por slot
        budget_remaining = max(0.0, self._daily_loss_budget_r - self._daily_loss_used)
        budget_ok = self._daily_loss_used < self._daily_loss_budget_r

        base_fraction = 1.0 / max(1, len(selected))
        for i, opp in enumerate(selected):
            # Slots posteriores reduzidos se orçamento de perda está gasto
            if not budget_ok and i > 0:
                opp.allocated_fraction = base_fraction * 0.5
            else:
                opp.allocated_fraction = base_fraction

        alloc = CapitalAllocation(
            top_assets=selected,
            rejected_assets=rejected,
            total_slots=self._top_k,
            used_slots=len(selected),
            daily_loss_used=self._daily_loss_used,
            budget_ok=budget_ok,
        )
        self._allocations.append(alloc)
        return alloc

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_ranking(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Retorna ranking de oportunidades sem alocar capital."""
        ranked = []
        for c in candidates:
            opp = AssetOpportunity(
                asset=c.get("asset", "?"),
                cluster=c.get("cluster", "other"),
                confidence=float(c.get("confidence", 0.5)),
                regime_quality=float(c.get("regime_quality", 0.5)),
                liquidity_score=float(c.get("liquidity_score", 1.0)),
            )
            opp.opportunity_score = self._compute_score(opp)
            ranked.append(opp.to_dict())
        ranked.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return ranked

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._allocations)
        if total == 0:
            return {"total_allocations": 0}
        avg_slots = np.mean([a.used_slots for a in self._allocations])
        return {
            "total_allocations": total,
            "avg_slots_used": round(float(avg_slots), 2),
            "daily_loss_used": round(self._daily_loss_used, 4),
            "daily_loss_budget": self._daily_loss_budget_r,
            "tracked_assets": len(self._win_rates),
        }
