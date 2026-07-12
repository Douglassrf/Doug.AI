import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

class ExperienceStore:
    def __init__(self, db_path="doug_os/logs/experience_store.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT,
                context TEXT,
                regime TEXT,
                decision TEXT,
                result TEXT,
                pnl REAL,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def _hash(self, context: dict) -> str:
        return hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()

    def save(self, context: dict, regime: str, decision: str, result: str, pnl: float):
        self.conn.execute(
            "INSERT INTO experiences (pattern_hash, context, regime, decision, result, pnl, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self._hash(context), json.dumps(context), regime, decision, result, float(pnl), datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def similar(self, context: dict) -> list[dict]:
        cur = self.conn.execute(
            "SELECT context, regime, decision, result, pnl FROM experiences WHERE pattern_hash=?",
            (self._hash(context),),
        )
        return [
            {"context": json.loads(row[0]), "regime": row[1], "decision": row[2], "result": row[3], "pnl": row[4]}
            for row in cur.fetchall()
        ]
