"""Wallet activity monitor for on‑chain intelligence (Missão 28).

This module provides a simple monitor for a set of wallets of interest.
It records transactions involving watched wallets and returns those
events for further analysis.  The monitor does not persist state
between calls; it is intended to be used by higher‑level services
which manage their own storage or caches.

Each transaction is a dictionary containing at least ``sender``,
``receiver``, ``symbol`` and ``amount``.  The monitor returns a mapping
from wallet address to a list of transactions where the wallet was
either the sender or the receiver.

Example
-------

>>> monitor = WalletMonitor(["0xWhale", "0xFriend"])
>>> events = monitor.update([
...     {"sender": "0xWhale", "receiver": "0xMarket", "amount": 1000, "symbol": "ETH"},
...     {"sender": "0xOther", "receiver": "0xFriend", "amount": 50, "symbol": "USDT"},
... ])
>>> len(events["0xWhale"])
1
>>> len(events["0xFriend"])
1
"""

from __future__ import annotations

from typing import Dict, Iterable, List


class WalletMonitor:
    """Monitor activity of specific wallet addresses."""

    def __init__(self, watchlist: Iterable[str]) -> None:
        # normalise addresses to lowercase for comparison
        self.watchlist = {addr.lower() for addr in watchlist}

    def update(self, transactions: Iterable[Dict[str, str | float]]) -> Dict[str, List[Dict[str, str | float]]]:
        """Return events involving watched wallets.

        Parameters
        ----------
        transactions : iterable of dict
            Transaction records with keys ``sender``, ``receiver``, ``amount`` and ``symbol``.

        Returns
        -------
        dict
            Mapping from watched wallet address (original case
            preserved) to a list of transaction dicts where the
            wallet was the sender or receiver.
        """
        events: Dict[str, List[Dict[str, str | float]]] = {}
        for tx in transactions:
            sender = str(tx.get("sender", ""))
            receiver = str(tx.get("receiver", ""))
            sender_lower = sender.lower()
            receiver_lower = receiver.lower()
            # check if transaction involves a watched wallet
            if sender_lower in self.watchlist:
                events.setdefault(sender, []).append(tx)
            if receiver_lower in self.watchlist:
                events.setdefault(receiver, []).append(tx)
        return events