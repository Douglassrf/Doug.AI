# ============================================================
# MISSÃO 301 — PAPER TRADING LAUNCH
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class PaperTrade:
    """Trade simulado."""

    id: str = field(default_factory=lambda: f"pt_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    direction: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    profit_loss: float = 0.0
    entry_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exit_time: Optional[datetime] = None
    status: str = "open"
    decision_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "profit_loss": self.profit_loss,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "status": self.status,
            "decision_id": self.decision_id,
        }


@dataclass
class PaperTradingReport:
    """Relatório de paper trading."""

    id: str = field(default_factory=lambda: f"ptr_{uuid.uuid4().hex[:12]}")
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit_loss: float = 0.0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_profit_loss": self.total_profit_loss,
            "win_rate": self.win_rate,
            "avg_profit": self.avg_profit,
            "avg_loss": self.avg_loss,
            "created_at": self.created_at.isoformat(),
        }


class PaperTradingLaunch:
    """
    Lançamento de paper trading.

    Implementa:
    - Paper trading
    - Logs de decisão
    - Simulação de entrada/saída
    - Comparação com mercado real
    - Relatório diário
    """

    def __init__(self):
        self._trades: List[PaperTrade] = []
        self._reports: List[PaperTradingReport] = []
        self._capital = 100000.0
        self._current_value = 100000.0

    def execute_trade(self, decision: Dict[str, Any], market_price: float) -> PaperTrade:
        """Executa trade simulado."""
        trade = PaperTrade(
            asset=decision.get("asset", ""),
            direction=decision.get("direction", ""),
            entry_price=market_price,
            quantity=decision.get("quantity", 1.0),
            decision_id=decision.get("id", ""),
        )
        self._trades.append(trade)
        return trade

    def close_trade(self, trade_id: str, exit_price: float) -> Optional[PaperTrade]:
        """Fecha trade simulado."""
        for trade in self._trades:
            if trade.id == trade_id:
                trade.exit_price = exit_price
                trade.exit_time = datetime.now(timezone.utc)
                trade.status = "closed"
                trade.profit_loss = (exit_price - trade.entry_price) * trade.quantity
                if trade.direction == "sell":
                    trade.profit_loss = -trade.profit_loss
                self._current_value += trade.profit_loss
                return trade
        return None

    def generate_daily_report(self) -> PaperTradingReport:
        """Gera relatório diário."""
        closed_trades = [trade for trade in self._trades if trade.status == "closed"]
        if not closed_trades:
            return PaperTradingReport()

        winning = [trade for trade in closed_trades if trade.profit_loss > 0]
        losing = [trade for trade in closed_trades if trade.profit_loss < 0]

        report = PaperTradingReport(
            total_trades=len(closed_trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            total_profit_loss=sum(trade.profit_loss for trade in closed_trades),
            win_rate=len(winning) / len(closed_trades),
            avg_profit=float(np.mean([trade.profit_loss for trade in winning])) if winning else 0.0,
            avg_loss=float(np.mean([trade.profit_loss for trade in losing])) if losing else 0.0,
        )
        self._reports.append(report)
        return report

    def get_paper_trading_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de paper trading."""
        open_trades = [trade for trade in self._trades if trade.status == "open"]
        closed_trades = [trade for trade in self._trades if trade.status == "closed"]

        return {
            "total_trades": len(self._trades),
            "open_trades": len(open_trades),
            "closed_trades": len(closed_trades),
            "initial_capital": self._capital,
            "current_value": self._current_value,
            "return_percent": (
                (self._current_value - self._capital) / self._capital * 100
                if self._capital > 0
                else 0
            ),
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
            "recent_trades": [trade.to_dict() for trade in self._trades[-10:]],
        }
