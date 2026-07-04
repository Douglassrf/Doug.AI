"""Brian Supreme package.

This package provides supervisory layers that audit decisions and
suggest adjustments.  Version 1 introduces enhanced auditing and
explanatory capabilities via :class:`~doug_os.brian.brian_supreme_v1.BrianSupremeV1`.
Future versions may extend these features.
"""

from .brian_supreme import BrianSupreme  # noqa: F401
from .brian_supreme_v1 import BrianSupremeV1  # noqa: F401
