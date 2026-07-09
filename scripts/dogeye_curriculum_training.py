#!/usr/bin/env python3
"""DogEye curriculum training — 100 pairs rotating in batches of 10, 10 layers, 331 missions."""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from training.coach import TrainingCoach
from training.confidence_gate import CONFIDENCE_THRESHOLD, MIN_SAMPLES_FOR_CONFIDENCE, gate_decision
from training.continuous_trainer import Leaderboard, TrainingResult, run_single_training
from training.curriculum import CurriculumTeacher
from training.strategies import STRATEGIES


def _binance_price(symbol: str) -> float | None:
    try:
        from integrations.binance_apprentice import BinanceApprenticeClient

        return BinanceApprenticeClient().price(symbol)
    except Exception:
        return None


def run_binance_batch(
    pairs: tuple[str, ...],
    samples_per_pair: int,
    coach: TrainingCoach,
    lb: Leaderboard,
) -> dict:
    from training.scenarios import detect_scenario
    from training.strategies import SIGNAL_FNS, evaluate_signal

    wins = losses = skipped = 0
    op_wins = op_losses = held_low_conf = held_insufficient_data = 0
    log_path = ROOT / "data" / "training" / "binance_apprentice.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(pairs)

    for idx, pair in enumerate(pairs, 1):
        if idx % 10 == 0 or idx == total:
            print(f"  Binance [{idx}/{total}] {pair}...", flush=True)
        for _ in range(samples_per_pair):
            try:
                px = _binance_price(pair)
                if px is None:
                    skipped += 1
                    continue
                jitter = [px * (1 + random.uniform(-0.003, 0.003)) for _ in range(30)]
                jitter.append(px)
                scenario = detect_scenario(jitter)
                drill = coach.pop_next_drill()
                if drill:
                    strat = next((s for s in STRATEGIES if s.id == drill.strategy_id), random.choice(STRATEGIES))
                    use_pair = drill.pair if drill.pair in pairs else pair
                else:
                    use_pair, strat = coach.pick_training_focus(pairs, STRATEGIES)
                # Mesma correcao do lado Deriv: o sinal nao pode ver o proprio
                # tick de saida (jitter[-1]), senao decisao e avaliacao usam o
                # mesmo dado e o "acerto" vira garantido, nao previsao real.
                direction = SIGNAL_FNS[strat.id](jitter[:-1])
                won = evaluate_signal(direction, jitter[-2], jitter[-1])

                # Filtro de confianca: so conta como "operacao real" se o historico
                # ja acumulado para essa combinacao bater a meta de confianca.
                bucket_key = lb.key(strat.id, use_pair, scenario)
                gate = gate_decision(direction, bucket_key, lb.stats)
                if gate["reason"] == "insufficient_data":
                    held_insufficient_data += 1
                elif gate["reason"] == "below_confidence":
                    held_low_conf += 1
                if gate["would_operate"]:
                    if won is True:
                        op_wins += 1
                    elif won is False:
                        op_losses += 1

                row = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "exchange": "binance",
                    "symbol": use_pair,
                    "scenario": scenario,
                    "strategy": strat.id,
                    "direction": direction,
                    "won": won,
                    "would_operate": gate["would_operate"],
                    "confidence": gate["confidence"],
                    "confidence_samples": gate["samples"],
                }
                with log_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                coach.review_result(
                    strategy_id=strat.id, scenario=scenario, pair=use_pair, won=won, direction=direction
                )
                # Registra no leaderboard compartilhado (memoria de confianca), mesmo
                # quando o gate bloqueou a operacao — e assim que o historico cresce.
                lb.record(
                    TrainingResult(
                        strategy_id=strat.id,
                        pair=use_pair,
                        scenario=scenario,
                        direction=direction,
                        entry=jitter[-2],
                        exit=jitter[-1],
                        won=won,
                        mission_ref=strat.mission_ref,
                    )
                )
                if won is True:
                    wins += 1
                elif won is False:
                    losses += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1

    total = wins + losses
    op_total = op_wins + op_losses
    return {
        "exchange": "binance",
        "pairs": list(pairs),
        "samples_target": len(pairs) * samples_per_pair,
        "wins": wins,
        "losses": losses,
        "skipped": skipped,
        "win_rate": round(wins / total, 4) if total else 0.0,
        "confidence_gate": {
            "threshold": CONFIDENCE_THRESHOLD,
            "min_samples": MIN_SAMPLES_FOR_CONFIDENCE,
            "would_operate_trades": op_total,
            "operate_wins": op_wins,
            "operate_losses": op_losses,
            "operate_win_rate": round(op_wins / op_total, 4) if op_total else None,
            "held_below_confidence": held_low_conf,
            "held_insufficient_data": held_insufficient_data,
        },
    }


