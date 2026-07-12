# ============================================================
# MISSÃO 304 — HUMAN-SUPERVISED MICRO LIVE TEST
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class MicroLiveTrade:
    """Trade micro live com supervisão humana."""

    id: str = field(default_factory=lambda: f"mlt_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    direction: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    capital_usd: float = 0.0
    supervisor_id: str = ""
    approved: bool = False
    status: str = "pending_approval"
    kill_switch_blocked: bool = False
    profit_loss: float = 0.0
    entry_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exit_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "capital_usd": self.capital_usd,
            "supervisor_id": self.supervisor_id,
            "approved": self.approved,
            "status": self.status,
            "kill_switch_blocked": self.kill_switch_blocked,
            "profit_loss": self.profit_loss,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MicroLiveTestReport:
    """Relatório de teste micro live."""

    id: str = field(default_factory=lambda: f"mlr_{uuid.uuid4().hex[:12]}")
    total_requests: int = 0
    approved_trades: int = 0
    rejected_trades: int = 0
    open_trades: int = 0
    closed_trades: int = 0
    total_pnl: float = 0.0
    kill_switch_active: bool = False
    verdict: str = "PENDING"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_requests": self.total_requests,
            "approved_trades": self.approved_trades,
            "rejected_trades": self.rejected_trades,
            "open_trades": self.open_trades,
            "closed_trades": self.closed_trades,
            "total_pnl": self.total_pnl,
            "kill_switch_active": self.kill_switch_active,
            "verdict": self.verdict,
            "created_at": self.created_at.isoformat(),
        }


class HumanSupervisedMicroLiveTest:
    """
    Teste micro live com supervisão humana.

    Implementa:
    - Aprovação humana obrigatória
    - Limite de capital por trade
    - Logging com supervisor_id
    - Kill switch de segurança
    - Relatório e dashboard
    """

    def __init__(self, max_capital_per_trade: float = 100.0):
        self._max_capital_per_trade = max_capital_per_trade
        self._trades: List[MicroLiveTrade] = []
        self._reports: List[MicroLiveTestReport] = []
        self._kill_switch_active = False
        self._kill_switch_reason = ""

    def request_trade(
        self,
        decision: Dict[str, Any],
        market_price: float,
        supervisor_id: str,
    ) -> MicroLiveTrade:
        """Solicita trade micro live (requer aprovação)."""
        requested_capital = float(decision.get("capital_usd", decision.get("quantity", 1.0)))
        capital_usd = min(requested_capital, self._max_capital_per_trade)

        trade = MicroLiveTrade(
            asset=decision.get("asset", ""),
            direction=decision.get("direction", "buy"),
            entry_price=market_price,
            quantity=decision.get("quantity", 1.0),
            capital_usd=capital_usd,
            supervisor_id=supervisor_id,
            approved=False,
            status="pending_approval",
        )

        if self._kill_switch_active:
            trade.status = "blocked"
            trade.kill_switch_blocked = True

        self._trades.append(trade)
        return trade

    def approve_trade(self, trade_id: str, supervisor_id: str) -> bool:
        """Aprova trade pendente."""
        if self._kill_switch_active:
            return False

        for trade in self._trades:
            if trade.id == trade_id and trade.status == "pending_approval":
                trade.approved = True
                trade.status = "approved"
                trade.supervisor_id = supervisor_id
                return True
        return False

    def reject_trade(self, trade_id: str, supervisor_id: str) -> bool:
        """Rejeita trade pendente."""
        for trade in self._trades:
            if trade.id == trade_id and trade.status == "pending_approval":
                trade.approved = False
                trade.status = "rejected"
                trade.supervisor_id = supervisor_id
                return True
        return False

    def execute_trade(self, trade_id: str, market_price: float) -> Optional[MicroLiveTrade]:
        """Executa trade aprovado."""
        if self._kill_switch_active:
            return None

        for trade in self._trades:
            if trade.id == trade_id and trade.status == "approved":
                trade.entry_price = market_price
                trade.status = "open"
                trade.entry_time = datetime.now(timezone.utc)
                return trade
        return None

    def close_trade(self, trade_id: str, exit_price: float) -> Optional[MicroLiveTrade]:
        """Fecha trade aberto."""
        for trade in self._trades:
            if trade.id == trade_id and trade.status == "open":
                trade.exit_price = exit_price
                trade.exit_time = datetime.now(timezone.utc)
                trade.status = "closed"
                trade.profit_loss = (exit_price - trade.entry_price) * trade.quantity
                if trade.direction == "sell":
                    trade.profit_loss = -trade.profit_loss
                return trade
        return None

    def activate_kill_switch(self, reason: str) -> None:
        """Ativa kill switch de segurança."""
        self._kill_switch_active = True
        self._kill_switch_reason = reason

    def deactivate_kill_switch(self, supervisor_id: str) -> bool:
        """Desativa kill switch com supervisão."""
        if not supervisor_id:
            return False
        self._kill_switch_active = False
        self._kill_switch_reason = ""
        return True

    def generate_report(self) -> MicroLiveTestReport:
        """Gera relatório do teste micro live."""
        approved = [trade for trade in self._trades if trade.status in {"approved", "open", "closed"}]
        rejected = [trade for trade in self._trades if trade.status == "rejected"]
        open_trades = [trade for trade in self._trades if trade.status == "open"]
        closed_trades = [trade for trade in self._trades if trade.status == "closed"]
        total_pnl = sum(trade.profit_loss for trade in closed_trades)

        verdict = "PENDING"
        if self._kill_switch_active:
            verdict = "HALTED"
        elif closed_trades and total_pnl >= 0:
            verdict = "PASS"
        elif closed_trades:
            verdict = "REVIEW"

        report = MicroLiveTestReport(
            total_requests=len(self._trades),
            approved_trades=len(approved),
            rejected_trades=len(rejected),
            open_trades=len(open_trades),
            closed_trades=len(closed_trades),
            total_pnl=total_pnl,
            kill_switch_active=self._kill_switch_active,
            verdict=verdict,
        )
        self._reports.append(report)
        return report

    def get_micro_live_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do teste micro live."""
        return {
            "max_capital_per_trade": self._max_capital_per_trade,
            "total_trades": len(self._trades),
            "pending_approval": sum(
                1 for trade in self._trades if trade.status == "pending_approval"
            ),
            "open_trades": sum(1 for trade in self._trades if trade.status == "open"),
            "closed_trades": sum(1 for trade in self._trades if trade.status == "closed"),
            "kill_switch_active": self._kill_switch_active,
            "kill_switch_reason": self._kill_switch_reason,
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
            "recent_trades": [trade.to_dict() for trade in self._trades[-10:]],
        }
