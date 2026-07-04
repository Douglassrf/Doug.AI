"""Central configuration for Doug.AI API integrations."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class DerivSettings:
    app_id: str = os.getenv("DERIV_APP_ID", "1089")
    endpoint: str = os.getenv("DERIV_ENDPOINT", "ws.derivws.com")
    token: str = os.getenv("DERIV_API_TOKEN", "")
    default_symbol: str = os.getenv("DERIV_DEFAULT_SYMBOL", "R_100")
    currency: str = os.getenv("DERIV_CURRENCY", "USD")
    timeout_seconds: float = float(os.getenv("DERIV_TIMEOUT_SECONDS", "10"))
    mock_enabled: bool = _env_bool("DERIV_MOCK_ENABLED", True)
    live_enabled: bool = _env_bool("DERIV_LIVE_ENABLED", False)

    @property
    def websocket_path(self) -> str:
        return f"/websockets/v3?app_id={self.app_id}"

    @property
    def websocket_url(self) -> str:
        return f"wss://{self.endpoint}{self.websocket_path}"


settings = DerivSettings()
