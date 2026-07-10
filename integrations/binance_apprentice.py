"""Binance integration for Doug.AI apprentices — TESTNET first, live blocked by default.

Douglas creates API keys manually at:
  - Testnet (aprendizes): https://testnet.binance.vision/
  - Live (futuro, gated): https://www.binance.com/pt-BR/my/settings/api-management

NEVER commit .env with real keys.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

BINANCE_TESTNET_REST = "https://testnet.binance.vision"
BINANCE_MAINNET_REST = "https://api.binance.com"

from training.pair_universe import BINANCE_PAIRS_100 as APPRENTICE_PAIRS
from integrations import money_guard


class BinanceError(RuntimeError):
    pass


class BinanceLiveBlocked(BinanceError):
    pass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BinanceSettings:
    api_key: str = os.getenv("BINANCE_API_KEY", "")
    api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    use_testnet: bool = field(default_factory=lambda: _env_bool("BINANCE_USE_TESTNET", True))
    live_enabled: bool = field(default_factory=lambda: _env_bool("BINANCE_LIVE_ENABLED", False))
    mock_enabled: bool = field(default_factory=lambda: _env_bool("BINANCE_MOCK_ENABLED", False))
    timeout: float = float(os.getenv("BINANCE_TIMEOUT_SECONDS", "15"))

    @property
    def base_url(self) -> str:
        if self.use_testnet:
            return BINANCE_TESTNET_REST
        return BINANCE_MAINNET_REST


@dataclass
class BinanceSnapshot:
    connected: bool
    testnet: bool
    account: dict[str, Any] | None = None
    prices: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "testnet": self.testnet,
            "account": self.account,
            "prices": self.prices,
            "error": self.error,
            "checked_at": self.checked_at,
        }


class BinanceApprenticeClient:
    """Safe Binance client — testnet for learning, live trading blocked."""

    def __init__(self, config: BinanceSettings | None = None) -> None:
        self.config = config or BinanceSettings()

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        signed: bool = False,
    ) -> Any:
        if self.config.mock_enabled:
            return {"mock": True, "path": path, "params": params or {}}

        params = dict(params or {})
        url = f"{self.config.base_url}{path}"
        headers = {"User-Agent": "Doug.AI-Apprentice/1.0"}

        if signed:
            # Defesa em profundidade: chamada assinada em MAINNET passa pelo
            # cofre (kill switch + live habilitado). Testnet é livre (fake money).
            if not self.config.use_testnet:
                try:
                    money_guard.assert_mainnet_allowed(live_enabled=self.config.live_enabled)
                except money_guard.MoneyGuardError as exc:
                    raise BinanceLiveBlocked(str(exc)) from exc
            if not self.config.api_key or not self.config.api_secret:
                raise BinanceError("BINANCE_API_KEY e BINANCE_API_SECRET necessarios para chamadas assinadas")
            params["timestamp"] = int(time.time() * 1000)
            query = urllib.parse.urlencode(params)
            sig = hmac.new(
                self.config.api_secret.encode("utf-8"),
                query.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            query = f"{query}&signature={sig}"
            headers["X-MBX-APIKEY"] = self.config.api_key
            full_url = f"{url}?{query}"
        else:
            if params:
                full_url = f"{url}?{urllib.parse.urlencode(params)}"
            else:
                full_url = url

        req = urllib.request.Request(full_url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise BinanceError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise BinanceError(str(exc)) from exc

    def ping(self) -> dict[str, Any]:
        if self.config.mock_enabled:
            return {"mock": True, "status": "ok"}
        self._request("GET", "/api/v3/ping")
        return {"status": "ok", "testnet": self.config.use_testnet}

    def price(self, symbol: str) -> float:
        if self.config.mock_enabled:
            return 68000.0 if symbol == "BTCUSDT" else 3500.0
        data = self._request("GET", "/api/v3/ticker/price", {"symbol": symbol})
        return float(data["price"])

    def prices(self, symbols: tuple[str, ...] | None = None) -> dict[str, float]:
        syms = symbols or APPRENTICE_PAIRS
        out: dict[str, float] = {}
        for sym in syms:
            try:
                out[sym] = self.price(sym)
            except BinanceError:
                continue
        return out

    def account_info(self) -> dict[str, Any]:
        return self._request("GET", "/api/v3/account", signed=True)

    def status(self) -> dict[str, Any]:
        return {
            "testnet": self.config.use_testnet,
            "live_enabled": self.config.live_enabled,
            "mock_enabled": self.config.mock_enabled,
            "has_key": bool(self.config.api_key),
            "base_url": self.config.base_url,
            "pairs": list(APPRENTICE_PAIRS),
        }

    def snapshot(self, symbols: tuple[str, ...] | None = None) -> BinanceSnapshot:
        syms = symbols or APPRENTICE_PAIRS[:5]
        try:
            self.ping()
            prices = self.prices(syms)
            account = None
            if self.config.api_key and self.config.api_secret and not self.config.mock_enabled:
                try:
                    account = self.account_info()
                except BinanceError:
                    account = None
            return BinanceSnapshot(
                connected=True,
                testnet=self.config.use_testnet,
                account=account,
                prices=prices,
            )
        except BinanceError as exc:
            return BinanceSnapshot(connected=False, testnet=self.config.use_testnet, error=str(exc))


def save_binance_status(snapshot: BinanceSnapshot, path: Path | None = None) -> None:
    data_dir = Path(os.environ.get("DOUG_DATA_DIR", "data"))
    target = path or data_dir / "binance_status.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
