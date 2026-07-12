"""Safe Deriv WebSocket client for Doug.AI.

The client is mock-first and blocks real purchases by default.  It uses only
Python's standard library for the minimal WebSocket/TLS transport needed by
Deriv API calls.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from app.core.config import DerivSettings, settings as default_settings

# Fonte UNICA da verdade para a trava de conta-demo. Reusa a validacao madura
# de integrations/deriv_demo.py em vez de reimplementar (evita divergencia na
# trava de seguranca mais critica do projeto). Fallback defensivo se o modulo
# raiz nao estiver no path do processo FastAPI.
try:
    import sys as _sys
    from pathlib import Path as _Path
    _root = _Path(__file__).resolve().parents[3]
    if str(_root) not in _sys.path:
        _sys.path.insert(0, str(_root))
    from integrations.deriv_demo import (  # type: ignore
        DerivLiveGate as _CanonLiveGate,
        RealAccountDetectedAbort as _CanonRealAccountAbort,
        assert_demo_account as _canon_assert_demo,
    )

    def _gate_allows_live() -> bool:
        return _CanonLiveGate().check().allowed

    def _assert_demo_account(auth: dict[str, Any]) -> None:
        try:
            _canon_assert_demo(auth)
        except _CanonRealAccountAbort as exc:
            # Propaga como abort fatal (nao um DerivError comum) -- este
            # cliente tambem deve derrubar o processo, nao so bloquear a
            # compra. Ver integrations/deriv_demo.py:RealAccountDetectedAbort.
            raise exc
except Exception:  # pragma: no cover - fallback minimo se o import canonico falhar
    def _gate_allows_live() -> bool:
        return False

    def _assert_demo_account(auth: dict[str, Any]) -> None:
        loginid = str(auth.get("loginid", ""))
        is_virtual = auth.get("is_virtual") in (1, True, "1") or loginid.upper().startswith("VRT")
        if not is_virtual:
            raise DerivLivePurchaseBlocked(
                f"Conta REAL detectada (loginid={loginid}). Doug.AI aceita apenas conta DEMO."
            )


class DerivError(RuntimeError):
    """Base Deriv integration error."""


class DerivLivePurchaseBlocked(DerivError):
    """Raised when a real Deriv buy is attempted without explicit enabling."""


@dataclass
class MinimalWebSocketTLS:
    """Tiny RFC6455 client sufficient for request/response JSON calls."""

    url: str
    timeout: float = 10.0

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        self.host = parsed.hostname or "ws.derivws.com"
        self.port = parsed.port or 443
        self.path = parsed.path or "/"
        if parsed.query:
            self.path += f"?{parsed.query}"
        self._sock: ssl.SSLSocket | None = None

    def __enter__(self) -> "MinimalWebSocketTLS":
        raw = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._sock = ssl.create_default_context().wrap_socket(raw, server_hostname=self.host)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self._sock.sendall(request.encode("ascii"))
        response = self._sock.recv(4096)
        accept = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
        ).decode("ascii")
        if b" 101 " not in response or accept.encode("ascii") not in response:
            raise DerivError("WebSocket handshake failed")
        return self

    def __exit__(self, *_: object) -> None:
        if self._sock:
            self._sock.close()

    def send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        if len(body) >= 126:
            raise DerivError("Minimal client only supports small JSON frames")
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(body))
        frame = bytes([0x81, 0x80 | len(body)]) + mask + masked
        assert self._sock is not None
        self._sock.sendall(frame)

    def recv_json(self) -> dict[str, Any]:
        assert self._sock is not None
        header = self._sock.recv(2)
        if len(header) < 2:
            raise DerivError("Empty WebSocket response")
        length = header[1] & 0x7F
        if length == 126:
            length = int.from_bytes(self._sock.recv(2), "big")
        elif length == 127:
            length = int.from_bytes(self._sock.recv(8), "big")
        data = self._sock.recv(length)
        return json.loads(data.decode("utf-8"))


class DerivClient:
    """Synchronous Deriv client with safe mock-first behavior."""

    def __init__(self, config: DerivSettings | None = None) -> None:
        self.config = config or default_settings

    def _mock(self, msg_type: str, **extra: Any) -> dict[str, Any]:
        return {"mock": True, "msg_type": msg_type, **extra}

    def _request(self, payload: dict[str, Any], *, private: bool = False) -> dict[str, Any]:
        if self.config.mock_enabled:
            return self._mock(str(next(iter(payload))), request=payload)
        with MinimalWebSocketTLS(self.config.websocket_url, self.config.timeout_seconds) as ws:
            if private:
                if not self.config.token:
                    raise DerivError("DERIV_API_TOKEN is required for private Deriv calls")
                ws.send_json({"authorize": self.config.token})
                auth = ws.recv_json()
                if auth.get("error"):
                    raise DerivError(str(auth["error"]))
                # TRAVA DE SEGURANCA CANONICA (nao duplicar!): reusa a mesma
                # validacao de conta-demo do cliente maduro. Fail-safe hard-
                # coded: a checagem so e dispensada quando o DerivLiveGate
                # canonico (deriv_demo.py) disser allowed=True -- hoje, nunca,
                # porque os gates de missao nao estao certificados. Antes isto
                # dependia so de self.config.live_enabled, uma flag de runtime
                # que qualquer .env mal configurado poderia flipar sem passar
                # pelos 3 gates de certificacao.
                if not _gate_allows_live():
                    _assert_demo_account(auth.get("authorize", {}))
            ws.send_json(payload)
            response = ws.recv_json()
            if response.get("error"):
                raise DerivError(str(response["error"]))
            return response

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "mock_enabled": self.config.mock_enabled,
            "live_enabled": self.config.live_enabled,
            "endpoint": self.config.websocket_url,
            "default_symbol": self.config.default_symbol,
            "currency": self.config.currency,
            "has_token": bool(self.config.token),
        }

    def ping(self) -> dict[str, Any]:
        if self.config.mock_enabled:
            return self._mock("ping", ping="pong")
        return self._request({"ping": 1})

    def ticks(self, symbol: str | None = None) -> dict[str, Any]:
        target = symbol or self.config.default_symbol
        if self.config.mock_enabled:
            return self._mock("tick", tick={"symbol": target, "quote": 0.0})
        return self._request({"ticks": target, "subscribe": 0})

    def proposal(
        self,
        *,
        amount: float,
        contract_type: str,
        duration: int,
        duration_unit: str,
        symbol: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        if not dry_run and not self.config.live_enabled:
            raise DerivLivePurchaseBlocked("Real Deriv purchase blocked: DERIV_LIVE_ENABLED=false")

        payload = {
            "proposal": 1,
            "amount": amount,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": self.config.currency,
            "duration": duration,
            "duration_unit": duration_unit,
            "symbol": symbol or self.config.default_symbol,
        }
        response = self._request(payload, private=not self.config.mock_enabled)
        if dry_run:
            response["dry_run"] = True
            response["purchase_blocked"] = True
            return response
        raise DerivLivePurchaseBlocked("Buy execution is intentionally not implemented in this safe integration")
