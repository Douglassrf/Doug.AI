#!/usr/bin/env python3
"""Preflight checks — DogEye must pass ALL before tip-to-tip certification."""
from __future__ import annotations

import importlib.util
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

CHECKS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    mark = "OK" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{mark}] {name}{suffix}")


def main() -> int:
    print("=== DogEye Preflight (obrigatorio antes do teste solo) ===\n")

    record("Python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0])

    for pkg in ("numpy", "websockets", "pytest"):
        record(f"pacote {pkg}", importlib.util.find_spec(pkg) is not None)

    env_path = ROOT / ".env"
    record(".env existe", env_path.exists(), str(env_path) if env_path.exists() else "copy .env.example .env")

    if env_path.exists():
        text = env_path.read_text(encoding="utf-8")
        record("DOUG_MODE=demo", "DOUG_MODE=demo" in text or os.getenv("DOUG_MODE", "").lower() == "demo")
        record("DERIV_LIVE_ENABLED=false", "DERIV_LIVE_ENABLED=false" in text.lower() or not os.getenv("DERIV_LIVE_ENABLED"))

    record("pasta missions/", (ROOT / "missions").is_dir())
    record("pasta integrations/", (ROOT / "integrations").is_dir())
    record("script tip_to_tip_training.py", (ROOT / "scripts" / "tip_to_tip_training.py").is_file())

    try:
        from integrations.deriv_bridge import DerivBridge

        bridge = DerivBridge()
        st = bridge.status
        record("DerivBridge carrega", True, f"app_id={st.app_id}")
        ping = bridge.ping()
        record("Ping Deriv", ping.get("msg_type") == "ping" or ping.get("ping") == "pong")
    except Exception as exc:
        record("DerivBridge carrega", False, str(exc))

    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "test_deriv_demo.py"), "--public-only", "--symbols", "R_100"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
        )
        record("test_deriv_demo public", proc.returncode == 0, proc.stdout.strip()[-80:] if proc.stdout else proc.stderr[:80])
    except Exception as exc:
        record("test_deriv_demo public", False, str(exc))

    record("rede (hostname)", True, platform.node())

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n=== Resultado: {len(CHECKS) - len(failed)}/{len(CHECKS)} OK ===")
    if failed:
        print("\nCorrija os FAIL acima SEM pedir ajuda ao agente. Depois rode de novo.")
        return 1
    print("\nPreflight OK. Pode iniciar certificacao:")
    print("  python scripts/tip_to_tip_training.py --certify --operator \"SEU_NOME\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
