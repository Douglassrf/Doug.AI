import pytest
from discovery.agent_communication_bus import AgentCommunicationBus, BusMessage


def test_subscribe_and_publish():
    bus = AgentCommunicationBus()
    received = []
    bus.subscribe("trade_signal", lambda m: received.append(m))
    msg = bus.publish("market_agent", "trade_signal", {"symbol": "BTC", "action": "buy"})
    assert len(received) == 1
    assert received[0].payload["symbol"] == "BTC"


def test_message_delivered_status():
    bus = AgentCommunicationBus()
    bus.subscribe("event", lambda m: None)
    msg = bus.publish("sender", "event", {})
    assert msg.status == "delivered"


def test_no_subscribers_broadcast():
    bus = AgentCommunicationBus()
    msg = bus.publish("sender", "orphan_event", {})
    assert msg.status in ("delivered", "sent")


def test_direct_message_no_handler_fails():
    bus = AgentCommunicationBus()
    msg = bus.publish("sender", "private_event", {}, recipient="agent1")
    assert msg.status == "failed"


def test_multiple_subscribers():
    bus = AgentCommunicationBus()
    counts = [0, 0]
    bus.subscribe("sig", lambda m: counts.__setitem__(0, counts[0] + 1))
    bus.subscribe("sig", lambda m: counts.__setitem__(1, counts[1] + 1))
    bus.publish("sender", "sig", {})
    assert counts[0] == 1
    assert counts[1] == 1


def test_dead_letter_on_handler_failure():
    bus = AgentCommunicationBus()
    def bad_handler(m):
        raise RuntimeError("fail")
    bus.subscribe("bad", bad_handler)
    msg = bus.publish("s", "bad", {})
    assert msg.status == "failed"
    assert len(bus.get_dead_letters()) > 0


def test_get_messages():
    bus = AgentCommunicationBus()
    bus.publish("s", "e", {"n": 1})
    bus.publish("s", "e", {"n": 2})
    msgs = bus.get_messages()
    assert len(msgs) == 2


def test_bus_metrics():
    bus = AgentCommunicationBus()
    bus.subscribe("x", lambda m: None)
    bus.publish("s", "x", {})
    m = bus.get_bus_metrics()
    assert m["total_messages"] == 1
    assert m["delivered_messages"] == 1


def test_message_to_dict():
    msg = BusMessage(sender="s", type="t", payload={"k": 1})
    d = msg.to_dict()
    assert d["sender"] == "s"
    assert d["type"] == "t"
