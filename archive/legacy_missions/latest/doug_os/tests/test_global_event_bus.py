import pytest
from discovery.global_event_bus import GlobalEventBus, Event


def test_subscribe_and_process():
    bus = GlobalEventBus()
    received = []
    bus.subscribe("trade", lambda e: received.append(e))
    event = Event(type="trade", source="engine", payload={"symbol": "BTC"})
    bus.publish(event)
    bus.process_pending()
    assert len(received) == 1
    assert received[0].payload["symbol"] == "BTC"


def test_publish_creates_event():
    bus = GlobalEventBus()
    event = Event(type="signal", source="detector", payload={})
    bus.publish(event)
    assert event.id in bus._persistence


def test_no_subscribers_event_stored():
    bus = GlobalEventBus()
    event = Event(type="orphan", source="test")
    bus.publish(event)
    assert len(bus._events) == 1


def test_multiple_subscribers():
    bus = GlobalEventBus()
    counts = [0, 0]
    bus.subscribe("x", lambda e: counts.__setitem__(0, counts[0] + 1))
    bus.subscribe("x", lambda e: counts.__setitem__(1, counts[1] + 1))
    bus.publish(Event(type="x", source="s"))
    bus.process_pending()
    assert counts[0] == 1
    assert counts[1] == 1


def test_replay_events():
    bus = GlobalEventBus()
    bus.subscribe("t", lambda e: None)
    e1 = Event(type="t", source="s", payload={"n": 1})
    e2 = Event(type="t", source="s", payload={"n": 2})
    bus.publish(e1)
    bus.publish(e2)
    bus.process_pending()
    replayed = bus.replay_events("t")
    assert len(replayed) == 2


def test_priority_ordering():
    bus = GlobalEventBus()
    order = []
    bus.subscribe("p", lambda e: order.append(e.priority))
    bus.publish(Event(type="p", source="s", priority=1))
    bus.publish(Event(type="p", source="s", priority=9))
    bus.process_pending()
    # high priority (9) should be processed first since lower number = (10 - priority) = 1 in queue
    assert order[0] == 9


def test_get_metrics():
    bus = GlobalEventBus()
    bus.publish(Event(type="m", source="s"))
    metrics = bus.get_metrics()
    assert "total_events" in metrics
    assert metrics["total_events"] >= 1


def test_event_to_dict():
    e = Event(type="t", source="s", payload={"k": "v"})
    d = e.to_dict()
    assert d["type"] == "t"
    assert d["source"] == "s"
