import pytest
from discovery.disaster_recovery_engine import DisasterRecoveryEngine, Backup, RecoveryPlan, RecoveryResult


def test_create_backup():
    dr = DisasterRecoveryEngine()
    b = dr.create_backup("snap1", {"key": "value"})
    assert b.name == "snap1"
    assert len(b.checksum) == 16


def test_backup_has_sha256_checksum():
    dr = DisasterRecoveryEngine()
    b = dr.create_backup("b", {"a": 1})
    assert b.checksum != ""


def test_validate_backup_success():
    dr = DisasterRecoveryEngine()
    b = dr.create_backup("b", {"x": 42})
    assert dr.validate_backup(b.id) is True


def test_validate_backup_unknown():
    dr = DisasterRecoveryEngine()
    assert dr.validate_backup("nonexistent") is False


def test_list_backups():
    dr = DisasterRecoveryEngine()
    dr.create_backup("b1", {})
    dr.create_backup("b2", {})
    backups = dr.list_backups()
    assert len(backups) == 2


def test_create_recovery_plan():
    dr = DisasterRecoveryEngine()
    plan = dr.create_recovery_plan("restore", "Full restore", [], rpo_minutes=60, rto_minutes=30)
    assert plan.name == "restore"
    assert plan.rpo_minutes == 60
    assert plan.rto_minutes == 30


def test_execute_recovery_no_plan():
    dr = DisasterRecoveryEngine()
    result = dr.execute_recovery("invalid_plan_id")
    assert result.success is False


def test_execute_recovery_success():
    dr = DisasterRecoveryEngine()
    plan = dr.create_recovery_plan("plan", "desc", [{"type": "validate", "name": "check"}])
    result = dr.execute_recovery(plan.id)
    assert result.success is True


def test_execute_recovery_with_backup():
    dr = DisasterRecoveryEngine()
    b = dr.create_backup("backup", {"state": "ok"})
    plan = dr.create_recovery_plan("plan", "desc", [{"type": "restore", "name": "restore_state"}])
    result = dr.execute_recovery(plan.id, backup_id=b.id)
    assert result.success is True


def test_get_dr_report():
    dr = DisasterRecoveryEngine()
    report = dr.get_dr_report()
    assert "total_recoveries" in report
    assert report["backups_available"] == 0
