"""Whale Mirror Engine (Missão 29).

Este módulo implementa um motor que detecta padrões recorrentes de
movimentação de grandes carteiras (whales) e atribui um *score de
influência* a cada endereço observado.  O objetivo é quantificar o
impacto potencial de uma carteira com base na frequência e no volume
das transações de grande porte realizadas.

A lógica aqui é simplificada: o motor mantém estatísticas cumulativas
(contagem e volume total) para cada endereço que realiza transações
acima de um limiar (`whale_threshold`).  O score de influência é
calculado como o volume total normalizado pela soma de volumes de
todas as carteiras observadas.  Em futuras missões, este motor poderá
ser aprimorado com reconhecimento de padrões temporais, correlação com
movimentos de mercado e classificação de estratégias.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class WhaleStats:
    """Cumulative statistics for a single whale (address)."""

    count: int = 0
    volume: float = 0.0


class WhaleMirrorEngine:
    """Engine that tracks whale transactions and computes influence scores.

    Parameters
    ----------
    whale_threshold : float, optional
        Minimum amount for a transaction to be considered a whale transaction.
    """

    def __init__(self, whale_threshold: float = 100_000.0) -> None:
        self.whale_threshold = float(whale_threshold)
        # internal mapping from address → stats
        self._stats: Dict[str, WhaleStats] = {}

    def process_transactions(self, transactions: Iterable[Dict[str, str | float]]) -> None:
        """Update internal statistics with a list of transactions.

        Each transaction should be a dict containing `sender`, `receiver`
        and `amount`.  Only the sender address is considered for scoring.

        Parameters
        ----------
        transactions : iterable of dict
            The on‑chain transactions to process.
        """
        for tx in transactions:
            try:
                amount = float(tx.get("amount", 0))
            except (TypeError, ValueError):
                continue
            if amount < self.whale_threshold:
                continue
            sender = str(tx.get("sender", "")).lower()
            if not sender:
                continue
            stats = self._stats.setdefault(sender, WhaleStats())
            stats.count += 1
            stats.volume += amount

    def get_influence_scores(self) -> Dict[str, float]:
        """Return normalised influence scores for all observed whales.

        The influence score for an address is computed as its total
        volume divided by the total volume of all whales.  If no
        whales have been observed yet, an empty dict is returned.

        Returns
        -------
        dict
            Mapping from whale address (lowercase) to influence score
            between 0 and 1.
        """
        total_volume = sum(stats.volume for stats in self._stats.values())
        if total_volume == 0:
            return {}
        return {addr: stats.volume / total_volume for addr, stats in self._stats.items()}

    def get_top_whales(self, n: int = 5) -> List[Tuple[str, float]]:
        """Return the top `n` whales sorted by influence score.

        Parameters
        ----------
        n : int, optional
            Number of whales to return (default 5).

        Returns
        -------
        list of (address, score)
            A list of tuples ordered by descending influence score.
        """
        scores = self.get_influence_scores()
        # sort addresses by descending score
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:n]