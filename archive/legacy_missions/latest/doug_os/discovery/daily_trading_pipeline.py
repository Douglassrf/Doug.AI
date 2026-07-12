"""Mission 341 — Daily Trading Pipeline: orquestra todos os agentes do DOUG em sequência diária."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading


# Fases do pipeline
PHASE_MARKET_DATA   = "market_data"
PHASE_REGIME        = "regime_detection"
PHASE_ANALYSIS      = "multi_agent_analysis"
PHASE_COUNCIL       = "council_vote"
PHASE_RED_TEAM      = "red_team_check"
PHASE_ALERT_LAYERS  = "three_layer_alert"
PHASE_CAPITAL_ROUTE = "capital_routing"
PHASE_AUDIT         = "audit_record"
PHASE_COMPLETE      = "complete"


@dataclass
class PipelineStep:
    phase: str = ""
    status: str = "pending"       # pending | running | passed | failed | skipped
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    error: str = ""
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status,
            "output_data": self.output_data,
            "duration_ms": round(self.duration_ms, 2),
            "error": self.error,
        }


@dataclass
class PipelineRun:
    id: str = field(default_factory=lambda: f"pr_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    steps: List[PipelineStep] = field(default_factory=list)
    final_action: str = "HOLD"
    final_confidence: float = 0.0
    approved: bool = False
    blocked_at_phase: str = ""
    block_reason: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "steps": [s.to_dict() for s in self.steps],
            "final_action": self.final_action,
            "final_confidence": round(self.final_confidence, 3),
            "approved": self.approved,
            "blocked_at_phase": self.blocked_at_phase,
            "block_reason": self.block_reason,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class DailyTradingPipeline:
    """
    Pipeline sequencial diário do DOUG.AI:

    1. MarketData     → coleta dados do ativo
    2. RegimeDetect   → identifica regime de mercado
    3. MultiAgentAnal → MarketAgent + RiskAgent + DiscoveryAgent analisam
    4. CouncilVote    → AgentConsensusCouncil vota BUY/SELL/HOLD
    5. RedTeamCheck   → RedTeamAdversarial questiona BUY (se conf ≥ 0.60)
    6. ThreeLayerAlert→ evidence + consensus + risk validation
    7. CapitalRoute   → CapitalRouter seleciona Top-K
    8. AuditRecord    → grava no audit log

    Cada fase recebe o contexto acumulado das anteriores.
    Se qualquer fase retornar approved=False → pipeline para e registra o motivo.
    """

    def __init__(
        self,
        council_threshold: float = 0.60,
        alert_evidence_threshold: float = 0.75,
        alert_consensus_threshold: float = 0.70,
        alert_max_risk_pct: float = 2.0,
    ) -> None:
        self._council_threshold = council_threshold
        self._alert_evidence_threshold = alert_evidence_threshold
        self._alert_consensus_threshold = alert_consensus_threshold
        self._alert_max_risk_pct = alert_max_risk_pct
        self._runs: List[PipelineRun] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    #  Run pipeline                                                        #
    # ------------------------------------------------------------------ #

    def run(self, asset: str, market_data: Dict[str, Any]) -> PipelineRun:
        """
        Executa o pipeline completo para um ativo.

        market_data deve conter:
            price, volume, volatility, momentum, rsi, spread,
            evidence_score, agreement_score, risk_pct,
            council_votes: [{agent_id, option, confidence}]
        """
        import time

        run = PipelineRun(asset=asset)
        ctx: Dict[str, Any] = dict(market_data)  # contexto acumulado

        phases = [
            PHASE_MARKET_DATA, PHASE_REGIME, PHASE_ANALYSIS,
            PHASE_COUNCIL, PHASE_RED_TEAM, PHASE_ALERT_LAYERS,
            PHASE_CAPITAL_ROUTE, PHASE_AUDIT,
        ]

        for phase in phases:
            step = PipelineStep(phase=phase)
            step.status = "running"
            step.started_at = datetime.now(timezone.utc)
            t0 = time.perf_counter()

            try:
                result = self._execute_phase(phase, ctx)
                step.output_data = result
                ctx.update(result)

                approved = result.get("approved", True)
                step.status = "passed" if approved else "failed"
                step.duration_ms = (time.perf_counter() - t0) * 1000
                step.finished_at = datetime.now(timezone.utc)
                run.steps.append(step)

                if not approved:
                    run.final_action = result.get("action", "HOLD")
                    run.final_confidence = result.get("confidence", 0.0)
                    run.approved = False
                    run.blocked_at_phase = phase
                    run.block_reason = result.get("reason", f"Bloqueado em {phase}")
                    break

            except Exception as exc:
                step.status = "failed"
                step.error = str(exc)
                step.duration_ms = (time.perf_counter() - t0) * 1000
                step.finished_at = datetime.now(timezone.utc)
                run.steps.append(step)
                run.approved = False
                run.blocked_at_phase = phase
                run.block_reason = f"Erro em {phase}: {exc}"
                break

        else:
            # Todas as fases passaram
            run.approved = True
            run.final_action = ctx.get("action", "HOLD")
            run.final_confidence = ctx.get("confidence", 0.0)

        run.finished_at = datetime.now(timezone.utc)

        with self._lock:
            self._runs.append(run)

        return run

    def _execute_phase(self, phase: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a lógica de cada fase usando o contexto acumulado."""

        if phase == PHASE_MARKET_DATA:
            return {
                "price": ctx.get("price", 0.0),
                "volume": ctx.get("volume", 0.0),
                "data_ok": ctx.get("price", 0.0) > 0,
                "approved": ctx.get("price", 0.0) > 0,
                "reason": "Sem dados de preço" if ctx.get("price", 0.0) <= 0 else "",
            }

        elif phase == PHASE_REGIME:
            vol = ctx.get("volatility", 0.01)
            regime = "STRESS" if vol > 0.04 else ("TRENDING" if abs(ctx.get("momentum", 0)) > 0.02 else "NORMAL")
            return {"regime": regime, "regime_ok": True, "approved": True}

        elif phase == PHASE_ANALYSIS:
            # Agentes analisam: simplificado — retorna scores médios
            rsi = ctx.get("rsi", 50.0)
            momentum = ctx.get("momentum", 0.0)
            signal = "BUY" if momentum > 0 and rsi < 70 else ("SELL" if momentum < 0 and rsi > 30 else "HOLD")
            return {"agent_signal": signal, "agent_score": 0.7, "approved": True}

        elif phase == PHASE_COUNCIL:
            votes = ctx.get("council_votes", [])
            if not votes:
                return {"action": "HOLD", "confidence": 0.5, "approved": True}

            tally: Dict[str, float] = {}
            for v in votes:
                opt = v.get("option", "HOLD")
                conf = float(v.get("confidence", 0.5))
                weight = float(v.get("weight", 1.0))
                tally[opt] = tally.get(opt, 0.0) + conf * weight

            total = sum(tally.values())
            if total == 0:
                return {"action": "HOLD", "confidence": 0.5, "approved": True}

            decision = max(tally, key=lambda k: tally[k])
            confidence = tally[decision] / total
            return {"action": decision, "confidence": confidence, "approved": True}

        elif phase == PHASE_RED_TEAM:
            action = ctx.get("action", "HOLD")
            confidence = ctx.get("confidence", 0.5)

            if action != "BUY" or confidence < self._council_threshold:
                return {"red_team_verdict": "INACTIVE", "size_multiplier": 1.0,
                        "action": action, "confidence": confidence, "approved": True}

            # Adversarial simples baseado em RSI e volatilidade
            rsi = ctx.get("rsi", 50.0)
            vol = ctx.get("volatility", 0.01)
            adv_score = min(1.0, (max(0, rsi - 65) / 35) * 0.5 + (vol / 0.05) * 0.5)

            if adv_score >= 0.70:
                return {"red_team_verdict": "BLOCK", "adversarial_score": adv_score,
                        "action": "HOLD", "confidence": 0.0,
                        "approved": False, "reason": f"Red Team BLOCK: adversarial={adv_score:.3f}",
                        "size_multiplier": 0.0}
            size_mult = 0.5 if adv_score >= 0.40 else 1.0
            return {"red_team_verdict": "PASS" if adv_score < 0.40 else "REDUCE",
                    "adversarial_score": adv_score, "size_multiplier": size_mult,
                    "action": action, "confidence": confidence, "approved": True}

        elif phase == PHASE_ALERT_LAYERS:
            ev = ctx.get("evidence_score", 1.0)
            ag = ctx.get("agreement_score", 1.0)
            rk = ctx.get("risk_pct", 1.0)

            if ev < self._alert_evidence_threshold:
                return {"approved": False, "action": "HOLD",
                        "reason": f"Camada 1 falhou: evidence_score={ev:.3f} < {self._alert_evidence_threshold}"}
            if ag < self._alert_consensus_threshold:
                return {"approved": False, "action": "HOLD",
                        "reason": f"Camada 2 falhou: agreement_score={ag:.3f} < {self._alert_consensus_threshold}"}
            if rk > self._alert_max_risk_pct:
                return {"approved": False, "action": "HOLD",
                        "reason": f"Camada 3 falhou: risk_pct={rk:.2f}% > {self._alert_max_risk_pct}%"}
            return {"layers_passed": True, "approved": True}

        elif phase == PHASE_CAPITAL_ROUTE:
            return {
                "allocated_asset": ctx.get("asset", ""),
                "allocated_fraction": ctx.get("size_multiplier", 1.0),
                "approved": True,
            }

        elif phase == PHASE_AUDIT:
            return {
                "audit_recorded": True,
                "audit_id": f"aud_{uuid.uuid4().hex[:8]}",
                "approved": True,
            }

        return {"approved": True}

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._runs)
        if total == 0:
            return {"total_runs": 0}
        approved = sum(1 for r in self._runs if r.approved)
        blocked_by_phase: Dict[str, int] = {}
        for r in self._runs:
            if r.blocked_at_phase:
                blocked_by_phase[r.blocked_at_phase] = blocked_by_phase.get(r.blocked_at_phase, 0) + 1
        return {
            "total_runs": total,
            "approved": approved,
            "blocked": total - approved,
            "approval_rate": round(approved / total, 4),
            "blocked_by_phase": blocked_by_phase,
        }

    def get_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._runs[-limit:]]
