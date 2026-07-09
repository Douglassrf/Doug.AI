"""Continuous paper-training engine — pairs × strategies × scenarios."""
from __future__ import annotations

import json
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard.data_store import append_audit_entry
from training.coach import TrainingCoach
from training.market_data import fetch_tick_history_sync
from training.scenarios import Scenario, detect_scenario
from training.strategies import STRATEGIES, SIGNAL_FNS, StrategySpec, evaluate_signal

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
TRAINING_DIR = DATA / "training"
SESSIONS_PATH = TRAINING_DIR / "sessions.jsonl"
LEADERBOARD_PATH = TRAINING_DIR / "leaderboard.json"
STATE_PATH = TRAINING_DIR / "continuous_state.json"

from training.pair_universe import DERIV_PAIRS_100 as ALL_PAIRS


@dataclass
class TrainingResult:
    strategy_id: str
    pair: str
    scenario: Scenario
    direction: str
    entry: float
    exit: float
    won: bool | None
    mission_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": f"tr_{uuid.uuid4().hex[:12]}",
            "ts": datetime.now(timezone.utc).isoformat(),
            "strategy_id": self.strategy_id,
            "pair": self.pair,
            "scenario": self.scenario,
            "direction": self.direction,
            "entry": self.entry,
            "exit": self.exit,
            "won": self.won,
            "mission_ref": self.mission_ref,
        }


@dataclass
class Leaderboard:
    stats: dict[str, dict[str, Any]] = field(default_factory=dict)

    def key(self, strategy_id: str, pair: str, scenario: str) -> str:
        return f"{strategy_id}|{pair}|{scenario}"

    def record(self, result: TrainingResult) -> None:
        if result.won is None:
            return
        k = self.key(result.strategy_id, result.pair, result.scenario)
        bucket = self.stats.setdefault(
            k,
            {
                "strategy_id": result.strategy_id,
                "pair": result.pair,
                "scenario": result.scenario,
                "wins": 0,
                "losses": 0,
                "trades": 0,
                "win_rate": 0.0,
            },
        )
        bucket["trades"] += 1
        if result.won:
            bucket["wins"] += 1
        else:
            bucket["losses"] += 1
        bucket["win_rate"] = round(bucket["wins"] / bucket["trades"], 4)

    def best_for_scenario(self, scenario: str, top_n: int = 5) -> list[dict[str, Any]]:
        rows = [v for v in self.stats.values() if v["scenario"] == scenario and v["trades"] >= 3]
        rows.sort(key=lambda r: (r["win_rate"], r["trades"]), reverse=True)
        return rows[:top_n]

    def save(self) -> None:
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        LEADERBOARD_PATH.write_text(
            json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "stats": self.stats}, indent=2)
            + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> "Leaderboard":
        lb = cls()
        if LEADERBOARD_PATH.exists():
            try:
                data = json.loads(LEADERBOARD_PATH.read_text(encoding="utf-8"))
                lb.stats = data.get("stats", {})
            except (json.JSONDecodeError, OSError):
                pass
        return lb


def run_single_training(
    pair: str,
    strategy: StrategySpec,
    *,
    tick_count: int = 40,
) -> TrainingResult | None:
    fn = SIGNAL_FNS.get(strategy.id)
    if not fn:
        return None

    market = fetch_tick_history_sync(pair, tick_count)
    if not market.get("ok"):
        return None

    prices = market["prices"]
    if len(prices) < 5:
        return None

    # IMPORTANTE: o sinal so pode ver dados ate o momento da entrada (prices[:-1]).
    # Ele NUNCA pode enxergar o proprio tick de saida (prices[-1]) — se visse, a
    # decisao e a avaliacao usariam o mesmo dado e o resultado seria adivinhacao
    # garantida, nao previsao real (bug encontrado em 2026-07-06: S05 tinha 100%
    # de acerto porque comparava exatamente os mesmos dois precos usados aqui).
    history = prices[:-1]
    scenario = detect_scenario(history)
    direction = fn(history)
    entry = prices[-2]
    exit_price = prices[-1]
    won = evaluate_signal(direction, entry, exit_price)

    return TrainingResult(
        strategy_id=strategy.id,
        pair=pair,
        scenario=scenario,
        direction=direction,
        entry=entry,
        exit=exit_price,
        won=won,
        mission_ref=strategy.mission_ref,
    )


