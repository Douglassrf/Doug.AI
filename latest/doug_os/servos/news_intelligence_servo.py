"""News Intelligence Servo (Missão 33).

Este módulo implementa um servo especializado em notícias de mercado.
Ele recebe uma lista de itens de notícia, cada um contendo um
``sentiment_score`` (0–100), um ``impact_score`` (0–100) e uma
``source_confidence`` (0–100).  O servo calcula estatísticas
agregadas e gera um :class:`~doug_os.core.intent_vector.IntentVector`
representando a direcção sugerida (BUY, SELL ou HOLD) juntamente
com métricas de confiança, risco, força de evidência, risco de
manipulação e outras pontuações.  A intenção é traduzir o fluxo
noticioso num sinal quantitativo para o DougBrain.

Caso nenhuma notícia seja fornecida, o servo devolve um vector neutro
indicando que não há evidência suficiente para agir.

As sensibilidades de compra e venda podem ser ajustadas via
``SERVO_THRESHOLDS['news_intelligence']`` em
``doug_os.config``.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Any

from doug_os.core.intent_vector import IntentVector
from doug_os.config import SERVO_THRESHOLDS, DEFAULT_SYMBOL


class NewsIntelligenceServo:
    """Servo de inteligência de notícias.

    Este servo sintetiza um conjunto de itens noticiosos num sinal
    quantitativo.  Cada item de notícia é esperado como um mapeamento
    contendo, pelo menos, as chaves:

    - ``sentiment_score``: sentimento da notícia em percentagem (0–100).
    - ``impact_score``: impacto esperado da notícia (0–100).
    - ``source_confidence``: confiança na fonte (0–100).

    Se um campo estiver ausente ou não for numérico, um valor
    intermediário de 50 é utilizado.  As médias são utilizadas para
    derivar direcção, confiança e risco.
    """

    name: str = "news_intelligence"

    async def analyze(self, news_items: Iterable[Mapping[str, Any]]) -> IntentVector:
        """Analisa uma lista de notícias e devolve um IntentVector.

        Parameters
        ----------
        news_items : iterable of mappings
            Colecção de notícias.  Cada item deve conter as chaves
            ``sentiment_score``, ``impact_score`` e ``source_confidence``.

        Returns
        -------
        IntentVector
            Vector que resume o sentimento e impacto das notícias.
        """
        news_list = list(news_items)
        # Se não houver notícias, retornar vector neutro
        if not news_list:
            return IntentVector(
                servo=self.name,
                symbol=DEFAULT_SYMBOL,
                direction="HOLD",
                confidence=0.0,
                risk=50.0,
                evidence_strength=0.0,
                manipulation_risk=0.0,
                entropy_score=50.0,
                reality_score=50.0,
                opportunity_score=0.0,
                reasons=("no_news",),
            )

        total_sentiment = 0.0
        total_impact = 0.0
        total_confidence = 0.0
        count = 0
        for item in news_list:
            try:
                total_sentiment += float(item.get("sentiment_score", 50.0))
            except (TypeError, ValueError):
                total_sentiment += 50.0
            try:
                total_impact += float(item.get("impact_score", 50.0))
            except (TypeError, ValueError):
                total_impact += 50.0
            try:
                total_confidence += float(item.get("source_confidence", 50.0))
            except (TypeError, ValueError):
                total_confidence += 50.0
            count += 1

        avg_sentiment = total_sentiment / count
        avg_impact = total_impact / count
        avg_confidence = total_confidence / count

        # Obter limiares a partir da configuração
        cfg = SERVO_THRESHOLDS.get(self.name, {})
        buy_threshold = float(cfg.get("sentiment_buy_threshold", 60.0))
        sell_threshold = float(cfg.get("sentiment_sell_threshold", 40.0))

        if avg_sentiment >= buy_threshold:
            direction = "BUY"
        elif avg_sentiment <= sell_threshold:
            direction = "SELL"
        else:
            direction = "HOLD"

        # A confiança baseia‑se no sentimento médio; risco é inversamente
        # proporcional ao sentimento e impacto; risco de manipulação é
        # inversamente proporcional à confiança na fonte.
        confidence = avg_sentiment
        # Risco decresce com sentimento e impacto; quanto maior o
        # sentimento, menor o risco.
        risk = 100.0 - (avg_sentiment * 0.6 + avg_impact * 0.4)
        # Evidência é determinada pelo impacto médio
        evidence_strength = avg_impact
        # Quanto maior a confiança na fonte, menor o risco de manipulação
        manipulation_risk = 100.0 - avg_confidence
        # A entropia do sinal pode ser o desvio à volta de 50
        entropy_score = abs(avg_sentiment - 50.0)
        # Reality score mede credibilidade da fonte
        reality_score = avg_confidence
        # Oportunidade segue o sentimento
        opportunity_score = avg_sentiment

        return IntentVector(
            servo=self.name,
            symbol=DEFAULT_SYMBOL,
            direction=direction,
            confidence=confidence,
            risk=risk,
            evidence_strength=evidence_strength,
            manipulation_risk=manipulation_risk,
            entropy_score=entropy_score,
            reality_score=reality_score,
            opportunity_score=opportunity_score,
            reasons=("sentiment_analysis", "impact_analysis", "source_confidence"),
        )
