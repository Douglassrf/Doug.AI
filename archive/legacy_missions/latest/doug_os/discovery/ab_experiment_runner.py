"""Mission 339 — A/B Experiment Runner: testa estratégias em paralelo com capital mínimo."""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class TradeResult:
    group: str = "A"
    won: bool = False
    pnl: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group": self.group,
            "won": self.won,
            "pnl": round(self.pnl, 4),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExperimentResult:
    id: str = field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:12]}")
    name: str = ""
    group_a_trades: int = 0
    group_b_trades: int = 0
    group_a_win_rate: float = 0.0
    group_b_win_rate: float = 0.0
    group_a_avg_pnl: float = 0.0
    group_b_avg_pnl: float = 0.0
    p_value: float = 1.0
    winner: str = "A"             # A | B | inconclusive
    promote_b: bool = False
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "group_a_trades": self.group_a_trades,
            "group_b_trades": self.group_b_trades,
            "group_a_win_rate": round(self.group_a_win_rate, 4),
            "group_b_win_rate": round(self.group_b_win_rate, 4),
            "group_a_avg_pnl": round(self.group_a_avg_pnl, 4),
            "group_b_avg_pnl": round(self.group_b_avg_pnl, 4),
            "p_value": round(self.p_value, 4),
            "winner": self.winner,
            "promote_b": self.promote_b,
            "completed_at": self.completed_at.isoformat(),
        }


class ABExperimentRunner:
    """
    Roda dois grupos em paralelo:
    - Grupo A: estratégia atual (capital_split_a % do alocável, ex.: 80%)
    - Grupo B: estratégia experimental (1 - capital_split_a, ex.: 20%)

    Após min_trades resultados em cada grupo, compara com teste de proporção.
    Se B vence com p < p_value_threshold → B é promovido (vira A).
    """

    def __init__(
        self,
        name: str = "default",
        capital_split_a: float = 0.80,
        min_trades: int = 20,
        p_value_threshold: float = 0.05,
        seed: int = 42,
    ) -> None:
        self._name = name
        self._capital_split_a = capital_split_a
        self._min_trades = min_trades
        self._p_value_threshold = p_value_threshold
        self._results_a: List[TradeResult] = []
        self._results_b: List[TradeResult] = []
        self._completed_experiments: List[ExperimentResult] = []
        self._rng = np.random.default_rng(seed)
        self._generation = 0        # quantas vezes B foi promovido

    # ------------------------------------------------------------------ #
    #  Registra resultados                                                 #
    # ------------------------------------------------------------------ #

    def record(self, group: str, won: bool, pnl: float = 0.0) -> TradeResult:
        result = TradeResult(group=group.upper(), won=won, pnl=pnl)
        if group.upper() == "A":
            self._results_a.append(result)
        else:
            self._results_b.append(result)
        return result

    def capital_for_group(self, group: str) -> float:
        """Retorna a fração de capital a alocar para cada grupo."""
        return self._capital_split_a if group.upper() == "A" else (1.0 - self._capital_split_a)

    # ------------------------------------------------------------------ #
    #  Avaliação estatística                                               #
    # ------------------------------------------------------------------ #

    def _proportion_p_value(self, wins_a: int, n_a: int, wins_b: int, n_b: int) -> float:
        """Teste de proporção duas amostras usando aproximação normal."""
        if n_a == 0 or n_b == 0:
            return 1.0
        p_a = wins_a / n_a
        p_b = wins_b / n_b
        p_pool = (wins_a + wins_b) / (n_a + n_b)
        denom = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
        if denom < 1e-9:
            return 1.0
        z = (p_b - p_a) / denom
        # Aproximação: p-value two-tailed via CDF normal
        # CDF normal aproximada via série de Taylor (sem scipy)
        abs_z = abs(z)
        p_val = 2.0 * (1.0 - self._norm_cdf(abs_z))
        return float(np.clip(p_val, 0.0, 1.0))

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """CDF normal padrão aproximada (Abramowitz & Stegun)."""
        t = 1.0 / (1.0 + 0.2316419 * x)
        poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937
               + t * (-1.821255978 + t * 1.330274429))))
        pdf = np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi)
        return float(1.0 - pdf * poly)

    # ------------------------------------------------------------------ #
    #  Evaluate & promote                                                  #
    # ------------------------------------------------------------------ #

    def evaluate(self) -> Optional[ExperimentResult]:
        """
        Avalia se há dados suficientes e decide se B deve ser promovido.
        Retorna ExperimentResult se avaliação foi feita, None se ainda inconclusivo.
        """
        n_a = len(self._results_a)
        n_b = len(self._results_b)

        if n_a < self._min_trades or n_b < self._min_trades:
            return None

        wins_a = sum(1 for r in self._results_a if r.won)
        wins_b = sum(1 for r in self._results_b if r.won)
        wr_a = wins_a / n_a
        wr_b = wins_b / n_b
        pnl_a = np.mean([r.pnl for r in self._results_a]) if self._results_a else 0.0
        pnl_b = np.mean([r.pnl for r in self._results_b]) if self._results_b else 0.0

        p_val = self._proportion_p_value(wins_a, n_a, wins_b, n_b)

        promote = bool(wr_b > wr_a and p_val < self._p_value_threshold)
        winner = "B" if promote else ("A" if wr_a >= wr_b else "inconclusive")

        result = ExperimentResult(
            name=f"{self._name}_gen{self._generation}",
            group_a_trades=n_a,
            group_b_trades=n_b,
            group_a_win_rate=wr_a,
            group_b_win_rate=wr_b,
            group_a_avg_pnl=float(pnl_a),
            group_b_avg_pnl=float(pnl_b),
            p_value=p_val,
            winner=winner,
            promote_b=promote,
        )
        self._completed_experiments.append(result)

        if promote:
            self._promote_b()

        return result

    def _promote_b(self) -> None:
        """B vira A: limpa resultados para próxima geração."""
        self._results_a = list(self._results_b)
        self._results_b = []
        self._generation += 1

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "generation": self._generation,
            "trades_a": len(self._results_a),
            "trades_b": len(self._results_b),
            "min_trades_required": self._min_trades,
            "p_value_threshold": self._p_value_threshold,
            "capital_split": {"A": self._capital_split_a, "B": round(1 - self._capital_split_a, 2)},
            "completed_experiments": len(self._completed_experiments),
        }

    def get_experiments(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._completed_experiments]
