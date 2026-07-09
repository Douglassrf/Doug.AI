"""Curriculum Teacher — rotating pairs, mistake review, 10 layers, 331 missions."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from training.pair_universe import (
    BATCH_SIZE,
    BINANCE_PAIRS_100,
    DERIV_PAIRS_100,
    batch_at,
    batches,
)

ROOT = Path(__file__).resolve().parent.parent
MISSIONS_DIR = ROOT / "missions"
TRAINING_DIR = ROOT / "data" / "training"
CURRICULUM_STATE_PATH = TRAINING_DIR / "curriculum_state.json"
MEMORY_PATH = TRAINING_DIR / "student_memory.json"

LAYER_NAMES = (
    "L1 Fundacao",
    "L2 Dados",
    "L3 Sinais",
    "L4 Risco",
    "L5 Execucao",
    "L6 Portfolio",
    "L7 Alpha",
    "L8 Predicao",
    "L9 Meta-Cognicao",
    "L10 Omega",
)


@dataclass
class MistakeRecord:
    pair: str
    strategy_id: str
    scenario: str
    message: str
    ts: str
    exchange: str = "deriv"


@dataclass
class CurriculumState:
    deriv_batch_index: int = 0
    binance_batch_index: int = 0
    layer_index: int = 0  # 0-9
    mission_rotation: int = 0
    sessions_completed: int = 0
    total_batches_deriv: int = 0
    total_batches_binance: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "deriv_batch_index": self.deriv_batch_index,
            "binance_batch_index": self.binance_batch_index,
            "layer_index": self.layer_index,
            "layer_name": LAYER_NAMES[self.layer_index % len(LAYER_NAMES)],
            "mission_rotation": self.mission_rotation,
            "sessions_completed": self.sessions_completed,
            "total_batches_deriv": self.total_batches_deriv,
            "total_batches_binance": self.total_batches_binance,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


class CurriculumTeacher:
    """Metodologia: revisar erros → treinar lote 10 pares → absorver → rotacionar."""

    def __init__(self) -> None:
        self.deriv_batches = batches(DERIV_PAIRS_100)
        self.binance_batches = batches(BINANCE_PAIRS_100)
        self.mission_ids = self._discover_missions()
        self.mission_layers = self._build_mission_layers()
        self.state = self._load_state()

    def _discover_missions(self) -> list[int]:
        ids: list[int] = []
        if not MISSIONS_DIR.exists():
            return list(range(258, 331))
        for p in MISSIONS_DIR.glob("mission_*.py"):
            m = re.search(r"mission_(\d+)", p.name)
            if m:
                ids.append(int(m.group(1)))
        return sorted(set(ids)) or list(range(258, 331))

    def _build_mission_layers(self) -> dict[int, list[int]]:
        """Map 10 layers to mission IDs (331 missions spread across layers)."""
        layers: dict[int, list[int]] = {i: [] for i in range(10)}
        if not self.mission_ids:
            return layers
        per_layer = max(1, len(self.mission_ids) // 10)
        for idx, mid in enumerate(self.mission_ids):
            layer = min(idx // per_layer, 9)
            layers[layer].append(mid)
        return layers

    def _load_state(self) -> CurriculumState:
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        if CURRICULUM_STATE_PATH.exists():
            try:
                d = json.loads(CURRICULUM_STATE_PATH.read_text(encoding="utf-8"))
                return CurriculumState(
                    deriv_batch_index=int(d.get("deriv_batch_index", 0)),
                    binance_batch_index=int(d.get("binance_batch_index", 0)),
                    layer_index=int(d.get("layer_index", 0)),
                    mission_rotation=int(d.get("mission_rotation", 0)),
                    sessions_completed=int(d.get("sessions_completed", 0)),
                    total_batches_deriv=len(self.deriv_batches),
                    total_batches_binance=len(self.binance_batches),
                )
            except (json.JSONDecodeError, OSError, ValueError):
                pass
        return CurriculumState(
            total_batches_deriv=len(self.deriv_batches),
            total_batches_binance=len(self.binance_batches),
        )

    def save_state(self) -> None:
        self.state.total_batches_deriv = len(self.deriv_batches)
        self.state.total_batches_binance = len(self.binance_batches)
        CURRICULUM_STATE_PATH.write_text(
            json.dumps(self.state.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def current_deriv_batch(self) -> tuple[str, ...]:
        return batch_at(DERIV_PAIRS_100, self.state.deriv_batch_index)

    def current_binance_batch(self) -> tuple[str, ...]:
        return batch_at(BINANCE_PAIRS_100, self.state.binance_batch_index)

    def current_layer_missions(self, count: int = 10) -> list[int]:
        layer = self.state.layer_index % 10
        missions = self.mission_layers.get(layer, [])
        if not missions:
            return []
        start = (self.state.mission_rotation * count) % len(missions)
        chunk: list[int] = []
        for i in range(count):
            chunk.append(missions[(start + i) % len(missions)])
        return chunk

    def load_mistakes(self, limit: int = 25) -> list[MistakeRecord]:
        records: list[MistakeRecord] = []
        sessions = TRAINING_DIR / "sessions.jsonl"
        if sessions.exists():
            lines = sessions.read_text(encoding="utf-8").strip().splitlines()
            for line in reversed(lines[-500:]):
                try:
                    row = json.loads(line)
                    if row.get("won") is False:
                        records.append(
                            MistakeRecord(
                                pair=row.get("pair", row.get("symbol", "?")),
                                strategy_id=row.get("strategy_id", row.get("strategy", "?")),
                                scenario=row.get("scenario", "?"),
                                message=f"Perda em {row.get('scenario')} dir={row.get('direction', '?')}",
                                ts=row.get("ts", ""),
                                exchange=row.get("exchange", "deriv"),
                            )
                        )
                except json.JSONDecodeError:
                    continue
                if len(records) >= limit:
                    break

        lessons = TRAINING_DIR / "lessons.jsonl"
        if lessons.exists() and len(records) < limit:
            for line in reversed(lessons.read_text(encoding="utf-8").strip().splitlines()[-200:]):
                try:
                    row = json.loads(line)
                    if row.get("kind") in ("correction", "wrong_tool", "intervention"):
                        records.append(
                            MistakeRecord(
                                pair=row.get("pair", "?"),
                                strategy_id=row.get("strategy_id", "?"),
                                scenario=row.get("scenario", "?"),
                                message=row.get("message", "")[:200],
                                ts=row.get("ts", ""),
                            )
                        )
                except json.JSONDecodeError:
                    continue
                if len(records) >= limit:
                    break
        return records[:limit]

    def build_remedial_drills(self, mistakes: list[MistakeRecord]) -> list[dict[str, str]]:
        """Re-drills obrigatorios: mesmo par+estrategia dos erros recentes."""
        seen: set[tuple[str, str]] = set()
        drills: list[dict[str, str]] = []
        for m in mistakes:
            key = (m.pair, m.strategy_id)
            if key in seen:
                continue
            seen.add(key)
            drills.append(
                {
                    "pair": m.pair,
                    "strategy_id": m.strategy_id,
                    "scenario": m.scenario,
                    "reason": f"Erro recente em {m.scenario} — re-drill ate acertar 100%",
                }
            )
            if len(drills) >= 10:
                break
        return drills

    def build_review_briefing(self) -> dict[str, Any]:
        mistakes = self.load_mistakes(20)
        by_pair: dict[str, int] = {}
        by_strategy: dict[str, int] = {}
        for m in mistakes:
            by_pair[m.pair] = by_pair.get(m.pair, 0) + 1
            by_strategy[m.strategy_id] = by_strategy.get(m.strategy_id, 0) + 1

        worst_pairs = sorted(by_pair.items(), key=lambda x: -x[1])[:5]
        worst_strategies = sorted(by_strategy.items(), key=lambda x: -x[1])[:5]
        remedial_drills = self.build_remedial_drills(mistakes)

        return {
            "phase": "REVISAO_PRE_TREINO",
            "accuracy_goal": 1.0,
            "mistakes_loaded": len(mistakes),
            "worst_pairs": worst_pairs,
            "worst_strategies": worst_strategies,
            "remedial_drills": remedial_drills,
            "recent_mistakes": [
                {"pair": m.pair, "strategy": m.strategy_id, "scenario": m.scenario, "msg": m.message[:120]}
                for m in mistakes[:8]
            ],
            "instruction": (
                "META: ACERTAR 100%. Antes de operar o lote de hoje, corrijam estes erros. "
                "Re-drill obrigatorio no mesmo par/estrategia apos cada perda. "
                "Nao repitam estrategia errada no mesmo cenario. Zero tolerancia a erro."
            ),
        }

    def session_plan(self, *, samples_per_pair: int = 12, all_pairs: bool = False) -> dict[str, Any]:
        if all_pairs:
            deriv_batch = DERIV_PAIRS_100
            binance_batch = BINANCE_PAIRS_100
            methodology = (
                "revisar_erros_100% -> re_drill_obrigatorio -> 100_pares_deriv -> "
                "100_pares_binance -> camada_missao (diario completo)"
            )
        else:
            deriv_batch = self.current_deriv_batch()
            binance_batch = self.current_binance_batch()
            methodology = (
                "revisar_erros_100% -> re_drill -> lote_10_deriv -> lote_10_binance -> "
                "camada_missao -> rotacionar"
            )

        missions = self.current_layer_missions(10)
        review = self.build_review_briefing()

        return {
            "methodology": methodology,
            "all_pairs_daily": all_pairs,
            "state": self.state.to_dict(),
            "deriv_batch": list(deriv_batch),
            "deriv_pair_count": len(deriv_batch),
            "deriv_batch_num": self.state.deriv_batch_index + 1 if not all_pairs else "ALL",
            "deriv_total_batches": len(self.deriv_batches) if not all_pairs else 1,
            "binance_batch": list(binance_batch),
            "binance_pair_count": len(binance_batch),
            "binance_batch_num": self.state.binance_batch_index + 1 if not all_pairs else "ALL",
            "binance_total_batches": len(self.binance_batches) if not all_pairs else 1,
            "layer": LAYER_NAMES[self.state.layer_index % 10],
            "layer_missions_today": missions,
            "mission_count_catalog": len(self.mission_ids),
            "samples_per_pair": samples_per_pair,
            "estimated_deriv_samples": len(deriv_batch) * samples_per_pair,
            "estimated_binance_samples": len(binance_batch) * samples_per_pair,
            "estimated_total_samples": (len(deriv_batch) + len(binance_batch)) * samples_per_pair,
            "review": review,
        }

    def advance_after_session(self, *, all_pairs: bool = False, unresolved_drills: int = 0) -> None:
        """After session: full daily rotates layer; batch mode rotates 10-pair lots."""
        if unresolved_drills > 0:
            # Nao avanca camada enquanto houver re-drills pendentes — so rotaciona lotes parciais
            if not all_pairs:
                self.state.deriv_batch_index = (self.state.deriv_batch_index + 1) % max(len(self.deriv_batches), 1)
                self.state.binance_batch_index = (self.state.binance_batch_index + 1) % max(len(self.binance_batches), 1)
            self.state.sessions_completed += 1
            self.save_state()
            return
        if not all_pairs:
            self.state.deriv_batch_index = (self.state.deriv_batch_index + 1) % max(len(self.deriv_batches), 1)
            self.state.binance_batch_index = (self.state.binance_batch_index + 1) % max(len(self.binance_batches), 1)
        self.state.mission_rotation += 1
        if all_pairs or self.state.deriv_batch_index == 0:
            self.state.layer_index = (self.state.layer_index + 1) % 10
        self.state.sessions_completed += 1
        self.save_state()

    def record_absorption(self, *, repeated_mistakes: int, avoided: int) -> None:
        mem: dict[str, Any] = {"history": []}
        if MEMORY_PATH.exists():
            try:
                mem = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        total = repeated_mistakes + avoided
        rate = round(avoided / total, 4) if total else 0.0
        mem.setdefault("history", []).append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "repeated_mistakes": repeated_mistakes,
                "avoided": avoided,
                "absorption_rate": rate,
                "layer": LAYER_NAMES[self.state.layer_index % 10],
            }
        )
        mem["history"] = mem["history"][-100:]
        mem["last_absorption_rate"] = rate
        MEMORY_PATH.write_text(json.dumps(mem, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
