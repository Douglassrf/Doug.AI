"""Macro Economic Servo (Missão 34).

Este servo interpreta indicadores macroeconômicos e traduz as
condições macro em um sinal de trading.  Ele observa valores como
taxas de juros, inflação, criação de empregos (payroll), índices de
preços (CPI), e decisões dos bancos centrais (FOMC/BCE).  Com base
nesses indicadores e em limiares configuráveis, o servo emite
sinais de compra, venda ou manutenção (BUY/SELL/HOLD).

A lógica de decisão utiliza duas variáveis principais – inflação e
taxa de juros – como proxies para restrição monetária.  Se
inflacion ou juros estiverem muito altos, assume‑se um ambiente
restritivo que favorece uma postura defensiva (SELL).  Se ambos
estiverem baixos, favorece‑se uma postura pró‑ativa (BUY).  Valores
intermediários resultam em HOLD.

Indicadores adicionais (payroll, CPI, decisões de FOMC e BCE) são
incorporados no cálculo de risco e confiança: surpresas positivas em
payroll/CPI reduzem o risco, enquanto decisões hawkish/hard tendem a
aumentá‑lo.
"""

from __future__ import annotations

from typing import Mapping, Any

from doug_os.core.intent_vector import IntentVector
from doug_os.config import SERVO_THRESHOLDS, DEFAULT_SYMBOL


class MacroEconomicServo:
    """Servo de interpretação macroeconômica."""

    name: str = "macro_economic"

    async def analyze(self, macro_data: Mapping[str, Any]) -> IntentVector:
        """Analisa indicadores macroeconômicos e retorna um IntentVector.

        Parameters
        ----------
        macro_data : mapping
            Dicionário contendo indicadores macroeconômicos.  Os campos
            esperados incluem:

            - ``interest_rate``: taxa básica de juros (percentual).
            - ``inflation_rate``: inflação acumulada anual (percentual).
            - ``payroll_change``: variação no payroll ou emprego (pode ser
              positiva ou negativa).
            - ``cpi_change``: variação do índice de preços ao consumidor.
            - ``fomc``: string indicando a decisão do FOMC ("hawkish",
              "dovish" ou "neutral").
            - ``bce``: string indicando a decisão do BCE ("hawkish",
              "dovish" ou "neutral").

            Campos ausentes são tratados como neutros.

        Returns
        -------
        IntentVector
            Vector contendo a direcção sugerida e métricas derivadas dos
            indicadores.
        """
        # Extrair indicadores com valores padrão neutros
        try:
            interest_rate = float(macro_data.get("interest_rate", 0.0))
        except (TypeError, ValueError):
            interest_rate = 0.0
        try:
            inflation_rate = float(macro_data.get("inflation_rate", 0.0))
        except (TypeError, ValueError):
            inflation_rate = 0.0
        try:
            payroll_change = float(macro_data.get("payroll_change", 0.0))
        except (TypeError, ValueError):
            payroll_change = 0.0
        try:
            cpi_change = float(macro_data.get("cpi_change", 0.0))
        except (TypeError, ValueError):
            cpi_change = 0.0
        fomc = str(macro_data.get("fomc", "neutral")).lower()
        bce = str(macro_data.get("bce", "neutral")).lower()

        cfg = SERVO_THRESHOLDS.get(self.name, {})
        inf_high = float(cfg.get("inflation_high", 5.0))
        inf_low = float(cfg.get("inflation_low", 2.0))
        int_high = float(cfg.get("interest_high", 5.0))
        int_low = float(cfg.get("interest_low", 2.0))

        # Direção baseada em inflação e juros
        if inflation_rate >= inf_high or interest_rate >= int_high:
            direction = "SELL"
        elif inflation_rate <= inf_low and interest_rate <= int_low:
            direction = "BUY"
        else:
            direction = "HOLD"

        # Calcular risco: maior inflação/juros aumentam risco; payroll positivo reduz
        base_risk = (inflation_rate + interest_rate) * 5.0  # escala 0–100
        # ajuste por payroll (positivos reduzem risco)
        risk = base_risk - payroll_change
        # Ajuste por decisões hawkish/dovish
        if fomc == "hawkish":
            risk += 10.0
        elif fomc == "dovish":
            risk -= 10.0
        if bce == "hawkish":
            risk += 10.0
        elif bce == "dovish":
            risk -= 10.0
        # Limitar risco entre 0 e 100
        risk = max(0.0, min(100.0, risk))

        # Confiança é inversamente proporcional ao risco e ajustada por
        # magnitude de payroll positivo/negativo e pelo sinal de CPI.
        confidence = max(0.0, min(100.0, 100.0 - risk + payroll_change - abs(cpi_change) * 2.0))

        # Evidência: magnitude absoluta das variações de payroll e CPI
        evidence_strength = min(100.0, abs(payroll_change) * 5.0 + abs(cpi_change) * 5.0)

        # Risco de manipulação é baixo para macro (assumimos 20)
        manipulation_risk = 20.0

        # Entropia: magnitude da diferença entre inflação e juros; maior
        # divergência implica mais incerteza
        entropy_score = abs(inflation_rate - interest_rate) * 5.0

        # Reality score: média de sinal de política (hawkish = 40, dovish = 60, neutral = 50)
        def policy_score(decision: str) -> float:
            if decision == "hawkish":
                return 40.0
            if decision == "dovish":
                return 60.0
            return 50.0
        reality_score = (policy_score(fomc) + policy_score(bce)) / 2.0

        # Oportunidade segue a confiança
        opportunity_score = confidence

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
            reasons=("macro_indicators", "policy_decisions"),
        )
