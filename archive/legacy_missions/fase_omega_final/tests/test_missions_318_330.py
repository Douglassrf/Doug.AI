"""Testes — Missões 318-330 (Fase Ômega Final — Doug.AI v1.0)."""

import sys
from pathlib import Path

import pytest

MISSIONS_DIR = Path(__file__).resolve().parent.parent / "missions"
sys.path.insert(0, str(MISSIONS_DIR))

from mission_318 import DougOperatingSystem, DougOSModule, DougOSState
from mission_319 import UniversalEventBus, UniversalEvent
from mission_320 import UniversalTimeMachine, TimeSnapshot, ReplayExecution
from mission_321 import AIDigitalGenome, GenomeNode
from mission_322 import IntelligenceCompiler, CompilerReport, CompiledIntelligence
from mission_323 import AutonomousArchitectureOptimizer, ArchitectureSuggestion
from mission_324 import GlobalSystemOrchestrator, SystemStatusReport
from mission_325 import OmegaMemoryConsolidation, PhaseMemory, MemoryLink
from mission_326 import OmegaGovernanceCouncil, GovernanceProposal, CouncilDecision
from mission_327 import OmegaSecurityFortress, SecurityThreat, SecurityReport
from mission_328 import OmegaPerformanceMonitor, PerformanceMetric, HealthReport
from mission_329 import OmegaCertificationGate, CertificationCriteria, OmegaCertificationReport
from mission_330 import DougAILaunchCeremony, LaunchManifest, CeremonyReport


@pytest.fixture(autouse=True)
def reset_doug_os_singleton():
    DougOperatingSystem.reset_singleton()
    yield
    DougOperatingSystem.reset_singleton()


@pytest.mark.parametrize(
    "cls",
    [
        DougOSModule,
        UniversalEvent,
        TimeSnapshot,
        ReplayExecution,
        GenomeNode,
        CompiledIntelligence,
        CompilerReport,
        ArchitectureSuggestion,
        SystemStatusReport,
        PhaseMemory,
        MemoryLink,
        GovernanceProposal,
        CouncilDecision,
        SecurityThreat,
        SecurityReport,
        PerformanceMetric,
        HealthReport,
        CertificationCriteria,
        OmegaCertificationReport,
        LaunchManifest,
        CeremonyReport,
    ],
)
def test_dataclass_instantiation(cls):
    obj = cls()
    assert obj.id
    assert obj.to_dict()["id"] == obj.id


def test_mission_318_singleton():
    os_a = DougOperatingSystem()
    os_b = DougOperatingSystem()
    assert os_a is os_b


@pytest.mark.asyncio
async def test_mission_318_doug_os_lifecycle():
    class DummyModule:
        async def initialize(self):
            self.initialized = True

        async def start(self):
            self.started = True

        async def stop(self):
            self.started = False

    doug_os = DougOperatingSystem()
    core = DummyModule()
    doug_os.register_module("core", "foundation", core, start_priority=1)
    doug_os.set_config("env", "test")

    assert await doug_os.start() is True
    assert doug_os.get_state().status == "running"
    assert doug_os.get_config("env") == "test"

    dashboard = doug_os.get_dashboard()
    assert dashboard["total_modules"] == 1
    assert dashboard["active_modules"] == 1

    await doug_os.stop()
    assert doug_os.get_state().status == "stopped"


def test_mission_318_duplicate_module_raises():
    doug_os = DougOperatingSystem()
    doug_os.register_module("core", "foundation", object())
    with pytest.raises(ValueError):
        doug_os.register_module("core", "foundation", object())


@pytest.mark.asyncio
async def test_mission_319_event_bus():
    bus = UniversalEventBus()
    received = []

    def handler(event: UniversalEvent):
        received.append(event.payload["value"])

    bus.subscribe("test.event", handler)
    await bus.start(workers=2)

    event = UniversalEvent(type="test.event", source="test", payload={"value": 42})
    await bus.publish(event)

    for _ in range(50):
        if received:
            break
        await __import__("asyncio").sleep(0.05)

    await bus.stop()

    assert received == [42]
    metrics = bus.get_metrics()
    assert metrics["processed"] >= 1
    assert bus.get_event_trace(event.id) is not None


@pytest.mark.asyncio
async def test_mission_319_dead_letter_without_handler():
    bus = UniversalEventBus()
    await bus.start(workers=1)

    event = UniversalEvent(type="orphan.event", source="test")
    await bus.publish(event)
    await __import__("asyncio").sleep(0.2)
    await bus.stop()

    assert bus.get_metrics()["failed"] >= 1
    assert len(bus._dead_letters) >= 1


