"""Liquidity Risk Engine (Missão 32).

Este módulo define um motor para avaliar o risco de liquidez de um ativo
com base em métricas simples de profundidade de livro de ofertas
(``order_book_depth``) e volume de negociação diário (``daily_volume``).
O objetivo é identificar três níveis de risco de liquidez – **vacuum**,
**stress** e **collapse** – e ajustar uma confiança associada ao ativo.

As métricas de profundidade e volume são normalizadas em relação a
valores ideais e transformadas em uma pontuação de risco entre 0 e 1.
Valores mais altos indicam menor liquidez (maior risco).

O motor opera em modo somente leitura; não envia ordens nem interage
com mercados reais.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Dict


@dataclass
class LiquidityRiskEngine:
    """Avalia o risco de liquidez de um ativo.

    Parameters
    ----------
    ideal_depth : float, optional
        Profundidade de livro considerada saudável (padrão 1.0).  Valores
        reais de ``order_book_depth`` são divididos por este valor para
        calcular a pontuação de risco.
    ideal_volume : float, optional
        Volume diário considerado saudável (padrão 1.0).  Valores reais
        de ``daily_volume`` são divididos por este valor para calcular
        a pontuação de risco.
    vacuum_threshold : float, optional
        Limite mínimo para categorizar risco como ``vacuum`` (padrão 0.3).
    stress_threshold : float, optional
        Limite mínimo para categorizar risco como ``stress`` (padrão 0.5).
    collapse_threshold : float, optional
        Limite mínimo para categorizar risco como ``collapse`` (padrão 0.8).
    """

    ideal_depth: float = 1.0
    ideal_volume: float = 1.0
    vacuum_threshold: float = 0.3
    stress_threshold: float = 0.5
    collapse_threshold: float = 0.8

    def evaluate(self, event: Mapping[str, float | int]) -> Dict[str, float | str]:
        """Calcular risco de liquidez e categoria.

        Parameters
        ----------
        event : dict
            Dicionário contendo ``order_book_depth`` e ``daily_volume``.

        Returns
        -------
        dict
            Dicionário com as chaves ``liquidity_risk`` (pontuação de 0 a 1),
            ``category`` ("collapse", "stress", "vacuum" ou "normal") e
            ``confidence_adjustment`` (valor de 0 a 1, onde menor
            indica redução de confiança).
        """
        depth = float(event.get("order_book_depth", 0) or 0)
        volume = float(event.get("daily_volume", 0) or 0)
        # Normalizar para [0,1]: 1 - depth/ideal, mas não abaixo de 0
        depth_risk = 1.0 - min(max(depth / self.ideal_depth, 0.0), 1.0)
        volume_risk = 1.0 - min(max(volume / self.ideal_volume, 0.0), 1.0)
        # Risco final é o maior dos dois
        liquidity_risk = max(depth_risk, volume_risk)
        # Categorizar
        if liquidity_risk >= self.collapse_threshold:
            category = "collapse"
        elif liquidity_risk >= self.stress_threshold:
            category = "stress"
        elif liquidity_risk >= self.vacuum_threshold:
            category = "vacuum"
        else:
            category = "normal"
        # Ajuste de confiança: quanto maior o risco, menor a confiança
        confidence_adjustment = round(max(0.0, 1.0 - liquidity_risk), 2)
        return {
            "liquidity_risk": round(liquidity_risk, 2),
            "category": category,
            "confidence_adjustment": confidence_adjustment,
        }