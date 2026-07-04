import pytest
from datetime import datetime, timezone, timedelta
from doug_os.discovery.global_knowledge_graph import (
    GlobalKnowledgeGraph, KnowledgeNode, KnowledgeEdge
)


def make_node(type_="concept", name="test", description="desc"):
    return KnowledgeNode(type=type_, name=name, description=description)


def test_add_and_get_node():
    g = GlobalKnowledgeGraph()
    n = make_node(name="alpha")
    g.add_node(n)
    result = g.get_node(n.id)
    assert result is n
    assert result.name == "alpha"


def test_get_node_missing_returns_none():
    g = GlobalKnowledgeGraph()
    assert g.get_node("nonexistent") is None


def test_add_edge_missing_node_raises():
    g = GlobalKnowledgeGraph()
    n = make_node()
    g.add_node(n)
    edge = KnowledgeEdge(source_id=n.id, target_id="missing", relationship="relates")
    with pytest.raises(ValueError):
        g.add_edge(edge)


def test_add_edge_missing_source_raises():
    g = GlobalKnowledgeGraph()
    n = make_node()
    g.add_node(n)
    edge = KnowledgeEdge(source_id="missing", target_id=n.id, relationship="relates")
    with pytest.raises(ValueError):
        g.add_edge(edge)


def test_get_nodes_by_type():
    g = GlobalKnowledgeGraph()
    n1 = make_node(type_="asset")
    n2 = make_node(type_="asset")
    n3 = make_node(type_="event")
    g.add_node(n1); g.add_node(n2); g.add_node(n3)
    assets = g.get_nodes_by_type("asset")
    assert len(assets) == 2
    assert all(n.type == "asset" for n in assets)
    events = g.get_nodes_by_type("event")
    assert len(events) == 1


def test_traverse_bfs_depth():
    g = GlobalKnowledgeGraph()
    n0 = make_node(name="root")
    n1 = make_node(name="child")
    n2 = make_node(name="grandchild")
    g.add_node(n0); g.add_node(n1); g.add_node(n2)
    g.add_edge(KnowledgeEdge(source_id=n0.id, target_id=n1.id, relationship="has"))
    g.add_edge(KnowledgeEdge(source_id=n1.id, target_id=n2.id, relationship="has"))
    result = g.traverse(n0.id, max_depth=2)
    depths = {r["node"]["id"]: r["depth"] for r in result}
    assert depths[n0.id] == 0
    assert depths[n1.id] == 1
    assert depths[n2.id] == 2


def test_traverse_max_depth_limits():
    g = GlobalKnowledgeGraph()
    n0 = make_node(name="root")
    n1 = make_node(name="child")
    n2 = make_node(name="grandchild")
    g.add_node(n0); g.add_node(n1); g.add_node(n2)
    g.add_edge(KnowledgeEdge(source_id=n0.id, target_id=n1.id, relationship="has"))
    g.add_edge(KnowledgeEdge(source_id=n1.id, target_id=n2.id, relationship="has"))
    result = g.traverse(n0.id, max_depth=1)
    ids = {r["node"]["id"] for r in result}
    assert n2.id not in ids


def test_traverse_missing_node_returns_empty():
    g = GlobalKnowledgeGraph()
    assert g.traverse("nope") == []


def test_semantic_search_by_name():
    g = GlobalKnowledgeGraph()
    n1 = make_node(name="bitcoin price", description="crypto")
    n2 = make_node(name="ethereum", description="smart contracts")
    g.add_node(n1); g.add_node(n2)
    results = g.semantic_search("bitcoin")
    assert len(results) == 1
    assert results[0]["node"]["name"] == "bitcoin price"
    assert results[0]["score"] > 0


def test_semantic_search_by_description():
    g = GlobalKnowledgeGraph()
    n = make_node(name="foo", description="hello world signal")
    g.add_node(n)
    results = g.semantic_search("signal")
    assert len(results) == 1


def test_find_path_connected():
    g = GlobalKnowledgeGraph()
    n1 = make_node(name="A")
    n2 = make_node(name="B")
    g.add_node(n1); g.add_node(n2)
    g.add_edge(KnowledgeEdge(source_id=n1.id, target_id=n2.id, relationship="links"))
    path = g.find_path(n1.id, n2.id)
    assert path == [n1.id, n2.id]


def test_find_path_no_connection():
    g = GlobalKnowledgeGraph()
    n1 = make_node(name="A")
    n2 = make_node(name="B")
    g.add_node(n1); g.add_node(n2)
    path = g.find_path(n1.id, n2.id)
    assert path == []


def test_find_path_missing_node():
    g = GlobalKnowledgeGraph()
    n = make_node()
    g.add_node(n)
    assert g.find_path(n.id, "missing") == []


def test_get_relationship_edges():
    g = GlobalKnowledgeGraph()
    n1 = make_node(); n2 = make_node(); n3 = make_node()
    g.add_node(n1); g.add_node(n2); g.add_node(n3)
    e1 = KnowledgeEdge(source_id=n1.id, target_id=n2.id, relationship="causes")
    e2 = KnowledgeEdge(source_id=n2.id, target_id=n3.id, relationship="correlates")
    g.add_edge(e1); g.add_edge(e2)
    causes = g.get_relationship_edges("causes")
    assert len(causes) == 1
    assert causes[0].relationship == "causes"
    correlates = g.get_relationship_edges("correlates")
    assert len(correlates) == 1


def test_to_dict_serializes_all():
    g = GlobalKnowledgeGraph()
    n1 = make_node(name="X"); n2 = make_node(name="Y")
    g.add_node(n1); g.add_node(n2)
    e = KnowledgeEdge(source_id=n1.id, target_id=n2.id, relationship="links")
    g.add_edge(e)
    d = g.to_dict()
    assert n1.id in d["nodes"]
    assert n2.id in d["nodes"]
    assert e.id in d["edges"]
