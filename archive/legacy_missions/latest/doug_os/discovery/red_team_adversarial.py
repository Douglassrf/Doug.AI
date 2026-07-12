"""Mission 334 — Red Team Adversarial: questiona toda decisão BUY antes de executar."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AdversarialCase:
    """Caso histórico em que BUY resultou em LOSS para o mesmo regime."""
    id: str = field(default_factory=lambda: f"ac_{uuid.uuid4().hex[:12]}")
    regime: str = ""
    action: str = "BUY"
    outcome: str = "LOSS"
    loss_pct: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "regime": self.regime,
            "action": self.action,
            "outcome": self.outcome,
            "loss_pct": self.loss_pct,
            "context": self.context,
            "recorded_at": self.recorded_at.isoformat(),
        }


@dataclass
class AdversarialVerdict:
    """Resultado do Red Team para uma decisão BUY candidata."""
    id: str = field(default_factory=lambda: f"rv_{uuid.uuid4().hex[:12]}")
    topic: str = ""
    original_action: str = "BUY"
    original_confidence: float = 0.0
    adversarial_score: float = 0.0          # 0 = inofensivo, 1 = bloquear
    historical_loss_score: float = 0.0      # 40% do adversarial
    logical_argument_score: float = 0.0     # 30% do adversarial
    shadow_divergence_score: float = 0.0    # 30% do adversarial
    verdict: str = "PASS"                   # PASS | REDUCE | BLOCK
    block_reason: str = ""
    arguments: List[str] = field(default_factory=list)
    historical_cases: List[Dict[str, Any]] = field(default_factory=list)
    size_multiplier: float = 1.0            # 1.0 = normal, 0.5 = reduz 50%
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "original_action": self.original_action,
            "original_confidence": self.original_confidence,
            "adversarial_score": self.adversarial_score,
            "historical_loss_score": self.historical_loss_score,
            "logical_argument_score": self.logical_argument_score,
            "shadow_divergence_score": self.shadow_divergence_score,
            "verdict": self.verdict,
            "block_reason": self.block_reason,
            "arguments": self.arguments,
            "historical_cases": self.historical_cases,
            "size_multiplier": self.size_multiplier,
            "created_at": self.created_at.isoformat(),
        }


class RedTeamAdversarial:
    """
    Guardião constitucional pós-Council: monta o melhor caso contrário
    para qualquer decisão BUY com confiança > threshold.

    adversarial_score = historical (40%) + logical (30%) + shadow_divergence (30%)
    - PASS   (score < 0.40): segue normal
    - REDUCE (0.40 ≤ score < 0.70): reduz tamanho 50%
    - BLOCK  (score ≥ 0.70): bloqueia + registra motivo no audit log
    """

    BLOCK_THRESHOLD = 0.70
    REDUCE_THRESHOLD = 0.40

    def __init__(
        self,
        activation_confidence: float = 0.60,
        block_threshold: float = 0.70,
        reduce_threshold: float = 0.40,
        seed: int = 42,
    ) -> None:
        self._activation_confidence = activation_confidence
        self._block_threshold = block_threshold
        self._reduce_threshold = reduce_threshold
        self._experience_store: List[AdversarialCase] = []
        self._verdicts: List[AdversarialVerdict] = []
        self._audit_log: List[Dict[str, Any]] = []
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ #
    #  Experience Store                                                    #
    # ------------------------------------------------------------------ #

    def add_case(
        self,
        regime: str,
        action: str,
        outcome: str,
        loss_pct: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdversarialCase:
        case = AdversarialCase(
            regime=regime,
            action=action,
            outcome=outcome,
            loss_pct=loss_pct,
            context=context or {},
        )
        self._experience_store.append(case)
        return case

    def _search_historical(self, regime: str, action: str) -> List[AdversarialCase]:
        return [
            c for c in self._experience_store
            if c.regime == regime and c.action == action and c.outcome == "LOSS"
        ]

    # ------------------------------------------------------------------ #
    #  Scoring                                                             #
    # ------------------------------------------------------------------ #

    def _historical_loss_score(self, regime: str, action: str) -> tuple[float, List[AdversarialCase]]:
        cases = self._search_historical(regime, action)
        if not cases:
            return 0.0, []
        avg_loss = np.mean([c.loss_pct for c in cases])
        # normalisa: loss de 10% → score 1.0
        score = min(1.0, avg_loss / 10.0)
        return float(score), cases

    def _logical_argument_score(
        self, market_data: Dict[str, Any], action: str
    ) -> tuple[float, List[str]]:
        """Gera argumentos lógicos contra o BUY baseados nos dados de mercado."""
        arguments: List[str] = []
        score = 0.0

        volatility = market_data.get("volatility", 0.0)
        momentum = market_data.get("momentum", 0.0)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        spread = market_data.get("spread", 0.0)
        rsi = market_data.get("rsi", 50.0)

        if volatility > 0.03:
            arguments.append(f"Volatilidade elevada ({volatility:.3f}) aumenta risco de gap adverso")
            score += 0.25

        if rsi > 70:
            arguments.append(f"RSI sobrecomprado ({rsi:.1f}) — risco de reversão iminente")
            score += 0.30

        if volume_ratio < 0.7:
            arguments.append(f"Volume abaixo da média ({volume_ratio:.2f}x) — falta de convicção")
            score += 0.20

        if spread > 0.002:
            arguments.append(f"Spread elevado ({spread:.4f}) — custo de entrada deteriora R:R")
            score += 0.15

        if momentum < 0 and action == "BUY":
            arguments.append("Momentum negativo contradiz diretamente o sinal de BUY")
            score += 0.35

        return min(1.0, score), arguments

    def _shadow_divergence_score(
        self, council_confidence: float, market_data: Dict[str, Any]
    ) -> float:
        """Mede divergência entre confiança do council e qualidade dos dados."""
        data_quality = market_data.get("data_quality", 1.0)
        regime_stability = market_data.get("regime_stability", 1.0)
        # alta confiança + dados ruins = alta divergência
        divergence = council_confidence * (1.0 - data_quality * regime_stability)
        return float(min(1.0, divergence))

    # ------------------------------------------------------------------ #
    #  Main evaluate                                                       #
    # ------------------------------------------------------------------ #

    def evaluate(
        self,
        topic: str,
        action: str,
        confidence: float,
        regime: str,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> AdversarialVerdict:
        """
        Avalia se um BUY deve ser bloqueado, reduzido ou aprovado.
        Só é ativado se action == 'BUY' e confidence >= activation_confidence.
        """
        md = market_data or {}

        # Red Team só atua em BUY com confiança suficiente
        if action != "BUY" or confidence < self._activation_confidence:
            verdict = AdversarialVerdict(
                topic=topic,
                original_action=action,
                original_confidence=confidence,
                adversarial_score=0.0,
                verdict="PASS",
                block_reason="Red Team inativo (ação não-BUY ou confiança baixa)",
                size_multiplier=1.0,
            )
            self._verdicts.append(verdict)
            return verdict

        hist_score, hist_cases = self._historical_loss_score(regime, action)
        logic_score, arguments = self._logical_argument_score(md, action)
        shadow_score = self._shadow_divergence_score(confidence, md)

        adv_score = (
            hist_score * 0.40
            + logic_score * 0.30
            + shadow_score * 0.30
        )

        # Determina veredito
        if adv_score >= self._block_threshold:
            verdict_str = "BLOCK"
            block_reason = f"adversarial_score={adv_score:.3f} ≥ {self._block_threshold} — BUY bloqueado"
            size_mult = 0.0
        elif adv_score >= self._reduce_threshold:
            verdict_str = "REDUCE"
            block_reason = f"adversarial_score={adv_score:.3f} — tamanho reduzido 50%"
            size_mult = 0.5
        else:
            verdict_str = "PASS"
            block_reason = ""
            size_mult = 1.0

        v = AdversarialVerdict(
            topic=topic,
            original_action=action,
            original_confidence=confidence,
            adversarial_score=adv_score,
            historical_loss_score=hist_score,
            logical_argument_score=logic_score,
            shadow_divergence_score=shadow_score,
            verdict=verdict_str,
            block_reason=block_reason,
            arguments=arguments,
            historical_cases=[c.to_dict() for c in hist_cases],
            size_multiplier=size_mult,
        )
        self._verdicts.append(v)

        # Audit log
        if verdict_str in ("BLOCK", "REDUCE"):
            self._audit_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "topic": topic,
                "verdict": verdict_str,
                "adversarial_score": round(adv_score, 4),
                "block_reason": block_reason,
                "arguments": arguments,
                "council_confidence": confidence,
                "regime": regime,
            })

        return v

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]

    def replay_last_vetoes(self, n: int = 10) -> List[Dict[str, Any]]:
        """Quais vetos acertamos ao bloquear? (para revisão pós-mercado)"""
        return [v.to_dict() for v in self._verdicts if v.verdict == "BLOCK"][-n:]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._verdicts)
        if total == 0:
            return {"total": 0, "pass": 0, "reduce": 0, "block": 0, "block_rate": 0.0}
        blocks = sum(1 for v in self._verdicts if v.verdict == "BLOCK")
        reduces = sum(1 for v in self._verdicts if v.verdict == "REDUCE")
        passes = total - blocks - reduces
        return {
            "total": total,
            "pass": passes,
            "reduce": reduces,
            "block": blocks,
            "block_rate": round(blocks / total, 4),
            "experience_store_size": len(self._experience_store),
        }
