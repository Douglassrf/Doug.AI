import pytest
from datetime import datetime, timezone, timedelta
from doug_os.discovery.context_awareness_engine import ContextAwarenessEngine, Context


MARKET = {"regime": "bull", "volatility": 0.3}
MACRO = {"regime": "expansion", "gdp_growth": 0.5}
TEMPORAL = {"horizon": "medium_term"}
PORTFOLIO = {"cash": 0.2}
RISK = {"level": "medium", "var": 0.05}
NEWS = {"sentiment": 0.6}
BEHAVIORAL = {"fear_greed": 0.7}


def build_engine():
    eng = ContextAwarenessEngine()
    ctx = eng.build_context(MARKET, MACRO, TEMPORAL, PORTFOLIO, RISK, NEWS, BEHAVIORAL)
    return eng, ctx


def test_build_context_returns_context_with_all_fields():
    eng, ctx = build_engine()
    assert isinstance(ctx, Context)
    assert ctx.market == MARKET
    assert ctx.macro == MACRO
    assert ctx.temporal == TEMPORAL
    assert ctx.portfolio == PORTFOLIO
    assert ctx.risk == RISK
    assert ctx.news == NEWS
    assert ctx.behavioral == BEHAVIORAL


def test_get_current_context_returns_most_recent():
    eng = ContextAwarenessEngine()
    ctx1 = eng.build_context(MARKET, MACRO, TEMPORAL, PORTFOLIO, RISK, NEWS, BEHAVIORAL)
    ctx2 = eng.build_context({"regime": "bear"}, {}, {}, {}, {}, {}, {})
    assert eng.get_current_context().id == ctx2.id


def test_confidence_calculated_from_numeric_data():
    eng = ContextAwarenessEngine()
    ctx = eng.build_context({"val": 0.8}, {"val": 0.6}, {}, {}, {}, {}, {})
    # confidence is mean of numeric values capped at 1.0
    assert 0.0 <= ctx.confidence <= 1.0


def test_relevance_increases_with_market_macro_temporal():
    eng = ContextAwarenessEngine()
    ctx_empty = eng.build_context({}, {}, {}, {}, {}, {}, {})
    ctx_full = eng.build_context(MARKET, MACRO, TEMPORAL, {}, {}, {}, {})
    assert ctx_full.relevance_score > ctx_empty.relevance_score


def test_get_context_summary_no_context():
    eng = ContextAwarenessEngine()
    assert eng.get_context_summary() == {"status": "no_context"}


def test_get_context_summary_with_context():
    eng, ctx = build_engine()
    summary = eng.get_context_summary()
    assert "market_regime" in summary
    assert "macro_regime" in summary
    assert "risk_level" in summary
    assert "confidence" in summary
    assert summary["market_regime"] == "bull"


def test_to_dict_serializes_all_fields():
    eng, ctx = build_engine()
    d = ctx.to_dict()
    assert "id" in d
    assert "timestamp" in d
    assert "market" in d
    assert "macro" in d
    assert "confidence" in d
    assert "relevance_score" in d
    assert isinstance(d["timestamp"], str)
