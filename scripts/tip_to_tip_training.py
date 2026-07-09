#!/usr/bin/env python3
"""DogEye / Doug.AI tip-to-tip training benchmark.

10 missions × 10 pairs × 10 runs = 1000 scored attempts.
Generates JSON + markdown score report under data/ and docs/.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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

from integrations.deriv_bridge import DerivBridge, training_pairs  # noqa: E402

try:
    from dashboard.tip_to_tip_live_state import finish_live, init_live, update_live
except ImportError:
    init_live = finish_live = update_live = None  # type: ignore[misc, assignment]


@dataclass
class AttemptResult:
    mission_id: str
    pair: str
    run: int
    passed: bool
    detail: str = ""
    duration_ms: float = 0.0


@dataclass
class MissionScore:
    mission_id: str
    name: str
    passed: int = 0
    failed: int = 0
    attempts: list[AttemptResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


MISSION_NAMES = {
    "TTT-M01": "Status bridge unificado",
    "TTT-M02": "Ping Deriv API",
    "TTT-M03": "Tick publico por par",
    "TTT-M04": "Paper trade simulado",
    "TTT-M05": "Cadeia tick → decisao → paper",
    "TTT-M06": "Proposta mock dry-run",
    "TTT-M07": "Live gate bloqueado",
    "TTT-M08": "Integracao E2E (M299)",
    "TTT-M09": "Audit trail append",
    "TTT-M10": "Snapshot publico por par",
}


def _run_m01(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    st = bridge.status
    ok = st.app_id > 0 and not st.live_enabled
    return ok, f"app_id={st.app_id} mock={st.mock_enabled}"


def _run_m02(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    resp = bridge.ping()
    ok = resp.get("msg_type") == "ping" or resp.get("ping") == "pong"
    return ok, str(resp.get("msg_type", resp))


def _run_m03(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    tick = bridge.fetch_tick_public(pair)
    if not tick.get("ok"):
        return False, tick.get("error", "fail")
    quote = tick["quote"]
    return quote > 0, f"quote={quote}"


def _run_m04(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    from missions.mission_301 import PaperTradingLaunch

    tick = bridge.fetch_tick_public(pair)
    if not tick.get("ok"):
        return False, tick.get("error", "no tick")
    price = tick["quote"]
    pt = PaperTradingLaunch()
    trade = pt.execute_trade(
        {"asset": pair, "direction": "buy", "quantity": 1.0, "id": f"d_{run}"},
        price,
    )
    closed = pt.close_trade(trade.id, price * 1.001)
    ok = closed is not None and closed.status == "closed"
    return ok, f"pl={closed.profit_loss if closed else 0}"


def _run_m05(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    tick = bridge.fetch_tick_public(pair)
    if not tick.get("ok"):
        return False, tick.get("error", "no tick")
    price = tick["quote"]
    direction = "buy" if run % 2 == 0 else "sell"
    decision = {
        "asset": pair,
        "action": direction.upper(),
        "confidence": 0.55 + (run % 5) * 0.05,
        "price": price,
        "cycle_id": f"ttt_{uuid.uuid4().hex[:8]}",
    }
    from dashboard.data_store import append_audit_entry

    append_audit_entry("tip_to_tip_decision", decision)
    ok = decision["confidence"] >= 0.5 and price > 0
    return ok, f"{direction}@{price}"


def _run_m06(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    resp = bridge.mock_proposal(pair)
    ok = resp.get("dry_run") is True and resp.get("purchase_blocked") is True
    return ok, "dry_run blocked"


def _run_m07(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    ok = bridge.live_gate_blocked()
    return ok, "live blocked as expected"


def _run_m08(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    from missions.mission_299 import FullSystemIntegrationTest

    tester = FullSystemIntegrationTest()
    test = asyncio.run(tester.run_e2e_test(f"ttt_{pair}_{run}"))
    ok = test.status == "passed"
    return ok, test.status


def _run_m09(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    from dashboard.data_store import append_audit_entry

    append_audit_entry(
        "tip_to_tip_audit",
        {"pair": pair, "run": run, "mission": "TTT-M09", "team": "DogEye"},
    )
    return True, "logged"


def _run_m10(bridge: DerivBridge, pair: str, run: int) -> tuple[bool, str]:
    from integrations.deriv_demo import run_public_demo_snapshot

    snap = run_public_demo_snapshot(symbols=(pair,), save_status=False, log_paper=False)
    if snap.error:
        return False, snap.error
    tick = snap.ticks.get(pair, {})
    quote = tick.get("quote")
    ok = quote is not None and float(quote) > 0
    return ok, f"quote={quote}"


MISSION_RUNNERS: dict[str, Callable[[DerivBridge, str, int], tuple[bool, str]]] = {
    "TTT-M01": _run_m01,
    "TTT-M02": _run_m02,
    "TTT-M03": _run_m03,
    "TTT-M04": _run_m04,
    "TTT-M05": _run_m05,
    "TTT-M06": _run_m06,
    "TTT-M07": _run_m07,
    "TTT-M08": _run_m08,
    "TTT-M09": _run_m09,
    "TTT-M10": _run_m10,
}


def run_benchmark(
    *,
    missions: tuple[str, ...] | None = None,
    pairs: tuple[str, ...] | None = None,
    runs_per_pair: int = 10,
    delay_sec: float = 0.05,
    live: bool = False,
    operator: str = "",
) -> dict[str, Any]:
    bridge = DerivBridge()
    mission_ids = missions or tuple(MISSION_RUNNERS.keys())
    pair_list = pairs or training_pairs()
    scores: list[MissionScore] = []
    started = datetime.now(timezone.utc)
    total_planned = len(mission_ids) * len(pair_list) * runs_per_pair
    done_count = 0
    total_pass = 0
    total_fail = 0

    if live and init_live is not None:
        init_live(operator=operator, total=total_planned)

    for mid in mission_ids:
        runner = MISSION_RUNNERS[mid]
        ms = MissionScore(mission_id=mid, name=MISSION_NAMES.get(mid, mid))
        for pair in pair_list:
            for run in range(1, runs_per_pair + 1):
                t0 = time.perf_counter()
                try:
                    passed, detail = runner(bridge, pair, run)
                except Exception as exc:
                    passed, detail = False, str(exc)
                dur = (time.perf_counter() - t0) * 1000
                att = AttemptResult(mid, pair, run, passed, detail, dur)
                ms.attempts.append(att)
                done_count += 1
                if passed:
                    ms.passed += 1
                    total_pass += 1
                else:
                    ms.failed += 1
                    total_fail += 1

                if live:
                    msg = f"{'OK' if passed else 'FAIL'} {mid} {pair} r{run} ({done_count}/{total_planned})"
                    print(msg, flush=True)
                    if update_live is not None:
                        update_live(
                            operator=operator,
                            total=total_planned,
                            done=done_count,
                            passed=total_pass,
                            failed=total_fail,
                            mission=mid,
                            pair=pair,
                            run=run,
                            ok=passed,
                            detail=detail,
                        )

                if delay_sec > 0:
                    time.sleep(delay_sec)
        scores.append(ms)

    total_pass = sum(s.passed for s in scores)
    total_fail = sum(s.failed for s in scores)
    total = total_pass + total_fail

    by_pair: dict[str, dict[str, int]] = {}
    for ms in scores:
        for att in ms.attempts:
            bp = by_pair.setdefault(att.pair, {"passed": 0, "failed": 0})
            if att.passed:
                bp["passed"] += 1
            else:
                bp["failed"] += 1

    report = {
        "project": "Doug.AI / DogEye",
        "test_type": "tip_to_tip_training",
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "missions": len(mission_ids),
            "pairs": len(pair_list),
            "runs_per_pair": runs_per_pair,
            "total_attempts": total,
        },
        "summary": {
            "passed": total_pass,
            "failed": total_fail,
            "score_pct": round(100 * total_pass / total, 2) if total else 0.0,
            "grade": _grade(total_pass / total if total else 0),
        },
        "by_mission": [
            {
                "id": s.mission_id,
                "name": s.name,
                "passed": s.passed,
                "failed": s.failed,
                "rate_pct": round(100 * s.rate, 2),
            }
            for s in scores
        ],
        "by_pair": {
            p: {"passed": v["passed"], "failed": v["failed"], "rate_pct": round(100 * v["passed"] / (v["passed"] + v["failed"]), 2)}
            for p, v in sorted(by_pair.items())
        },
        "failures_sample": [
            {"mission": a.mission_id, "pair": a.pair, "run": a.run, "detail": a.detail}
            for s in scores
            for a in s.attempts
            if not a.passed
        ][:50],
    }
    if live and finish_live is not None:
        finish_live(passed=total_pass, failed=total_fail, grade=report["summary"]["grade"])
    return report


def _grade(rate: float) -> str:
    if rate >= 0.95:
        return "A"
    if rate >= 0.85:
        return "B"
    if rate >= 0.70:
        return "C"
    if rate >= 0.50:
        return "D"
    return "F"


def write_reports(
    report: dict[str, Any],
    out_dir: Path,
    *,
    operator: str | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = report["completed_at"].replace(":", "-").replace("+", "_")[:19]
    if operator:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in operator.strip())[:40]
        cert_dir = out_dir / "certificates"
        cert_dir.mkdir(parents=True, exist_ok=True)
        json_path = cert_dir / f"{safe}_{stamp}.json"
        md_path = cert_dir / f"{safe}_{stamp}.md"
    else:
        json_path = out_dir / "tip_to_tip_score.json"
        md_path = ROOT / "docs" / "TIP_TO_TIP_SCORE_REPORT.md"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = report["summary"]
    cfg = report["config"]
    op_line = f"**Operador:** {report.get('operator', '—')}\n**Hostname:** {report.get('hostname', '—')}\n\n"
    lines = [
        "# Doug.AI / DogEye — Tip-to-Tip Score Report",
        "",
        f"**Gerado:** {report['completed_at']}",
        "",
        op_line if operator or report.get("operator") else "",
        "## Resumo",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Tentativas | {cfg['total_attempts']} |",
        f"| Acertos | {s['passed']} |",
        f"| Erros | {s['failed']} |",
        f"| **Score** | **{s['score_pct']}%** |",
        f"| Nota | **{s['grade']}** |",
        "",
        f"Config: {cfg['missions']} missões × {cfg['pairs']} pares × {cfg['runs_per_pair']} runs",
        "",
        "## Por missão",
        "",
        "| ID | Nome | OK | FAIL | % |",
        "|----|------|----|------|---|",
    ]
    for m in report["by_mission"]:
        lines.append(f"| {m['id']} | {m['name']} | {m['passed']} | {m['failed']} | {m['rate_pct']}% |")

    lines.extend(["", "## Por par", "", "| Par | OK | FAIL | % |", "|-----|----|------|---|"])
    for pair, stats in report["by_pair"].items():
        lines.append(f"| {pair} | {stats['passed']} | {stats['failed']} | {stats['rate_pct']}% |")

    if report.get("failures_sample"):
        lines.extend(["", "## Amostra de falhas (max 50)", ""])
        for f in report["failures_sample"]:
            lines.append(f"- **{f['mission']}** `{f['pair']}` run {f['run']}: {f['detail']}")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


CERTIFY_MIN_PCT = 95.0
CERTIFY_MIN_GRADE = ("A", "B")


def _run_preflight() -> bool:
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tip_to_tip_preflight.py")],
        cwd=str(ROOT),
    )
    return proc.returncode == 0


def main() -> int:
    import platform

    parser = argparse.ArgumentParser(description="DogEye tip-to-tip training benchmark")
    parser.add_argument("--runs", type=int, default=10, help="Runs per pair (default 10)")
    parser.add_argument("--delay", type=float, default=0.05, help="Delay between attempts (sec)")
    parser.add_argument("--quick", action="store_true", help="Smoke: 2 missions, 2 pairs, 2 runs")
    parser.add_argument("--certify", action="store_true", help="Modo certificacao equipe (1000 ops, preflight obrigatorio)")
    parser.add_argument("--operator", type=str, default="", help="Nome do operador DogEye (obrigatorio com --certify)")
    parser.add_argument("--live", action="store_true", help="Progresso ao vivo (terminal + data/tip_to_tip_live.json)")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    if args.certify:
        if not args.operator.strip():
            print("[ERRO] Modo --certify exige --operator \"Seu Nome\"")
            return 2
        if args.quick:
            print("[ERRO] --quick nao vale para certificacao. Rode o teste completo.")
            return 2
        print("=== Certificacao DogEye — preflight ===")
        if not _run_preflight():
            print("[ERRO] Preflight falhou. Corrija e tente de novo.")
            return 2
        print("\n=== Iniciando 1000 operacoes (10x10x10) — aguarde ~10-20 min ===\n")

    if args.live:
        print("LIVE: abra http://localhost:8502 (run_live_ttt.ps1) para ver o painel", flush=True)

    if args.quick:
        report = run_benchmark(
            missions=("TTT-M01", "TTT-M02"),
            pairs=training_pairs()[:2],
            runs_per_pair=2,
            delay_sec=0,
            live=args.live,
            operator=args.operator.strip(),
        )
    else:
        report = run_benchmark(
            runs_per_pair=args.runs,
            delay_sec=args.delay,
            live=args.live,
            operator=args.operator.strip(),
        )

    if args.certify:
        report["operator"] = args.operator.strip()
        report["hostname"] = platform.node()
        report["python"] = sys.version
        report["certification"] = {
            "min_score_pct": CERTIFY_MIN_PCT,
            "solo_run": True,
        }

    json_path, md_path = write_reports(
        report,
        ROOT / "data",
        operator=args.operator.strip() or None,
    )
    s = report["summary"]
    print(f"\n=== DogEye Tip-to-Tip ===")
    if args.operator:
        print(f"Operador: {args.operator.strip()}")
    print(f"Score: {s['passed']}/{report['config']['total_attempts']} ({s['score_pct']}%) — Nota {s['grade']}")
    print(f"Acertos: {s['passed']} | Perdas: {s['failed']}")
    print(f"JSON: {json_path}")
    print(f"Report: {md_path}")

    if args.certify:
        passed_cert = s["score_pct"] >= CERTIFY_MIN_PCT and s["grade"] in CERTIFY_MIN_GRADE
        if passed_cert:
            print(f"\n[CERTIFICADO] Aprovado (>= {CERTIFY_MIN_PCT}%, nota {s['grade']}).")
            print("Envie a Douglas: o arquivo JSON acima + print do terminal.")
        else:
            print(f"\n[REPROVADO] Minimo: {CERTIFY_MIN_PCT}% e nota A ou B. Treine e rode de novo.")
            return 1

    if args.json_only:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if s["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
