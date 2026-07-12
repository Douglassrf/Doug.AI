from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class MemoryBlock:
    id: str = field(default_factory=lambda: f"mb_{uuid.uuid4().hex[:12]}")
    key: str = ""
    value: Any = None
    importance: float = 0.5
    access_count: int = 0
    last_access: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    compressed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_access": self.last_access.isoformat() if self.last_access else None,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "compressed": self.compressed,
        }


@dataclass
class MemoryOptimizationReport:
    blocks_compressed: int = 0
    blocks_removed: int = 0
    blocks_aged: int = 0
    total_size_saved_bytes: int = 0
    new_total_size_bytes: int = 0
    compression_ratio: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blocks_compressed": self.blocks_compressed,
            "blocks_removed": self.blocks_removed,
            "blocks_aged": self.blocks_aged,
            "total_size_saved_bytes": self.total_size_saved_bytes,
            "new_total_size_bytes": self.new_total_size_bytes,
            "compression_ratio": self.compression_ratio,
            "created_at": self.created_at.isoformat(),
        }


class AdaptiveMemoryOptimizer:
    """Otimizador adaptativo de memória — compressão, envelhecimento e eliminação de duplicatas."""

    def __init__(self, max_memory_blocks: int = 1000) -> None:
        self._blocks: Dict[str, MemoryBlock] = {}
        self._max_blocks = max_memory_blocks
        self._optimization_history: List[MemoryOptimizationReport] = []

    def store(self, key: str, value: Any, importance: float = 0.5) -> MemoryBlock:
        # Update existing
        for block in self._blocks.values():
            if block.key == key:
                block.value = value
                block.importance = importance
                block.access_count += 1
                block.last_access = datetime.now(timezone.utc)
                block.size_bytes = len(str(value))
                return block

        block = MemoryBlock(key=key, value=value, importance=importance, size_bytes=len(str(value)))
        self._blocks[block.id] = block

        if len(self._blocks) > self._max_blocks:
            self._optimize()

        return block

    def retrieve(self, key: str) -> Optional[Any]:
        for block in self._blocks.values():
            if block.key == key:
                block.access_count += 1
                block.last_access = datetime.now(timezone.utc)
                return block.value
        return None

    def delete(self, key: str) -> bool:
        for bid, block in list(self._blocks.items()):
            if block.key == key:
                del self._blocks[bid]
                return True
        return False

    def optimize(self) -> MemoryOptimizationReport:
        return self._optimize()

    def _optimize(self) -> MemoryOptimizationReport:
        report = MemoryOptimizationReport()
        original_size = sum(b.size_bytes for b in self._blocks.values())

        # 1. Deduplicate by key
        seen: Dict[str, str] = {}
        for bid, block in list(self._blocks.items()):
            if block.key in seen:
                del self._blocks[bid]
                report.blocks_removed += 1
            else:
                seen[block.key] = bid

        # 2. Age-out stale blocks
        now = datetime.now(timezone.utc)
        for block in list(self._blocks.values()):
            if block.last_access is None:
                age_days = 0.0
            else:
                age_days = (now - block.last_access).total_seconds() / 86400
            if age_days > 30:
                block.importance *= 0.5
                report.blocks_aged += 1
                if block.importance < 0.1:
                    self._blocks.pop(block.id, None)
                    report.blocks_removed += 1

        # 3. Compress large blocks
        for block in self._blocks.values():
            if block.size_bytes > 1000 and not block.compressed:
                block.value = self._compress_value(block.value)
                block.compressed = True
                block.size_bytes = len(str(block.value))
                report.blocks_compressed += 1

        new_size = sum(b.size_bytes for b in self._blocks.values())
        report.total_size_saved_bytes = original_size - new_size
        report.new_total_size_bytes = new_size
        report.compression_ratio = new_size / original_size if original_size > 0 else 1.0
        self._optimization_history.append(report)
        return report

    @staticmethod
    def _compress_value(value: Any) -> Any:
        if isinstance(value, str) and len(value) > 100:
            return value[:100] + "..."
        return value

    def get_memory_heatmap(self) -> Dict[str, float]:
        return {b.key: b.importance for b in self._blocks.values()}

    def get_optimization_dashboard(self) -> Dict[str, Any]:
        total = len(self._blocks)
        total_size = sum(b.size_bytes for b in self._blocks.values())
        avg_imp = float(np.mean([b.importance for b in self._blocks.values()])) if total else 0.0
        return {
            "total_blocks": total,
            "total_size_bytes": total_size,
            "avg_importance": avg_imp,
            "optimizations_performed": len(self._optimization_history),
            "last_optimization": self._optimization_history[-1].to_dict() if self._optimization_history else None,
        }
