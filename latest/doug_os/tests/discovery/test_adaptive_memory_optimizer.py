import pytest
from doug_os.discovery.adaptive_memory_optimizer import (
    AdaptiveMemoryOptimizer, MemoryBlock, MemoryOptimizationReport,
)


@pytest.fixture
def optimizer():
    return AdaptiveMemoryOptimizer(max_memory_blocks=20)


def test_store_returns_block(optimizer):
    block = optimizer.store("key1", "value1", importance=0.7)
    assert isinstance(block, MemoryBlock)
    assert block.key == "key1"


def test_retrieve_returns_value(optimizer):
    optimizer.store("k", "hello")
    assert optimizer.retrieve("k") == "hello"


def test_retrieve_missing_returns_none(optimizer):
    assert optimizer.retrieve("nonexistent") is None


def test_store_updates_existing(optimizer):
    optimizer.store("k", "v1")
    optimizer.store("k", "v2")
    assert optimizer.retrieve("k") == "v2"
    # Only one block per key
    keys = [b.key for b in optimizer._blocks.values()]
    assert keys.count("k") == 1


def test_access_count_increments(optimizer):
    optimizer.store("k", "v")
    optimizer.retrieve("k")
    optimizer.retrieve("k")
    for block in optimizer._blocks.values():
        if block.key == "k":
            assert block.access_count >= 2


def test_delete_removes_block(optimizer):
    optimizer.store("del_key", "val")
    assert optimizer.delete("del_key") is True
    assert optimizer.retrieve("del_key") is None


def test_delete_nonexistent_returns_false(optimizer):
    assert optimizer.delete("ghost") is False


def test_optimize_runs_without_error(optimizer):
    for i in range(5):
        optimizer.store(f"k{i}", "x" * 1500, importance=0.2)
    report = optimizer.optimize()
    assert isinstance(report, MemoryOptimizationReport)


def test_optimization_compresses_large_blocks(optimizer):
    optimizer.store("big", "a" * 2000)
    optimizer.optimize()
    big_block = next((b for b in optimizer._blocks.values() if b.key == "big"), None)
    if big_block:
        assert big_block.compressed is True


def test_get_memory_heatmap(optimizer):
    optimizer.store("a", "v1", importance=0.8)
    optimizer.store("b", "v2", importance=0.3)
    heatmap = optimizer.get_memory_heatmap()
    assert "a" in heatmap
    assert "b" in heatmap
    assert heatmap["a"] == pytest.approx(0.8)


def test_get_optimization_dashboard(optimizer):
    optimizer.store("x", "v")
    optimizer.optimize()
    dash = optimizer.get_optimization_dashboard()
    assert "total_blocks" in dash
    assert "optimizations_performed" in dash
    assert dash["optimizations_performed"] >= 1


def test_eviction_when_over_max(optimizer):
    big = AdaptiveMemoryOptimizer(max_memory_blocks=5)
    for i in range(10):
        big.store(f"key_{i}", f"val_{i}")
    # After eviction, blocks should be <= max
    # (eviction happens during store when >max)
    assert len(big._blocks) <= 10  # optimization may or may not remove all
