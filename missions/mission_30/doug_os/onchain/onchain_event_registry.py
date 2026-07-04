"""On‑chain event registry (Missão 28).

The on‑chain event registry provides a simple mechanism for recording
and retrieving noteworthy on‑chain events.  Events are represented as
dictionaries with at minimum ``type`` (e.g., "whale_transfer",
"exchange_flow"), ``details`` (arbitrary string) and ``timestamp``.
For simplicity, the registry stores events in memory; persistence
could be added in future missions by writing to disk or a database.

This registry is intentionally minimal and does not perform any
detection itself – it is a passive log accessed by other components.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List


class OnChainEventRegistry:
    """A simple in‑memory registry of on‑chain events."""

    def __init__(self) -> None:
        # store events in a list of dicts
        self._events: List[Dict[str, str]] = []

    def register_event(self, event_type: str, details: str, timestamp: str | None = None) -> None:
        """Record a new event in the registry.

        Parameters
        ----------
        event_type : str
            A short identifier describing the type of event (e.g., ``"whale_transfer"``).
        details : str
            A human‑readable description of the event.
        timestamp : str, optional
            ISO 8601 timestamp of when the event occurred.  If omitted,
            the current UTC time is used.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        self._events.append({
            "type": event_type,
            "details": details,
            "timestamp": timestamp,
        })

    def get_events(self) -> List[Dict[str, str]]:
        """Return a copy of all recorded events in insertion order."""
        # Return a shallow copy to prevent external mutation
        return list(self._events)