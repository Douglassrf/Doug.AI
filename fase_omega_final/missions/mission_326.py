# ============================================================
# MISSÃO 326 — OMEGA GOVERNANCE COUNCIL
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class GovernanceProposal:
    """Proposta de mudança no sistema."""

    id: str = field(default_factory=lambda: f"gp_{uuid.uuid4().hex[:12]}")
    title: str = ""
    description: str = ""
    change_type: str = ""
    proposer: str = ""
    status: str = "pending"
    votes_for: int = 0
    votes_against: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "change_type": self.change_type,
            "proposer": self.proposer,
            "status": self.status,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CouncilDecision:
    """Decisão final do conselho."""

    id: str = field(default_factory=lambda: f"cd_{uuid.uuid4().hex[:12]}")
    proposal_id: str = ""
    verdict: str = "PENDING"
    policy_enforced: bool = False
    rationale: str = ""
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "verdict": self.verdict,
            "policy_enforced": self.policy_enforced,
            "rationale": self.rationale,
            "decided_at": self.decided_at.isoformat(),
        }


class OmegaGovernanceCouncil:
    """
    Conselho final de governança.

    Implementa propostas, votação, aprovação/rejeição e enforcement de políticas.
    """

    QUORUM = 3
    POLICIES = (
        "no_unauthorized_external_apis",
        "require_evidence_for_changes",
        "human_review_for_launch",
    )

    def __init__(self):
        self._proposals: Dict[str, GovernanceProposal] = {}
        self._votes: Dict[str, Dict[str, str]] = {}
        self._decisions: List[CouncilDecision] = []
        self._policies: List[str] = list(self.POLICIES)

    def submit_proposal(
        self,
        title: str,
        description: str,
        change_type: str,
        proposer: str,
    ) -> GovernanceProposal:
        """Submete proposta de mudança."""
        proposal = GovernanceProposal(
            title=title,
            description=description,
            change_type=change_type,
            proposer=proposer,
        )
        self._proposals[proposal.id] = proposal
        self._votes[proposal.id] = {}
        return proposal

    def vote(self, proposal_id: str, council_member: str, approve: bool) -> bool:
        """Registra voto do conselho."""
        proposal = self._proposals.get(proposal_id)
        if not proposal or proposal.status != "pending":
            return False

        self._votes[proposal_id][council_member] = "for" if approve else "against"
        proposal.votes_for = sum(
            1 for vote in self._votes[proposal_id].values() if vote == "for"
        )
        proposal.votes_against = sum(
            1 for vote in self._votes[proposal_id].values() if vote == "against"
        )
        return True

    def decide(self, proposal_id: str) -> CouncilDecision:
        """Decide proposta com base nos votos."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return CouncilDecision(proposal_id=proposal_id, verdict="INVALID")

        total_votes = proposal.votes_for + proposal.votes_against
        decision = CouncilDecision(proposal_id=proposal_id)

        if total_votes < self.QUORUM:
            decision.verdict = "PENDING"
            decision.rationale = f"Quorum not met ({total_votes}/{self.QUORUM})"
        elif proposal.votes_for > proposal.votes_against:
            decision.verdict = "APPROVED"
            proposal.status = "approved"
            decision.policy_enforced = self._enforce_policies(proposal)
            decision.rationale = "Majority approved the proposal"
        else:
            decision.verdict = "REJECTED"
            proposal.status = "rejected"
            decision.rationale = "Majority rejected the proposal"

        self._decisions.append(decision)
        return decision

    def _enforce_policies(self, proposal: GovernanceProposal) -> bool:
        """Aplica políticas de governança."""
        if proposal.change_type == "external_api" and "no_unauthorized_external_apis" in self._policies:
            return False
        return True

    def get_council_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do conselho."""
        return {
            "total_proposals": len(self._proposals),
            "pending": sum(1 for p in self._proposals.values() if p.status == "pending"),
            "approved": sum(1 for p in self._proposals.values() if p.status == "approved"),
            "rejected": sum(1 for p in self._proposals.values() if p.status == "rejected"),
            "policies": self._policies,
            "latest_decisions": [decision.to_dict() for decision in self._decisions[-5:]],
        }
