# ============================================================
# MISSÃO 331 — COGNITIVE TRADING LOOP (CTL)
# Fase XXII — Evolução Cognitiva Contínua
# ============================================================

from __future__ import annotations

import json
import math
import random
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass
class CognitiveTradeRecord:
    """Registro epistêmico de uma decisão/trade com contexto de mercado."""

    id: str = field(default_factory=lambda: f"ctr_{uuid.uuid4().hex[:12]}")
    strategy_id: str = ""
    pair: str = ""
    params: Dict[str, float] = field(default_factory=dict)
    result: float = 0.0
    market_context: Dict[str, float] = field(default_factory=dict)
    status: str = "SIMULATION"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "pair": self.pair,
            "params": self.params,
            "result": self.result,
            "market_context": self.market_context,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class TradeValidationReport:
    """Veredito pré-trade emitido pelo loop cognitivo."""

    id: str = field(default_factory=lambda: f"tvr_{uuid.uuid4().hex[:12]}")
    strategy_id: str = ""
    pair: str = ""
    probability: float = 0.0
    similar_scenarios: int = 0
    total_scenarios: int = 0
    verdict: str = "STANDBY"
    reasons: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "pair": self.pair,
            "probability": self.probability,
            "similar_scenarios": self.similar_scenarios,
            "total_scenarios": self.total_scenarios,
            "verdict": self.verdict,
            "reasons": self.reasons,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GeneticEvolutionReport:
    """Relatório de evolução de DNA estratégico."""

    id: str = field(default_factory=lambda: f"ger_{uuid.uuid4().hex[:12]}")
    parent_params: Dict[str, float] = field(default_factory=dict)
    child_params: Dict[str, float] = field(default_factory=dict)
    promoted: bool = False
    fitness_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_params": self.parent_params,
            "child_params": self.child_params,
            "promoted": self.promoted,
            "fitness_score": self.fitness_score,
            "created_at": self.created_at.isoformat(),
        }


