from dataclasses import dataclass, field
from time import time
from uuid import uuid4

@dataclass
class CycleRecord:
    cycle_id: str
    symbol: str
    created_at: float = field(default_factory=time)
    status: str = "OPEN"
    notes: list[str] = field(default_factory=list)

class CycleRegistry:
    def __init__(self):
        self.cycles: dict[str, CycleRecord] = {}

    def create(self, symbol: str) -> CycleRecord:
        cycle = CycleRecord(cycle_id=str(uuid4()), symbol=symbol)
        self.cycles[cycle.cycle_id] = cycle
        return cycle

    def close(self, cycle_id: str, status: str = "CLOSED", note: str | None = None):
        cycle = self.cycles.get(cycle_id)
        if not cycle:
            return None
        cycle.status = status
        if note:
            cycle.notes.append(note)
        return cycle
