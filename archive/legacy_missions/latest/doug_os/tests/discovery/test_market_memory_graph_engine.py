import pytest
from datetime import datetime, timezone, timedelta
from doug_os.discovery.market_memory_graph_engine import (
    MarketMemoryGraphEngine, GraphNode, GraphEdge, GraphQueryResult,
)


@pytest.fixture
def engine():
    return MarketMemoryGraphEngine()


def test_add_node_stored(engine):
    n = GraphNode(type="market_event", label="crash", description="BTC crash")
    engine.add_node(n)
    assert n.id in engine._nodes


def test_add_edge_invalid_source_raises(engine):
    n = GraphNode(type="decision", label="buy")
    engine.add_node(n)
    e = GraphEdge(source="nonexistent", target=n.id, relationship="causes")
    with pytest.raises(ValueError):
        engine.add_edge(e)


def test_add_market_event(engine):
    n = engine.add_market_event("flash_crash", "market dropped 20%", {"asset": "BTC"}, importance=0.9)
    assert n.type == "market_event"
    assert n.importance == 0.9


def test_add_decision(engine):
    n = engine.add_decision("buy_signal", {"signal": "RSI oversold"}, confidence=0.8)
    assert n.type == "decision"
    assert n.confidence == 0.8


def test_add_causal_relationship(engine):
    cause = engine.add_market_event("high_vol", "volatility spike", {})
    effect = engine.add_market_event("panic_sell", "sell off", {})
    edge = engine.add_causal_relationship(cause.id, effect.id, "volatility caused sell-off")
    assert edge.relationship == "causes"
    assert edge.source == cause.id


def test_query_events_by_type(engine):
    engine.add_market_event("pump", "price pump", {})
    engine.add_decision("hold", {})
    events = engine.query_events_by_type("market_event")
    assert len(events) == 1
    assert events[0].label == "pump"


def test_query_path_no_path(engine):
    n1 = engine.add_market_event("A", "event A", {})
    n2 = engine.add_market_event("B", "event B", {})
    result = engine.query_path(n1.id, n2.id)
    assert result.paths == []
    assert result.confidence == 0.0


def test_query_path_found(engine):
    n1 = engine.add_market_event("A", "event A", {})
    n2 = engine.add_market_event("B", "event B", {})
    engine.add_causal_relationship(n1.id, n2.id)
    result = engine.query_path(n1.id, n2.id)
    assert len(result.paths) > 0
    assert result.confidence == 0.5


def test_search_similar_events(engine):
    engine.add_market_event("btc_pump", "Bitcoin price pump", {"asset": "BTC"})
    engine.add_market_event("eth_dump", "Ethereum dump", {"asset": "ETH"})
    results = engine.search_similar_events("bitcoin")
    assert len(results) >= 1
    assert results[0].label == "btc_pump"


def test_get_historical_context(engine):
    now = datetime.now(timezone.utc)
    n = GraphNode(type="market_event", label="old_event",
                  timestamp=now - timedelta(days=3))
    engine.add_node(n)
    ctx = engine.get_historical_context(now, window_days=7)
    assert len(ctx.nodes) >= 1


def test_get_graph_statistics(engine):
    engine.add_market_event("event1", "desc", {})
    stats = engine.get_graph_statistics()
    assert stats["total_nodes"] == 1
    assert stats["total_edges"] == 0
    assert "market_event" in stats["node_types"]


def test_to_dict_serializes(engine):
    n = engine.add_market_event("event", "desc", {"key": "val"})
    d = n.to_dict()
    assert all(k in d for k in ("id", "type", "label", "description", "timestamp"))
