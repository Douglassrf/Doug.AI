"""Experience store for market memory (Missão 24).

This module defines a simple persistent storage for trading experiences.  Each
experience captures the **context** (arbitrary JSON‑serialisable dict), the
market **regime** (e.g., ``"bull"`` or ``"bear"``), the **decision** taken
(e.g., ``"BUY"``, ``"SELL"``, ``"HOLD"``), the **result** of that decision
(``"WIN"`` or ``"LOSS"``) and the observed **PnL**.  Experiences are
identified by a hash of their context to allow quick lookup of similar
situations.

This store is read/write but does not expose any method to delete data,
preserving the full history for later analysis.  It uses SQLite under
the hood and automatically creates the necessary table on first use.
"""

from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

class ExperienceStore:
    """Persistent storage for trading experiences.

    Parameters
    ----------
    db_path : str
        Location of the SQLite database file.  If the file does not exist
        it will be created along with its directory.
    """

    def __init__(self, db_path: str = "doug_os/logs/experience_store.db") -> None:
        self.db_path = Path(db_path)
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Connect to database
        self.conn = sqlite3.connect(str(self.db_path))
        # Create table if not exists
        self.conn.execute(
            """
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
            """
        )
        self.conn.commit()

    def _hash(self, context: Dict) -> str:
        """Compute a stable hash of the context dict.

        The context is serialised using JSON with sorted keys to ensure
        identical dictionaries yield the same hash.  A SHA‑256 digest is
        used to minimise collisions.
        """
        return hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()

    def save(
        self,
        context: Dict,
        regime: str,
        decision: str,
        result: str,
        pnl: float,
    ) -> None:
        """Persist a new trading experience.

        Parameters
        ----------
        context : dict
            Arbitrary data describing the market state at the time of the trade.
        regime : str
            Market regime when the decision was taken (e.g., ``"bull"``, ``"bear"``).
        decision : str
            Decision taken by the agent (e.g., ``"BUY"``, ``"SELL"``, ``"HOLD"``).
        result : str
            Outcome of the decision (``"WIN"`` or ``"LOSS"``).
        pnl : float
            Profit or loss resulting from the trade.
        """
        self.conn.execute(
            "INSERT INTO experiences (pattern_hash, context, regime, decision, result, pnl, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self._hash(context),
                json.dumps(context),
                regime,
                decision,
                result,
                float(pnl),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()

    def similar(self, context: Dict) -> List[Dict]:
        """Retrieve experiences with the same context pattern.

        Parameters
        ----------
        context : dict
            Context for which to find similar historical experiences.

        Returns
        -------
        list of dict
            A list of experiences with matching pattern hash.  Each entry
            contains the original context, regime, decision, result and pnl.
        """
        cur = self.conn.execute(
            "SELECT context, regime, decision, result, pnl FROM experiences WHERE pattern_hash=?",
            (self._hash(context),),
        )
        return [
            {
                "context": json.loads(row[0]),
                "regime": row[1],
                "decision": row[2],
                "result": row[3],
                "pnl": row[4],
            }
            for row in cur.fetchall()
        ]