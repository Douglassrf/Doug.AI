"""Live tip-to-tip progress — polled by Streamlit dashboard."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("DOUG_DATA_DIR", "data"))
if not DATA_DIR.is_absolute():
    DATA_DIR = Path(__file__).resolve().parent.parent / DATA_DIR

LIVE_PATH = DATA_DIR / "tip_to_tip_live.json"
LOG_PATH = DATA_DIR / "tip_to_tip_live.log"


def init_live(operator: str = "", total: int = 1000) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "running",
        "operator": operator,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "done": 0,
        "passed": 0,
        "failed": 0,
        "current_mission": "",
        "current_pair": "",
        "current_run": 0,
        "score_pct": 0.0,
        "recent": [],
    }
    _write(payload)
    LOG_PATH.write_text("", encoding="utf-8")


def update_live(
    *,
    operator: str,
    total: int,
    done: int,
    passed: int,
    failed: int,
    mission: str,
    pair: str,
    run: int,
    ok: bool,
    detail: str,
) -> None:
    recent: list[dict[str, Any]] = []
    if LIVE_PATH.exists():
        try:
            recent = json.loads(LIVE_PATH.read_text(encoding="utf-8")).get("recent", [])
        except (json.JSONDecodeError, OSError):
            recent = []

    mark = "OK" if ok else "FAIL"
    line = f"[{mark}] {mission} {pair} run{run} — {detail}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    recent.insert(0, {
        "ts": datetime.now(timezone.utc).isoformat(),
        "mission": mission,
        "pair": pair,
        "run": run,
        "ok": ok,
        "detail": detail[:120],
    })
    recent = recent[:30]

    payload = {
        "status": "running" if done < total else "finished",
        "operator": operator,
        "started_at": _read_field("started_at") or datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "done": done,
        "passed": passed,
        "failed": failed,
        "current_mission": mission,
        "current_pair": pair,
        "current_run": run,
        "score_pct": round(100 * passed / done, 2) if done else 0.0,
        "recent": recent,
    }
    _write(payload)


def finish_live(*, passed: int, failed: int, grade: str) -> None:
    total = passed + failed
    payload = _read_all()
    payload.update({
        "status": "finished",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "done": total,
        "passed": passed,
        "failed": failed,
        "score_pct": round(100 * passed / total, 2) if total else 0.0,
        "grade": grade,
        "current_mission": "—",
        "current_pair": "—",
        "current_run": 0,
    })
    _write(payload)


def _read_field(key: str) -> str | None:
    data = _read_all()
    val = data.get(key)
    return str(val) if val is not None else None


def _read_all() -> dict[str, Any]:
    if not LIVE_PATH.exists():
        return {}
    try:
        return json.loads(LIVE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write(payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
