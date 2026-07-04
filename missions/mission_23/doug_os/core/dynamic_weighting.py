"""Dynamic weighting combines servo recommendations based on market regime.

This class now delegates weight definitions to the global configuration
defined in :mod:`doug_os.config`.  Modifying the configuration file will
automatically propagate to consumers of this class.
"""

from doug_os.config import DYNAMIC_WEIGHT_BASE, DYNAMIC_WEIGHT_BY_REGIME


class DynamicWeighting:
    """Look up servo weights based on the detected market regime.

    Attributes are read from :mod:`doug_os.config` so that external
    configuration can drive the weighting strategy.  If an unknown regime
    is requested, the base weights are returned.
    """

    @staticmethod
    def get_weights(regime: str) -> dict[str, float]:
        # Obtain weights for the given regime, falling back to base.
        return dict(DYNAMIC_WEIGHT_BY_REGIME.get(regime, DYNAMIC_WEIGHT_BASE))
