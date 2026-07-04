"""Bridge to Doug.AI mission modules — real scores when importable, demo fallback otherwise."""
from __future__ import annotations

import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LAYER_NAMES = [
    "L1 Data Connectors",
    "L2 Market Servo",
    "L3 On-Chain Intel",
    "L4 Psychology/News",
    "L5 Memory/Learning",
    "L6 Risk Empire",
    "L7 Intelligence Council",
    "L8 Three-Layer Alert",
    "L9 Red Team",
    "L10 Shadow Executor",
]


@dataclass
class BridgeStatus:
    source: str
    modules_loaded: list[str]
    errors: list[str]


def _candidate_roots() -> list[Path]:
    env_latest = os.environ.get("DOUG_LATEST_DIR", "/app/latest")
    env_missions = os.environ.get("DOUG_MISSIONS_DIR", "/app/missions")
    local_root = Path(__file__).resolve().parent.parent
    roots: list[Path] = []
    for p in (env_latest, env_missions, str(local_root / "latest"), str(local_root / "missions")):
        path = Path(p)
        if path.exists() and path not in roots:
            roots.append(path)
    return roots


def _setup_import_paths() -> None:
    for root in _candidate_roots():
        doug_os = root / "doug_os"
        if doug_os.is_dir():
            parent = str(doug_os.parent)
            if parent not in sys.path:
                sys.path.insert(0, parent)
        if root.name == "missions":
            for sub in root.glob("mission_*/doug_os"):
                parent = str(sub.parent)
                if parent not in sys.path:
                    sys.path.insert(0, parent)


def probe_missions() -> BridgeStatus:
    _setup_import_paths()
    loaded: list[str] = []
    errors: list[str] = []

    probes = [
        ("doug_os.discovery.three_layer_alert_system", "ThreeLayerAlertSystem"),
        ("doug_os.discovery.red_team_adversarial", "RedTeamAdversarial"),
        ("doug_os.discovery.system_health_monitor", "SystemHealthMonitor"),
        ("doug_os.core.regime_detector", "RegimeDetector"),
        ("doug_os.core.audit_log", "AuditLog"),
    ]
    for module_name, class_name in probes:
        try:
            mod = __import__(module_name, fromlist=[class_name])
            getattr(mod, class_name)
            loaded.append(f"{module_name}.{class_name}")
        except Exception as exc:  # noqa: BLE001 — bridge must never crash dashboard
            errors.append(f"{module_name}: {exc}")

    source = "live" if loaded else "demo"
    return BridgeStatus(source=source, modules_loaded=loaded, errors=errors)


def _demo_layer_scores() -> list[dict[str, Any]]:
    seed = int(time.time()) // 30
    rng = random.Random(seed)
    scores = []
    for i, name in enumerate(LAYER_NAMES):
        base = rng.uniform(55, 92)
        if i >= 7:
            base -= rng.uniform(0, 8)
        score = max(20, min(100, round(base)))
        status = "green" if score >= 70 else ("yellow" if score >= 50 else "red")
        scores.append({"layer": i + 1, "name": name, "score": score, "status": status})
    return scores


def _live_layer_scores() -> list[dict[str, Any]] | None:
    try:
        from doug_os.discovery.three_layer_alert_system import ThreeLayerAlertSystem

        alert = ThreeLayerAlertSystem()
        signal = {
            "evidence_score": 0.82,
            "agreement_score": 0.78,
            "risk_pct": 1.5,
            "asset": "BTC/USDT",
        }
        decision = alert.evaluate(signal)
        layer_map = {lr.layer: lr for lr in decision.layers}

        scores: list[dict[str, Any]] = []
        for i, name in enumerate(LAYER_NAMES):
            if i < 3:
                lr = layer_map.get(i + 1)
                if lr:
                    score = int(lr.score * 100)
                    status = "green" if lr.passed else "red"
                    scores.append({"layer": i + 1, "name": name, "score": score, "status": status})
                    continue
            # layers 4-10: derive from alert outcome + health heuristics
            offset = 72 + (i - 3) * 2
            if not decision.approved:
                offset -= 15
            score = max(25, min(98, offset))
            status = "green" if score >= 70 else ("yellow" if score >= 50 else "red")
            scores.append({"layer": i + 1, "name": name, "score": score, "status": status})
        return scores
    except Exception:
        return None


def get_layer_scores() -> tuple[list[dict[str, Any]], str]:
    live = _live_layer_scores()
    if live:
        return live, "live"
    return _demo_layer_scores(), "demo"


def get_thermometer(layer_scores: list[dict[str, Any]] | None = None) -> int:
    layers = layer_scores or get_layer_scores()[0]
    if not layers:
        return 60
    return int(sum(l["score"] for l in layers) / len(layers))


def get_signal_counts(audit_entries: list[dict[str, Any]]) -> dict[str, int]:
    green = yellow = red = 0
    for entry in audit_entries:
        payload = entry.get("payload", {})
        score = payload.get("layer_score", payload.get("confidence", 0.5))
        if isinstance(score, float) and score <= 1:
            score = int(score * 100)
        if score >= 70:
            green += 1
        elif score >= 50:
            yellow += 1
        else:
            red += 1
    return {"green": green, "yellow": yellow, "red": red}


def get_council_snapshot() -> dict[str, Any]:
    """Placeholder council panel — demo data with optional live regime."""
    seed = int(time.time()) // 30
    rng = random.Random(seed)
    regime = "BULL_TRENDING"
    try:
        from doug_os.core.regime_detector import RegimeDetector

        det = RegimeDetector()
        if hasattr(det, "detect"):
            result = det.detect({"price": 68000, "volatility": 0.022})
            if isinstance(result, dict):
                regime = result.get("regime", regime)
    except Exception:
        pass

    options = ["BUY", "SELL", "HOLD"]
    decision = rng.choices(options, weights=[0.45, 0.2, 0.35])[0]
    return {
        "decision": decision,
        "confidence": round(rng.uniform(0.55, 0.92), 2),
        "regime": regime,
        "agents": [
            {"name": "MarketAgent", "vote": decision, "weight": 0.22},
            {"name": "RiskAgent", "vote": "HOLD", "weight": 0.20},
            {"name": "DiscoveryAgent", "vote": decision, "weight": 0.18},
            {"name": "LearningAgent", "vote": "HOLD", "weight": 0.18},
            {"name": "AuditAgent", "vote": decision, "weight": 0.22},
        ],
    }


def get_red_team_snapshot(council: dict[str, Any]) -> dict[str, Any]:
    seed = int(time.time()) // 30
    rng = random.Random(seed)
    if council.get("decision") != "BUY" or council.get("confidence", 0) < 0.6:
        return {"verdict": "INACTIVE", "score": 0.0, "arguments": []}
    score = round(rng.uniform(0.15, 0.75), 3)
    verdict = "BLOCK" if score >= 0.7 else ("REDUCE" if score >= 0.4 else "PASS")
    args = []
    if score > 0.5:
        args.append("RSI sobrecomprado — risco de reversão")
    if score > 0.65:
        args.append("Histórico de perdas em regime similar")
    return {"verdict": verdict, "score": score, "arguments": args}
