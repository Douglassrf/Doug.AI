from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import hashlib
import json
from collections import OrderedDict


@dataclass
class CacheEntry:
    key: str = ""
    value: Any = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_access: Optional[datetime] = None
    size: int = 0

    def is_expired(self) -> bool:
        if self.expires_at is None: return False
        return datetime.now(timezone.utc) > self.expires_at


class IntelligentCacheEngine:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry: self._misses += 1; return None
        if entry.is_expired(): self._cache.pop(key, None); self._misses += 1; return None
        entry.access_count += 1
        entry.last_access = datetime.now(timezone.utc)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            semantic_key: Optional[str] = None) -> None:
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=effective_ttl) if effective_ttl > 0 else None
        entry = CacheEntry(key=key, value=value, expires_at=expires_at, size=len(str(value)))
        self._cache[key] = entry
        self._cache.move_to_end(key)
        if semantic_key:
            self._cache[f"semantic_{semantic_key}"] = entry

    def get_or_compute(self, key: str, compute_fn: Callable, ttl: Optional[int] = None,
                       *args, **kwargs) -> Any:
        result = self.get(key)
        if result is not None: return result
        result = compute_fn(*args, **kwargs)
        self.set(key, result, ttl)
        return result

    def get_semantic(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        q = query.lower()
        results = {}
        for key, entry in self._cache.items():
            if entry.is_expired(): continue
            if q in key.lower():
                results[key] = {"value": entry.value, "score": 0.5, "access_count": entry.access_count}
            elif isinstance(entry.value, str) and q in entry.value.lower():
                results[key] = {"value": entry.value, "score": 0.3, "access_count": entry.access_count}
        sorted_r = sorted(results.items(), key=lambda x: (x[1]["score"] + x[1]["access_count"] * 0.1), reverse=True)
        return dict(sorted_r[:max_results])

    def invalidate(self, key: str) -> bool:
        if key in self._cache: self._cache.pop(key); return True
        return False

    def clear_expired(self) -> int:
        expired = [k for k, e in self._cache.items() if e.is_expired()]
        for k in expired: self._cache.pop(k)
        return len(expired)

    def get_stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size": len(self._cache), "max_size": self._max_size,
            "hits": self._hits, "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "avg_size": sum(e.size for e in self._cache.values()) / len(self._cache) if self._cache else 0.0,
        }
