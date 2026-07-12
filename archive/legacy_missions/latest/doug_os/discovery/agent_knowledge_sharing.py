from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class KnowledgeItem:
    id: str = field(default_factory=lambda: f"ki_{uuid.uuid4().hex[:12]}")
    source_agent: str = ""
    knowledge_type: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    tags: List[str] = field(default_factory=list)
    access_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_agent": self.source_agent,
            "knowledge_type": self.knowledge_type,
            "content": self.content,
            "confidence": self.confidence,
            "tags": self.tags,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class AgentKnowledgeSharing:
    """Repositório de conhecimento compartilhado entre agentes — tags, confiança, replay."""

    def __init__(self, confidence_threshold: float = 0.5) -> None:
        self._items: Dict[str, KnowledgeItem] = {}
        self._agent_subscriptions: Dict[str, List[str]] = {}
        self._confidence_threshold = confidence_threshold

    def publish_knowledge(
        self,
        source_agent: str,
        knowledge_type: str,
        content: Dict[str, Any],
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
    ) -> KnowledgeItem:
        item = KnowledgeItem(
            source_agent=source_agent,
            knowledge_type=knowledge_type,
            content=content,
            confidence=confidence,
            tags=tags or [],
        )
        self._items[item.id] = item
        return item

    def subscribe_agent(self, agent_id: str, knowledge_types: List[str]) -> None:
        self._agent_subscriptions[agent_id] = knowledge_types

    def get_for_agent(self, agent_id: str) -> List[KnowledgeItem]:
        subscribed = self._agent_subscriptions.get(agent_id, [])
        result = []
        now = datetime.now(timezone.utc)
        for item in self._items.values():
            if item.confidence < self._confidence_threshold:
                continue
            if item.expires_at and item.expires_at < now:
                continue
            if not subscribed or item.knowledge_type in subscribed:
                item.access_count += 1
                result.append(item)
        return result

    def search(self, tag: Optional[str] = None, knowledge_type: Optional[str] = None) -> List[KnowledgeItem]:
        results = []
        for item in self._items.values():
            if tag and tag not in item.tags:
                continue
            if knowledge_type and item.knowledge_type != knowledge_type:
                continue
            results.append(item)
        return sorted(results, key=lambda x: x.confidence, reverse=True)

    def get_top_items(self, n: int = 5) -> List[KnowledgeItem]:
        return sorted(self._items.values(), key=lambda x: x.confidence * (x.access_count + 1), reverse=True)[:n]

    def get_sharing_stats(self) -> Dict[str, Any]:
        items = list(self._items.values())
        return {
            "total_items": len(items),
            "avg_confidence": sum(i.confidence for i in items) / len(items) if items else 0.0,
            "knowledge_types": list({i.knowledge_type for i in items}),
            "subscribed_agents": len(self._agent_subscriptions),
            "most_accessed": sorted(items, key=lambda x: x.access_count, reverse=True)[0].id if items else None,
        }
