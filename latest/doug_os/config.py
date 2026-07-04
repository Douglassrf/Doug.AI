"""Global configuration for Doug.OS missions.

This module centralizes thresholds and parameters used across servos,
engines, detectors and decision logic.  By collecting all tunable
values in a single location we avoid scattering “magic numbers”
throughout the codebase.  Future missions can modify this file to
tune behaviour (e.g. risk tolerances, weighting regimes, thresholds)
without touching the core logic.  The configuration is grouped into
semantic categories to aid discoverability.
"""

# Threshold values for servos.  Each servo may look up its
# configuration by its name and use sensible defaults.  Comments
# document the meaning of each threshold.
SERVO_THRESHOLDS: dict[str, dict[str, float]] = {
    # Evolution research servo will issue a BUY when the
    # historical edge exceeds this threshold.
    "evolution_research": {
        "min_historical_edge": 55.0,
    },
    # News & psychology servo thresholds
    "news_psychology": {
        # Minimum sentiment score required to consider a buy signal
        "min_sentiment_for_buy": 60.0,
        # Maximum panic score allowed for a buy signal
        "max_panic": 50.0,
    },
    # On-chain intelligence servo thresholds
    "onchain": {
        # Minimum whale accumulation score required for BUY
        "min_whale_accumulation": 50.0,
        # Maximum calculated dump risk before a warning is issued
        "max_dump_risk_warning": 65.0,
    },
    # Risk empire servo uses its own engine thresholds; provided here
    # for completeness in case future missions need to override.
    "risk_empire": {},

    # News intelligence servo thresholds
    # The news intelligence servo computes an average sentiment score from
    # recent headlines.  When the average sentiment meets or exceeds
    # ``sentiment_buy_threshold`` the servo issues a BUY.  When the
    # average sentiment is below ``sentiment_sell_threshold`` it issues
    # a SELL.  Between these bounds the servo holds.  These values
    # may be tuned to adjust sensitivity to news sentiment.
    "news_intelligence": {
        "sentiment_buy_threshold": 60.0,
        "sentiment_sell_threshold": 40.0,
    },

    # Macro economic servo thresholds
    # O servo macroeconômico interpreta indicadores como taxa de juros e inflação.
    # Quando a inflação ou a taxa de juros excedem `inflation_high` ou
    # `interest_high`, o servo emitirá um sinal de venda.  Quando ambos
    # estiverem abaixo de `inflation_low` e `interest_low`, um sinal de
    # compra é gerado.  Valores intermediários resultam em HOLD.
    "macro_economic": {
        "inflation_high": 5.0,
        "inflation_low": 2.0,
        "interest_high": 5.0,
        "interest_low": 2.0,
    },
}

# Default trading symbol used when none is provided.
DEFAULT_SYMBOL: str = "BTCUSDT"

# ---------------------------------------------------------------------------
# Dynamic weighting configuration
#
# The Doug.OS combines signals from multiple servos using a regime‑aware
# weighting scheme.  When adding new regimes or adjusting the relative
# importance of servos in existing regimes, update these dictionaries.

# Base weights when the market is considered "NORMAL".
DYNAMIC_WEIGHT_BASE: dict[str, float] = {
    "market": 0.18,
    "onchain": 0.25,
    "news_psychology": 0.12,
    "risk_empire": 0.20,
    "evolution_research": 0.10,
    # Allocate a share of the weighting to the news intelligence servo.
    "news_intelligence": 0.10,
    # Weighting for macro economic servo.  Macro signals tend to be lower
    # frequency and thus have a smaller weight in the short term.
    "macro_economic": 0.05,
}

