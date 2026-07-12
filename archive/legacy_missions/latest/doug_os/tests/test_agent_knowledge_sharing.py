import pytest
from discovery.agent_knowledge_sharing import AgentKnowledgeSharing, KnowledgeItem


def test_publish_knowledge():
    aks = AgentKnowledgeSharing()
    item = aks.publish_knowledge("market_agent", "trend", {"direction": "up"}, confidence=0.9)
    assert item.knowledge_type == "trend"
    assert item.confidence == 0.9


def test_get_for_subscribed_agent():
    aks = AgentKnowledgeSharing(confidence_threshold=0.5)
    aks.publish_knowledge("m", "trend", {"dir": "up"}, confidence=0.8, tags=["crypto"])
    aks.subscribe_agent("risk_agent", ["trend"])
    items = aks.get_for_agent("risk_agent")
    assert len(items) == 1


def test_confidence_filter():
    aks = AgentKnowledgeSharing(confidence_threshold=0.7)
    aks.publish_knowledge("m", "trend", {}, confidence=0.4)
    aks.subscribe_agent("a", ["trend"])
    items = aks.get_for_agent("a")
    assert len(items) == 0


def test_access_count_incremented():
    aks = AgentKnowledgeSharing(confidence_threshold=0.0)
    item = aks.publish_knowledge("m", "news", {}, confidence=0.8)
    aks.subscribe_agent("a", ["news"])
    aks.get_for_agent("a")
    aks.get_for_agent("a")
    assert item.access_count == 2


def test_search_by_tag():
    aks = AgentKnowledgeSharing()
    aks.publish_knowledge("m", "t", {"x": 1}, confidence=0.8, tags=["crypto"])
    aks.publish_knowledge("m", "t", {"x": 2}, confidence=0.7, tags=["equity"])
    results = aks.search(tag="crypto")
    assert len(results) == 1


def test_search_by_type():
    aks = AgentKnowledgeSharing()
    aks.publish_knowledge("m", "risk", {}, confidence=0.8)
    aks.publish_knowledge("m", "trend", {}, confidence=0.7)
    results = aks.search(knowledge_type="risk")
    assert len(results) == 1
    assert results[0].knowledge_type == "risk"


def test_get_top_items():
    aks = AgentKnowledgeSharing(confidence_threshold=0.0)
    for i in range(10):
        aks.publish_knowledge("m", "t", {}, confidence=i * 0.1)
    top = aks.get_top_items(n=3)
    assert len(top) == 3


def test_get_sharing_stats():
    aks = AgentKnowledgeSharing()
    aks.publish_knowledge("m", "trend", {}, confidence=0.8)
    stats = aks.get_sharing_stats()
    assert stats["total_items"] == 1
    assert "trend" in stats["knowledge_types"]


def test_all_agents_get_unsubscribed():
    aks = AgentKnowledgeSharing(confidence_threshold=0.0)
    aks.publish_knowledge("m", "global", {}, confidence=0.9)
    # agent with no subscriptions gets everything
    aks.subscribe_agent("wide", [])
    items = aks.get_for_agent("wide")
    assert len(items) == 1
