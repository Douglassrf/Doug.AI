"""Servo package.

This package groups together all servo implementations used by Doug.OS.
Servos analyse different aspects of the market or environment and
produce :class:`~doug_os.core.intent_vector.IntentVector` signals.

New servos should be imported here to make them available to other
modules via ``doug_os.servos``.
"""

# re-export common servos for convenience
from .news_psychology_servo import NewsPsychologyServo  # noqa: F401
from .market_servo import MarketIntelligenceServo  # noqa: F401
from .onchain_servo import OnChainIntelligenceServo  # noqa: F401
from .risk_empire_servo import RiskEmpireServo  # noqa: F401
from .evolution_research_servo import EvolutionResearchServo  # noqa: F401
from .news_intelligence_servo import NewsIntelligenceServo  # noqa: F401
from .macro_economic_servo import MacroEconomicServo  # noqa: F401
from .macro_economic_servo import MacroEconomicServo  # noqa: F401
