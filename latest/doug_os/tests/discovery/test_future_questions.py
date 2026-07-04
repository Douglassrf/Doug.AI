import pytest
from doug_os.discovery.future_questions import FutureQuestionsGenerator, ResearchQuestion


def test_generate_questions_count():
    gen = FutureQuestionsGenerator(seed=42)
    questions = gen.generate_questions(n_questions=7)
    assert len(questions) == 7


def test_generate_questions_text_not_empty():
    gen = FutureQuestionsGenerator(seed=1)
    questions = gen.generate_questions(n_questions=5)
    for q in questions:
        assert q.text != ""


def test_priority_in_range():
    gen = FutureQuestionsGenerator(seed=0)
    questions = gen.generate_questions(n_questions=20)
    for q in questions:
        assert 1 <= q.priority <= 10


def test_market_regime_filter():
    gen = FutureQuestionsGenerator(seed=5)
    questions = gen.generate_questions(market_regime="crisis", n_questions=5)
    for q in questions:
        assert q.market_regime == "crisis"


def test_identify_gaps():
    gen = FutureQuestionsGenerator(seed=10)
    questions = gen.generate_questions(n_questions=5)
    texts = [q.text for q in questions]
    known = texts[:4]
    resolved = texts[:2]
    gaps = gen.identify_gaps(known=known, resolved=resolved)
    for g in gaps:
        assert g.text in known
        assert g.text not in resolved


def test_get_priority_queue_sorted():
    gen = FutureQuestionsGenerator(seed=77)
    gen.generate_questions(n_questions=10)
    queue = gen.get_priority_queue(n=10)
    priorities = [q.priority for q in queue]
    assert priorities == sorted(priorities, reverse=True)


def test_to_dict_serialization():
    q = ResearchQuestion(text="What drives volatility?", priority=8, market_regime="crisis")
    d = q.to_dict()
    assert d["text"] == "What drives volatility?"
    assert d["priority"] == 8
    assert d["market_regime"] == "crisis"
    assert "created_at" in d
    assert d["status"] == "pending"
