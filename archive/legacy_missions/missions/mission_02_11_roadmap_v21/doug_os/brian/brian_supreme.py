from collections import defaultdict
from doug_os.core.audit_log import AuditLog

class BrianSupreme:
    def __init__(self, audit_log: AuditLog | None = None):
        self.audit_log = audit_log or AuditLog()

    def learn(self) -> dict:
        events = [e for e in self.audit_log.read_all() if e.get("event_type") == "market_cycle"]
        servo_stats = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0})

        for event in events:
            payload = event.get("payload", {})
            outcome = payload.get("outcome", "UNKNOWN")
            accepted = payload.get("decision", {}).get("accepted", [])
            for vector in accepted:
                stats = servo_stats[vector["servo"]]
                stats["total"] += 1
                if outcome == "WIN":
                    stats["wins"] += 1
                elif outcome == "LOSS":
                    stats["losses"] += 1

        ranking = []
        for servo, stats in servo_stats.items():
            accuracy = stats["wins"] / stats["total"] if stats["total"] else 0
            ranking.append({
                "servo": servo,
                "accuracy": round(accuracy, 4),
                **stats,
            })

        return {
            "events_read": len(events),
            "servo_ranking": sorted(ranking, key=lambda x: x["accuracy"], reverse=True),
            "lesson": "audit_log_processed",
        }
