import json
from datetime import datetime
from pathlib import Path

class AuditLog:
    def __init__(self, path='doug_os/logs/audit_log.jsonl'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event_type: str, payload: dict) -> None:
        event = {'timestamp': datetime.utcnow().isoformat(), 'event_type': event_type, 'payload': payload}
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
