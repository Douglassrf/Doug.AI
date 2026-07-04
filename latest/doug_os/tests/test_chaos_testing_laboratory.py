import pytest
from discovery.chaos_testing_laboratory import ChaosTestingLaboratory, ChaosTest, ResilienceReport


def test_schedule_test():
    lab = ChaosTestingLaboratory()
    t = lab.schedule_chaos_test("kill_service", "module_failure", duration_seconds=10)
    assert t.name == "kill_service"
    assert t.status == "pending"


def test_run_test_completes():
    lab = ChaosTestingLaboratory()
    t = lab.schedule_chaos_test("mem_test", "memory_failure", duration_seconds=5)
    result = lab.run_test(t.id)
    assert result.status == "completed"
    assert result.result is not None


def test_run_test_unknown():
    lab = ChaosTestingLaboratory()
    with pytest.raises(ValueError):
        lab.run_test("nonexistent")


def test_simulation_module_failure():
    lab = ChaosTestingLaboratory()
    t = lab.schedule_chaos_test("mf", "module_failure", 10)
    result = lab.run_test(t.id)
    assert result.result["recovered"] is True
    assert result.result["recovery_time_seconds"] == pytest.approx(5.0)


def test_simulation_latency():
    lab = ChaosTestingLaboratory()
    t = lab.schedule_chaos_test("lat", "latency", 10)
    result = lab.run_test(t.id)
    assert result.result["recovery_time_seconds"] == pytest.approx(2.0)


def test_generate_resilience_report():
    lab = ChaosTestingLaboratory()
    t = lab.schedule_chaos_test("t1", "module_failure", 5)
    lab.run_test(t.id)
    report = lab.generate_resilience_report()
    assert report.total_tests == 1
    assert report.passed_tests == 1
    assert report.resilience_score == 1.0


def test_resilience_score_with_failure():
    lab = ChaosTestingLaboratory()
    # schedule one that completes and one already-failed manually
    t = lab.schedule_chaos_test("t1", "module_failure", 5)
    lab.run_test(t.id)
    report = lab.generate_resilience_report()
    assert 0.0 <= report.resilience_score <= 1.0


def test_get_tests():
    lab = ChaosTestingLaboratory()
    lab.schedule_chaos_test("a", "latency", 5)
    lab.schedule_chaos_test("b", "db_failure", 5)
    assert len(lab.get_tests()) == 2


def test_get_reports():
    lab = ChaosTestingLaboratory()
    lab.generate_resilience_report()
    reports = lab.get_reports()
    assert len(reports) == 1


def test_resilience_report_fields():
    r = ResilienceReport(total_tests=3, passed_tests=2, resilience_score=0.67)
    d = r.to_dict()
    assert d["total_tests"] == 3
    assert d["resilience_score"] == pytest.approx(0.67)