@pytest.mark.asyncio
async def test_mission_320_time_machine():
    tm = UniversalTimeMachine()
    snapshot = tm.create_snapshot("baseline", {"counter": 10, "mode": "live"})

    assert snapshot.hash
    assert len(snapshot.hash) == 16

    def replay_fn(state):
        state["counter"] += 5
        return {"counter": state["counter"]}

    result = await tm.replay(snapshot.id, replay_fn)
    assert result.success is True
    assert result.changes["counter"] == 15

    assert tm.rollback(snapshot.id) is True
    assert len(tm.search_snapshots("base")) == 1

    dashboard = tm.get_time_machine_dashboard()
    assert dashboard["total_snapshots"] == 1
    assert dashboard["successful_replays"] == 1


@pytest.mark.asyncio
async def test_mission_320_async_replay():
    tm = UniversalTimeMachine()
    snapshot = tm.create_snapshot("async", {"value": 1})

    async def async_fn(state):
        state["value"] *= 2
        return {"value": state["value"]}

    result = await tm.replay(snapshot.id, async_fn)
    assert result.success is True
    assert result.changes["value"] == 2


def test_mission_321_genome():
    genome = AIDigitalGenome()
    root = genome.create_genome("root", "architecture", {"version": "1.0.0"}, fitness=0.5)
    child = genome.mutate(root.id, {"feature": "alpha"})

    path = genome.get_evolution_path(child.id)
    assert path[0] == root.id
    assert path[-1] == child.id

    tree = genome.get_evolution_tree(root.id)
    assert root.id in tree

    results = genome.search_genome("alpha")
    assert len(results) >= 1

    dashboard = genome.get_genome_dashboard()
    assert dashboard["total_nodes"] == 2
    assert dashboard["avg_fitness"] > 0


def test_mission_322_intelligence_compiler():
    compiler = IntelligenceCompiler()
    compiler.register_module(
        "brain",
        {"role": "intelligence"},
        ["core"],
        ["rule_a", "rule_b"],
        {"brain": 0.8},
    )
    compiler.register_module(
        "core",
        {"role": "foundation"},
        [],
        ["rule_a"],
        {"core": 1.0},
    )

    report = compiler.compile()
    assert isinstance(compiler._reports, list)
    assert report.total_modules == 2
    assert report.redundancies == 1
    assert report.consistency_score <= 1.0

    compiled = compiler.get_latest_compiled()
    assert compiled is not None
    assert "rule_a" in compiled.rules

    dashboard = compiler.get_compiler_dashboard()
    assert dashboard["compiled_count"] == 1


def test_mission_322_circular_conflict():
    compiler = IntelligenceCompiler()
    compiler.register_module("a", {}, ["b"], [], {})
    compiler.register_module("b", {}, ["a"], [], {})

    report = compiler.compile()
    assert report.conflicts >= 1
    assert any("conflict" in rec.lower() for rec in report.recommendations)


def test_mission_323_architecture_optimizer():
    optimizer = AutonomousArchitectureOptimizer()
    optimizer.register_module("heavy", ["core"], complexity=0.9, cohesion=0.2)
    optimizer.register_module("core", [], complexity=0.3, cohesion=0.8)

    analysis = optimizer.analyze_architecture()
    assert isinstance(optimizer._suggestions, list)
    assert 0 <= analysis["technical_debt"] <= 1
    assert analysis["total_modules"] == 2
    assert len(analysis["suggestions"]) >= 1

    simulation = optimizer.simulate_refactor("heavy")
    assert simulation["success"] is True
    assert simulation["after"]["complexity"] < simulation["before"]["complexity"]

    dashboard = optimizer.get_architecture_dashboard()
    assert dashboard["total_suggestions"] >= 1


@pytest.mark.asyncio
async def test_mission_324_global_orchestrator():
    orchestrator = GlobalSystemOrchestrator()
    report = await orchestrator.boot_sequence()

    assert isinstance(report.boot_steps, list)
    assert report.boot_complete is True

    status = orchestrator.get_unified_status()
    assert "doug_os" in status["components"]
    assert "event_bus" in status["components"]

    await orchestrator.shutdown()


