import pytest
from doug_os.discovery.internal_market import InternalMarket


@pytest.fixture
def market():
    return InternalMarket()


def test_register_model_initial_capital(market):
    m = market.register_model("m1", "Alpha")
    assert m.symbolic_capital == pytest.approx(100.0)
    assert m.win_rate == 0.0
    assert m.score == 0.0


def test_correct_trade_increases_capital(market):
    market.register_model("m2", "Beta")
    capital = market.trade("m2", {"direction": 1}, {"direction": 1})
    assert capital > 100.0


def test_wrong_trade_decreases_capital(market):
    market.register_model("m3", "Gamma")
    capital = market.trade("m3", {"direction": 1}, {"direction": -1})
    assert capital < 100.0


def test_win_rate_calculated_correctly(market):
    market.register_model("m4", "Delta")
    market.trade("m4", {"direction": 1}, {"direction": 1})  # win
    market.trade("m4", {"direction": 1}, {"direction": 1})  # win
    market.trade("m4", {"direction": 1}, {"direction": -1})  # loss
    m = market._models["m4"]
    assert m.win_rate == pytest.approx(2 / 3)


def test_get_ranking_sorted_by_score(market):
    market.register_model("m5", "E")
    market.register_model("m6", "F")
    # give m5 a win, m6 a loss
    market.trade("m5", {"direction": 1}, {"direction": 1})
    market.trade("m6", {"direction": 1}, {"direction": -1})
    ranking = market.get_ranking()
    assert ranking[0].model_id == "m5"


def test_get_best_model_returns_leader(market):
    market.register_model("m7", "G")
    market.register_model("m8", "H")
    market.trade("m7", {"direction": 1}, {"direction": 1})
    market.trade("m8", {"direction": 1}, {"direction": -1})
    best = market.get_best_model()
    assert best.model_id == "m7"


def test_to_dict_accuracy_history_max_10(market):
    market.register_model("m9", "I")
    for _ in range(15):
        market.trade("m9", {"direction": 1}, {"direction": 1})
    d = market._models["m9"].to_dict()
    assert len(d["accuracy_history"]) <= 10
