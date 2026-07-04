"""Market Integrity V2 Engine (Missão 31).

Este módulo define um motor para avaliar a integridade do mercado,
focando em comportamentos de manipulação como **spoofing**, **armadilhas
de liquidez**, **falsos rompimentos** e **wash trading**.  O motor
recebe pontuações normalizadas (0 a 1) para cada tipo de manipulação
observado em um evento de mercado e calcula uma pontuação agregada.
Dependendo desta pontuação agregada, o evento é classificado como
**dangerous**, **warning** ou **ok**.  Valores altos indicam alta
probabilidade de manipulação e potencial risco de mercado.

Todos os cálculos são em modo leitura; o motor não interage com
exchanges nem envia ordens.  Ele destina‑se a complementar o
`ManipulationIntelligenceEngine` existente, oferecendo uma visão
simplificada de quatro padrões chave de manipulação para testes e
modelagem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping


@dataclass
class MarketIntegrityV2Engine:
    """Engine para avaliar a integridade do mercado com base em quatro
    pontuações de manipulação.

    Parameters
    ----------
    weights : Mapping[str, float], optional
        Dicionário com pesos atribuídos a cada tipo de manipulação.  As
        chaves esperadas são ``spoofing``, ``liquidity_trap``,
        ``fake_breakout`` e ``wash_trading``.  Se não fornecido, cada
        categoria recebe peso igual (0,25).
    threshold_high : float, optional
        Limite acima do qual a classificação será ``dangerous`` (padrão
        0,6).  A pontuação agregada é normalizada de 0 a 1.
    threshold_warning : float, optional
        Limite acima do qual a classificação será ``warning`` (padrão
        0,4).  Valores abaixo desse limite são classificados como ``ok``.
    """

    weights: Mapping[str, float] = field(default_factory=lambda: {
        "spoofing": 0.25,
        "liquidity_trap": 0.25,
        "fake_breakout": 0.25,
        "wash_trading": 0.25,
    })
    threshold_high: float = 0.6
    threshold_warning: float = 0.4

    def detect(self, event: Mapping[str, float | int]) -> Dict[str, object]:
        """Calcular a pontuação agregada e classificação.

        Parameters
        ----------
        event : Mapping[str, float | int]
            Dicionário contendo pontuações normalizadas (0 – 1) para cada
            tipo de manipulação.  As chaves esperadas são
            ``spoofing_score``, ``liquidity_trap_score``,
            ``fake_breakout_score`` e ``wash_trading_score``.  Valores
            ausentes ou inválidos são tratados como 0.

        Returns
        -------
        dict
            Dicionário com as chaves ``score`` (pontuação agregada de 0 a 100),
            ``classification`` ("dangerous", "warning" ou "ok") e
            ``details`` com as pontuações individuais.
        """
        # Extrair pontuações individuais, default 0
        spoofing = float(event.get("spoofing_score", 0) or 0)
        liquidity = float(event.get("liquidity_trap_score", 0) or 0)
        breakout = float(event.get("fake_breakout_score", 0) or 0)
        wash = float(event.get("wash_trading_score", 0) or 0)
        # Garantir limites [0,1]
        spoofing = min(max(spoofing, 0.0), 1.0)
        liquidity = min(max(liquidity, 0.0), 1.0)
        breakout = min(max(breakout, 0.0), 1.0)
        wash = min(max(wash, 0.0), 1.0)

        # Calcular pontuação ponderada
        total_weight = float(sum(self.weights.values())) or 1.0
        weighted_sum = (
            self.weights.get("spoofing", 0) * spoofing
            + self.weights.get("liquidity_trap", 0) * liquidity
            + self.weights.get("fake_breakout", 0) * breakout
            + self.weights.get("wash_trading", 0) * wash
        )
        # Normalizar para 0 a 1
        normalized = weighted_sum / total_weight
        score_pct = round(normalized * 100, 2)
        # Determinar classificação
        if normalized >= self.threshold_high:
            classification = "dangerous"
        elif normalized >= self.threshold_warning:
            classification = "warning"
        else:
            classification = "ok"
        return {
            "score": score_pct,
            "classification": classification,
            "details": {
                "spoofing": spoofing,
                "liquidity_trap": liquidity,
                "fake_breakout": breakout,
                "wash_trading": wash,
            },
        }