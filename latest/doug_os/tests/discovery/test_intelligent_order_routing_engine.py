import pytest
from doug_os.discovery.intelligent_order_routing_engine import (
    IntelligentOrderRoutingEngine, OrderRoute, RoutingDecision,
)


@pytest.fixture
def engine():
    e = IntelligentOrderRoutingEngine()
    e.add_exchange_metrics("binance", liquidity=0.9, cost=0.1, reliability=0.95, avg_fill_time=0.5)
    e.add_exchange_metrics("kraken",  liquidity=0.7, cost=0.2, reliability=0.85, avg_fill_time=1.0)
    e.add_exchange_metrics("coinbase", liquidity=0.8, cost=0.15, reliability=0.90, avg_fill_time=0.8)
    return e


def test_add_exchange_metrics_stores(engine):
    assert "binance" in engine._exchange_metrics
    assert engine._exchange_metrics["binance"]["liquidity"] == 0.9


def test_generate_routes_empty_engine():
    e = IntelligentOrderRoutingEngine()
    routes = e.generate_routes(100.0, "market", "BTC/USDT")
    assert routes == []


def test_generate_routes_count(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    assert len(routes) == 3


def test_generate_routes_sorted_by_score(engine):
    routes = engine.generate_routes(100.0, "limit", "ETH/USDT")
    scores = [r.route_score for r in routes]
    assert scores == sorted(scores, reverse=True)


def test_priority_1_is_best(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    assert routes[0].priority == 1


def test_select_route_no_routes():
    e = IntelligentOrderRoutingEngine()
    decision = e.select_route("ord_001", [])
    assert decision.reasoning == "No routes available"
    assert decision.confidence == 0.0


def test_select_route_balanced(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    decision = engine.select_route("ord_001", routes, preference="balanced")
    assert decision.selected_route.exchange in ("binance", "kraken", "coinbase")
    assert 0.0 <= decision.confidence <= 1.0


def test_select_route_reliable_prefers_high_reliability(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    decision = engine.select_route("ord_002", routes, preference="reliable")
    assert decision.selected_route.exchange == "binance"


def test_select_route_alternatives(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    decision = engine.select_route("ord_003", routes)
    assert len(decision.alternatives) <= 3


def test_get_route_metrics(engine):
    m = engine.get_route_metrics("kraken")
    assert m is not None
    assert m["reliability"] == 0.85


def test_get_route_metrics_missing():
    e = IntelligentOrderRoutingEngine()
    assert e.get_route_metrics("unknown") is None


def test_get_routing_summary_no_data():
    e = IntelligentOrderRoutingEngine()
    assert e.get_routing_summary() == {"status": "no_data"}


def test_get_routing_summary_after_decisions(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    engine.select_route("ord_001", routes)
    engine.select_route("ord_002", routes)
    summary = engine.get_routing_summary()
    assert summary["total_decisions"] == 2
    assert summary["top_exchange"] is not None
    assert 0.0 <= summary["avg_confidence"] <= 1.0


def test_to_dict_serializes_all_fields(engine):
    routes = engine.generate_routes(100.0, "market", "BTC/USDT")
    decision = engine.select_route("ord_x", routes)
    d = decision.to_dict()
    assert all(k in d for k in ("id", "order_id", "selected_route", "alternatives",
                                 "confidence", "reasoning", "created_at"))
