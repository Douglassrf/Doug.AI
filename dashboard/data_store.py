"""Read/write dashboard data files (settings + audit log)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("DOUG_DATA_DIR", "/app/data"))
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SETTINGS_PATH = DATA_DIR / "settings.json"
AUDIT_LOG_PATH = DATA_DIR / "audit_log.jsonl"
# Log SEPARADO para ticks sinteticos do demo generator — nunca deve entrar no
# mesmo arquivo de decisoes reais (achado real 2026-07-10: com demo_generator
# default=True, BUY/SELL/HOLD aleatorios eram gravados no MESMO audit_log.jsonl
# onde decision_engine.py e continuous_trainer.py gravam decisoes de verdade,
# ficando indistinguiveis no historico).
DEMO_AUDIT_LOG_PATH = DATA_DIR / "audit_log_demo.jsonl"

DEFAULT_SETTINGS: dict[str, Any] = {
    "refresh_interval_sec": 30,
    "horizon": "daily",
    "paper_mode": True,
    "max_assets": 3,
    "theme": "dark",
    "demo_generator": False,
    "mode": "PAPER",
    "deriv": {
        "enabled": True,
        "app_id": 1089,
        "symbols": ["R_100", "cryBTCUSD"],
    },
}


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    with SETTINGS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(settings: dict[str, Any]) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_audit_log(limit: int = 100) -> list[dict[str, Any]]:
    if not AUDIT_LOG_PATH.exists():
        return []
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(entries[-limit:]))


def append_audit_entry(
    event_type: str,
    payload: dict[str, Any],
    *,
    path: Path | None = None,
) -> dict[str, Any]:
    target = path or AUDIT_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
