"""Whale detector for on‑chain intelligence (Missão 28).

This module implements a simple detector that identifies "whale"
transactions – transfers whose value exceeds a configurable threshold.
It is designed to run in read‑only mode on pre‑processed on‑chain
transaction data.  Each transaction is expected to be represented as a
dictionary with at least the keys ``sender``, ``receiver`` and
``amount`` (denominated in the asset's native unit or USD).  The
detector returns a list of dicts summarising the whale transactions
detected.

The detection logic is intentionally conservative: no classification of
entities (e.g., exchange vs. private wallet) is performed here.  Such
enrichment could be added in future missions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Dict


@dataclass
class WhaleTransaction:
    """Data structure representing a detected whale transaction."""

    sender: str
    receiver: str
    amount: float


class WhaleDetector:
    """Detector for large on‑chain transactions.

    Parameters
    ----------
    threshold : float, optional
        Minimum amount to consider a transaction as a whale transaction.  The
        default of ``100_000.0`` represents 100 000 units of the asset (or
        USD if transactions are denominated in dollars).
    """

    def __init__(self, threshold: float = 100_000.0) -> None:
        self.threshold = float(threshold)

    def detect(self, transactions: Iterable[Dict[str, float | str]]) -> List[WhaleTransaction]:
        """Return a list of whale transactions.

        Parameters
        ----------
        transactions : iterable of dict
            An iterable of transaction dictionaries.  Each dict should
            contain the keys ``sender``, ``receiver`` and ``amount``.

        Returns
        -------
        list of WhaleTransaction
            A list of detected whale transactions ordered as they appear
            in the input.
        """
        whales: List[WhaleTransaction] = []
        for tx in transactions:
            try:
                amount = float(tx.get("amount", 0))
                if amount >= self.threshold:
                    whales.append(WhaleTransaction(
                        sender=str(tx.get("sender")),
                        receiver=str(tx.get("receiver")),
                        amount=amount,
                    ))
            except (ValueError, TypeError):
                # If the amount cannot be converted to float, skip this transaction
                continue
        return whales