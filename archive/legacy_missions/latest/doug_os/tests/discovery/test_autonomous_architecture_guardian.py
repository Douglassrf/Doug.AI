import pytest
from doug_os.discovery.autonomous_architecture_guardian import (
    AutonomousArchitectureGuardian,
    ArchitectureViolation,
    ArchitectureReport,
)


class FatModule:
    """Module with >20 public methods to trigger solid_s violation."""
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
    def m9(self): pass
    def m10(self): pass
    def m11(self): pass
    def m12(self): pass
    def m13(self): pass
    def m14(self): pass
    def m15(self): pass
    def m16(self): pass
    def m17(self): pass
    def m18(self): pass
    def m19(self): pass
    def m20(self): pass
    def m21(self): pass


def make_guardian():
    return AutonomousArchitectureGuardian()


def test_register_module_adds_to_modules_and_graph():
    g = make_guardian()
    obj = object()
    g.register_module("mod_a", obj)
    assert "mod_a" in g._modules
    assert g._modules["mod_a"] is obj
    assert "mod_a" in g._dependency_graph
    assert g._dependency_graph["mod_a"] == set()


def test_scan_zero_modules_returns_zero_total():
    g = make_guardian()
    report = g.scan()
    assert report.total_modules == 0
    assert report.violations == []


def test_scan_detects_clean_arch_violation_presentation_domain():
    g = make_guardian()
    g.register_module("presentation_domain_module", object())
    report = g.scan()
    types = [v.violation_type for v in report.violations]
    assert "clean_arch" in types
    assert report.high_violations >= 1


def test_scan_detects_solid_s_violation_for_fat_module():
    g = make_guardian()
    g.register_module("fat_module", FatModule())
    report = g.scan()
    types = [v.violation_type for v in report.violations]
    assert "solid_s" in types


def test_detect_circular_dependencies_ab_ba():
    g = make_guardian()
    g.register_module("A", object())
    g.register_module("B", object())
    # manually inject cycle A->B->A
    g._dependency_graph["A"].add("B")
    g._dependency_graph["B"].add("A")
    cycles = g._detect_circular_dependencies()
    assert len(cycles) > 0
    # each cycle contains both A and B
    all_nodes = set()
    for c in cycles:
        all_nodes.update(c)
    assert "A" in all_nodes
    assert "B" in all_nodes


def test_fix_violation_valid_id_returns_true_and_sets_fixed():
    g = make_guardian()
    g.register_module("presentation_domain_module", object())
    report = g.scan()
    assert len(report.violations) > 0
    vid = report.violations[0].id
    result = g.fix_violation(vid)
    assert result is True
    assert report.violations[0].fixed is True


def test_fix_violation_invalid_id_returns_false():
    g = make_guardian()
    g.register_module("presentation_domain_module", object())
    g.scan()
    result = g.fix_violation("nonexistent_id")
    assert result is False


def test_architecture_violation_to_dict_has_all_fields():
    v = ArchitectureViolation(
        module="test_mod", violation_type="circular",
        description="desc", severity="critical",
        recommendation="rec",
    )
    d = v.to_dict()
    for key in ("id", "module", "violation_type", "description", "severity",
                 "recommendation", "detected_at", "fixed"):
        assert key in d
    assert d["module"] == "test_mod"
    assert d["fixed"] is False


def test_overall_score_between_0_and_1():
    g = make_guardian()
    g.register_module("fat_module", FatModule())
    g.register_module("presentation_domain_module", object())
    report = g.scan()
    assert 0.0 <= report.overall_score <= 1.0


def test_architecture_report_to_dict_has_all_fields():
    g = make_guardian()
    report = g.scan()
    d = report.to_dict()
    for key in ("total_modules", "violations", "critical_violations", "high_violations",
                 "medium_violations", "low_violations", "soli_score", "clean_arch_score",
                 "overall_score", "created_at"):
        assert key in d
