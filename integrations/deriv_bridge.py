"""Unified Deriv facade — bridges dashboard (deriv_demo) and API layer (src/app).

DogEye / Doug.AI team training uses this module for tip-to-tip exercises.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from integrations.deriv_demo import (  # noqa: E402
    DEFAULT_APP_ID,
    DerivLiveGate,
    is_doug_demo_mode,
    load_config,
    run_public_demo_snapshot,
)

from app.core.config import DerivSettings  # noqa: E402
from app.integrations.deriv import DerivClient  # noqa: E402


TRAINING_PAIRS: tuple[str, ...] = (
    "R_100",
    "R_75",
    "R_50",
    "cryBTCUSD",
    "cryETHUSD",
    "frxEURUSD",
    "frxGBPUSD",
    "frxUSDJPY",
    "BOOM1000",
    "CRASH1000",
)


@dataclass
class BridgeStatus:
    demo_mode: bool
    has_token: bool
    app_id: int
    mock_enabled: bool
    live_enabled: bool
    websocket_url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "demo_mode": self.demo_mode,
            "has_token": self.has_token,
            "app_id": self.app_id,
            "mock_enabled": self.mock_enabled,
            "live_enabled": self.live_enabled,
            "websocket_url": self.websocket_url,
        }


class DerivBridge:
    """Single entry point for Doug.AI Deriv integrations."""

    def __init__(self) -> None:
        self._token, self._app_id = load_config()
        self._settings = DerivSettings(
            app_id=str(self._app_id),
            token=self._token or "",
            mock_enabled=os.getenv("DERIV_MOCK_ENABLED", "true").strip().lower()
            in {"1", "true", "yes", "on"},
            live_enabled=os.getenv("DERIV_LIVE_ENABLED", "false").strip().lower()
            in {"1", "true", "yes", "on"},
        )
        self._api = DerivClient(self._settings)

    @property
    def status(self) -> BridgeStatus:
        api = self._api.status()
        return BridgeStatus(
            demo_mode=is_doug_demo_mode(),
            has_token=bool(self._token),
            app_id=self._app_id,
            mock_enabled=bool(api.get("mock_enabled")),
            live_enabled=bool(api.get("live_enabled")),
            websocket_url=str(api.get("endpoint", "")),
        )

    def ping(self) -> dict[str, Any]:
        return self._api.ping()

    def mock_proposal(self, symbol: str) -> dict[str, Any]:
        return self._api.proposal(
            amount=1.0,
            contract_type="CALL",
            duration=5,
            duration_unit="t",
            symbol=symbol,
            dry_run=True,
        )

    def live_gate_blocked(self) -> bool:
        gate = DerivLiveGate().check()
        return not gate.allowed

    def fetch_tick_public(self, symbol: str) -> dict[str, Any]:
        snap = run_public_demo_snapshot(
            app_id=self._app_id,
            symbols=(symbol,),
            save_status=False,
            log_paper=False,
        )
        if snap.error:
            return {"ok": False, "error": snap.error}
        tick = snap.ticks.get(symbol, {})
        quote = tick.get("quote")
        if quote is None:
            return {"ok": False, "error": tick.get("error", "no quote")}
        return {"ok": True, "symbol": symbol, "quote": float(quote)}

    def unified_status_dict(self) -> dict[str, Any]:
        return {
            "bridge": self.status.to_dict(),
            "api": self._api.status(),
        }


def training_pairs() -> tuple[str, ...]:
    return TRAINING_PAIRS
