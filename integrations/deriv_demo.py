"""Deriv WebSocket integration — DEMO / virtual accounts ONLY.

Hard-fails if the authorized account is not virtual (demo).
Never places real-money orders; paper signals are logged locally.
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import websockets

DERIV_WS_BASE = "wss://ws.derivws.com/websockets/v3"
DEFAULT_APP_ID = 1089
DEFAULT_SYMBOLS = ("R_100", "cryBTCUSD")
DERIV_STATUS_PATH = Path(os.environ.get("DOUG_DATA_DIR", "data")) / "deriv_status.json"

# Same host for demo and live — separation is by mode, flags, and account validation.
DERIV_WS_DEMO = DERIV_WS_BASE
DERIV_WS_LIVE = DERIV_WS_BASE


class DerivDemoError(Exception):
    """Base error for Deriv demo integration."""


class DerivNotDemoAccountError(DerivDemoError):
    """Raised when the token belongs to a real (non-virtual) account."""


class DerivLiveNotEnabledError(DerivDemoError):
    """Raised when live trading is attempted without explicit gates."""


class DerivAuthError(DerivDemoError):
    """Raised when authorization fails."""


@dataclass
class DerivAccountInfo:
    loginid: str
    balance: float
    currency: str
    is_virtual: bool
    email: str = ""
    fullname: str = ""


@dataclass
class DerivSnapshot:
    connected: bool
    account: DerivAccountInfo | None
    ticks: dict[str, dict[str, Any]] = field(default_factory=dict)
    candles: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    paper_signals: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "account": None
            if self.account is None
            else {
                "loginid": self.account.loginid,
                "balance": self.account.balance,
                "currency": self.account.currency,
                "is_virtual": self.account.is_virtual,
                "email": self.account.email,
                "fullname": self.account.fullname,
            },
            "ticks": self.ticks,
            "candles": self.candles,
            "paper_signals": self.paper_signals,
            "error": self.error,
            "checked_at": self.checked_at,
        }


def _ws_url(app_id: int, *, live: bool = False) -> str:
    base = DERIV_WS_LIVE if live else DERIV_WS_DEMO
    return f"{base}?app_id={app_id}"


def _is_demo_account(auth: dict[str, Any]) -> bool:
    """Return True only when Deriv reports a virtual/demo account."""
    if auth.get("is_virtual") in (1, True, "1"):
        return True
    loginid = str(auth.get("loginid", ""))
    if loginid.upper().startswith("VRT"):
        return True
    account_type = str(auth.get("account_type", "")).lower()
    if account_type in ("demo", "virtual"):
        return True
    return False


def assert_demo_account(auth: dict[str, Any]) -> None:
    """Hard-fail if authorize payload is not a virtual/demo account."""
    if not _is_demo_account(auth):
        loginid = auth.get("loginid", "?")
        raise DerivNotDemoAccountError(
            f"Conta REAL detectada (loginid={loginid}). "
            "Doug.AI aceita apenas contas DEMO/virtual. "
            "Gere um token na conta demo em home.deriv.com."
        )


def is_doug_demo_mode() -> bool:
    """True when Doug.AI runs in local demo mode (token optional)."""
    return os.environ.get("DOUG_MODE", "").strip().lower() == "demo"


def is_doug_live_mode() -> bool:
    """True when DOUG_MODE=live (does NOT imply live trading is enabled)."""
    return os.environ.get("DOUG_MODE", "").strip().lower() == "live"


def is_deriv_live_enabled() -> bool:
    """True only when DERIV_LIVE_ENABLED=true explicitly set."""
    return os.environ.get("DERIV_LIVE_ENABLED", "").strip().lower() in ("1", "true", "yes")


def current_doug_mode_label() -> str:
    """Human-readable mode for dashboard: DEMO, LIVE, or PAPER."""
    mode = os.environ.get("DOUG_MODE", "paper").strip().lower()
    if mode == "demo":
        return "DEMO"
    if mode == "live":
        return "LIVE"
    return mode.upper() or "PAPER"


@dataclass
class DerivLiveGateStatus:
    """Result of live-trading gate check (stub for Phase 2)."""

    allowed: bool
    reason: str
    gates_pending: list[str] = field(default_factory=list)


class DerivLiveGate:
    """Gate for official/live Deriv — never auto-enables live trading.

    Phase 2 stub: checks env flags and documents required mission gates.
    """

    REQUIRED_GATES = (
        "SmallCapitalReadinessGate",
        "HumanSupervisedMicroLive",
        "Certification GO",
    )

    def __init__(self) -> None:
        load_config()  # ensure .env loaded

    def check(self) -> DerivLiveGateStatus:
        if not is_doug_live_mode():
            return DerivLiveGateStatus(
                allowed=False,
                reason="DOUG_MODE não é 'live'. Operações live bloqueadas.",
                gates_pending=list(self.REQUIRED_GATES),
            )
        if not is_deriv_live_enabled():
            return DerivLiveGateStatus(
                allowed=False,
                reason="DERIV_LIVE_ENABLED=false (padrão). Defina true + confirmação humana.",
                gates_pending=list(self.REQUIRED_GATES),
            )
        return DerivLiveGateStatus(
            allowed=False,
            reason="Portões de missão ainda não certificados neste build.",
            gates_pending=list(self.REQUIRED_GATES),
        )

    def assert_live_allowed(self) -> None:
        status = self.check()
        if not status.allowed:
            raise DerivLiveNotEnabledError(status.reason)

    @staticmethod
    def confirm_human() -> bool:
        """Placeholder — future interactive confirmation before live enable."""
        return False


def load_config() -> tuple[str | None, int]:
    """Load DERIV_API_TOKEN and DERIV_APP_ID from env or data/settings.json."""
    try:
        from dotenv import load_dotenv

        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env")
    except ImportError:
        pass

    token = os.environ.get("DERIV_API_TOKEN", "").strip() or None
    app_id_raw = os.environ.get("DERIV_APP_ID", "").strip()
    app_id = int(app_id_raw) if app_id_raw.isdigit() else DEFAULT_APP_ID

    settings_path = Path(os.environ.get("DOUG_DATA_DIR", "data")) / "settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            deriv = data.get("deriv", {})
            if not token:
                t = str(deriv.get("api_token", "")).strip()
                token = t or None
            if deriv.get("app_id"):
                app_id = int(deriv["app_id"])
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    return token, app_id


class DerivDemoClient:
    """Async Deriv WebSocket client restricted to demo accounts."""

    def __init__(self, token: str, app_id: int = DEFAULT_APP_ID) -> None:
        if not token or not token.strip():
            raise DerivDemoError("DERIV_API_TOKEN is required")
        self.token = token.strip()
        self.app_id = app_id
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._req_id = 0
        self._account: DerivAccountInfo | None = None

    async def __aenter__(self) -> DerivDemoClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def connect(self) -> None:
        if is_doug_live_mode():
            DerivLiveGate().assert_live_allowed()
        self._ws = await websockets.connect(
            _ws_url(self.app_id, live=is_doug_live_mode()), open_timeout=15
        )

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._ws is None:
            raise DerivDemoError("Not connected")
        req_id = self._next_id()
        payload = {**payload, "req_id": req_id}
        await self._ws.send(json.dumps(payload))
        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=20)
            data = json.loads(raw)
            if data.get("req_id") == req_id:
                if "error" in data:
                    msg = data["error"].get("message", str(data["error"]))
                    raise DerivDemoError(msg)
                return data
            # ignore subscription pushes while waiting for req response

    async def authorize(self) -> DerivAccountInfo:
        data = await self._send({"authorize": self.token})
        auth = data.get("authorize", {})
        if not auth:
            raise DerivAuthError("Empty authorize response")

        if is_doug_live_mode():
            DerivLiveGate().assert_live_allowed()
        else:
            assert_demo_account(auth)

        self._account = DerivAccountInfo(
            loginid=str(auth.get("loginid", "")),
            balance=float(auth.get("balance", 0)),
            currency=str(auth.get("currency", "USD")),
            is_virtual=_is_demo_account(auth),
            email=str(auth.get("email", "")),
            fullname=str(auth.get("fullname", "")),
        )
        return self._account

    async def refresh_balance(self) -> float:
        data = await self._send({"balance": 1})
        bal = data.get("balance", {})
        amount = float(bal.get("balance", self._account.balance if self._account else 0))
        if self._account:
            self._account.balance = amount
        return amount

    async def get_tick(self, symbol: str) -> dict[str, Any]:
        data = await self._send(
            {
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": 1,
                "end": "latest",
                "style": "ticks",
            }
        )
        history = data.get("history", {})
        prices = history.get("prices", [])
        times = history.get("times", [])
        if not prices:
            raise DerivDemoError(f"No tick data for {symbol}")
        return {
            "symbol": symbol,
            "quote": float(prices[-1]),
            "epoch": int(times[-1]) if times else None,
            "pip_size": history.get("pip_size"),
        }

    async def get_candles(
        self, symbol: str, *, granularity: int = 60, count: int = 10
    ) -> list[dict[str, Any]]:
        data = await self._send(
            {
                "candles": symbol,
                "adjust_start_time": 1,
                "count": count,
                "end": "latest",
                "granularity": granularity,
            }
        )
        candles = data.get("candles", [])
        return [
            {
                "epoch": c.get("epoch"),
                "open": float(c.get("open", 0)),
                "high": float(c.get("high", 0)),
                "low": float(c.get("low", 0)),
                "close": float(c.get("close", 0)),
            }
            for c in candles
        ]

    def paper_signal(self, symbol: str, action: str, price: float, reason: str = "") -> dict[str, Any]:
        """Local paper signal — NOT sent to Deriv as an order."""
        signal = {
            "source": "deriv_demo",
            "symbol": symbol,
            "action": action.upper(),
            "price": price,
            "reason": reason or "doug_ai_paper_simulation",
            "mode": "DEMO_PAPER",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return signal

    async def snapshot(
        self,
        symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
        *,
        log_paper: bool = True,
        audit_path: Path | None = None,
    ) -> DerivSnapshot:
        try:
            account = await self.authorize()
            balance = await self.refresh_balance()
            account.balance = balance

            ticks: dict[str, dict[str, Any]] = {}
            candles: dict[str, list[dict[str, Any]]] = {}
            for sym in symbols:
                try:
                    ticks[sym] = await self.get_tick(sym)
                    candles[sym] = await self.get_candles(sym, granularity=60, count=5)
                except DerivDemoError as exc:
                    ticks[sym] = {"symbol": sym, "error": str(exc)}

            paper_signals: list[dict[str, Any]] = []
            if log_paper and ticks:
                for sym, tick in ticks.items():
                    if "quote" not in tick:
                        continue
                    action = "HOLD"
                    if sym == "R_100":
                        action = "OBSERVE"
                    sig = self.paper_signal(sym, action, tick["quote"])
                    paper_signals.append(sig)
                    if audit_path is not None:
                        _append_audit(audit_path, "deriv_paper_signal", sig)

            return DerivSnapshot(
                connected=True,
                account=account,
                ticks=ticks,
                candles=candles,
                paper_signals=paper_signals,
            )
        except DerivNotDemoAccountError as exc:
            return DerivSnapshot(connected=False, account=None, error=str(exc))
        except (DerivDemoError, DerivAuthError, asyncio.TimeoutError, OSError) as exc:
            return DerivSnapshot(connected=False, account=None, error=str(exc))


def _append_audit(path: Path, event_type: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


async def _recv_for_req(ws: websockets.WebSocketClientProtocol, req_id: int) -> dict[str, Any]:
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=20)
        data = json.loads(raw)
        if data.get("req_id") == req_id:
            if "error" in data:
                msg = data["error"].get("message", str(data["error"]))
                raise DerivDemoError(msg)
            return data


async def public_demo_snapshot(
    app_id: int = DEFAULT_APP_ID,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    *,
    log_paper: bool = True,
    audit_path: Path | None = None,
) -> DerivSnapshot:
    """Public ticks via app_id 1089 — no API token required."""
    demo_account = DerivAccountInfo(
        loginid="VRT_DEMO_LOCAL",
        balance=10000.0,
        currency="USD",
        is_virtual=True,
        fullname="Doug.AI demo local (sem token)",
    )
    try:
        async with websockets.connect(_ws_url(app_id, live=False), open_timeout=15) as ws:
            ticks: dict[str, dict[str, Any]] = {}
            candles: dict[str, list[dict[str, Any]]] = {}
            req_id = 0
            for sym in symbols:
                req_id += 1
                await ws.send(
                    json.dumps(
                        {
                            "ticks_history": sym,
                            "count": 1,
                            "end": "latest",
                            "style": "ticks",
                            "req_id": req_id,
                        }
                    )
                )
                data = await _recv_for_req(ws, req_id)
                history = data.get("history", {})
                prices = history.get("prices", [])
                times = history.get("times", [])
                if prices:
                    ticks[sym] = {
                        "symbol": sym,
                        "quote": float(prices[-1]),
                        "epoch": int(times[-1]) if times else None,
                        "pip_size": data.get("pip_size"),
                        "source": "public_app_id",
                    }
                else:
                    ticks[sym] = {"symbol": sym, "error": "no tick data", "source": "public_app_id"}

                req_id += 1
                await ws.send(
                    json.dumps(
                        {
                            "ticks_history": sym,
                            "count": 5,
                            "end": "latest",
                            "style": "candles",
                            "granularity": 60,
                            "req_id": req_id,
                        }
                    )
                )
                data = await _recv_for_req(ws, req_id)
                candles[sym] = [
                    {
                        "epoch": c.get("epoch"),
                        "open": float(c.get("open", 0)),
                        "high": float(c.get("high", 0)),
                        "low": float(c.get("low", 0)),
                        "close": float(c.get("close", 0)),
                    }
                    for c in data.get("candles", [])
                ]

            paper_signals: list[dict[str, Any]] = []
            if log_paper:
                for sym, tick in ticks.items():
                    if "quote" not in tick:
                        continue
                    sig = {
                        "source": "deriv_public_demo",
                        "symbol": sym,
                        "action": "OBSERVE",
                        "price": tick["quote"],
                        "reason": "doug_ai_public_app_id_1089",
                        "mode": "DEMO_PUBLIC",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    paper_signals.append(sig)
                    if audit_path is not None:
                        _append_audit(audit_path, "deriv_paper_signal", sig)

            return DerivSnapshot(
                connected=True,
                account=demo_account,
                ticks=ticks,
                candles=candles,
                paper_signals=paper_signals,
            )
    except (DerivDemoError, asyncio.TimeoutError, OSError) as exc:
        return DerivSnapshot(
            connected=False,
            account=demo_account,
            error=f"Demo público falhou: {exc}. Configure DERIV_API_TOKEN para conta demo real.",
        )


def run_public_demo_snapshot(
    app_id: int | None = None,
    *,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    save_status: bool = True,
    log_paper: bool = True,
) -> DerivSnapshot:
    """Synchronous public demo (no token) for dashboard and CLI."""
    _, cfg_app_id = load_config()
    app_id = app_id or cfg_app_id
    data_dir = Path(os.environ.get("DOUG_DATA_DIR", "data"))
    audit_path = data_dir / "audit_log.jsonl" if log_paper else None
    snap = asyncio.run(public_demo_snapshot(app_id, symbols, log_paper=log_paper, audit_path=audit_path))
    if save_status:
        save_deriv_status(snap)
    return snap


def run_snapshot(
    token: str | None = None,
    app_id: int | None = None,
    *,
    symbols: tuple[str, ...] = DEFAULT_SYMBOLS,
    save_status: bool = True,
    log_paper: bool = True,
    allow_public_demo: bool | None = None,
) -> DerivSnapshot:
    """Synchronous entry point for dashboard and CLI."""
    cfg_token, cfg_app_id = load_config()
    token = (token or cfg_token or "").strip()
    app_id = app_id or cfg_app_id
    use_public = allow_public_demo if allow_public_demo is not None else is_doug_demo_mode()
    if not token:
        if use_public:
            return run_public_demo_snapshot(app_id, symbols=symbols, save_status=save_status, log_paper=log_paper)
        return DerivSnapshot(
            connected=False,
            account=None,
            error="DERIV_API_TOKEN não configurado. Veja README — Deriv Demo Setup.",
        )

    data_dir = Path(os.environ.get("DOUG_DATA_DIR", "data"))
    audit_path = data_dir / "audit_log.jsonl" if log_paper else None

    async def _run() -> DerivSnapshot:
        async with DerivDemoClient(token, app_id) as client:
            return await client.snapshot(symbols, log_paper=log_paper, audit_path=audit_path)

    snap = asyncio.run(_run())
    if save_status:
        save_deriv_status(snap)
    return snap


def save_deriv_status(snapshot: DerivSnapshot, path: Path | None = None) -> None:
    target = path or DERIV_STATUS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_deriv_status(path: Path | None = None) -> dict[str, Any] | None:
    target = path or DERIV_STATUS_PATH
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