def test_mission_325_memory_consolidation():
    memory = OmegaMemoryConsolidation()
    m1 = memory.register_phase_memory(
        "omega_final",
        "318-330",
        {"status": "complete"},
        tags=["launch"],
    )
    m2 = memory.register_phase_memory(
        "trading_final",
        "298-307",
        {"status": "complete"},
        tags=["trading"],
    )

    link = memory.link_phases("trading_final", "omega_final", "evolution", 0.9)
    assert link.strength == 0.9

    results = memory.search("launch")
    assert m1 in results

    links = memory.get_cross_phase_links("omega_final")
    assert len(links) == 1
    assert len(memory.get_timeline()) >= 2

    dashboard = memory.get_memory_dashboard()
    assert dashboard["total_memories"] == 2


def test_mission_326_governance_council():
    council = OmegaGovernanceCouncil()
    proposal = council.submit_proposal(
        "Enable v1.0",
        "Launch Doug.AI v1.0",
        "launch",
        "douglas",
    )

    council.vote(proposal.id, "member_1", True)
    council.vote(proposal.id, "member_2", True)
    council.vote(proposal.id, "member_3", True)

    decision = council.decide(proposal.id)
    assert decision.verdict == "APPROVED"
    assert proposal.status == "approved"

    api_proposal = council.submit_proposal(
        "External API",
        "Connect paid API",
        "external_api",
        "dev",
    )
    council.vote(api_proposal.id, "member_1", True)
    council.vote(api_proposal.id, "member_2", True)
    council.vote(api_proposal.id, "member_3", True)
    api_decision = council.decide(api_proposal.id)
    assert api_decision.policy_enforced is False


def test_mission_327_security_fortress():
    fortress = OmegaSecurityFortress()
    fortress.register_user("admin_1", "admin")
    fortress.register_user("viewer_1", "viewer")

    assert fortress.check_access("admin_1", "write") is True
    assert fortress.check_access("viewer_1", "write") is False

    threat = fortress.detect_threat("injection", "critical", "external", "SQL injection attempt")
    assert fortress.mitigate_threat(threat.id) is True

    report = fortress.run_security_audit()
    assert report.verdict in {"PASS", "WARN", "FAIL"}

    dashboard = fortress.get_security_dashboard()
    assert dashboard["total_threats"] >= 1


def test_mission_328_performance_monitor():
    monitor = OmegaPerformanceMonitor()
    monitor.record_metric("doug_os", "latency_ms", 25.0, "ms")
    monitor.record_metric("doug_os", "throughput", 1000.0, "ops/s")
    monitor.record_metric("event_bus", "latency_ms", 10.0, "ms")

    report = monitor.aggregate_health()
    assert 0 <= report.overall_health <= 1
    assert report.status in {"healthy", "degraded", "critical"}
    assert "doug_os" in report.components

    dashboard = monitor.get_performance_dashboard()
    assert dashboard["total_metrics"] == 3


def test_mission_329_certification_gate():
    gate = OmegaCertificationGate()

    for category in OmegaCertificationGate.REQUIRED_CATEGORIES:
        criterion = gate.add_criterion(
            f"{category} check",
            category,
            "omega_final",
            f"Validate {category}",
        )
        gate.evaluate_criterion(criterion.id, True)

    report = gate.certify()
    assert report.verdict == "GO"
    assert report.version == "1.0.0"

    status = gate.get_certification_status()
    assert status["passed"] == len(OmegaCertificationGate.REQUIRED_CATEGORIES)


def test_mission_329_certification_no_go():
    gate = OmegaCertificationGate()
    criterion = gate.add_criterion("Security", "security", "omega", "No critical issues")
    gate.evaluate_criterion(criterion.id, False)

    report = gate.certify()
    assert report.verdict == "NO_GO"


def test_mission_330_launch_ceremony():
    ceremony = DougAILaunchCeremony()
    for mission_number in range(318, 330):
        ceremony.collect_mission_status(f"mission_{mission_number}", {"verdict": "GO"})

    manifest = ceremony.build_manifest()
    assert manifest.version == "1.0.0"
    assert manifest.all_ready is True

    report = ceremony.conduct_ceremony()
    assert report.launch_verdict == "LAUNCHED"
    assert report.version == "1.0.0"

    dashboard = ceremony.get_launch_dashboard()
    assert dashboard["all_ready"] is True
    assert dashboard["missions_collected"] == 12


def test_mission_330_launch_pending():
    ceremony = DougAILaunchCeremony()
    ceremony.collect_mission_status("mission_318", {"verdict": "GO"})

    report = ceremony.conduct_ceremony()
    assert report.launch_verdict == "PENDING"
    assert ceremony.get_launch_dashboard()["all_ready"] is False
