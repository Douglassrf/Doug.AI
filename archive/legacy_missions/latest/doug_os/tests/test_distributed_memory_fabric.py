import pytest
from discovery.distributed_memory_fabric import DistributedMemoryFabric, MemoryNode


def test_add_node():
    fabric = DistributedMemoryFabric()
    node = fabric.add_node("n1", "host1", 6379)
    assert node.name == "n1"
    assert node.port == 6379


def test_set_and_get():
    fabric = DistributedMemoryFabric(replication_factor=1)
    fabric.add_node("n1", "host1", 6379)
    assert fabric.set("mykey", "myvalue") is True
    assert fabric.get("mykey") == "myvalue"


def test_get_missing_key():
    fabric = DistributedMemoryFabric(replication_factor=1)
    fabric.add_node("n1", "host1", 6379)
    assert fabric.get("missing") is None


def test_set_no_nodes_fails():
    fabric = DistributedMemoryFabric()
    assert fabric.set("key", "val") is False


def test_delete():
    fabric = DistributedMemoryFabric(replication_factor=1)
    fabric.add_node("n1", "h", 80)
    fabric.set("k", "v")
    fabric.delete("k")
    assert fabric.get("k") is None


def test_replication():
    fabric = DistributedMemoryFabric(replication_factor=2)
    fabric.add_node("n1", "h1", 1)
    fabric.add_node("n2", "h2", 2)
    fabric.add_node("n3", "h3", 3)
    fabric.set("rkey", "rval")
    assert fabric.get("rkey") == "rval"


def test_sync_all():
    fabric = DistributedMemoryFabric(replication_factor=1)
    fabric.add_node("n1", "h1", 1)
    fabric.set("k", "v")
    fabric.sync_all()  # returns None; just ensure no exception


def test_get_cluster_status():
    fabric = DistributedMemoryFabric()
    fabric.add_node("n1", "h1", 1)
    status = fabric.get_cluster_status()
    assert "nodes" in status or "total_nodes" in status


def test_multiple_keys():
    fabric = DistributedMemoryFabric(replication_factor=1)
    fabric.add_node("n1", "h1", 1)
    for i in range(5):
        fabric.set(f"key{i}", i)
    for i in range(5):
        assert fabric.get(f"key{i}") == i
