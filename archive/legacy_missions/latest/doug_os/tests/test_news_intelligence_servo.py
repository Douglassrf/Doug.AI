import asyncio

import pytest

from doug_os.servos.news_intelligence_servo import NewsIntelligenceServo


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_buy_signal_on_positive_news():
    servo = NewsIntelligenceServo()
    news = [
        {"sentiment_score": 80, "impact_score": 70, "source_confidence": 90},
        {"sentiment_score": 75, "impact_score": 60, "source_confidence": 80},
    ]
    iv = run(servo.analyze(news))
    assert iv.direction == "BUY"
    # Confidence should be close to average sentiment
    assert iv.confidence > 70
    # Risk should be less than 50 because sentiment is high
    assert iv.risk < 50


def test_sell_signal_on_negative_news():
    servo = NewsIntelligenceServo()
    news = [
        {"sentiment_score": 30, "impact_score": 70, "source_confidence": 90},
        {"sentiment_score": 35, "impact_score": 60, "source_confidence": 80},
    ]
    iv = run(servo.analyze(news))
    assert iv.direction == "SELL"
    assert iv.confidence < 40
    assert iv.manipulation_risk < 30  # high confidence reduces manipulation risk


def test_hold_signal_on_neutral_news():
    servo = NewsIntelligenceServo()
    news = [
        {"sentiment_score": 55, "impact_score": 50, "source_confidence": 50},
        {"sentiment_score": 45, "impact_score": 50, "source_confidence": 50},
    ]
    iv = run(servo.analyze(news))
    assert iv.direction == "HOLD"
    # evidence strength should be around 50
    assert 45 <= iv.evidence_strength <= 55


def test_no_news_returns_neutral_vector():
    servo = NewsIntelligenceServo()
    iv = run(servo.analyze([]))
    assert iv.direction == "HOLD"
    assert iv.evidence_strength == 0
    assert iv.reasons == ("no_news",)