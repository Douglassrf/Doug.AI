from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import json
import hashlib


@dataclass
class Backup:
    id: str = field(default_factory=lambda: f"backup_{uuid.uuid4().hex[:12]}")
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    backup_type: str = "full"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "backup_type": self.backup_type,
        }


@dataclass
class RecoveryPlan:
    id: str = field(default_factory=lambda: f"rplan_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    estimated_time_minutes: int = 0
    rpo_minutes: int = 0
    rto_minutes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "estimated_time_minutes": self.estimated_time_minutes,
            "rpo_minutes": self.rpo_minutes,
            "rto_minutes": self.rto_minutes,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RecoveryResult:
    plan_id: str = ""
    success: bool = False
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    rpo_achieved: bool = False
    rto_achieved: bool = False
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "rpo_achieved": self.rpo_achieved,
            "rto_achieved": self.rto_achieved,
            "errors": self.errors,
        }


class DisasterRecoveryEngine:
    """Motor de recuperação de desastres com backup, validação e DR drill."""

    def __init__(self) -> None:
        self._backups: Dict[str, Backup] = {}
        self._plans: Dict[str, RecoveryPlan] = {}
        self._results: List[RecoveryResult] = []
        self._current_state: Dict[str, Any] = {}

    def create_backup(self, name: str, data: Dict[str, Any], backup_type: str = "full") -> Backup:
        data_str = json.dumps(data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        backup = Backup(
            name=name,
            data=data,
            checksum=checksum,
            size_bytes=len(data_str),
            backup_type=backup_type,
        )
        self._backups[backup.id] = backup
        return backup

    def list_backups(self, limit: int = 10) -> List[Backup]:
        return sorted(self._backups.values(), key=lambda x: x.created_at, reverse=True)[:limit]

    def validate_backup(self, backup_id: str) -> bool:
        backup = self._backups.get(backup_id)
        if not backup:
            return False
        data_str = json.dumps(backup.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16] == backup.checksum

    def create_recovery_plan(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        rpo_minutes: int = 60,
        rto_minutes: int = 30,
    ) -> RecoveryPlan:
        plan = RecoveryPlan(
            name=name,
            description=description,
            steps=steps,
            estimated_time_minutes=sum(s.get("estimated_minutes", 5) for s in steps),
            rpo_minutes=rpo_minutes,
            rto_minutes=rto_minutes,
        )
        self._plans[plan.id] = plan
        return plan

    def execute_recovery(self, plan_id: str, backup_id: Optional[str] = None) -> RecoveryResult:
        plan = self._plans.get(plan_id)
        if not plan:
            return RecoveryResult(plan_id=plan_id, success=False, errors=["Plan not found"])

        result = RecoveryResult(plan_id=plan_id)
        result.start_time = datetime.now(timezone.utc)

        try:
            if backup_id and not self.validate_backup(backup_id):
                result.errors.append("Backup validation failed")
                result.success = False
                return result

            for step in plan.steps:
                step_result = self._execute_step(step, backup_id)
                if not step_result["success"]:
                    result.errors.append(
                        f"Step {step.get('name', 'unknown')} failed: {step_result.get('error', 'unknown')}"
                    )
                    result.success = False
                    break
            else:
                result.success = True
                result.rpo_achieved = True
                result.rto_achieved = True

        except Exception as exc:
            result.errors.append(str(exc))
            result.success = False
        finally:
            result.end_time = datetime.now(timezone.utc)
            result.duration_minutes = (result.end_time - result.start_time).total_seconds() / 60

        self._results.append(result)
        return result

    def _execute_step(self, step: Dict[str, Any], backup_id: Optional[str]) -> Dict[str, Any]:
        step_type = step.get("type", "restore")
        if step_type == "restore" and backup_id:
            backup = self._backups.get(backup_id)
            if backup:
                self._current_state.update(backup.data)
                return {"success": True}
            return {"success": False, "error": "Backup not found"}
        return {"success": True}

    def get_dr_report(self) -> Dict[str, Any]:
        total = len(self._results)
        successful = sum(1 for r in self._results if r.success)
        return {
            "total_recoveries": total,
            "successful_recoveries": successful,
            "success_rate": successful / total if total else 0.0,
            "avg_rto_achieved": sum(1 for r in self._results if r.rto_achieved) / total if total else 0.0,
            "last_recovery": self._results[-1].to_dict() if self._results else None,
            "backups_available": len(self._backups),
            "plans_available": len(self._plans),
        }
