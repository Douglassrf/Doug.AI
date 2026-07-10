"""Testes do Money Guard — as travas preventivas de dinheiro real do Doug.AI.
Todos offline, sem tocar a rede."""
import pytest

from integrations import money_guard as mg
from integrations.binance_apprentice import (
    BinanceApprenticeClient,
    BinanceLiveBlocked,
    BinanceSettings,
)


def _no_kill(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "sem_kill")


# ── Kill switch ─────────────────────────────────────────────────────────────
def test_kill_trip_reset(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "KILL")
    assert mg.is_killed() is False
    mg.trip("anomalia teste")
    assert mg.is_killed() is True
    assert "anomalia teste" in mg.kill_reason()
    mg.reset()
    assert mg.is_killed() is False


# ── Teto absoluto ───────────────────────────────────────────────────────────
def test_teto_padrao_e_env(monkeypatch):
    monkeypatch.delenv("DOUG_MAX_ORDEM_USD", raising=False)
    assert mg.max_ordem_usd() == mg.DEFAULT_MAX_ORDEM_USD
    monkeypatch.setenv("DOUG_MAX_ORDEM_USD", "25")
    assert mg.max_ordem_usd() == 25.0


# ── Trava anti-saque ────────────────────────────────────────────────────────
def test_anti_saque_bloqueia():
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_no_withdrawal({"canWithdraw": True})


def test_anti_saque_permite_trade_only():
    mg.assert_no_withdrawal({"canWithdraw": False})  # não levanta


# ── Portão de mainnet ───────────────────────────────────────────────────────
def test_mainnet_bloqueada_sem_live(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_mainnet_allowed(live_enabled=False)


def test_mainnet_bloqueada_com_kill(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "KILL")
    mg.trip("parada")
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_mainnet_allowed(live_enabled=True)  # kill vence o live


def test_mainnet_liberada_com_live_e_sem_kill(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    mg.assert_mainnet_allowed(live_enabled=True)  # não levanta


# ── Chokepoint de ordem real ────────────────────────────────────────────────
def test_testnet_sempre_liberado(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    mg.assert_safe_to_trade(usd_amount=99999, is_testnet=True, live_enabled=False)  # fake money, ok


def test_real_sem_live_bloqueia(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_safe_to_trade(usd_amount=5, is_testnet=False, live_enabled=False)


def test_real_acima_do_teto_bloqueia(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    monkeypatch.delenv("DOUG_MAX_ORDEM_USD", raising=False)
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_safe_to_trade(usd_amount=1000, is_testnet=False, live_enabled=True,
                                account_info={"canWithdraw": False})


def test_real_com_chave_de_saque_bloqueia(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    with pytest.raises(mg.MoneyGuardError):
        mg.assert_safe_to_trade(usd_amount=5, is_testnet=False, live_enabled=True,
                                account_info={"canWithdraw": True})


def test_real_trade_only_dentro_do_teto_ok(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    mg.assert_safe_to_trade(usd_amount=5, is_testnet=False, live_enabled=True,
                            account_info={"canWithdraw": False})  # não levanta


# ── Integração: cliente Binance respeita o cofre em mainnet ─────────────────
def test_binance_mainnet_assinado_bloqueado_sem_live(monkeypatch, tmp_path):
    _no_kill(monkeypatch, tmp_path)
    cfg = BinanceSettings(api_key="k", api_secret="s", use_testnet=False,
                          live_enabled=False, mock_enabled=False)
    client = BinanceApprenticeClient(cfg)
    with pytest.raises(BinanceLiveBlocked):
        client.account_info()  # chamada assinada em mainnet -> bloqueada pelo cofre


def test_binance_mainnet_assinado_bloqueado_com_kill(monkeypatch, tmp_path):
    monkeypatch.setattr(mg, "KILL_FILE", tmp_path / "KILL")
    mg.trip("emergencia")
    cfg = BinanceSettings(api_key="k", api_secret="s", use_testnet=False,
                          live_enabled=True, mock_enabled=False)
    client = BinanceApprenticeClient(cfg)
    with pytest.raises(BinanceLiveBlocked):
        client.account_info()
