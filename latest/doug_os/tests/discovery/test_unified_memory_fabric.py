import pytest
from datetime import datetime, timezone, timedelta
from doug_os.discovery.unified_memory_fabric import UnifiedMemoryFabric, MemoryType, MemoryEntry


def test_store_and_retrieve_returns_correct_value():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "stock_price", 150.0)
    assert fabric.retrieve("stock_price") == 150.0


def test_retrieve_unknown_key_returns_none():
    fabric = UnifiedMemoryFabric()
    assert fabric.retrieve("nonexistent_key") is None


def test_retrieve_by_type_returns_only_that_type():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "k1", "v1")
    fabric.store(MemoryType.EPISODIC, "k2", "v2")
    fabric.store(MemoryType.SEMANTIC, "k3", "v3")
    semantic = fabric.retrieve_by_type(MemoryType.SEMANTIC)
    types = {e.memory_type for e in semantic}
    assert types == {MemoryType.SEMANTIC}
    assert len(semantic) == 2


def test_retrieve_by_tag_returns_tagged_entries():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "k1", "v1", tags={"finance", "stocks"})
    fabric.store(MemoryType.SEMANTIC, "k2", "v2", tags={"crypto"})
    results = fabric.retrieve_by_tag("finance")
    assert len(results) == 1
    assert results[0].key == "k1"


def test_search_finds_entry_by_key_substring():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "bitcoin_price", 50000.0)
    fabric.store(MemoryType.SEMANTIC, "ethereum_price", 3000.0)
    results = fabric.search("bitcoin")
    assert len(results) >= 1
    assert any(e.key == "bitcoin_price" for e in results)


def test_update_context_and_get_context():
    fabric = UnifiedMemoryFabric()
    fabric.update_context({"market": "bullish", "vol": 0.2})
    ctx = fabric.get_context()
    assert ctx["market"] == "bullish"
    assert ctx["vol"] == 0.2


def test_forget_removes_entry_and_second_call_returns_false():
    fabric = UnifiedMemoryFabric()
    entry = fabric.store(MemoryType.SEMANTIC, "temp_key", "temp_val")
    assert fabric.forget(entry.id) is True
    assert fabric.forget(entry.id) is False


def test_get_statistics_total_memories():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "k1", "v1")
    fabric.store(MemoryType.EPISODIC, "k2", "v2")
    fabric.store(MemoryType.WORKING, "k3", "v3")
    stats = fabric.get_statistics()
    assert stats["total_memories"] == 3
    assert "avg_importance" in stats


def test_store_returns_memory_entry_with_correct_fields():
    fabric = UnifiedMemoryFabric()
    entry = fabric.store(MemoryType.EPISODIC, "event1", {"data": 42}, importance=0.9)
    assert isinstance(entry, MemoryEntry)
    assert entry.memory_type == MemoryType.EPISODIC
    assert entry.key == "event1"
    assert entry.importance == 0.9


def test_retrieve_increments_access_count():
    fabric = UnifiedMemoryFabric()
    fabric.store(MemoryType.SEMANTIC, "counter_key", "val")
    fabric.retrieve("counter_key")
    fabric.retrieve("counter_key")
    ids = fabric._index["counter_key"]
    entry = fabric._memories[next(iter(ids))]
    assert entry.access_count == 2
