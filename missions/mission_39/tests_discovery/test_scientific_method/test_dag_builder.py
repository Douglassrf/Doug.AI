import pytest
from doug_os.discovery.scientific_method.dag_builder import DAGBuilder, DAGNode, DAGEdge


@pytest.fixture
def builder():
    return DAGBuilder()


def test_add_node(builder):
    builder.add_node(DAGNode(name="volatility", node_type="treatment"))
    dag = builder.build()
    assert "volatility" in dag.nodes


def test_add_edge(builder):
    builder.add_node(DAGNode("A"))
    builder.add_node(DAGNode("B"))
    builder.add_edge(DAGEdge(source="A", target="B"))
    dag = builder.build()
    assert dag.has_edge("A", "B")


def test_cycle_raises(builder):
    builder.add_node(DAGNode("X"))
    builder.add_node(DAGNode("Y"))
    builder.add_edge(DAGEdge("X", "Y"))
    with pytest.raises(ValueError, match="cycle"):
        builder.add_edge(DAGEdge("Y", "X"))


def test_get_ancestors(builder):
    for name in ["A", "B", "C"]:
        builder.add_node(DAGNode(name))
    builder.add_edge(DAGEdge("A", "B"))
    builder.add_edge(DAGEdge("B", "C"))
    ancestors = builder.get_ancestors("C")
    assert "A" in ancestors and "B" in ancestors


def test_get_paths(builder):
    for name in ["A", "B", "C"]:
        builder.add_node(DAGNode(name))
    builder.add_edge(DAGEdge("A", "B"))
    builder.add_edge(DAGEdge("B", "C"))
    paths = builder.get_paths("A", "C")
    assert len(paths) == 1
    assert paths[0] == ["A", "B", "C"]


def test_to_dict(builder):
    builder.add_node(DAGNode("X", node_type="treatment"))
    builder.add_node(DAGNode("Y", node_type="outcome"))
    builder.add_edge(DAGEdge("X", "Y"))
    d = builder.to_dict()
    assert len(d["nodes"]) == 2
    assert len(d["edges"]) == 1
