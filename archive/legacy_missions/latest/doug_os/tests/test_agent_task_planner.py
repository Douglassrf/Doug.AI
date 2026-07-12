import pytest
from discovery.agent_task_planner import AgentTaskPlanner, AgentPlan, PlanStep


def test_create_plan():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("Optimize Portfolio", priority=8)
    assert plan.goal == "Optimize Portfolio"
    assert plan.priority == 8
    assert plan.status == "created"


def test_add_step():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("Goal")
    step = planner.add_step(plan.id, "Fetch Data", "market_analysis")
    assert step.name == "Fetch Data"
    assert step.capability == "market_analysis"
    assert len(plan.steps) == 1


def test_add_step_unknown_plan():
    planner = AgentTaskPlanner()
    with pytest.raises(ValueError):
        planner.add_step("bad_id", "step", "cap")


def test_get_ready_steps_no_deps():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s1 = planner.add_step(plan.id, "S1", "cap")
    s2 = planner.add_step(plan.id, "S2", "cap")
    ready = planner.get_ready_steps(plan.id)
    assert len(ready) == 2


def test_dependency_blocks_step():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s1 = planner.add_step(plan.id, "S1", "cap")
    s2 = planner.add_step(plan.id, "S2", "cap", depends_on=[s1.id])
    ready = planner.get_ready_steps(plan.id)
    assert s2 not in ready
    assert s1 in ready


def test_complete_step_unlocks_dependent():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s1 = planner.add_step(plan.id, "S1", "cap")
    s2 = planner.add_step(plan.id, "S2", "cap", depends_on=[s1.id])
    planner.complete_step(plan.id, s1.id, {"result": "ok"})
    ready = planner.get_ready_steps(plan.id)
    assert s2 in ready


def test_plan_completed_when_all_steps_done():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s = planner.add_step(plan.id, "S", "cap")
    planner.complete_step(plan.id, s.id, {})
    assert plan.status == "completed"


def test_fail_step_fails_plan():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s = planner.add_step(plan.id, "S", "cap")
    planner.fail_step(plan.id, s.id, "timeout")
    assert plan.status == "failed"


def test_get_plan_progress():
    planner = AgentTaskPlanner()
    plan = planner.create_plan("G")
    s1 = planner.add_step(plan.id, "S1", "cap")
    s2 = planner.add_step(plan.id, "S2", "cap")
    planner.complete_step(plan.id, s1.id, {})
    prog = planner.get_plan_progress(plan.id)
    assert prog["total_steps"] == 2
    assert prog["completed_steps"] == 1
    assert prog["progress_pct"] == pytest.approx(50.0)
