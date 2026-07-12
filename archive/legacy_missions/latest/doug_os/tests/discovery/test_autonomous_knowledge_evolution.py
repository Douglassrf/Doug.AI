import pytest
from doug_os.discovery.autonomous_knowledge_evolution import (
    AutonomousKnowledgeEvolution, KnowledgeItem, EvolutionReport
)


@pytest.fixture
def ake():
    return AutonomousKnowledgeEvolution()


def test_add_knowledge_active(ake):
    item = ake.add_knowledge("Python is great", "programming", "manual", confidence=0.7, importance=0.8)
    assert isinstance(item, KnowledgeItem)
    assert item.status == "active"
    assert item.content == "Python is great"
    assert item.category == "programming"
    assert item.confidence == 0.7


def test_validate_knowledge_increments_and_increases_confidence(ake):
    item = ake.add_knowledge("Test fact", "science", "source", confidence=0.5)
    original_confidence = item.confidence
    result = ake.validate_knowledge(item.id)
    assert result is True
    assert item.validation_count == 1
    assert item.confidence > original_confidence
    assert item.last_validated is not None


def test_validate_knowledge_invalid_id(ake):
    result = ake.validate_knowledge("nonexistent_id")
    assert result is False


def test_promote_knowledge(ake):
    item = ake.add_knowledge("Important fact", "business", "research")
    result = ake.promote_knowledge(item.id)
    assert result is True
    assert item.status == "promoted"
    assert item.importance > 0.5


def test_archive_knowledge(ake):
    item = ake.add_knowledge("Old fact", "history", "archive_source")
    result = ake.archive_knowledge(item.id)
    assert result is True
    assert item.status == "archived"


def test_evolve_processes_items(ake):
    ake.add_knowledge("Fact 1", "cat1", "src1")
    ake.add_knowledge("Fact 2", "cat2", "src2")
    ake.add_knowledge("Fact 3", "cat1", "src3")
    report = ake.evolve()
    assert isinstance(report, EvolutionReport)
    assert report.items_processed == 3


def test_evolve_recommendations(ake):
    ake.add_knowledge("Low confidence fact", "cat", "src", confidence=0.2)
    report = ake.evolve()
    assert isinstance(report.recommendations, list)


def test_get_knowledge_by_category_active_only(ake):
    ake.add_knowledge("Active fact", "tech", "src1")
    archived = ake.add_knowledge("Old fact", "tech", "src2")
    ake.archive_knowledge(archived.id)
    ake.add_knowledge("Other cat", "science", "src3")
    tech_items = ake.get_knowledge_by_category("tech")
    assert len(tech_items) == 1
    assert tech_items[0].content == "Active fact"
    assert all(i.status == "active" for i in tech_items)


def test_get_top_knowledge_sorted(ake):
    ake.add_knowledge("Low", "cat", "src", confidence=0.3, importance=0.3)
    ake.add_knowledge("High", "cat", "src", confidence=0.9, importance=0.9)
    ake.add_knowledge("Mid", "cat", "src", confidence=0.5, importance=0.6)
    top = ake.get_top_knowledge(3)
    assert len(top) == 3
    scores = [i.importance * i.confidence for i in top]
    assert scores[0] >= scores[1] >= scores[2]
    assert top[0].content == "High"


def test_to_dict_all_fields(ake):
    item = ake.add_knowledge("Dict test", "testing", "unit_test", confidence=0.6, importance=0.7)
    d = item.to_dict()
    for key in ["id", "content", "category", "source", "confidence", "importance",
                "age_days", "validation_count", "last_validated", "created_at", "status"]:
        assert key in d
    assert d["status"] == "active"
    assert d["last_validated"] is None
    assert d["confidence"] == 0.6
