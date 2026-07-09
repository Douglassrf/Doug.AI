"""Cerebro de Decisao Doug.AI — decisao viva, explicada e com abstencao inteligente.

Liga TUDO ponta a ponta: candles reais -> cenario -> voto ponderado das 10
estrategias pelo desempenho historico REAL do bucket (backtest M38 + treino
continuo) -> gate de confianca -> expectancy -> tamanho de posicao (Kelly
fracionado) -> decisao explicada.

Filosofia central (a unica forma honesta de "nao errar"): o erro nao e
eliminado, e EVITADO POR ABSTENCAO. O Doug so recomenda operar quando a
vantagem esta comprovada nos dados; na duvida, observa; sem vantagem, fica
de fora. Tres niveis de decisao:

  OPERAR    — bucket passou no gate (win rate alto + amostra minima) e
              expectancy positiva. Recomendacao paper com stake sugerido.
  OBSERVAR  — vantagem estatistica detectada (WR >= WATCH_WIN_RATE com
              amostra razoavel) mas ainda abaixo do gate. Coletar mais dados.
  FICAR_DE_FORA — sem sinal, sem historico ou sem vantagem. Nao opera.

Modo seguro: 100%% paper. Nenhuma ordem real e enviada a lugar nenhum.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from training.backtester import BACKTEST_LEADERBOARD_PATH, fetch_candles_sync
from training.confidence_gate import CONFIDENCE_THRESHOLD, MIN_SAMPLES_FOR_CONFIDENCE
from training.continuous_trainer import LEADERBOARD_PATH
from training.news_feed import load_news_snapshot, topic_for_pair
from training.scenarios import detect_scenario
from training.strategies import SIGNAL_FNS, STRATEGIES

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
DECISIONS_PATH = DATA / "training" / "live_decisions.jsonl"
PLAYBOOK_PATH = DATA / "training" / "playbook.json"


def load_playbook() -> dict[str, dict[str, Any]]:
    """Carrega o Playbook (vantagens comprovadas pelo treino de edge M38),
    indexado por 'strategy|pair|scenario' -> {win_rate, trades, nivel}."""
    if not PLAYBOOK_PATH.exists():
        return {}
    try:
        edges = json.loads(PLAYBOOK_PATH.read_text(encoding="utf-8")).get("edges", [])
    except (json.JSONDecodeError, OSError):
        return {}
    idx: dict[str, dict[str, Any]] = {}
    for e in edges:
        key = f"{e.get('strategy_id')}|{e.get('pair')}|{e.get('scenario')}"
        idx[key] = e
    return idx


def playbook_edge_for(pair: str, scenario: str, playbook: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Melhor edge comprovado do Playbook para este par+cenario (qualquer estrategia)."""
    candidatos = [
        e for k, e in playbook.items()
        if k.endswith(f"|{pair}|{scenario}")
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda e: e.get("win_rate", 0))

# Nivel OBSERVAR: vantagem estatistica plausivel, ainda sem o rigor do gate
WATCH_WIN_RATE = 0.60
WATCH_MIN_SAMPLES = 20
# Peso minimo de consenso para nao ficar de fora mesmo no nivel OBSERVAR
MIN_CONSENSUS_SCORE = 0.10
# Kelly fracionado: fracao de seguranca e teto duro de stake por operacao
KELLY_FRACTION = 0.25
MAX_STAKE_PCT = 2.0  # nunca sugerir mais que 2% do capital por operacao
# Filtro de noticias (anti-manipulacao): acima deste impacto, nao opera
NEWS_RISK_BLOCK = 0.70
# Sentimento fortemente contrario ao sinal tambem barra a operacao
NEWS_BIAS_CONFLICT = 0.30


@dataclass
class StrategyVote:
    strategy_id: str
    direction: str
    win_rate: float | None
    trades: int
    expectancy_pct: float | None
    weight: float
    source: str  # "backtest" | "tick" | "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "direction": self.direction,
            "win_rate": self.win_rate,
            "trades": self.trades,
            "expectancy_pct": self.expectancy_pct,
            "weight": round(self.weight, 4),
            "source": self.source,
        }


