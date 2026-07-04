"""Tests for on‑chain intelligence core (Missão 28)."""

import pytest

from doug_os.onchain import (
    WhaleDetector,
    ExchangeFlowTracker,
    StablecoinTracker,
    WalletMonitor,
    OnChainEventRegistry,
)


def test_whale_detector() -> None:
    detector = WhaleDetector(threshold=100_000)
    txs = [
        {"sender": "0xA", "receiver": "0xB", "amount": 50_000},
        {"sender": "0xC", "receiver": "0xD", "amount": 150_000},
        {"sender": "0xE", "receiver": "0xF", "amount": "200000"},
        {"sender": "0xG", "receiver": "0xH", "amount": 99_999},
    ]
    whales = detector.detect(txs)
    assert len(whales) == 2
    assert whales[0].sender == "0xC" and whales[0].amount == 150_000.0
    assert whales[1].receiver == "0xF"


def test_exchange_flow_tracker() -> None:
    tracker = ExchangeFlowTracker(exchanges=["0xEx", "0xEx2"])
    txs = [
        {"sender": "0xUser1", "receiver": "0xEx", "amount": 1000, "symbol": "BTC"},
        {"sender": "0xEx", "receiver": "0xUser2", "amount": 500, "symbol": "BTC"},
        {"sender": "0xEx", "receiver": "0xEx2", "amount": 200, "symbol": "ETH"},  # ignored
    ]
    flows = tracker.track(txs)
    # net flow BTC: +1000 (deposit) -500 (withdrawal) = 500
    assert flows["BTC"] == pytest.approx(500.0)
    assert "ETH" not in flows


def test_stablecoin_tracker() -> None:
    tracker = StablecoinTracker(stablecoins=["USDT", "USDC"], exchanges=["0xEx"])
    txs = [
        {"symbol": "USDT", "sender": "0xAlice", "receiver": "0xEx", "amount": 100},  # deposit
        {"symbol": "USDT", "sender": "0xEx", "receiver": "0xBob", "amount": 50},    # withdrawal
        {"symbol": "USDC", "sender": "0xCarol", "receiver": "0xEx", "amount": 30},  # deposit
        {"symbol": "DAI", "sender": "0xDave", "receiver": "0xEx", "amount": 20},    # ignored
    ]
    flows = tracker.track_flows(txs)
    assert flows["USDT"]["deposit"] == pytest.approx(100.0)
    assert flows["USDT"]["withdrawal"] == pytest.approx(50.0)
    assert flows["USDC"]["deposit"] == pytest.approx(30.0)
    assert "USDC" in flows and flows["USDC"]["withdrawal"] == 0.0


def test_wallet_monitor() -> None:
    monitor = WalletMonitor(["0xWhale", "0xFriend"])
    txs = [
        {"sender": "0xWhale", "receiver": "0xMarket", "amount": 1000, "symbol": "ETH"},
        {"sender": "0xOther", "receiver": "0xFriend", "amount": 50, "symbol": "USDT"},
        {"sender": "0xOther", "receiver": "0xOther2", "amount": 10, "symbol": "ETH"},
    ]
    events = monitor.update(txs)
    assert len(events["0xWhale"]) == 1
    assert events["0xWhale"][0]["amount"] == 1000
    assert len(events["0xFriend"]) == 1
    assert events["0xFriend"][0]["symbol"] == "USDT"


def test_onchain_event_registry() -> None:
    registry = OnChainEventRegistry()
    registry.register_event("whale_transfer", "Whale moved 1M USDT", timestamp="2025-01-01T00:00:00Z")
    registry.register_event("exchange_flow", "Net inflow of BTC", timestamp="2025-01-02T00:00:00Z")
    events = registry.get_events()
    assert len(events) == 2
    assert events[0]["type"] == "whale_transfer"
    assert events[1]["details"].startswith("Net inflow")