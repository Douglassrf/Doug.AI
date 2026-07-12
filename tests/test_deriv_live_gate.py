"""Testes do fail-safe do DerivLiveGate — abort hard-coded independente de flags.
Todos offline, sem tocar a rede."""
import pytest

from integrations import money_guard as mg
from integrations.deriv_demo import (
    DerivLiveGate,
    RealAccountDetectedAbort,
    assert_demo_account,
)


def _no_kill(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "sem_kill")


# ── DerivLiveGate: stub hard-coded, nenhuma flag consegue liberar live ──────
def test_gate_bloqueia_mesmo_com_todas_as_flags_live(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    monkeypatch.setenv("DOUG_MODE", "live")
    monkeypatch.setenv("DERIV_LIVE_ENABLED", "true")
    status = DerivLiveGate().check()
    assert status.allowed is False
    assert "não certificados" in status.reason


def test_gate_bloqueia_em_demo(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    monkeypatch.delenv("DOUG_MODE", raising=False)
    monkeypatch.delenv("DERIV_LIVE_ENABLED", raising=False)
    assert DerivLiveGate().check().allowed is False


def test_gate_libera_so_se_certificado_e_flags_e_sem_kill(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    monkeypatch.setenv("DOUG_MODE", "live")
    monkeypatch.setenv("DERIV_LIVE_ENABLED", "true")
    monkeypatch.setattr(DerivLiveGate, "MISSION_GATES_CERTIFIED", True)
    assert DerivLiveGate().check().allowed is True


def test_gate_bloqueia_com_kill_switch_mesmo_certificado(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "KILL")
    mg.trip("emergencia")
    monkeypatch.setenv("DOUG_MODE", "live")
    monkeypatch.setenv("DERIV_LIVE_ENABLED", "true")
    monkeypatch.setattr(DerivLiveGate, "MISSION_GATES_CERTIFIED", True)
    status = DerivLiveGate().check()
    assert status.allowed is False
    assert "KILL SWITCH" in status.reason


# ── assert_demo_account: abort fatal + kill switch, independente de flags ──
def test_conta_real_aborta_e_aciona_kill_switch(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    with pytest.raises(RealAccountDetectedAbort):
        assert_demo_account({"loginid": "CR900000", "is_virtual": False})
    assert mg.is_killed() is True
    assert "CR900000" in mg.kill_reason()


def test_conta_real_aborta_mesmo_com_flags_dizendo_live(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    monkeypatch.setenv("DOUG_MODE", "live")
    monkeypatch.setenv("DERIV_LIVE_ENABLED", "true")
    with pytest.raises(RealAccountDetectedAbort):
        assert_demo_account({"loginid": "CR900001", "is_virtual": False})


def test_conta_demo_nao_aborta(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    assert_demo_account({"loginid": "VRT900002", "is_virtual": True})  # não levanta
    assert mg.is_killed() is False
