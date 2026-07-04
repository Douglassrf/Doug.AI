from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class KnowledgeItem:
    id: str = field(default_factory=lambda: f"know_{uuid.uuid4().hex[:12]}")
    content: str = ""
    category: str = ""
    source: str = ""
    confidence: float = 0.5
    importance: float = 0.5
    age_days: float = 0.0
    validation_count: int = 0
    last_validated: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "content": self.content, "category": self.category,
            "source": self.source, "confidence": self.confidence,
            "importance": self.importance, "age_days": self.age_days,
            "validation_count": self.validation_count,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "created_at": self.created_at.isoformat(), "status": self.status,
        }


@dataclass
class EvolutionReport:
    items_processed: int = 0
    items_promoted: int = 0
    items_archived: int = 0
    avg_confidence: float = 0.0
    knowledge_growth_rate: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items_processed": self.items_processed, "items_promoted": self.items_promoted,
            "items_archived": self.items_archived, "avg_confidence": self.avg_confidence,
            "knowledge_growth_rate": self.knowledge_growth_rate,
            "recommendations": self.recommendations, "created_at": self.created_at.isoformat(),
        }


class AutonomousKnowledgeEvolution:
    def __init__(self, max_age_days: float = 365.0):
        self._knowledge_items: Dict[str, KnowledgeItem] = {}
        self._max_age_days = max_age_days
        self._evolution_history: List[EvolutionReport] = []

    def add_knowledge(self, content: str, category: str, source: str,
                      confidence: float = 0.5, importance: float = 0.5) -> KnowledgeItem:
        item = KnowledgeItem(content=content, category=category, source=source,
                             confidence=confidence, importance=importance)
        self._knowledge_items[item.id] = item
        return item

    def validate_knowledge(self, item_id: str) -> bool:
        item = self._knowledge_items.get(item_id)
        if not item:
            return False
        item.validation_count += 1
        item.last_validated = datetime.now(timezone.utc)
        item.confidence = min(item.confidence + 0.1, 1.0)
        return True

    def promote_knowledge(self, item_id: str) -> bool:
        item = self._knowledge_items.get(item_id)
        if not item:
            return False
        item.status = "promoted"
        item.importance = min(item.importance + 0.2, 1.0)
        return True

    def archive_knowledge(self, item_id: str) -> bool:
        item = self._knowledge_items.get(item_id)
        if not item:
            return False
        item.status = "archived"
        return True

    def evolve(self) -> EvolutionReport:
        report = EvolutionReport()
        now = datetime.now(timezone.utc)
        for item in self._knowledge_items.values():
            report.items_processed += 1
            item.age_days = (now - item.created_at).total_seconds() / 86400
            decay = min(item.age_days / self._max_age_days, 1.0)
            item.confidence = max(item.confidence - decay * 0.1, 0.1)
            if item.confidence > 0.8 and item.validation_count > 5 and item.status != "promoted":
                self.promote_knowledge(item.id)
                report.items_promoted += 1
            elif item.confidence < 0.3 and item.age_days > self._max_age_days * 0.5 and item.status != "archived":
                self.archive_knowledge(item.id)
                report.items_archived += 1
        active = [i for i in self._knowledge_items.values() if i.status == "active"]
        if active:
            report.avg_confidence = float(np.mean([i.confidence for i in active]))
        if self._evolution_history:
            prev = self._evolution_history[-1].items_processed
            report.knowledge_growth_rate = (report.items_processed - prev) / prev if prev > 0 else 0.0
        report.recommendations = self._generate_recommendations(report)
        self._evolution_history.append(report)
        return report

    def _generate_recommendations(self, report: EvolutionReport) -> List[str]:
        recs = []
        if report.avg_confidence < 0.5:
            recs.append("Low knowledge confidence. Focus on validation.")
        if report.items_promoted == 0:
            recs.append("No knowledge promoted. Review quality criteria.")
        if report.knowledge_growth_rate < 0.01:
            recs.append("Slow knowledge growth. Accelerate learning process.")
        return recs

    def get_knowledge_by_category(self, category: str) -> List[KnowledgeItem]:
        return [i for i in self._knowledge_items.values() if i.category == category and i.status == "active"]

    def get_top_knowledge(self, n: int = 10) -> List[KnowledgeItem]:
        active = [i for i in self._knowledge_items.values() if i.status == "active"]
        return sorted(active, key=lambda x: x.importance * x.confidence, reverse=True)[:n]