@dataclass
class Decision:
    pair: str
    scenario: str
    level: str  # "OPERAR" | "OBSERVAR" | "FICAR_DE_FORA"
    direction: str  # "buy" | "sell" | "hold"
    consensus_score: float
    confidence: float | None
    stake_pct: float
    price: float | None
    reasons: list[str] = field(default_factory=list)
    votes: list[StrategyVote] = field(default_factory=list)
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "pair": self.pair,
            "scenario": self.scenario,
            "level": self.level,
            "direction": self.direction,
            "consensus_score": round(self.consensus_score, 4),
            "confidence": self.confidence,
            "stake_pct": self.stake_pct,
            "price": self.price,
            "reasons": self.reasons,
            "votes": [v.to_dict() for v in self.votes],
            "mode": "PAPER",
        }


def _load_stats(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("stats", {})
    except (json.JSONDecodeError, OSError):
        return {}


def load_knowledge() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Retorna (backtest_stats, tick_stats) — a memoria acumulada do Doug."""
    return _load_stats(BACKTEST_LEADERBOARD_PATH), _load_stats(LEADERBOARD_PATH)


def _bucket_info(
    key: str,
    backtest: dict[str, dict[str, Any]],
    tick: dict[str, dict[str, Any]],
) -> tuple[float | None, int, float | None, str]:
    """(win_rate, trades, expectancy_pct, fonte) — prioriza o backtest M38 (mais amostra)."""
    b = backtest.get(key)
    if b and int(b.get("trades", 0)) > 0:
        return (
            float(b.get("win_rate", 0.0)),
            int(b.get("trades", 0)),
            float(b.get("expectancy_pct", 0.0)),
            "backtest",
        )
    t = tick.get(key)
    if t and int(t.get("trades", 0)) > 0:
        return float(t.get("win_rate", 0.0)), int(t.get("trades", 0)), None, "tick"
    return None, 0, None, "none"


def _vote_weight(win_rate: float | None, trades: int, expectancy_pct: float | None) -> float:
    """Peso do voto: vantagem acima de 50%, amortecida pela amostra.

    Sem historico -> peso zero (voto nao conta). Vantagem negativa -> peso
    negativo (o voto vira alerta contrario). Expectancy negativa zera o peso
    mesmo com win rate alto (ganhar pouco e perder muito nao e vantagem).
    """
    if win_rate is None or trades <= 0:
        return 0.0
    sample_factor = min(1.0, trades / 50.0)
    edge = (win_rate - 0.5) * 2.0  # -1..1
    weight = edge * sample_factor
    if expectancy_pct is not None and expectancy_pct <= 0 and weight > 0:
        return 0.0
    return weight


def apply_news_filter(
    level: str,
    direction: str,
    pair: str,
    news_snapshot: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    """Filtro anti-manipulacao por noticias. Retorna (novo_nivel, motivos).

    - Noticia de ALTO impacto recente no topico do par -> rebaixa OPERAR para
      OBSERVAR (janela de movimento erratico/manipulavel; melhor nao operar).
    - Sentimento fortemente CONTRARIO ao sinal -> FICAR_DE_FORA.
    - Pares sinteticos (R_*) sao imunes a noticias: filtro nao se aplica.
    """
    if level == "FICAR_DE_FORA" or direction == "hold":
        return level, []
    topic = topic_for_pair(pair)
    if topic is None:
        return level, []
    if not news_snapshot:
        return level, ["Radar de noticias sem snapshot recente — filtro neutro (rode scripts/fetch_news.py)."]
    summary = (news_snapshot.get("summary") or {}).get(topic)
    if not summary:
        return level, []

    reasons: list[str] = []
    risk = float(summary.get("risk", 0.0))
    bias = float(summary.get("bias", 0.0))
    top = summary.get("top_headline") or "?"

    if risk >= NEWS_RISK_BLOCK:
        reasons.append(
            f"NOTICIA QUENTE ({topic}, impacto {risk:.2f}): \"{top}\". "
            "Janela sujeita a movimento erratico/manipulado — sem operacao agora."
        )
        return ("OBSERVAR" if level == "OPERAR" else level), reasons

    signed = bias if direction == "buy" else -bias
    if signed <= -NEWS_BIAS_CONFLICT:
        reasons.append(
            f"Sentimento de noticias ({topic}: {bias:+.2f}) fortemente contrario ao sinal "
            f"{direction.upper()}. Abstencao prudente."
        )
        return "FICAR_DE_FORA", reasons

    if abs(bias) >= 0.15:
        reasons.append(f"Noticias ({topic}) com vies {bias:+.2f} — sem conflito com o sinal.")
    return level, reasons


def _kelly_stake(win_rate: float) -> float:
    """Kelly fracionado p/ payoff 1:1: f = (2*wr - 1) * fracao, com teto duro."""
    kelly = max(0.0, 2.0 * win_rate - 1.0)
    return round(min(kelly * KELLY_FRACTION * 100.0, MAX_STAKE_PCT), 2)


def decide_pair(
    pair: str,
    *,
    candles: int = 120,
    granularity: int = 60,
    backtest_stats: dict[str, dict[str, Any]] | None = None,
    tick_stats: dict[str, dict[str, Any]] | None = None,
) -> Decision:
    """Decisao completa e explicada para um par, AGORA, com dados reais."""
    if backtest_stats is None or tick_stats is None:
        backtest_stats, tick_stats = load_knowledge()

    series = fetch_candles_sync(pair, candles, granularity)
    closes = [c["close"] for c in series if c.get("close")]
    if len(closes) < 25:
        return Decision(
            pair=pair, scenario="?", level="FICAR_DE_FORA", direction="hold",
            consensus_score=0.0, confidence=None, stake_pct=0.0, price=None,
            reasons=["Sem dados de mercado suficientes agora — impossivel avaliar."],
        )

    scenario = detect_scenario(closes[-30:])
    price = closes[-1]
    votes: list[StrategyVote] = []
    buy_score = sell_score = 0.0
    best_bucket: tuple[float, int] | None = None  # (win_rate, trades) do melhor voto na direcao vencedora

    for spec in STRATEGIES:
        fn = SIGNAL_FNS.get(spec.id)
        if fn is None:
            continue
        direction = fn(closes)
        if direction == "hold":
            continue
        key = f"{spec.id}|{pair}|{scenario}"
        wr, trades, exp, source = _bucket_info(key, backtest_stats, tick_stats)
        weight = _vote_weight(wr, trades, exp)
        votes.append(StrategyVote(spec.id, direction, wr, trades, exp, weight, source))
        if direction == "buy":
            buy_score += weight
        else:
            sell_score += weight

    consensus = buy_score - sell_score
    direction = "buy" if consensus > 0 else "sell" if consensus < 0 else "hold"
    score = abs(consensus)

    reasons: list[str] = [f"Cenario atual: {scenario} | {len(votes)} estrategias sinalizaram."]

    if direction == "hold" or score < MIN_CONSENSUS_SCORE:
        reasons.append(
            "Sem consenso com respaldo historico — as estrategias divergem ou nao ha "
            "vantagem comprovada neste cenario. Decisao: nao operar."
        )
        d = Decision(pair, scenario, "FICAR_DE_FORA", "hold", score, None, 0.0, price, reasons, votes)
        _log_decision(d)
        return d

    # Melhor bucket na direcao vencedora define confianca e gate
    winning = [v for v in votes if v.direction == direction and v.weight > 0 and v.win_rate is not None]
    winning.sort(key=lambda v: (v.win_rate or 0, v.trades), reverse=True)
    top = winning[0] if winning else None
    best_bucket_strategy: str | None = None

    if top and top.win_rate is not None:
        best_bucket = (top.win_rate, top.trades)
        best_bucket_strategy = top.strategy_id

    # PLAYBOOK: consulta as vantagens comprovadas pelo treino de edge (M38).
    # Se este par+cenario esta no Playbook com edge de elite, o Doug ganha
    # respaldo extra (usa o edge comprovado como confianca). Se NAO esta em
    # lugar nenhum e o historico local tambem e fraco, reforca a abstencao —
    # o Doug so opera onde os numeros JA PROVARAM que ele acerta.
    playbook = load_playbook()
    pb_edge = playbook_edge_for(pair, scenario, playbook)
    if pb_edge:
        pb_wr = float(pb_edge.get("win_rate", 0))
        pb_trades = int(pb_edge.get("trades", 0))
        pb_strat = pb_edge.get("strategy_id", "?")
        nivel = pb_edge.get("nivel", "BOM")
        reasons.append(
            f"📘 PLAYBOOK [{nivel}]: {pb_strat} tem {pb_wr*100:.0f}% comprovado em {pb_trades} trades "
            f"neste par+cenario (treino de edge M38)."
        )
        # Usa o edge do Playbook se for mais forte/robusto que o bucket local.
        # IMPORTANTE: quando o Playbook e a fonte, o "top" local pode nao
        # existir (top=None) — sempre guardar o strategy_id junto com o
        # numero, nunca assumir que "top" corresponde ao best_bucket atual
        # (bug real 2026-07-07: crashava com AttributeError quando o unico
        # respaldo era o Playbook, sem voto local vencedor).
        if best_bucket is None or (pb_wr, pb_trades) > best_bucket:
            best_bucket = (pb_wr, pb_trades)
            best_bucket_strategy = pb_strat

    if (
        best_bucket
        and best_bucket[0] >= CONFIDENCE_THRESHOLD
        and best_bucket[1] >= MIN_SAMPLES_FOR_CONFIDENCE
    ):
        stake = _kelly_stake(best_bucket[0])
        reasons.append(
            f"GATE APROVADO: {best_bucket_strategy} tem {best_bucket[0]*100:.1f}% de acerto real "
            f"em {best_bucket[1]} trades neste exato cenario. Stake sugerido (Kelly/4): {stake}% do capital."
        )
        d = Decision(pair, scenario, "OPERAR", direction, score, best_bucket[0], stake, price, reasons, votes)
    elif best_bucket and best_bucket[0] >= WATCH_WIN_RATE and best_bucket[1] >= WATCH_MIN_SAMPLES:
        reasons.append(
            f"Vantagem detectada ({best_bucket_strategy}: {best_bucket[0]*100:.1f}% em {best_bucket[1]} trades) "
            f"mas ainda abaixo do padrao de {CONFIDENCE_THRESHOLD*100:.0f}%. "
            "Coletando mais amostra antes de liberar operacao."
        )
        d = Decision(pair, scenario, "OBSERVAR", direction, score, best_bucket[0], 0.0, price, reasons, votes)
    else:
        motivo = "Ha sinal, mas o historico real desta combinacao nao comprova vantagem."
        if not pb_edge:
            motivo += " Este par+cenario tambem NAO esta no Playbook de edges comprovados."
        reasons.append(motivo + " Abstencao e a jogada certa aqui.")
        d = Decision(pair, scenario, "FICAR_DE_FORA", "hold", score, best_bucket[0] if best_bucket else None, 0.0, price, reasons, votes)

    # Filtro anti-manipulacao por noticias (apenas pares sensiveis a noticia)
    news_snap = load_news_snapshot()
    new_level, news_reasons = apply_news_filter(d.level, d.direction, d.pair, news_snap)
    if news_reasons:
        d.reasons.extend(news_reasons)
    if new_level != d.level:
        d.level = new_level
        if new_level == "FICAR_DE_FORA":
            d.direction = "hold"
        d.stake_pct = 0.0

    _log_decision(d)
    return d


def decide_many(
    pairs: tuple[str, ...],
    *,
    candles: int = 120,
    granularity: int = 60,
) -> list[Decision]:
    backtest_stats, tick_stats = load_knowledge()
    return [
        decide_pair(
            p, candles=candles, granularity=granularity,
            backtest_stats=backtest_stats, tick_stats=tick_stats,
        )
        for p in pairs
    ]


def _log_decision(d: Decision) -> None:
    try:
        DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DECISIONS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d.to_dict(), ensure_ascii=False) + "\n")
    except OSError:
        pass
    try:
        from dashboard.data_store import append_audit_entry

        append_audit_entry(
            "doug_decision",
            {
                "pair": d.pair,
                "scenario": d.scenario,
                "level": d.level,
                "direction": d.direction,
                "confidence": d.confidence,
                "stake_pct": d.stake_pct,
            },
        )
    except Exception:
        pass
