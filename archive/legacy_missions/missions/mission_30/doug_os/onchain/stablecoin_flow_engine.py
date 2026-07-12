"""Stablecoin Flow Intelligence Engine (Missão 30).

Este módulo expande o monitoramento de stablecoins introduzido pelo
`StablecoinTracker` na Missão 28.  O `StablecoinFlowEngine` mantém
contadores de depósitos e retiradas para cada stablecoin observada e
deriva métricas de fluxo e pressão de compra/venda.  A intenção é
identificar se uma moeda está experimentando uma pressão de compra
(depósitos superam retiradas), pressão de venda (retiradas superam
depósitos) ou fluxo neutro.

As transações devem ser representadas como dicionários com as chaves
``symbol`` (ticker da stablecoin), ``sender`` (endereço do remetente),
``receiver`` (endereço do destinatário) e ``amount`` (valor).  O
conjunto de endereços de exchanges deve ser fornecido para que o
engine possa determinar se uma transferência representa depósito (de
um usuário para uma exchange) ou retirada (de uma exchange para um
usuário).  Transfers entre exchanges ou entre usuários são ignoradas.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple


class StablecoinFlowEngine:
    """Engine that tracks stablecoin flows and infers market pressure.

    Parameters
    ----------
    stablecoins : iterable of str
        List of stablecoin tickers (e.g., ``["USDT", "USDC"]``) a serem monitorados.
    exchanges : iterable of str
        Lista de endereços conhecidos de exchanges; usada para determinar se uma
        transação representa depósito (usuário → exchange) ou retirada (exchange → usuário).
    pressure_threshold : float, optional
        Threshold between 0 and 1 used to classify pressão de compra ou venda.
        O valor representa a fração de volume de depósito em relação ao volume
        total (depósitos + retiradas).  Valores acima de ``pressure_threshold``
        indicam pressão de compra; valores abaixo de ``1 - pressure_threshold``
        indicam pressão de venda.  Entre esses limites, a pressão é neutra.
    """

    def __init__(self, stablecoins: Iterable[str], exchanges: Iterable[str], pressure_threshold: float = 0.55) -> None:
        self.stablecoins = {s.upper() for s in stablecoins}
        self.exchanges = {addr.lower() for addr in exchanges}
        self.pressure_threshold = float(pressure_threshold)
        # internal counters per coin: {symbol: {"deposit": float, "withdrawal": float}}
        self.flows: Dict[str, Dict[str, float]] = {s: {"deposit": 0.0, "withdrawal": 0.0} for s in self.stablecoins}

    def process_transactions(self, transactions: Iterable[Dict[str, str | float]]) -> None:
        """Update internal flow counters based on a list of transactions."""
        for tx in transactions:
            symbol = str(tx.get("symbol", "")).upper()
            if symbol not in self.stablecoins:
                continue
            sender = str(tx.get("sender", "")).lower()
            receiver = str(tx.get("receiver", "")).lower()
            try:
                amount = float(tx.get("amount", 0))
            except (TypeError, ValueError):
                continue
            if amount <= 0:
                continue
            sender_is_exch = sender in self.exchanges
            receiver_is_exch = receiver in self.exchanges
            # deposit: user → exchange
            if receiver_is_exch and not sender_is_exch:
                self.flows[symbol]["deposit"] += amount
            # withdrawal: exchange → user
            elif sender_is_exch and not receiver_is_exch:
                self.flows[symbol]["withdrawal"] += amount
            # ignore other cases

    def net_flows(self) -> Dict[str, float]:
        """Return net flows (deposit − withdrawal) per stablecoin."""
        return {symbol: v["deposit"] - v["withdrawal"] for symbol, v in self.flows.items()}

    def pressure(self) -> Dict[str, str]:
        """Classify pressure (buy/sell/neutral) per stablecoin.

        A pressão de compra ocorre quando a fração de depósitos (depósitos / (depósitos + retiradas))
        é maior ou igual ao ``pressure_threshold``.  A pressão de venda ocorre
        quando a fração de retiradas (retiradas / total) é maior ou igual ao mesmo
        threshold, i.e. depósitos / total <= 1 - threshold.  Caso contrário a
        pressão é considerada neutra.
        """
        pressure_map: Dict[str, str] = {}
        for symbol, v in self.flows.items():
            total = v["deposit"] + v["withdrawal"]
            if total == 0:
                pressure_map[symbol] = "neutral"
                continue
            deposit_ratio = v["deposit"] / total
            if deposit_ratio >= self.pressure_threshold:
                pressure_map[symbol] = "buy"
            elif deposit_ratio <= 1.0 - self.pressure_threshold:
                pressure_map[symbol] = "sell"
            else:
                pressure_map[symbol] = "neutral"
        return pressure_map

    def reset(self) -> None:
        """Reset internal counters, e.g., between analysis windows."""
        for symbol in self.flows:
            self.flows[symbol]["deposit"] = 0.0
            self.flows[symbol]["withdrawal"] = 0.0