class CognitiveMemory:
    """Memória SQLite que preserva contexto, parâmetros e resultados."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_schema()

    def create_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cognitive_trades (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                pair TEXT NOT NULL,
                params TEXT NOT NULL,
                result REAL NOT NULL,
                market_context TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cognitive_pair_strategy ON cognitive_trades(pair, strategy_id, created_at)"
        )
        self.conn.commit()

    def record_trade(
        self,
        strategy_id: str,
        pair: str,
        params: Dict[str, float],
        result: float,
        market_context: Dict[str, float],
        status: str = "SIMULATION",
    ) -> CognitiveTradeRecord:
        record = CognitiveTradeRecord(
            strategy_id=strategy_id,
            pair=pair,
            params=params,
            result=float(result),
            market_context=market_context,
            status=status,
        )
        self.conn.execute(
            """
            INSERT INTO cognitive_trades
            (id, created_at, strategy_id, pair, params, result, market_context, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.created_at.isoformat(),
                record.strategy_id,
                record.pair,
                json.dumps(record.params, sort_keys=True),
                record.result,
                json.dumps(record.market_context, sort_keys=True),
                record.status,
            ),
        )
        self.conn.commit()
        return record

    def fetch_recent(self, pair: str, strategy_id: Optional[str] = None, limit: int = 100) -> List[CognitiveTradeRecord]:
        params: List[Any] = [pair]
        where = "pair = ?"
        if strategy_id:
            where += " AND strategy_id = ?"
            params.append(strategy_id)
        params.append(limit)
        rows = self.conn.execute(
            f"SELECT * FROM cognitive_trades WHERE {where} ORDER BY created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: sqlite3.Row) -> CognitiveTradeRecord:
        return CognitiveTradeRecord(
            id=row["id"],
            strategy_id=row["strategy_id"],
            pair=row["pair"],
            params=json.loads(row["params"]),
            result=float(row["result"]),
            market_context=json.loads(row["market_context"]),
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class CognitiveTradingLoop:
    """Orquestra memória, validação por similaridade, evolução e proteção de capital."""

    DNA_LIMITS: Dict[str, Tuple[float, float]] = {
        "rsi_period": (7.0, 21.0),
        "band_width": (10.0, 30.0),
        "stop_loss_pct": (0.5, 2.0),
    }

    def __init__(
        self,
        memory: Optional[CognitiveMemory] = None,
        approval_threshold: float = 0.72,
        min_samples: int = 20,
        similarity_tolerance: float = 0.12,
        random_seed: Optional[int] = 42,
    ):
        self.memory = memory or CognitiveMemory()
        self.approval_threshold = approval_threshold
        self.min_samples = min_samples
        self.similarity_tolerance = similarity_tolerance
        self.random = random.Random(random_seed)
        self._validations: List[TradeValidationReport] = []
        self._evolutions: List[GeneticEvolutionReport] = []

    def validate_trade(self, strategy_id: str, pair: str, current_context: Dict[str, float]) -> TradeValidationReport:
        scenarios = self.memory.fetch_recent(pair=pair, strategy_id=strategy_id, limit=100)
        similar = [s for s in scenarios if self._is_similar(current_context, s.market_context)]
        reasons: List[str] = []

        if len(scenarios) < self.min_samples:
            reasons.append("Amostra histórica insuficiente para liberar operação.")
        if len(similar) < max(5, self.min_samples // 4):
            reasons.append("Poucos cenários semelhantes encontrados na memória.")

        probability = self._empirical_probability(similar) if similar else 0.0
        if probability < self.approval_threshold:
            reasons.append("Probabilidade empírica abaixo do limiar de aprovação.")

        significant = self.is_statistically_significant([s.result for s in similar])
        if not significant:
            reasons.append("Vantagem recente sem significância estatística mínima.")

        verdict = "APPROVED" if not reasons else "STANDBY"
        report = TradeValidationReport(
            strategy_id=strategy_id,
            pair=pair,
            probability=probability,
            similar_scenarios=len(similar),
            total_scenarios=len(scenarios),
            verdict=verdict,
            reasons=reasons,
        )
        self._validations.append(report)
        return report

    def evolve_dna(self, parent_params: Dict[str, float], fitness_results: Sequence[float]) -> GeneticEvolutionReport:
        fitness_score = mean(fitness_results) if fitness_results else 0.0
        child: Dict[str, float] = {}
        for key, (lower, upper) in self.DNA_LIMITS.items():
            base = float(parent_params.get(key, (lower + upper) / 2))
            mutation = self.random.uniform(0.90, 1.10)
            child[key] = max(lower, min(upper, base * mutation))

        promoted = fitness_score > 0 and self.is_statistically_significant(fitness_results, min_count=10)
        report = GeneticEvolutionReport(
            parent_params=parent_params.copy(),
            child_params=child,
            promoted=promoted,
            fitness_score=fitness_score,
        )
        self._evolutions.append(report)
        return report

    def protective_verdict(self, strategy_id: str, pair: str) -> str:
        recent = self.memory.fetch_recent(pair=pair, strategy_id=strategy_id, limit=30)
        if len(recent) < self.min_samples:
            return "PROTECTIVE_STOP"
        drawdown_like_losses = sum(1 for record in recent[:10] if record.result < 0)
        if drawdown_like_losses >= 7:
            return "PROTECTIVE_STOP"
        return "MONITORING" if self.is_statistically_significant([r.result for r in recent]) else "PROTECTIVE_STOP"

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "approval_threshold": self.approval_threshold,
            "min_samples": self.min_samples,
            "validations": len(self._validations),
            "evolutions": len(self._evolutions),
            "latest_validation": self._validations[-1].to_dict() if self._validations else None,
            "latest_evolution": self._evolutions[-1].to_dict() if self._evolutions else None,
        }

    def _is_similar(self, current: Dict[str, float], historical: Dict[str, float]) -> bool:
        comparable = set(current).intersection(historical)
        if not comparable:
            return False
        distances = []
        for key in comparable:
            baseline = max(abs(float(historical[key])), 1.0)
            distances.append(abs(float(current[key]) - float(historical[key])) / baseline)
        return mean(distances) <= self.similarity_tolerance

    def _empirical_probability(self, records: Iterable[CognitiveTradeRecord]) -> float:
        values = [record.result for record in records]
        return sum(1 for value in values if value > 0) / len(values) if values else 0.0

    def is_statistically_significant(self, results: Sequence[float], min_count: int = 20) -> bool:
        if len(results) < min_count:
            return False
        avg = mean(results)
        deviation = pstdev(results) or 1e-9
        t_like_score = avg / (deviation / math.sqrt(len(results)))
        return avg > 0 and t_like_score >= 1.65
