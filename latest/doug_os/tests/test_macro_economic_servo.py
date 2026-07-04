import asyncio

import pytest

from doug_os.servos.macro_economic_servo import MacroEconomicServo


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_sell_on_high_inflation_and_interest():
    servo = MacroEconomicServo()
    macro = {
        "interest_rate": 6.0,
        "inflation_rate": 6.5,
        "payroll_change": 0.0,
        "cpi_change": 0.0,
        "fomc": "neutral",
        "bce": "neutral",
    }
    iv = run(servo.analyze(macro))
    assert iv.direction == "SELL"
    assert iv.risk > 0


def test_buy_on_low_inflation_and_interest():
    servo = MacroEconomicServo()
    macro = {
        "interest_rate": 1.5,
        "inflation_rate": 1.5,
        "payroll_change": 10.0,  # positive payroll reduces risk
        "cpi_change": 0.2,
        "fomc": "dovish",
        "bce": "dovish",
    }
    iv = run(servo.analyze(macro))
    assert iv.direction == "BUY"
    # Confiança deve ser relativamente alta
    assert iv.confidence > 50
    # Risco deve ser moderado
    assert iv.risk < 50


def test_hold_on_mixed_indicators():
    servo = MacroEconomicServo()
    macro = {
        "interest_rate": 3.0,
        "inflation_rate": 3.5,
        "payroll_change": -5.0,
        "cpi_change": 1.0,
        "fomc": "hawkish",
        "bce": "neutral",
    }
    iv = run(servo.analyze(macro))
    assert iv.direction == "HOLD"
    # Risco deve ser alto devido à decisão hawkish e inflação alta
    assert iv.risk > 30
