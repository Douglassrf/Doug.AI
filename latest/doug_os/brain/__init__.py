"""Doug.OS brain package.

This package exposes the core DougBrain and the unified intelligence
layer.  The unified layer aggregates signals from multiple servos,
applies the intelligence council and supervisor to produce a final
decision with context and explanations.
"""

from .doug_brain import DougBrain  # noqa: F401
from .unified_intelligence_layer import UnifiedIntelligenceLayer  # noqa: F401
