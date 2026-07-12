"""Exchange flow tracker for on‑chain intelligence (Missão 28).

This module provides a basic tracker for net flows into and out of
exchanges.  Given a sequence of on‑chain transactions, the tracker
computes the net amount of assets moving *into* exchanges (inflow
positive) and *out of* exchanges (outflow negative) per asset symbol.

The tracker requires a mapping of known exchange addresses.  In real
deployments this could be a comprehensive list of addresses belonging
to centralised exchanges.  For testing and demonstration purposes a
small set of addresses can be supplied when instantiating the tracker.

Transactions should be dictionaries with the fields ``sender``,
``receiver``, ``amount`` and ``symbol``.
"""

from __future__ import annotations

from typing import Dict, Iterable, List


class ExchangeFlowTracker:
    """Track net flows of assets into and out of exchanges.

    Parameters
    ----------
    exchanges : iterable of str
        A collection of known exchange addresses.  Addresses are
        case‑insensitive.
    """

    def __init__(self, exchanges: Iterable[str]) -> None:
        # normalise exchange addresses to lower case for comparison
        self.exchanges = {addr.lower() for addr in exchanges}

    def track(self, transactions: Iterable[Dict[str, str | float]]) -> Dict[str, float]:
        """Compute net flows per asset symbol.

        For each transaction, determine if it represents an inflow
        (sender not an exchange but receiver is) or an outflow (sender is
        exchange, receiver is not).  Unknown directions (both sender
        and receiver exchange or both non‑exchange) are ignored.

        Parameters
        ----------
        transactions : iterable of dict
            Each transaction must include ``sender``, ``receiver``,
            ``amount`` and ``symbol`` (asset symbol).

        Returns
        -------
        dict
            Mapping from symbol to net flow amount.  Positive values
            indicate net inflow into exchanges; negative values
            indicate net outflow.
        """
        net_flows: Dict[str, float] = {}
        for tx in transactions:
            sender = str(tx.get("sender", "")).lower()
            receiver = str(tx.get("receiver", "")).lower()
            amount = float(tx.get("amount", 0))
            symbol = str(tx.get("symbol", "")).upper()
            if not symbol:
                continue
            # Determine direction
            sender_is_exchange = sender in self.exchanges
            receiver_is_exchange = receiver in self.exchanges
            if sender_is_exchange and not receiver_is_exchange:
                # Outflow from exchange
                net_flows[symbol] = net_flows.get(symbol, 0.0) - amount
            elif receiver_is_exchange and not sender_is_exchange:
                # Inflow into exchange
                net_flows[symbol] = net_flows.get(symbol, 0.0) + amount
            else:
                # Ignore transactions where both parties are or are not exchanges
                continue
        return net_flows