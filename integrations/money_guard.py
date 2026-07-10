"""Money Guard — o cofre de segurança único do Doug.AI (blindagem preventiva).

Hoje o Doug.AI NÃO tem caminho de ordem real (só leitura + paper/simulação).
Este módulo é a trava que QUALQUER execução real futura terá obrigatoriamente
que atravessar — para que, no dia em que alguém ligar o dinheiro real, a
segurança já esteja pronta e não dependa de lembrar de fazer certo.

Espelha as travas provadas no Caça Tesouro:
  1. KILL SWITCH persistente (arquivo data/KILL) — para tudo em milissegundos.
  2. TETO ABSOLUTO por ordem — nenhuma ordem real acima do limite passa.
  3. TRADE-ONLY — recusa operar se a conta/chave pode SACAR (canWithdraw).
  4. TESTNET é livre (dinheiro falso); MAINNET exige live_enabled explícito.

Regra de ouro: na dúvida, BLOQUEIA. É a rede que garante que o dono nunca
perde mais do que decidiu conscientemente arriscar.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("DOUG_DATA_DIR", "data"))
KILL_FILE = DATA_DIR / "KILL"

# Teto absoluto por ordem, em dólares. Ajustável só à mão via env. Padrão $10
# (mesmo piloto do Caça Tesouro). Trava física: acima disso, nenhuma ordem real.
DEFAULT_MAX_ORDEM_USD = 10.0


class MoneyGuardError(RuntimeError):
    """Bloqueio de segurança — impede qualquer operação real insegura."""


# ── Kill switch persistente ─────────────────────────────────────────────────
def is_killed() -> bool:
    return KILL_FILE.exists()


def kill_reason() -> str:
    try:
        return KILL_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def trip(why: str) -> None:
    """Aciona o kill switch AGORA (idempotente)."""
    KILL_FILE.parent.mkdir(parents=True, exist_ok=True)
    KILL_FILE.write_text(f"[{datetime.now(timezone.utc).isoformat()}] {why}\n", encoding="utf-8")


def reset() -> None:
    """Rearma (desliga o kill switch). Ato manual e consciente."""
    try:
        KILL_FILE.unlink()
    except OSError:
        pass


# ── Teto absoluto ───────────────────────────────────────────────────────────
def max_ordem_usd() -> float:
    try:
        return max(0.0, float(os.environ.get("DOUG_MAX_ORDEM_USD", DEFAULT_MAX_ORDEM_USD)))
    except (TypeError, ValueError):
        return DEFAULT_MAX_ORDEM_USD


# ── Trava anti-saque (trade-only) ───────────────────────────────────────────
def account_can_withdraw(account_info: dict[str, Any] | None) -> bool:
    """True se a conta/chave reporta permissão de SAQUE (perigoso p/ dinheiro real)."""
    if not isinstance(account_info, dict):
        return False
    val = account_info.get("canWithdraw")
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes")


def assert_no_withdrawal(account_info: dict[str, Any] | None) -> None:
    if account_can_withdraw(account_info):
        raise MoneyGuardError(
            "🚨 A chave/conta TEM permissão de SAQUE. RECUSANDO operar em dinheiro real. "
            "Gere uma chave TRADE-ONLY (saque desabilitado) e IP travado."
        )


# ── Portão de MAINNET (leitura ou ordem assinada em rede real) ──────────────
def assert_mainnet_allowed(*, live_enabled: bool) -> None:
    """Defesa em profundidade para qualquer chamada assinada em MAINNET.

    Testnet NÃO passa por aqui (é livre — dinheiro falso). Mainnet exige que o
    kill switch esteja desarmado E o modo live esteja explicitamente ligado.
    """
    if is_killed():
        raise MoneyGuardError(f"🛑 KILL SWITCH ativo — mainnet bloqueada. Motivo: {kill_reason() or 'manual'}")
    if not live_enabled:
        raise MoneyGuardError(
            "Mainnet assinada bloqueada: LIVE não habilitado. Use testnet para aprender."
        )


# ── Chokepoint ÚNICO para QUALQUER ordem real futura ────────────────────────
def assert_safe_to_trade(
    *,
    usd_amount: float,
    is_testnet: bool,
    live_enabled: bool,
    account_info: dict[str, Any] | None = None,
) -> None:
    """A porta por onde TODA execução real deve passar. Testnet é liberado."""
    if is_killed():
        raise MoneyGuardError(f"🛑 KILL SWITCH ativo. Motivo: {kill_reason() or 'manual'}")

    if is_testnet:
        return  # dinheiro falso — sem risco, liberado para aprender

    # A partir daqui é DINHEIRO REAL — todas as travas valem.
    if not live_enabled:
        raise MoneyGuardError("Dinheiro real bloqueado: LIVE não habilitado explicitamente.")
    teto = max_ordem_usd()
    if usd_amount > teto:
        raise MoneyGuardError(
            f"Ordem de ${usd_amount:.2f} excede o teto absoluto de ${teto:.2f}. "
            "Aumente DOUG_MAX_ORDEM_USD conscientemente para arriscar mais."
        )
    assert_no_withdrawal(account_info)
