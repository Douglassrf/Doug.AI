"""Fetch Deriv market data for training (public demo, no token required)."""
from __future__ import annotations

import asyncio
import json
from typing import Any

import websockets

from integrations.deriv_demo import DEFAULT_APP_ID, _recv_for_req, _ws_url, load_config


async def fetch_tick_history(symbol: str, count: int = 50) -> dict[str, Any]:
    """Return recent tick prices for strategy simulation."""
    _, app_id = load_config()
    app_id = app_id or DEFAULT_APP_ID
    try:
        async with websockets.connect(_ws_url(app_id, live=False), open_timeout=20) as ws:
            payload = {
                "ticks_history": symbol,
                "count": count,
                "end": "latest",
                "style": "ticks",
                "req_id": 1,
            }
            await ws.send(json.dumps(payload))
            data = await _recv_for_req(ws, 1)
            history = data.get("history", {})
            prices = [float(p) for p in history.get("prices", [])]
            times = history.get("times", [])
            if not prices:
                return {"ok": False, "symbol": symbol, "error": "no prices"}
            return {
                "ok": True,
                "symbol": symbol,
                "prices": prices,
                "times": times,
                "last": prices[-1],
                "pip_size": data.get("pip_size"),
            }
    except Exception as exc:
        return {"ok": False, "symbol": symbol, "error": str(exc)}


def fetch_tick_history_sync(symbol: str, count: int = 50) -> dict[str, Any]:
    return asyncio.run(fetch_tick_history(symbol, count))