def run_deriv_batch(
    pairs: tuple[str, ...],
    samples_per_pair: int,
    coach: TrainingCoach,
    lb: Leaderboard,
) -> dict:
    wins = losses = skipped = 0
    op_wins = op_losses = held_low_conf = held_insufficient_data = 0
    total = len(pairs)
    for idx, pair in enumerate(pairs, 1):
        if idx % 10 == 0 or idx == total:
            print(f"  Deriv [{idx}/{total}] {pair}...", flush=True)
        for _ in range(samples_per_pair):
            drill = coach.pop_next_drill()
            if drill or coach.remedial_mode:
                pair, strat = coach.pick_training_focus(pairs, STRATEGIES)
            else:
                strat = random.choice(STRATEGIES)
            result = run_single_training(pair, strat)
            if result is None:
                skipped += 1
                continue

            # Filtro de confianca: so conta como "operacao real" se o historico
            # ja acumulado para essa combinacao bater a meta de confianca (>=90%,
            # com amostra minima). Caso contrario, seria "hold" na pratica.
            bucket_key = lb.key(result.strategy_id, result.pair, result.scenario)
            gate = gate_decision(result.direction, bucket_key, lb.stats)
            if gate["reason"] == "insufficient_data":
                held_insufficient_data += 1
            elif gate["reason"] == "below_confidence":
                held_low_conf += 1
            if gate["would_operate"]:
                if result.won is True:
                    op_wins += 1
                elif result.won is False:
                    op_losses += 1

            coach.review_result(
                strategy_id=result.strategy_id,
                scenario=result.scenario,
                pair=result.pair,
                won=result.won,
                direction=result.direction,
            )
            lb.record(result)
            if result.won is True:
                wins += 1
            elif result.won is False:
                losses += 1
            else:
                skipped += 1
    lb.save()
    total = wins + losses
    op_total = op_wins + op_losses
    return {
        "exchange": "deriv",
        "pairs": list(pairs),
        "samples_target": len(pairs) * samples_per_pair,
        "wins": wins,
        "losses": losses,
        "skipped": skipped,
        "win_rate": round(wins / total, 4) if total else 0.0,
        "confidence_gate": {
            "threshold": CONFIDENCE_THRESHOLD,
            "min_samples": MIN_SAMPLES_FOR_CONFIDENCE,
            "would_operate_trades": op_total,
            "operate_wins": op_wins,
            "operate_losses": op_losses,
            "operate_win_rate": round(op_wins / op_total, 4) if op_total else None,
            "held_below_confidence": held_low_conf,
            "held_insufficient_data": held_insufficient_data,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DogEye curriculum session")
    parser.add_argument("--samples-per-pair", type=int, default=5, help="Runs per pair (default 5)")
    parser.add_argument("--batch-mode", action="store_true", help="Legacy: only 10 pairs per session")
    parser.add_argument("--plan-only", action="store_true", help="Show session plan without training")
    parser.add_argument("--no-advance", action="store_true", help="Do not rotate after session")
    args = parser.parse_args()

    all_pairs = not args.batch_mode
    teacher = CurriculumTeacher()
    plan = teacher.session_plan(samples_per_pair=args.samples_per_pair, all_pairs=all_pairs)

    if args.plan_only:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    print("=== REVISAO (memoria de erros) ===", flush=True)
    print(json.dumps(plan["review"], indent=2, ensure_ascii=False), flush=True)
    print(f"\n=== LOTE Deriv {plan['deriv_pair_count']} pares ===", flush=True)
    print(f"=== LOTE Binance {plan['binance_pair_count']} pares ===", flush=True)
    print(f"=== CAMADA {plan['layer']} | missoes: {plan['layer_missions_today']} ===\n", flush=True)

    coach = TrainingCoach()
    lb = Leaderboard.load()

    deriv_result = run_deriv_batch(
        tuple(plan["deriv_batch"]),
        args.samples_per_pair,
        coach,
        lb,
    )
    binance_result = run_binance_batch(
        tuple(plan["binance_batch"]),
        args.samples_per_pair,
        coach,
        lb,
    )
    lb.save()

    coach.review_cycle(
        (deriv_result["win_rate"] + binance_result["win_rate"]) / 2,
        lb.stats,
    )

    deriv_gate = deriv_result["confidence_gate"]
    binance_gate = binance_result["confidence_gate"]
    gate_total_ops = deriv_gate["would_operate_trades"] + binance_gate["would_operate_trades"]
    gate_total_wins = deriv_gate["operate_wins"] + binance_gate["operate_wins"]
    print(
        f"\n=== FILTRO DE CONFIANCA (so opera com >={CONFIDENCE_THRESHOLD*100:.0f}% "
        f"de historico real, amostra minima {MIN_SAMPLES_FOR_CONFIDENCE}) ===",
        flush=True,
    )
    print(
        f"Operacoes que passariam no filtro hoje: {gate_total_ops} "
        f"(vitorias: {gate_total_wins}, "
        f"win rate real dessas operacoes: "
        f"{round(gate_total_wins / gate_total_ops * 100, 1) if gate_total_ops else 'sem dado'}%)",
        flush=True,
    )
    print(
        f"Sinais barrados por confianca insuficiente: "
        f"{deriv_gate['held_below_confidence'] + binance_gate['held_below_confidence']} | "
        f"barrados por falta de amostra (<{MIN_SAMPLES_FOR_CONFIDENCE} trades no historico): "
        f"{deriv_gate['held_insufficient_data'] + binance_gate['held_insufficient_data']}",
        flush=True,
    )

    if not args.no_advance:
        teacher.advance_after_session(
            all_pairs=all_pairs,
            unresolved_drills=len(coach.pending_drills),
        )

    report = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "plan": plan,
        "deriv": deriv_result,
        "binance": binance_result,
        "coach_remedial": coach.remedial_mode,
        "next_state": teacher.state.to_dict(),
    }

    reports_dir = ROOT / "data" / "training" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    out = reports_dir / f"curriculum_{stamp}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nRelatorio: {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
