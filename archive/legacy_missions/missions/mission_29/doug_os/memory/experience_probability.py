import json, sqlite3, hashlib
from datetime import datetime, timezone

class ExperienceProbabilityEngine:
    def __init__(self, db_path="doug_os/logs/experience_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_hash TEXT,
            context TEXT,
            result TEXT,
            pnl REAL,
            created_at TEXT
        )
        """)
        self.conn.commit()

    def _hash(self, context):
        return hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()

    def save(self, context: dict, result: str, pnl: float):
        self.conn.execute(
            "INSERT INTO experiences (pattern_hash, context, result, pnl, created_at) VALUES (?, ?, ?, ?, ?)",
            (self._hash(context), json.dumps(context), result, float(pnl), datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()

    def similar_count(self, context: dict) -> int:
        cur = self.conn.execute("SELECT COUNT(*) FROM experiences WHERE pattern_hash=?", (self._hash(context),))
        return int(cur.fetchone()[0])
