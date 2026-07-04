import pytest
from discovery.multi_doug_collaboration_network import MultiDougCollaborationNetwork, DougNode, CollaborationEvent


def test_register_node():
    net = MultiDougCollaborationNetwork()
    node = net.register_node("DOUG-1", "1.0.0")
    assert node.name == "DOUG-1"
    assert node.trust_score == 0.5


def test_update_trust_positive():
    net = MultiDougCollaborationNetwork()
    node = net.register_node("DOUG-1")
    net.update_trust(node.id, 0.2)
    assert net._nodes[node.id].trust_score == pytest.approx(0.7)


def test_update_trust_clamped():
    net = MultiDougCollaborationNetwork()
    node = net.register_node("DOUG-1")
    net.update_trust(node.id, 1.0)
    assert net._nodes[node.id].trust_score == pytest.approx(1.0)


def test_share_discovery_trusted():
    net = MultiDougCollaborationNetwork(trust_threshold=0.4)
    n1 = net.register_node("D1")
    n2 = net.register_node("D2")
    n2.trust_score = 0.8
    events = net.share_discovery(n1.id, {"symbol": "BTC", "direction": "buy"})
    assert len(events) > 0


def test_share_discovery_untrusted_skipped():
    net = MultiDougCollaborationNetwork(trust_threshold=0.9)
    n1 = net.register_node("D1")
    n2 = net.register_node("D2")  # default trust 0.5 < 0.9
    events = net.share_discovery(n1.id, {"direction": "buy"})
    assert len(events) == 0


def test_conflict_detection():
    net = MultiDougCollaborationNetwork(trust_threshold=0.0)
    n1 = net.register_node("D1")
    n2 = net.register_node("D2")
    n2.shared_discoveries.append({"direction": "sell"})
    events = net.share_discovery(n1.id, {"direction": "buy"})
    conflict_events = [e for e in events if e.conflict]
    assert len(conflict_events) > 0


def test_share_risk():
    net = MultiDougCollaborationNetwork(trust_threshold=0.0)
    n1 = net.register_node("D1")
    net.register_node("D2")
    events = net.share_risk(n1.id, {"risk_type": "drawdown", "level": "high"})
    assert len(events) > 0
    assert all(e.event_type == "risk_share" for e in events)


def test_get_network_status():
    net = MultiDougCollaborationNetwork()
    net.register_node("D1")
    net.register_node("D2")
    status = net.get_network_status()
    assert status["total_nodes"] == 2
    assert "avg_trust" in status


def test_node_to_dict():
    node = DougNode(name="D1", version="2.0")
    d = node.to_dict()
    assert d["name"] == "D1"
    assert "trust_score" in d
