"""Tests for Stablecoin Flow Intelligence Engine (Missão 30)."""

from doug_os.onchain import StablecoinFlowEngine


def test_stablecoin_flow_engine_net_flows_and_pressure() -> None:
    engine = StablecoinFlowEngine(stablecoins=["USDT", "USDC"], exchanges=["0xEx"], pressure_threshold=0.6)
    # Round 1: more deposits than withdrawals for USDT; equal flows for USDC
    txs = [
        {"symbol": "USDT", "sender": "0xAlice", "receiver": "0xEx", "amount": 100},  # deposit
        {"symbol": "USDT", "sender": "0xBob", "receiver": "0xEx", "amount": 50},   # deposit
        {"symbol": "USDT", "sender": "0xEx", "receiver": "0xCharlie", "amount": 30},  # withdrawal
        {"symbol": "USDC", "sender": "0xDave", "receiver": "0xEx", "amount": 20},  # deposit
        {"symbol": "USDC", "sender": "0xEx", "receiver": "0xEve", "amount": 20},    # withdrawal
    ]
    engine.process_transactions(txs)
    flows = engine.net_flows()
    assert flows["USDT"] == 100 + 50 - 30
    assert flows["USDC"] == 0
    pressure = engine.pressure()
    # USDT deposit ratio = 150/ (150+30) = 0.8333 > 0.6 → buy pressure
    assert pressure["USDT"] == "buy"
    # USDC deposit ratio = 20/40 = 0.5, within neutral zone (0.4–0.6)
    assert pressure["USDC"] == "neutral"

    # Round 2: heavy withdrawals for USDC create sell pressure
    txs2 = [
        {"symbol": "USDC", "sender": "0xEx", "receiver": "0xFrank", "amount": 100},  # withdrawal
        {"symbol": "USDC", "sender": "0xGeorge", "receiver": "0xEx", "amount": 10},  # deposit
    ]
    engine.process_transactions(txs2)
    pressure2 = engine.pressure()
    # USDC deposit ratio = (20+10) / (20+20+100+10) = 30/150 = 0.2 <= 0.4 → sell
    assert pressure2["USDC"] == "sell"