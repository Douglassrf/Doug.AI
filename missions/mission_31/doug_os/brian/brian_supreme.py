from collections import defaultdict
from doug_os.core.audit_log import AuditLog

class BrianSupreme:
    def __init__(self, audit_log: AuditLog | None = None):
        self.audit_log = audit_log or AuditLog()

    def learn_from_audit(self) -> dict:
        events = [e for e in self.audit_log.read_all() if e.get("event_type") == "market_cycle"]
        servo_scores = defaultdict(lambda: {"wins":0, "losses":0, "total":0})
        lessons = []
        for event in events:
            payload = event["payload"]
            decision = payload.get("decision", {})
            accepted = decision.get("accepted", [])
            outcome = payload.get("outcome", "UNKNOWN")
            for v in accepted:
                s = servo_scores[v["servo"]]
                s["total"] += 1
                if outcome == "WIN":
                    s["wins"] += 1
                elif outcome == "LOSS":
                    s["losses"] += 1
        for servo, s in servo_scores.items():
            accuracy = s["wins"] / s["total"] if s["total"] else 0
            lessons.append({"servo": servo, "accuracy": round(accuracy, 4), "total": s["total"]})
        return {"lessons": lessons, "events_read": len(events)}
