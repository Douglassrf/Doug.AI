"""Testes — Missões 298-307 (Fase Final — Final Trading Operating System)."""

import asyncio
import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_298 import ArchitectureConsolidator, ArchitectureModule, ArchitectureReport
from mission_299 import FullSystemIntegrationTest, IntegrationTest
from mission_300 import DougAICertificationGate, CertificationCriteria, CertificationReport
from mission_301 import PaperTradingLaunch, PaperTrade, PaperTradingReport
from mission_302 import LiveShadowMode, ShadowSignal, ShadowReport
from mission_303 import SmallCapitalReadinessGate, ReadinessCriteria, ReadinessReport
from mission_304 import HumanSupervisedMicroLiveTest, MicroLiveTrade, MicroLiveTestReport
from mission_305 import ControlledCapitalScaling, ScalingTier, ScalingDecision, ScalingReport
from mission_306 import FullAutonomousOperationsGate, OperationalCriterion, AutonomousOperationsReport
from mission_307 import DougAILaunchCeremony, LaunchManifest, CeremonyReport


@pytest.mark.parametrize(
    "cls",
    [
        ArchitectureModule,
        ArchitectureReport,
        IntegrationTest,
        CertificationCriteria,
        CertificationReport,
        PaperTrade,
        PaperTradingReport,
        ShadowSignal,
        ShadowReport,
        ReadinessCriteria,
        ReadinessReport,
        MicroLiveTrade,
        MicroLiveTestReport,
        ScalingTier,
        ScalingDecision,
        ScalingReport,
        OperationalCriterion,
        AutonomousOperationsReport,
        LaunchManifest,
        CeremonyReport,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_298_architecture_consolidator():
    consolidator = ArchitectureConsolidator()
    foundation = ArchitectureModule(name="core", layer="foundation")
    intelligence = ArchitectureModule(
        name="brain",
        layer="intelligence",
        dependencies=[foundation.id],
    )
    risk = ArchitectureModule(name="risk", layer="risk", dependencies=[intelligence.id])
    orphan = ArchitectureModule(name="orphan", layer="intelligence")

    consolidator.register_module(foundation)
    consolidator.register_module(intelligence)
    consolidator.register_module(risk)
    consolidator.register_module(orphan)

    report = consolidator.consolidate()
    assert report.total_modules == 4
    assert report.layers["foundation"] == 1
    assert report.layers["intelligence"] == 2
    assert len(report.flows) == 3
    assert any(risk_item["type"] == "orphan_module" for risk_item in report.risks)
    assert consolidator.get_architecture_report().total_modules == 4


def test_mission_298_circular_dependency_risk():
    consolidator = ArchitectureConsolidator()
    mod_a = ArchitectureModule(name="a", layer="foundation", dependencies=[])
    mod_b = ArchitectureModule(name="b", layer="intelligence", dependencies=[mod_a.id])
    mod_a.dependencies = [mod_b.id]

    consolidator.register_module(mod_a)
    consolidator.register_module(mod_b)

    report = consolidator.consolidate()
    circular = [risk for risk in report.risks if risk["type"] == "circular_dependency"]
    assert len(circular) == 1


def test_mission_299_full_system_integration():
    async def _run_tests():
        tester = FullSystemIntegrationTest()
        e2e = await tester.run_e2e_test("pipeline")
        load = await tester.run_load_test("stress", concurrent=20)
        failure = await tester.run_failure_test("recovery")
        return tester, e2e, load, failure

    tester, e2e, load, failure = asyncio.run(_run_tests())

    assert e2e.status == "passed"
    assert load.status == "passed"
    assert failure.status == "passed"

    report = tester.get_compatibility_report()
    assert report["total_tests"] == 3
    assert report["passed"] == 3
    assert report["pass_rate"] == 1.0


def test_mission_300_certification_gate():
    gate = DougAICertificationGate()
    c1 = gate.add_criterion("Architecture", "architecture", "All modules mapped")
    c2 = gate.add_criterion("Security", "security", "No critical issues")

    gate.evaluate_criterion(c1.id, True)
    gate.evaluate_criterion(c2.id, True)

    report = gate.certify()
    assert report.verdict == "GO"
    assert report.version == "1.0.0"
    assert gate.get_certification_status()["passed"] == 2


def test_mission_300_certification_no_go():
    gate = DougAICertificationGate()
    criterion = gate.add_criterion("Testing", "testing", "Coverage >= 80%")
    gate.evaluate_criterion(criterion.id, False)

    report = gate.certify()
    assert report.verdict == "NO_GO"


def test_mission_301_paper_trading_launch():
    launcher = PaperTradingLaunch()
    trade = launcher.execute_trade(
        {"id": "d1", "asset": "EURUSD", "direction": "buy", "quantity": 2.0},
        1.1000,
    )
    assert trade.status == "open"
    assert isinstance(launcher._trades, list)

    closed = launcher.close_trade(trade.id, 1.1050)
    assert closed is not None
    assert closed.profit_loss == pytest.approx(0.01)

    report = launcher.generate_daily_report()
    assert report.total_trades == 1
    assert report.win_rate == 1.0

    dashboard = launcher.get_paper_trading_dashboard()
    assert dashboard["closed_trades"] == 1
    assert dashboard["current_value"] > launcher._capital


def test_mission_302_live_shadow_mode():
    shadow = LiveShadowMode()
    decision = {"asset": "BTCUSD", "direction": "buy", "confidence": 0.8}

    for price in [50000 + i * 10 for i in range(12)]:
        shadow.generate_signal(decision, float(price))

    divergence = shadow.calculate_divergence("BTCUSD")
    assert divergence >= 0.0

    divergence_repeat = shadow.calculate_divergence("BTCUSD")
    assert divergence == divergence_repeat

    report = shadow.generate_shadow_report()
    assert report.total_signals == 12
    assert isinstance(shadow._signals, list)

    dashboard = shadow.get_shadow_dashboard()
    assert dashboard["total_signals"] == 12


def test_mission_303_readiness_gate():
    gate = SmallCapitalReadinessGate()
    win_rate = gate.add_criterion("Win Rate", "win_rate", 0.55)
    drawdown = gate.add_criterion("Max Drawdown", "drawdown", 0.10)

    gate.evaluate_criterion(win_rate.id, 0.60)
    gate.evaluate_criterion(drawdown.id, 0.08)

    report = gate.evaluate_readiness()
    assert report.verdict == "READY"
    assert report.human_review_required is True

    status = gate.get_readiness_status()
    assert status["met"] == 2


def test_mission_303_drawdown_not_met():
    gate = SmallCapitalReadinessGate()
    drawdown = gate.add_criterion("Max Drawdown", "drawdown", 0.10)
    gate.evaluate_criterion(drawdown.id, 0.15)

    report = gate.evaluate_readiness()
    assert report.verdict == "NOT_READY"


def test_mission_304_micro_live_test():
    micro = HumanSupervisedMicroLiveTest(max_capital_per_trade=100.0)
    trade = micro.request_trade(
        {"asset": "EURUSD", "direction": "buy", "quantity": 1.0, "capital_usd": 150.0},
        1.1000,
        "supervisor_01",
    )
    assert trade.capital_usd == 100.0
    assert trade.status == "pending_approval"

    assert micro.approve_trade(trade.id, "supervisor_01") is True
    executed = micro.execute_trade(trade.id, 1.1000)
    assert executed is not None
    assert executed.status == "open"

    closed = micro.close_trade(trade.id, 1.1020)
    assert closed is not None
    assert closed.profit_loss == pytest.approx(0.0020)

    report = micro.generate_report()
    assert report.closed_trades == 1
    assert report.verdict == "PASS"

    dashboard = micro.get_micro_live_dashboard()
    assert dashboard["max_capital_per_trade"] == 100.0


def test_mission_304_kill_switch():
    micro = HumanSupervisedMicroLiveTest()
    micro.activate_kill_switch("manual halt")

    trade = micro.request_trade({"asset": "EURUSD", "direction": "buy"}, 1.10, "sup1")
    assert trade.status == "blocked"
    assert micro.approve_trade(trade.id, "sup1") is False

    assert micro.deactivate_kill_switch("sup1") is True
    report = micro.generate_report()
    assert report.kill_switch_active is False or report.verdict == "PENDING"


def test_mission_305_controlled_capital_scaling():
    scaler = ControlledCapitalScaling()
    decision = scaler.evaluate_performance({"win_rate": 0.55, "sharpe": 0.9, "drawdown": 0.05})
    assert decision.proposed_tier == "small"

    assert scaler.approve_scaling(decision.id, "approver_01") is True
    assert scaler.get_scaling_dashboard()["current_tier"] == "small"

    rollback = scaler.rollback("drawdown spike")
    assert rollback.rollback_triggered is True

    report = scaler.generate_scaling_report()
    assert report.current_tier == "micro"


def test_mission_305_drawdown_triggers_rollback():
    scaler = ControlledCapitalScaling()
    scaler.evaluate_performance({"win_rate": 0.60, "sharpe": 1.2, "drawdown": 0.05})
    scaler.approve_scaling(scaler._decisions[-1].id, "approver")

    decision = scaler.evaluate_performance({"win_rate": 0.60, "sharpe": 1.2, "drawdown": 0.20})
    assert decision.rollback_triggered is True


def test_mission_306_autonomous_operations_gate():
    gate = FullAutonomousOperationsGate()
    for gate_name in FullAutonomousOperationsGate.REQUIRED_GATES:
        gate.register_gate_status(gate_name, True)

    criterion = gate.add_criterion("Uptime", "reliability", "99.9% uptime")
    gate.evaluate_criterion(criterion.id, True)

    report = gate.evaluate_autonomous_readiness()
    assert report.verdict == "GO"
    assert gate.get_operations_status()["gates_passed"] == 5


def test_mission_306_missing_gate_blocks_go():
    gate = FullAutonomousOperationsGate()
    gate.register_gate_status("certification", True)
    gate.register_gate_status("readiness", True)

    report = gate.evaluate_autonomous_readiness()
    assert report.verdict == "NO_GO"


def test_mission_307_launch_ceremony():
    ceremony = DougAILaunchCeremony()
    for mission_number in range(298, 307):
        ceremony.collect_mission_status(f"mission_{mission_number}", {"verdict": "GO"})

    manifest = ceremony.build_manifest()
    assert manifest.version == "1.0.0"
    assert manifest.all_ready is True

    report = ceremony.conduct_ceremony()
    assert report.launch_verdict == "LAUNCHED"
    assert report.version == "1.0.0"

    dashboard = ceremony.get_launch_dashboard()
    assert dashboard["all_ready"] is True
    assert dashboard["missions_collected"] == 9


def test_mission_307_launch_pending():
    ceremony = DougAILaunchCeremony()
    ceremony.collect_mission_status("mission_298", {"verdict": "GO"})

    report = ceremony.conduct_ceremony()
    assert report.launch_verdict == "PENDING"
    assert ceremony.get_launch_dashboard()["all_ready"] is False