def run_training_cycle(
    *,
    pairs: tuple[str, ...] | None = None,
    strategies: tuple[StrategySpec, ...] | None = None,
    samples_per_cycle: int = 20,
    leaderboard: Leaderboard | None = None,
    coach: TrainingCoach | None = None,
    use_coach: bool = True,
) -> dict[str, Any]:
    lb = leaderboard or Leaderboard.load()
    coach = coach or TrainingCoach()
    pair_list = pairs or ALL_PAIRS
    strat_list = strategies or STRATEGIES
    results: list[TrainingResult] = []
    wins = losses = skipped = 0
    cycle_lessons: list[str] = []

    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    weak = coach.weak_buckets_from_leaderboard(lb.stats) if use_coach else []

    for _ in range(samples_per_cycle):
        if use_coach:
            pair, strategy = coach.pick_training_focus(pair_list, strat_list, weak_buckets=weak)
        else:
            pair = random.choice(pair_list)
            strategy = random.choice(strat_list)

        result = run_single_training(pair, strategy)
        if result is None:
            skipped += 1
            continue
        results.append(result)
        row = result.to_dict()
        with SESSIONS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        if use_coach:
            lesson = coach.review_result(
                strategy_id=result.strategy_id,
                scenario=result.scenario,
                pair=result.pair,
                won=result.won,
                direction=result.direction,
            )
            if lesson:
                cycle_lessons.append(lesson.message)

        if result.won is True:
            wins += 1
        elif result.won is False:
            losses += 1
        else:
            skipped += 1
        lb.record(result)

    lb.save()

    cycle_wr = round(wins / (wins + losses), 4) if (wins + losses) else 0.0
    coach_lessons = coach.review_cycle(cycle_wr, lb.stats) if use_coach else []
    for les in coach_lessons:
        cycle_lessons.append(les.message)

    summary = {
        "cycle_at": datetime.now(timezone.utc).isoformat(),
        "samples": len(results),
        "wins": wins,
        "losses": losses,
        "skipped": skipped,
        "win_rate": cycle_wr,
        "coach_remedial_mode": coach.remedial_mode if use_coach else False,
        "coach_lessons": cycle_lessons[-8:],
        "best_trending_up": lb.best_for_scenario("trending_up", 3),
        "best_ranging": lb.best_for_scenario("ranging", 3),
        "best_high_volatility": lb.best_for_scenario("high_volatility", 3),
    }

    append_audit_entry(
        "continuous_training_cycle",
        {
            "wins": wins,
            "losses": losses,
            "win_rate": summary["win_rate"],
            "samples": len(results),
            "coach_remedial": summary["coach_remedial_mode"],
        },
    )

    STATE_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def run_continuous(
    *,
    interval_sec: int = 90,
    samples_per_cycle: int = 25,
    max_cycles: int | None = None,
    pairs: tuple[str, ...] | None = None,
) -> None:
    cycles = 0
    active_pairs = pairs or ALL_PAIRS
    print(f"DogEye treino continuo — intervalo {interval_sec}s, {samples_per_cycle} simulacoes/ciclo")
    print(f"Pares: {len(active_pairs)} | Estrategias: {len(STRATEGIES)} | Ctrl+C para parar\n")

    lb = Leaderboard.load()
    coach = TrainingCoach()

    while True:
        cycles += 1
        t0 = time.perf_counter()
        try:
            summary = run_training_cycle(
                pairs=active_pairs,
                samples_per_cycle=samples_per_cycle,
                leaderboard=lb,
                coach=coach,
            )
        except Exception as exc:
            print(f"[CICLO {cycles}] ERRO: {exc}")
            time.sleep(interval_sec)
            continue

        elapsed = time.perf_counter() - t0
        remedial = " [CORRECAO]" if summary.get("coach_remedial_mode") else ""
        print(
            f"[CICLO {cycles}]{remedial} {summary['samples']} sims | "
            f"W:{summary['wins']} L:{summary['losses']} | "
            f"WR:{summary['win_rate']*100:.1f}% | {elapsed:.1f}s",
            flush=True,
        )
        for msg in summary.get("coach_lessons", [])[:3]:
            print(f"  PROFESSOR: {msg[:120]}", flush=True)

        if max_cycles and cycles >= max_cycles:
            break
        time.sleep(max(0, interval_sec - elapsed))
