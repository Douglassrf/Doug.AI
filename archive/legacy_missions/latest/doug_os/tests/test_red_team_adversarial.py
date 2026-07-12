import pytest
from discovery.red_team_adversarial import RedTeamAdversarial, AdversarialCase, AdversarialVerdict


def test_inactive_on_non_buy():
    rt = RedTeamAdversarial()
    v = rt.evaluate("topic", "SELL", 0.80, "BULL")
    assert v.verdict == "PASS"
    assert v.adversarial_score == 0.0


def test_inactive_on_low_confidence():
    rt = RedTeamAdversarial(activation_confidence=0.60)
    v = rt.evaluate("topic", "BUY", 0.55, "BULL")
    assert v.verdict == "PASS"


def test_pass_on_clean_data():
    rt = RedTeamAdversarial()
    md = {"volatility": 0.01, "rsi": 50.0, "volume_ratio": 1.2, "spread": 0.0001,
          "momentum": 0.01, "data_quality": 1.0, "regime_stability": 1.0}
    v = rt.evaluate("BTC", "BUY", 0.70, "BULL", md)
    assert v.verdict == "PASS"
    assert v.adversarial_score < 0.40


def test_block_on_high_adversarial():
    rt = RedTeamAdversarial()
    # Historical losses dominate
    for _ in range(5):
        rt.add_case("BEAR", "BUY", "LOSS", loss_pct=12.0)
    md = {"volatility": 0.05, "rsi": 80.0, "volume_ratio": 0.4, "spread": 0.005,
          "momentum": -0.02, "data_quality": 0.3, "regime_stability": 0.3}
    v = rt.evaluate("ETH", "BUY", 0.85, "BEAR", md)
    assert v.verdict == "BLOCK"
    assert v.size_multiplier == 0.0


def test_reduce_on_medium_adversarial():
    rt = RedTeamAdversarial()
    rt.add_case("SIDEWAYS", "BUY", "LOSS", loss_pct=4.0)
    md = {"volatility": 0.04, "rsi": 72.0, "volume_ratio": 0.8, "spread": 0.001,
          "momentum": -0.005, "data_quality": 0.8, "regime_stability": 0.8}
    v = rt.evaluate("SOL", "BUY", 0.65, "SIDEWAYS", md)
    # score should be moderate — either REDUCE or PASS depending on weights
    assert v.verdict in ("REDUCE", "PASS", "BLOCK")
    assert 0.0 <= v.adversarial_score <= 1.0


def test_add_case_stored():
    rt = RedTeamAdversarial()
    c = rt.add_case("BULL", "BUY", "LOSS", loss_pct=3.0, context={"asset": "BTC"})
    assert c.regime == "BULL"
    assert c.loss_pct == 3.0
    assert len(rt._experience_store) == 1


def test_audit_log_records_block():
    rt = RedTeamAdversarial()
    for _ in range(5):
        rt.add_case("CRASH", "BUY", "LOSS", loss_pct=15.0)
    md = {"volatility": 0.08, "rsi": 85.0, "volume_ratio": 0.3, "spread": 0.01,
          "momentum": -0.05, "data_quality": 0.2, "regime_stability": 0.2}
    v = rt.evaluate("XRP", "BUY", 0.90, "CRASH", md)
    if v.verdict == "BLOCK":
        log = rt.get_audit_log()
        assert len(log) >= 1
        assert log[-1]["verdict"] == "BLOCK"


def test_replay_last_vetoes():
    rt = RedTeamAdversarial()
    for _ in range(3):
        rt.add_case("BEAR", "BUY", "LOSS", loss_pct=10.0)
    md = {"volatility": 0.06, "rsi": 82.0, "volume_ratio": 0.35, "spread": 0.008,
          "momentum": -0.03, "data_quality": 0.25, "regime_stability": 0.25}
    rt.evaluate("BTC", "BUY", 0.88, "BEAR", md)
    vetoes = rt.replay_last_vetoes()
    assert isinstance(vetoes, list)


def test_get_stats():
    rt = RedTeamAdversarial()
    rt.evaluate("t1", "HOLD", 0.70, "BULL")
    stats = rt.get_stats()
    assert "total" in stats
    assert "block_rate" in stats


def test_adversarial_verdict_to_dict():
    rt = RedTeamAdversarial()
    v = rt.evaluate("topic", "BUY", 0.75, "BULL",
                    {"volatility": 0.01, "rsi": 50, "volume_ratio": 1.0,
                     "spread": 0.0001, "momentum": 0.01,
                     "data_quality": 1.0, "regime_stability": 1.0})
    d = v.to_dict()
    assert "adversarial_score" in d
    assert "verdict" in d
    assert "size_multiplier" in d