# Weight adjustments by detected regime.  The keys of this mapping should
# match those returned by the RegimeDetector.  Each nested mapping
# overrides values in ``DYNAMIC_WEIGHT_BASE`` for the given regime.
DYNAMIC_WEIGHT_BY_REGIME: dict[str, dict[str, float]] = {
    "NORMAL": DYNAMIC_WEIGHT_BASE,
    "TRENDING": {
        "market": 0.35,
        "onchain": 0.30,
        "news_psychology": 0.10,
        "risk_empire": 0.15,
        "evolution_research": 0.10,
        # Keep a modest weight on the news intelligence servo during trending
        # regimes where technical signals are dominant.
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
    "MANIPULATED": {
        "market": 0.10,
        "onchain": 0.35,
        "news_psychology": 0.05,
        "risk_empire": 0.40,
        "evolution_research": 0.10,
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
    "SYSTEMIC_RISK": {
        "market": 0.05,
        "onchain": 0.15,
        "news_psychology": 0.05,
        "risk_empire": 0.65,
        "evolution_research": 0.10,
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
    "CHAOTIC": {
        "market": 0.05,
        "onchain": 0.15,
        "news_psychology": 0.05,
        "risk_empire": 0.65,
        "evolution_research": 0.10,
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
    "VOLATILE": {
        "market": 0.15,
        "onchain": 0.20,
        "news_psychology": 0.10,
        "risk_empire": 0.45,
        "evolution_research": 0.10,
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
    "WHITE_NOISE": {
        "market": 0.05,
        "onchain": 0.05,
        "news_psychology": 0.05,
        "risk_empire": 0.75,
        "evolution_research": 0.10,
        "news_intelligence": 0.10,
        "macro_economic": 0.05,
    },
}

# ---------------------------------------------------------------------------
# Risk empire defaults
#
# The RiskEmpire engine enforces high‑level risk limits on market exposure.
# These defaults define the maximum tolerances used when evaluating market
# events.  Users may override these values by passing custom parameters
# into ``RiskEmpire`` at runtime.
RISK_EMPIRE_DEFAULTS: dict[str, float] = {
    "max_risk": 80.0,
    "max_manipulation": 70.0,
    "min_reality": 40.0,
    "max_entropy_hold": 85.0,
    "max_drawdown": 0.03,
    "max_daily_loss": 0.05,
    "max_position_risk": 0.01,
}

# ---------------------------------------------------------------------------
# Regime detection thresholds
#
# The RegimeDetector inspects aggregated IntentVectors and classifies the
# current market regime.  To adjust the sensitivity or add new regimes,
# modify these values.  The detector compares averages of manipulation risk,
# entropy, risk, confidence and evidence strength against these thresholds.
REGIME_THRESHOLDS: dict[str, float] = {
    # When average manipulation_risk >= this value we classify as MANIPULATED
    "manipulation": 70.0,
    # When average entropy_score >= this value we classify as CHAOTIC
    "entropy_chaotic": 80.0,
    # When average risk >= this value we classify as SYSTEMIC_RISK
    "risk_systemic": 80.0,
    # When average entropy_score >= this value and confidence <= confidence_whitenoise
    # we classify as WHITE_NOISE
    "entropy_whitenoise": 65.0,
    "confidence_whitenoise": 45.0,
    # When average confidence >= this value and average evidence_strength >= evidence_trending
    # we classify as TRENDING
    "confidence_trending": 70.0,
    "evidence_trending": 65.0,
    # When average risk >= this value we classify as VOLATILE
    "risk_volatile": 60.0,
}

# ---------------------------------------------------------------------------
# Intent vector block thresholds
#
# These values control when an IntentVector should immediately block
# trading and trigger bunker mode.  When any of these criteria are met,
# ``IntentVector.is_blocking()`` returns True.  You can tweak these
# thresholds to adjust the defensive posture of the system.
INTENT_VECTOR_BLOCK_THRESHOLDS: dict[str, float] = {
    "risk": 80.0,
    "manipulation_risk": 70.0,
    "reality_score": 40.0,
    "entropy_score": 85.0,
}

# ---------------------------------------------------------------------------
# Confidence thresholds
#
# These optional levels can be used by decision logic to categorise
# signals.  They are not currently used but provide a foundation for
# future missions.
CONFIDENCE_LEVELS: dict[str, float] = {
    "low": 30.0,
    "medium": 60.0,
    "high": 80.0,
}