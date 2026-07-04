"""On‑chain intelligence core for Doug.OS (Missão 28).

This package groups together detectors and trackers that analyse
on‑chain data in a purely observacional manner.  All components in
``doug_os.onchain`` operate in **read‑only** mode: they consume
transactional data supplied by other layers (e.g., mock connectors or
off‑chain simulations) and extract high‑level insights.  No function
inside this package sends transactions or interacts with real
blockchains.

Modules included:

* :mod:`whale_detector` – identifies large movements from whales.
* :mod:`exchange_flow_tracker` – tracks net inflow/outflow from exchanges.
* :mod:`stablecoin_tracker` – tracks stablecoin flows between exchanges/wallets.
* :mod:`wallet_monitor` – monitors activity of specific wallets.
* :mod:`onchain_event_registry` – simple registry of on‑chain events.
"""

from .whale_detector import WhaleDetector  # noqa: F401
from .exchange_flow_tracker import ExchangeFlowTracker  # noqa: F401
from .stablecoin_tracker import StablecoinTracker  # noqa: F401
from .wallet_monitor import WalletMonitor  # noqa: F401
from .onchain_event_registry import OnChainEventRegistry  # noqa: F401

__all__ = [
    "WhaleDetector",
    "ExchangeFlowTracker",
    "StablecoinTracker",
    "WalletMonitor",
    "OnChainEventRegistry",
]