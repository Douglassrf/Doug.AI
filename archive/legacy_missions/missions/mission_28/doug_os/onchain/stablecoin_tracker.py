"""Stablecoin flow intelligence (Missão 30 preliminar).

Although full stablecoin flow intelligence is part of Missão 30, this
module implements a basic tracker for stablecoin movements.  It
monitors specified stablecoins and distinguishes between deposits and
withdrawals relative to exchanges.

Transactions are represented as dictionaries with ``symbol``, ``sender``,
``receiver`` and ``amount``.  The tracker requires a list of stablecoin
symbols and a list of known exchange addresses.

Usage
-----

>>> tracker = StablecoinTracker(stablecoins=["USDT", "USDC"], exchanges=["0xEx1", "0xEx2"])
>>> flows = tracker.track_flows([
...     {"symbol": "USDT", "sender": "0xAlice", "receiver": "0xEx1", "amount": 1000},
...     {"symbol": "USDC", "sender": "0xEx2", "receiver": "0xBob", "amount": 500},
... ])
>>> flows["USDT"]["deposit"]
1000.0
>>> flows["USDC"]["withdrawal"]
500.0
"""

from __future__ import annotations

from typing import Dict, Iterable, List


class StablecoinTracker:
    """Track deposit and withdrawal flows of stablecoins relative to exchanges."""

    def __init__(self, stablecoins: Iterable[str], exchanges: Iterable[str]) -> None:
        # normalise symbols and addresses
        self.stablecoins = {s.upper() for s in stablecoins}
        self.exchanges = {addr.lower() for addr in exchanges}

    def track_flows(self, transactions: Iterable[Dict[str, str | float]]) -> Dict[str, Dict[str, float]]:
        """Compute deposit and withdrawal amounts for each stablecoin.

        Parameters
        ----------
        transactions : iterable of dict
            Each transaction should include ``symbol``, ``sender``, ``receiver`` and ``amount``.

        Returns
        -------
        dict
            A nested mapping ``{symbol: {"deposit": total_in, "withdrawal": total_out}}``.
        """
        flows: Dict[str, Dict[str, float]] = {}
        for tx in transactions:
            symbol = str(tx.get("symbol", "")).upper()
            if symbol not in self.stablecoins:
                continue
            sender = str(tx.get("sender", "")).lower()
            receiver = str(tx.get("receiver", "")).lower()
            amount = float(tx.get("amount", 0))
            # Determine if deposit or withdrawal relative to exchanges
            is_sender_exchange = sender in self.exchanges
            is_receiver_exchange = receiver in self.exchanges
            if is_receiver_exchange and not is_sender_exchange:
                # deposit: user sending to exchange
                flows.setdefault(symbol, {"deposit": 0.0, "withdrawal": 0.0})
                flows[symbol]["deposit"] += amount
            elif is_sender_exchange and not is_receiver_exchange:
                # withdrawal: exchange sending to user
                flows.setdefault(symbol, {"deposit": 0.0, "withdrawal": 0.0})
                flows[symbol]["withdrawal"] += amount
            # ignore internal movements (exchange <-> exchange, user <-> user)
        return flows