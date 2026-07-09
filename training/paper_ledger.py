"""Livro-razao de posicoes em paper trading — o que faltava pra existir
gestao de risco de PORTFOLIO de verdade (curva de capital, drawdown agregado,
kill-switch automatico) e um "veredito protetor" por combinacao (detecta uma
sequencia recente de perdas MAIS RAPIDO do que esperar o proximo treino
agendado perceber pelo agregado historico inteiro).

Por que isto nao existia: toda a "confianca" do sistema vinha de estatisticas
agregadas calculadas em treino (Playbook, leaderboard). Uma decisao OPERAR ao
vivo nunca era conferida depois — o sistema nunca sabia se aquele "OPERAR"
especifico teria ganhado ou perdido de verdade. Sem isso, nao ha curva de
capital real, nao ha nocao de drawdown, e uma mudanca de regime so seria
percebida no proximo treino de edge (2x/dia).

Fluxo:
  1. decision_engine.decide_pair loga toda decisao OPERAR aqui como posicao
     aberta (record_open_position).
  2. A cada ciclo da Torre de Controle, core/orchestrator chama
     resolve_pending_positions ANTES de decidir — busca o preco atual dos
     pares com posicao pendente vencida, avalia ganho/perda, grava o
     resultado, atualiza a curva de capital agregada e o kill-switch.
  3. decision_engine consulta rolling_bucket_health antes de aprovar um novo
     OPERAR — se as ultimas operacoes REAIS dessa combinacao especifica
     vieram mal, rebaixa para OBSERVAR mesmo que o Playbook (estatistica
     historica agregada) ainda diga que e um edge comprovado.

Modo seguro: tudo aqui e paper — nenhuma ordem real, so contabilidade de
"e se eu tivesse operado".
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
TRAINING_DIR = DATA / "training"
OPEN_POSITIONS_PATH = TRAINING_DIR / "paper_open_positions.json"
LEDGER_PATH = TRAINING_DIR / "paper_trades.jsonl"
EQUITY_PATH = TRAINING_DIR / "paper_equity.json"

# Horizonte de avaliacao: mesma convencao do treino de edge (M38, horizon=3
# candles de 60s) — a posicao e avaliada no mesmo prazo em que o edge foi
# comprovado, nao num prazo arbitrario diferente.
HORIZON_SECONDS = 180

# Drawdown agregado (sobre capital nocional 100.0) que aciona o kill-switch:
# para novas OPERAR ate o capital se recuperar. Nivel escolhido a partir da
# pratica comum de mesas prop (10-15% de drawdown maximo antes de parar).
KILL_SWITCH_DRAWDOWN_PCT = 15.0
# Recuperacao parcial exigida antes de destravar o kill-switch (evita ligar/
# desligar toda hora perto do limite — histerese).
KILL_SWITCH_RESET_DRAWDOWN_PCT = 8.0

# Veredito protetor: para uma combinacao especifica se as ultimas N operacoes
# reais tiverem M ou mais derrotas — pego de mission_331 (fase_xxii), so que
# aqui aplicado a resultado REAL resolvido, nao a replay de backtest.
PROTECTIVE_WINDOW = 10
PROTECTIVE_MAX_LOSSES = 7


def _bucket_key(strategy_id: str, pair: str, scenario: str) -> str:
    return f"{strategy_id}|{pair}|{scenario}"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data: Any) -> None:
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def record_open_position(
    *,
    pair: str,
    scenario: str,
    strategy_id: str,
    direction: str,
    entry: float,
    stake_pct: float,
) -> None:
    """Registra uma decisao OPERAR como posicao aberta, pra ser resolvida depois."""
    if direction not in ("buy", "sell") or not entry:
        return
    positions = _load_json(OPEN_POSITIONS_PATH, [])
    positions.append({
        "id": f"pp_{datetime.now(timezone.utc).timestamp():.6f}",
        "pair": pair, "scenario": scenario, "strategy_id": strategy_id,
        "direction": direction, "entry": entry, "stake_pct": stake_pct,
        "opened_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_json(OPEN_POSITIONS_PATH, positions)


def _current_equity() -> dict[str, Any]:
    return _load_json(EQUITY_PATH, {
        "equity_pct": 100.0,
        "peak_pct": 100.0,
        "drawdown_pct": 0.0,
        "kill_switch_active": False,
        "resolved_trades": 0,
        "updated_at": None,
    })


def resolve_pending_positions(price_lookup) -> list[dict[str, Any]]:
    """Resolve posicoes cujo horizonte ja passou. `price_lookup(pair) -> float|None`
    e injetado por quem chama (o orchestrator ja busca candles por pair a cada
    ciclo — evita este modulo depender diretamente de integrations/).

    Retorna a lista de trades resolvidos neste ciclo (pode ser vazia)."""
    from training.strategies import evaluate_signal

    positions = _load_json(OPEN_POSITIONS_PATH, [])
    if not positions:
        return []

    still_open = []
    resolved: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    equity = _current_equity()

    for pos in positions:
        opened_at = datetime.fromisoformat(pos["opened_at"])
        if now < opened_at + timedelta(seconds=HORIZON_SECONDS):
            still_open.append(pos)
            continue
        exit_price = price_lookup(pos["pair"])
        if exit_price is None:
            # Sem preco agora (par fechado/erro de rede) — tenta de novo no
            # proximo ciclo em vez de descartar a posicao.
            still_open.append(pos)
            continue

        won = evaluate_signal(pos["direction"], pos["entry"], exit_price)
        move_pct = (exit_price - pos["entry"]) / pos["entry"] * 100.0
        signed_move = move_pct if pos["direction"] == "buy" else -move_pct
        pnl_pct = signed_move * (pos["stake_pct"] / 100.0)  # PnL sobre o capital nocional

        trade = {
            **pos, "exit": exit_price, "closed_at": now.isoformat(),
            "won": won, "move_pct": round(signed_move, 6), "pnl_pct": round(pnl_pct, 6),
        }
        resolved.append(trade)
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trade, ensure_ascii=False) + "\n")

        equity["equity_pct"] = round(equity["equity_pct"] + pnl_pct, 6)
        equity["peak_pct"] = max(equity["peak_pct"], equity["equity_pct"])
        equity["resolved_trades"] += 1

    drawdown = 0.0
    if equity["peak_pct"] > 0:
        drawdown = max(0.0, (equity["peak_pct"] - equity["equity_pct"]) / equity["peak_pct"] * 100.0)
    equity["drawdown_pct"] = round(drawdown, 4)

    # Histerese: liga o kill-switch em 15% de drawdown, so desliga quando
    # recuperar pra abaixo de 8% — sem isto, o kill-switch ligaria/desligaria
    # a cada ciclo perto do limite (comportamento instavel e inutil).
    if drawdown >= KILL_SWITCH_DRAWDOWN_PCT:
        equity["kill_switch_active"] = True
    elif drawdown <= KILL_SWITCH_RESET_DRAWDOWN_PCT:
        equity["kill_switch_active"] = False

    equity["updated_at"] = now.isoformat()
    _save_json(EQUITY_PATH, equity)
    _save_json(OPEN_POSITIONS_PATH, still_open)
    return resolved


def open_positions() -> list[dict[str, Any]]:
    """Posicoes paper atualmente abertas (ainda nao resolvidas) — usado pelo
    dimensionamento ciente de correlacao (decision_engine.py): antes de abrir
    uma nova OPERAR, olha o que ja esta aberto pra nao dobrar risco em pares
    que se movem parecido (ex.: BOOM1000 e BOOM500 ao mesmo tempo, no mesmo
    lado, e sem essa checagem cada um seria dimensionado como se fosse a
    UNICA aposta em risco, quando na pratica sao duas apostas correlacionadas)."""
    return _load_json(OPEN_POSITIONS_PATH, [])


def is_kill_switch_active() -> bool:
    return bool(_current_equity().get("kill_switch_active", False))


def equity_snapshot() -> dict[str, Any]:
    return _current_equity()


def rolling_bucket_health(strategy_id: str, pair: str, scenario: str) -> dict[str, Any]:
    """Ultimas PROTECTIVE_WINDOW operacoes REAIS resolvidas desta combinacao
    exata. Retorna {'n': int, 'losses': int, 'tripped': bool} — 'tripped' =
    True quando >= PROTECTIVE_MAX_LOSSES das ultimas PROTECTIVE_WINDOW
    operacoes foram derrota, mesmo que o Playbook (agregado historico) ainda
    aprove — pega quebra de regime mais rapido que esperar novo treino."""
    key = _bucket_key(strategy_id, pair, scenario)
    if not LEDGER_PATH.exists():
        return {"n": 0, "losses": 0, "tripped": False}
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"n": 0, "losses": 0, "tripped": False}

    matches = []
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if _bucket_key(row.get("strategy_id", ""), row.get("pair", ""), row.get("scenario", "")) == key:
            matches.append(row)
            if len(matches) >= PROTECTIVE_WINDOW:
                break

    n = len(matches)
    losses = sum(1 for m in matches if m.get("won") is False)
    tripped = n >= PROTECTIVE_WINDOW and losses >= PROTECTIVE_MAX_LOSSES
    return {"n": n, "losses": losses, "tripped": tripped}
