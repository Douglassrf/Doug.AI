#!/usr/bin/env python3
"""Setup Deriv API for Doug.AI demo — opens URLs, validates .env, tests connection."""
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from integrations.deriv_demo import (  # noqa: E402
    DEFAULT_APP_ID,
    is_doug_demo_mode,
    load_config,
    run_public_demo_snapshot,
    run_snapshot,
)

ENV_TEMPLATE = """# Deriv Demo — Doug.AI (NUNCA commite este arquivo com token real)
# Gerado/atualizado por scripts/setup_deriv_api.py

DERIV_APP_ID=1089
DERIV_API_TOKEN=
DOUG_MODE=demo
DOUG_DATA_DIR=data
"""

DERIV_DEVELOPERS_URL = "https://developers.deriv.com/"
DERIV_TOKEN_URL = "https://app.deriv.com/account/api-token"
DERIV_REGISTER_APP_URL = "https://api.deriv.com/"

TOKEN_STEPS = """
=== Token DEMO Deriv (3 cliques apos login) ===
1. Login em app.deriv.com -> selecione **Conta demo** (canto superior).
2. Configuracoes da conta -> **API token** -> **Create** (ou Criar).
3. Marque **Read** + **Trade** -> **Create** -> copie o token para .env:
   DERIV_API_TOKEN=seu_token_aqui

App ID publico para MVP: 1089 (nao precisa registrar app customizado).
Registro opcional de app: https://api.deriv.com/ (Register application).
"""


def ensure_env(env_path: Path, *, force_defaults: bool = False) -> bool:
    """Create or patch .env with required Deriv demo keys."""
    changed = False
    if not env_path.exists():
        env_path.write_text(ENV_TEMPLATE, encoding="utf-8")
        print(f"[OK] Criado {env_path}")
        return True

    lines = env_path.read_text(encoding="utf-8").splitlines()
    required = {
        "DERIV_APP_ID": "1089",
        "DERIV_API_TOKEN": "",
        "DOUG_MODE": "demo",
    }
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.strip().startswith("#") else ""
        if key in required:
            seen.add(key)
            if force_defaults:
                out.append(f"{key}={required[key]}")
                if line != f"{key}={required[key]}":
                    changed = True
            else:
                out.append(line)
        else:
            out.append(line)
    for key, val in required.items():
        if key not in seen:
            out.append(f"{key}={val}")
            changed = True
    if changed or force_defaults:
        env_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
        print(f"[OK] .env validado/atualizado em {env_path}")
    else:
        print(f"[OK] .env já contém chaves Deriv demo")
    return changed


def open_deriv_urls(*, open_browser: bool = True) -> None:
    urls = [DERIV_DEVELOPERS_URL, DERIV_TOKEN_URL]
    for url in urls:
        print(f"  -> {url}")
        if open_browser:
            webbrowser.open(url)


def validate_env() -> tuple[str | None, int, str]:
    load_dotenv = None
    try:
        from dotenv import load_dotenv as _ld

        load_dotenv = _ld
    except ImportError:
        pass
    if load_dotenv:
        load_dotenv(ROOT / ".env")
    token, app_id = load_config()
    mode = __import__("os").environ.get("DOUG_MODE", "?")
    print(f"  DERIV_APP_ID={app_id}")
    print(f"  DOUG_MODE={mode}")
    print(f"  DERIV_API_TOKEN={'(vazio — demo público OK)' if not token else '(configurado)'}")
    return token, app_id, mode


def test_connection(*, public_only: bool = False) -> int:
    token, app_id, _ = validate_env()
    if token and not public_only:
        print(f"\n[Teste] Conexão autenticada (app_id={app_id})...")
        snap = run_snapshot(token=token, app_id=app_id, log_paper=False)
    elif is_doug_demo_mode() or public_only or not token:
        print(f"\n[Teste] Demo público sem token (app_id={app_id or DEFAULT_APP_ID})...")
        snap = run_public_demo_snapshot(app_id=app_id, log_paper=False)
    else:
        print("[ERRO] Sem token e DOUG_MODE != demo")
        return 1

    if snap.error:
        print(f"[ERRO] {snap.error}")
        return 2
    acct = snap.account
    if acct:
        print(f"[OK] Conta: {acct.loginid} | Saldo: {acct.balance:.2f} {acct.currency}")
    for sym, tick in snap.ticks.items():
        if "quote" in tick:
            print(f"   Tick {sym}: {tick['quote']}")
    print("[OK] Conexão Deriv demo OK — data/deriv_status.json atualizado")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup Deriv API for Doug.AI demo")
    parser.add_argument("--no-browser", action="store_true", help="Não abrir URLs no navegador")
    parser.add_argument("--skip-test", action="store_true", help="Só validar .env, sem testar WS")
    parser.add_argument("--public-only", action="store_true", help="Testar só demo público (sem token)")
    parser.add_argument("--force-env", action="store_true", help="Resetar chaves Deriv no .env")
    args = parser.parse_args()

    env_path = ROOT / ".env"
    print("=== Doug.AI — Setup Deriv API (demo) ===\n")
    ensure_env(env_path, force_defaults=args.force_env)

    print("\nAbrindo portais Deriv:")
    open_deriv_urls(open_browser=not args.no_browser)

    print(TOKEN_STEPS)

    if args.skip_test:
        return 0
    return test_connection(public_only=args.public_only)


if __name__ == "__main__":
    raise SystemExit(main())
