import pytest
import time
from doug_os.discovery.intelligent_cache_engine import IntelligentCacheEngine, CacheEntry


def test_set_and_get_returns_correct_value():
    cache = IntelligentCacheEngine()
    cache.set("price_btc", 50000)
    assert cache.get("price_btc") == 50000


def test_get_missing_key_returns_none_and_increments_misses():
    cache = IntelligentCacheEngine()
    result = cache.get("nonexistent")
    assert result is None
    stats = cache.get_stats()
    assert stats["misses"] == 1


def test_expired_entry_returns_none():
    cache = IntelligentCacheEngine(default_ttl=1)
    cache.set("expiring", "soon", ttl=-1)  # negative ttl => no expiry? No - ttl=-1 <= 0 => expires_at=None...
    # Use ttl=1 and mock via direct manipulation
    cache2 = IntelligentCacheEngine()
    cache2.set("will_expire", "val", ttl=1)
    # Manipulate expires_at to be in the past
    from datetime import datetime, timezone, timedelta
    cache2._cache["will_expire"].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    result = cache2.get("will_expire")
    assert result is None


def test_lru_eviction_removes_oldest_when_max_size_reached():
    cache = IntelligentCacheEngine(max_size=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.set("d", 4)  # should evict "a"
    assert cache.get("a") is None
    assert cache.get("b") == 2


def test_get_or_compute_calls_fn_only_first_time():
    cache = IntelligentCacheEngine()
    call_count = [0]

    def compute():
        call_count[0] += 1
        return 42

    r1 = cache.get_or_compute("computed", compute)
    r2 = cache.get_or_compute("computed", compute)
    assert r1 == 42
    assert r2 == 42
    assert call_count[0] == 1


def test_semantic_key_creates_prefixed_entry():
    cache = IntelligentCacheEngine()
    cache.set("main_key", "main_val", semantic_key="myquery")
    assert "semantic_myquery" in cache._cache


def test_invalidate_removes_entry_and_second_call_returns_false():
    cache = IntelligentCacheEngine()
    cache.set("del_me", "val")
    assert cache.invalidate("del_me") is True
    assert cache.invalidate("del_me") is False


def test_get_stats_hit_rate_correct():
    cache = IntelligentCacheEngine()
    cache.set("k", "v")
    cache.get("k")   # hit
    cache.get("k")   # hit
    cache.get("x")   # miss
    stats = cache.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert abs(stats["hit_rate"] - 2/3) < 0.01
