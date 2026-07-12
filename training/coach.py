"""Training Coach (Professor) — guides DogEye students, prevents degradation, builds wisdom."""
from __future__ import annotations

import json
import os
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from training.strategies import STRATEGIES, StrategySpec
from training.strategy_trend import MIN_SAMPLES_FOR_TREND, bucket_trend

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
TRAINING_DIR = DATA / "training"
WISDOM_PATH = TRAINING_DIR / "wisdom.json"
LESSONS_PATH = TRAINING_DIR / "lessons.jsonl"
COACH_STATE_PATH = TRAINING_DIR / "coach_state.json"
PLAYBOOK_PATH = TRAINING_DIR / "playbook.json"  # vantagens comprovadas (produto real)
PAPER_LEDGER_PATH = TRAINING_DIR / "paper_trades.jsonl"  # mesmo arquivo de training/paper_ledger.py

# Scenario → strategies that SHOULD work (curriculum truth)
SCENARIO_BEST_PRACTICE: dict[str, tuple[str, ...]] = {
    "trending_up": ("S01", "S04", "S05"),
    "trending_down": ("S01", "S04", "S05"),
    "ranging": ("S02", "S08", "S07"),
    "high_volatility": ("S06", "S09", "S10"),
    "low_volatility": ("S05", "S09", "S08"),
}

LEVEL_NAMES = ("Aprendiz", "Praticante", "Operador", "Especialista", "Mestre")


@dataclass
class RemedialDrill:
    pair: str
    strategy_id: str
    scenario: str
    attempts: int = 0

    def key(self) -> tuple[str, str, str]:
        return (self.pair, self.strategy_id, self.scenario)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair": self.pair,
            "strategy_id": self.strategy_id,
            "scenario": self.scenario,
            "attempts": self.attempts,
        }


@dataclass
class StudentProfile:
    strategy_id: str
    level: int = 1
    xp: int = 0
    streak_wins: int = 0
    streak_losses: int = 0
    remedial: bool = False
    weak_scenarios: list[str] = field(default_factory=list)
    accuracy_streak: int = 0  # streak toward accuracy goal (90%)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "level": self.level,
            "level_name": LEVEL_NAMES[min(self.level - 1, len(LEVEL_NAMES) - 1)],
            "xp": self.xp,
            "streak_wins": self.streak_wins,
            "streak_losses": self.streak_losses,
            "remedial": self.remedial,
            "weak_scenarios": self.weak_scenarios,
            "accuracy_streak": self.accuracy_streak,
        }


@dataclass
class Lesson:
    kind: str
    message: str
    strategy_id: str = ""
    scenario: str = ""
    pair: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": self.kind,
            "message": self.message,
            "strategy_id": self.strategy_id,
            "scenario": self.scenario,
            "pair": self.pair,
        }


class TrainingCoach:
    """Professor: corrige erros, evita queda, acumula sabedoria. Meta: acertar 90% (realista)."""

    # Metas ESTATISTICAMENTE HONESTAS (a verdade que faltava):
    # 90% de acerto nao existe em trading. O que existe e VANTAGEM (edge):
    # acertar consistentemente ACIMA de cara-ou-coroa (50%), com amostra grande
    # o suficiente para nao ser sorte. Um sistema que acerta 58% em 200 trades
    # ganha muito dinheiro; um que "acerta 90%" em 7 trades e ruido puro.
    # Margem de EXCELENCIA para entrar no Playbook: 80% de acerto com amostra
    # significativa. E uma barra ALTA de proposito — so as combinacoes de elite
    # entram. (Diferente da fantasia de 90% antiga: aquela era a META que fazia
    # o Professor gritar sobre TUDO abaixo; esta e so o selo de excelencia, e o
    # que perde continua sendo julgado por LOSING_BAR, sem ruido.)
    EDGE_BAR = 0.80           # >= isto (com amostra) = vantagem de ELITE (Playbook)
    NEUTRAL_FLOOR = 0.45      # entre 0.45 e 0.80 = ok/neutro, nao e problema nem elite
    LOSING_BAR = 0.45         # < isto (com amostra) = perde de verdade (problema real)
    DEGRADE_THRESHOLD = 0.40  # win rate below this = degradacao seria
    # So julga um bucket com amostra estatisticamente significativa. Abaixo
    # disso o win rate oscila por acaso — flagar e criar ruido, nao aprender.
    MIN_TRADES_FOR_JUDGMENT = 30
    # compat: codigo legado ainda referencia PERFECT_WR_THRESHOLD
    PERFECT_WR_THRESHOLD = 0.80
    ACCURACY_GOAL = 0.80  # margem de excelencia (Playbook), nao meta impossivel
    MAX_LESSONS_LINES = 2000  # limita lessons.jsonl (evita lentidao por arquivo gigante)
    XP_WIN = 10
    XP_LOSS = -12  # penalidade forte — erro nao e aceitavel
    XP_LEVEL_UP = 100
    STREAK_BONUS = {3: 8, 5: 20, 10: 50}  # bonus XP por sequencia de acertos
    REMEDIAL_EXIT_STREAK = 5  # sair da correcao so com 5 acertos seguidos
    MAX_DRILL_ATTEMPTS = 20  # depois disso, para de insistir — combinacao provavelmente quebrada no codigo

    def __init__(self) -> None:
        self.students: dict[str, StudentProfile] = {
            s.id: StudentProfile(strategy_id=s.id) for s in STRATEGIES
        }
        self.recent_cycle_wr: deque[float] = deque(maxlen=10)
        self.wisdom_rules: list[dict[str, Any]] = []
        self.pending_drills: deque[RemedialDrill] = deque(maxlen=50)
        self.remedial_mode = False
        self.broken_combos: set[tuple[str, str, str]] = set()
        self._load()

    def _load(self) -> None:
        TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        if COACH_STATE_PATH.exists():
            try:
                data = json.loads(COACH_STATE_PATH.read_text(encoding="utf-8"))
                for sid, prof in data.get("students", {}).items():
                    if sid in self.students:
                        p = self.students[sid]
                        p.level = prof.get("level", 1)
                        p.xp = prof.get("xp", 0)
                        p.streak_wins = prof.get("streak_wins", 0)
                        p.streak_losses = prof.get("streak_losses", 0)
                        p.remedial = prof.get("remedial", False)
                        p.weak_scenarios = prof.get("weak_scenarios", [])
                        p.accuracy_streak = prof.get("accuracy_streak", 0)
                self.recent_cycle_wr = deque(data.get("recent_cycle_wr", []), maxlen=10)
                self.pending_drills = deque(
                    (
                        RemedialDrill(d["pair"], d["strategy_id"], d["scenario"], d.get("attempts", 0))
                        for d in data.get("pending_drills", [])
                    ),
                    maxlen=50,
                )
                self.remedial_mode = data.get("remedial_mode", False)
                self.broken_combos = {tuple(c) for c in data.get("broken_combos", [])}
            except (json.JSONDecodeError, OSError):
                pass
        if WISDOM_PATH.exists():
            try:
                self.wisdom_rules = json.loads(WISDOM_PATH.read_text(encoding="utf-8")).get("rules", [])
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "remedial_mode": self.remedial_mode,
            "accuracy_goal": self.ACCURACY_GOAL,
            "recent_cycle_wr": list(self.recent_cycle_wr),
            "pending_drills": [d.to_dict() for d in self.pending_drills],
            "students": {sid: p.to_dict() for sid, p in self.students.items()},
            "broken_combos": [list(c) for c in self.broken_combos],
        }
        COACH_STATE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        WISDOM_PATH.write_text(
            json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "rules": self.wisdom_rules}, indent=2)
            + "\n",
            encoding="utf-8",
        )

    def _log_lesson(self, lesson: Lesson) -> None:
        with LESSONS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(lesson.to_dict(), ensure_ascii=False) + "\n")
        # Poda periodica: sem isto, lessons.jsonl cresce pra sempre e cada ciclo
        # fica mais lento (a lentidao que voce viu: ciclos pulando de 15s p/ 80s).
        # Mantem so as ultimas MAX_LESSONS_LINES linhas. Checa o tamanho REAL do
        # arquivo a cada chamada (nao um contador em memoria) — um contador de
        # instancia zerava a cada novo processo (cada treino agendado cria um
        # TrainingCoach novo), entao a poda nunca disparava entre execucoes e o
        # arquivo cresceu sem limite (achado real 2026-07-09: 18.383 linhas /
        # 5.8MB acumuladas). So reescreve quando passa a margem (nao a cada
        # linha) pra nao ficar reescrevendo o arquivo toda hora.
        try:
            linhas = LESSONS_PATH.read_text(encoding="utf-8").splitlines()
            if len(linhas) > self.MAX_LESSONS_LINES + 200:
                LESSONS_PATH.write_text(
                    "\n".join(linhas[-self.MAX_LESSONS_LINES:]) + "\n", encoding="utf-8"
                )
        except OSError:
            pass

    def review_result(
        self,
        *,
        strategy_id: str,
        scenario: str,
        pair: str,
        won: bool | None,
        direction: str,
    ) -> Lesson | None:
        if won is None:
            return None

        student = self.students.get(strategy_id)
        if not student:
            return None

        best = SCENARIO_BEST_PRACTICE.get(scenario, ())
        lesson: Lesson | None = None

        if won:
            student.streak_wins += 1
            student.streak_losses = 0
            student.accuracy_streak += 1
            student.xp += self.XP_WIN
            for threshold, bonus in self.STREAK_BONUS.items():
                if student.accuracy_streak == threshold:
                    student.xp += bonus
                    self._log_lesson(
                        Lesson(
                            "streak_bonus",
                            f"{strategy_id}: {threshold} acertos seguidos! +{bonus} XP. "
                            f"Meta: acertar {self.ACCURACY_GOAL*100:.0f}% — continue a sequencia.",
                            strategy_id=strategy_id,
                            scenario=scenario,
                            pair=pair,
                        )
                    )
            self._clear_drill(pair, strategy_id, scenario)
            if student.remedial and student.streak_wins >= self.REMEDIAL_EXIT_STREAK:
                student.remedial = False
                lesson = Lesson(
                    "recovery",
                    f"{strategy_id} saiu do modo correcao apos {self.REMEDIAL_EXIT_STREAK} acertos seguidos. "
                    f"Meta permanece: acertar {self.ACCURACY_GOAL*100:.0f}%.",
                    strategy_id=strategy_id,
                    scenario=scenario,
                )
        else:
            student.streak_losses += 1
            student.streak_wins = 0
            student.accuracy_streak = 0
            student.xp = max(0, student.xp + self.XP_LOSS)
            if scenario not in student.weak_scenarios:
                student.weak_scenarios.append(scenario)
            gave_up = self._queue_drill(pair, strategy_id, scenario)
            if gave_up:
                self._log_lesson(
                    Lesson(
                        "broken_combo",
                        f"DESISTINDO — {strategy_id} em {scenario} ({pair}) falhou "
                        f"{self.MAX_DRILL_ATTEMPTS}x seguidas em re-drill sem nunca acertar. "
                        f"Isso nao e falta de treino, e provavel bug/incompatibilidade real na "
                        f"estrategia para esse cenario. Parando de forcar essa combinacao — "
                        f"precisa de revisao de codigo, nao de mais repeticao.",
                        strategy_id=strategy_id,
                        scenario=scenario,
                        pair=pair,
                    )
                )

            recommended = ", ".join(best) if best else "S10"
            lesson = Lesson(
                "correction",
                f"ERRO — meta e acertar {self.ACCURACY_GOAL*100:.0f}%: {strategy_id} errou em {scenario} ({pair}). "
                f"Voce usou '{direction}' — neste cenario o professor recomenda: {recommended}. "
                f"RE-DRILL obrigatorio no mesmo par/estrategia antes de avancar. "
                f"Estude a missao {self._mission_ref(strategy_id)}.",
                strategy_id=strategy_id,
                scenario=scenario,
                pair=pair,
            )
            if strategy_id not in best and best:
                lesson = Lesson(
                    "wrong_tool",
                    f"ERRO GRAVE — meta {self.ACCURACY_GOAL*100:.0f}%: {strategy_id} nao e estrategia para {scenario}. "
                    f"Troque para {best[0]} ou fique em HOLD. Re-drill em {pair} ate acertar.",
                    strategy_id=strategy_id,
                    scenario=scenario,
                    pair=pair,
                )

            if student.streak_losses >= 2:
                student.remedial = True
                self._log_lesson(
                    Lesson(
                        "remedial",
                        f"{strategy_id} entrou em MODO CORRECAO — {student.streak_losses} erros seguidos. "
                        f"So treine {scenario} com {recommended} em {pair} ate acertar "
                        f"{self.REMEDIAL_EXIT_STREAK}x seguidos (meta: {self.ACCURACY_GOAL*100:.0f}%).",
                        strategy_id=strategy_id,
                        scenario=scenario,
                        pair=pair,
                    )
                )

        while student.xp >= self.XP_LEVEL_UP and student.level < 5:
            student.xp -= self.XP_LEVEL_UP
            student.level += 1
            self._log_lesson(
                Lesson(
                    "level_up",
                    f"{strategy_id} subiu para nivel {student.level} ({LEVEL_NAMES[student.level - 1]}). "
                    f"Mais responsabilidade — menos erro tolerado.",
                    strategy_id=strategy_id,
                )
            )

        if lesson:
            self._log_lesson(lesson)
        return lesson

    def _mission_ref(self, strategy_id: str) -> str:
        for s in STRATEGIES:
            if s.id == strategy_id:
                return s.mission_ref
        return "?"

    def _queue_drill(self, pair: str, strategy_id: str, scenario: str) -> bool:
        """Enfileira um re-drill obrigatorio. Retorna True se essa combinacao
        acabou de ser desistida (excedeu MAX_DRILL_ATTEMPTS) — nesse caso ela
        vai para broken_combos e para de ser forcada, porque martelar uma
        combinacao que nunca acerta e sinal de bug na estrategia, nao de falta
        de treino (achado real: S08|CRASH500 chegou a 1325 tentativas, 0.08%)."""
        target = (pair, strategy_id, scenario)
        existing = next((d for d in self.pending_drills if d.key() == target), None)
        if existing:
            existing.attempts += 1
            if existing.attempts >= self.MAX_DRILL_ATTEMPTS:
                self.pending_drills = deque(
                    (d for d in self.pending_drills if d.key() != target),
                    maxlen=50,
                )
                self.broken_combos.add(target)
                return True
            return False
        self.pending_drills.appendleft(RemedialDrill(pair, strategy_id, scenario, attempts=1))
        return False

    def _clear_drill(self, pair: str, strategy_id: str, scenario: str) -> None:
        target = (pair, strategy_id, scenario)
        self.pending_drills = deque(
            (d for d in self.pending_drills if d.key() != target),
            maxlen=50,
        )

    def pop_next_drill(self) -> RemedialDrill | None:
        """Proximo re-drill obrigatorio (mesmo par/estrategia apos erro). Pula
        combinacoes ja marcadas como quebradas (broken_combos)."""
        for d in self.pending_drills:
            if d.key() not in self.broken_combos:
                return d
        return None

    def _check_bucket_trends(self) -> list[Lesson]:
        """Alerta precoce de tendencia de declinio por bucket (estrategia+par+
        cenario), via regressao linear sobre o historico cronologico REAL de
        pnl_pct em data/training/paper_trades.jsonl (decisoes OPERAR ja
        resolvidas ao vivo, nao dado de treino/backtest).

        Complementa (nao substitui) o julgamento por limiar absoluto acima
        (LOSING_BAR com MIN_TRADES_FOR_JUDGMENT): a inclinacao pode ficar
        negativa bem antes do win rate absoluto cruzar 0.45 -- validado por
        simulacao walk-forward contra data/training/sessions.jsonl (buckets
        rotulados "declining" na 1a metade do historico tiveram win rate medio
        de 35.9% na 2a metade, fora da amostra, contra 62.8% dos "stable")."""
        if not PAPER_LEDGER_PATH.exists():
            return []
        try:
            lines = PAPER_LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
        except OSError:
            return []

        by_bucket: dict[tuple[str, str, str], list[float]] = {}
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (row.get("strategy_id", ""), row.get("pair", ""), row.get("scenario", ""))
            pnl = row.get("pnl_pct")
            if pnl is None or not all(key):
                continue
            by_bucket.setdefault(key, []).append(float(pnl))

        lessons: list[Lesson] = []
        for (sid, pair, scenario), history in by_bucket.items():
            if len(history) < MIN_SAMPLES_FOR_TREND:
                continue
            trend = bucket_trend(history)
            if trend["label"] != "declining":
                continue
            student = self.students.get(sid)
            if student:
                student.remedial = True
                if scenario not in student.weak_scenarios:
                    student.weak_scenarios.append(scenario)
            lesson = Lesson(
                "trend_warning",
                f"TENDENCIA [{sid}]: performance real de {sid} em {pair}/{scenario} esta em "
                f"declinio (inclinacao {trend['slope']:+.4f} nos ultimos {trend['samples']} trades "
                "resolvidos) -- ainda pode estar acima do limiar absoluto de problema, mas a "
                "direcao e ruim. Alerta precoce, antes do veredito protetor.",
                strategy_id=sid,
                scenario=scenario,
                pair=pair,
            )
            lessons.append(lesson)
            self._log_lesson(lesson)
        return lessons

    def review_cycle(self, cycle_wr: float, leaderboard_stats: dict[str, dict[str, Any]]) -> list[Lesson]:
        """End-of-cycle: detect degradation, update wisdom, assign class focus."""
        lessons: list[Lesson] = []
        lessons.extend(self._check_bucket_trends())
        self.recent_cycle_wr.append(cycle_wr)

        # So intervem em problema REAL: estrategia que PERDE (wr < 0.45) com
        # AMOSTRA SIGNIFICATIVA (>= 30 trades). Buckets com pouca amostra ou na
        # zona de cara-ou-coroa (0.45-0.55) NAO sao flagados — antes o codigo
        # gritava sobre qualquer coisa abaixo de 90% com so 3 trades, gerando o
        # ruido perpetuo que voce viu no log (mesma estrategia ciclo apos ciclo).
        for key, bucket in leaderboard_stats.items():
            sid = bucket.get("strategy_id", "")
            scenario = bucket.get("scenario", "")
            trades = bucket.get("trades", 0)
            wr = bucket.get("win_rate", 0)
            if trades < self.MIN_TRADES_FOR_JUDGMENT:
                continue  # amostra insuficiente — julgar aqui seria ruido, nao aprendizado
            if wr >= self.LOSING_BAR:
                continue  # 45%+ nao e "problema" — e neutro ou tem vantagem; deixa quieto
            # Aqui sim: perde de verdade, com amostra que comprova. Isso e sinal.
            student = self.students.get(sid)
            if student:
                student.remedial = True
                if scenario not in student.weak_scenarios:
                    student.weak_scenarios.append(scenario)
            severity = "CRITICO" if wr < self.DEGRADE_THRESHOLD else "PERDE"
            best = SCENARIO_BEST_PRACTICE.get(scenario, ())
            dica = f"Em {scenario}, use {best[0]}." if best else ""
            lesson = Lesson(
                "intervention",
                f"PROFESSOR [{severity}]: {sid} PERDE em {scenario} — {wr*100:.1f}% em "
                f"{trades} trades (abaixo de cara-ou-coroa). Isso e vantagem NEGATIVA comprovada. "
                f"{dica} Considere inverter o sinal ou tirar {sid} deste cenario.",
                strategy_id=sid,
                scenario=scenario,
            )
            lessons.append(lesson)
            self._log_lesson(lesson)

        # System degradation: 3 cycles declining
        if len(self.recent_cycle_wr) >= 3:
            last3 = list(self.recent_cycle_wr)[-3:]
            if last3[0] > last3[1] > last3[2] and last3[2] < 0.45:
                self.remedial_mode = True
                lesson = Lesson(
                    "class_alert",
                    "TURMA INTEIRA PIORANDO — 3 ciclos seguidos em queda. "
                    "Modo BASICO ativado: so estrategias S09 (Capital Shield) e S05 (Scalp) ate estabilizar.",
                )
                lessons.append(lesson)
                self._log_lesson(lesson)
            elif last3[2] > 0.55 and self.remedial_mode:
                self.remedial_mode = False
                lesson = Lesson(
                    "class_recovery",
                    "Turma estabilizou. Modo normal retomado — continuem evoluindo com disciplina.",
                )
                lessons.append(lesson)
                self._log_lesson(lesson)

        # Build wisdom from proven winners
        for key, bucket in leaderboard_stats.items():
            trades = bucket.get("trades", 0)
            wr = bucket.get("win_rate", 0)
            if trades >= 8 and wr >= 0.65:
                rule = {
                    "scenario": bucket.get("scenario"),
                    "strategy_id": bucket.get("strategy_id"),
                    "pair": bucket.get("pair"),
                    "win_rate": wr,
                    "trades": trades,
                    "rule": f"Em {bucket.get('scenario')}, {bucket.get('strategy_id')} + {bucket.get('pair')} "
                    f"funciona ({wr*100:.0f}% em {trades} trades).",
                }
                if rule not in self.wisdom_rules:
                    self.wisdom_rules.append(rule)
                    if len(self.wisdom_rules) > 100:
                        self.wisdom_rules = self.wisdom_rules[-100:]

        # Grava o PLAYBOOK — as vantagens comprovadas. Este e o produto util do
        # treino: onde o Doug realmente tem edge, com base estatistica.
        # Grava TODOS os edges qualificados, sem corte artificial. Um corte
        # fixo (ex.: top 50) fazia pares com edge real, so que fora do topo
        # global por win_rate, sumirem da lista monitorada pela Torre de
        # Controle entre um ciclo de treino e outro (achado real 2026-07-09:
        # JD25 tinha edge comprovado e desapareceu do Playbook so porque
        # ficou na posicao 51+ depois de um novo treino, nao porque parou de
        # funcionar). O arquivo continua pequeno (poucas centenas de linhas
        # no maximo, dado MIN_TRADES_FOR_JUDGMENT + GOOD_BAR), sem custo real.
        edges = self.proven_edges(leaderboard_stats)
        try:
            PLAYBOOK_PATH.write_text(
                json.dumps({
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "edge_bar": self.EDGE_BAR,
                    "min_trades": self.MIN_TRADES_FOR_JUDGMENT,
                    "total_edges": len(edges),
                    "edges": edges,
                }, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError:
            pass

        self.save()
        return lessons

    def pick_training_focus(
        self,
        all_pairs: tuple[str, ...],
        all_strategies: tuple[StrategySpec, ...],
        *,
        weak_buckets: list[dict[str, Any]] | None = None,
    ) -> tuple[str, StrategySpec]:
        """Professor escolhe proximo exercicio — foco em fraquezas, nao aleatorio cego."""
        import random

        drill = self.pop_next_drill()
        if drill:
            # Conta esta selecao como uma tentativa, nao importa se o resultado
            # vai ser vitoria, derrota ou hold — sem isso, uma combinacao que so
            # da "hold" repetido nunca perde (entao nunca soma tentativa via
            # review_result) e nunca ganha (entao nunca sai da fila): fica presa
            # para sempre sendo forcada. Achado real em 2026-07-06: S09|BOOM500|
            # trending_up travou em "attempts: 8" por dezenas de ciclos seguidos,
            # sempre em hold, sem nunca resolver.
            drill.attempts += 1
            if drill.attempts >= self.MAX_DRILL_ATTEMPTS:
                target = drill.key()
                self.pending_drills = deque(
                    (d for d in self.pending_drills if d.key() != target),
                    maxlen=50,
                )
                self.broken_combos.add(target)
                self._log_lesson(
                    Lesson(
                        "broken_combo",
                        f"DESISTINDO — {drill.strategy_id} em {drill.scenario} ({drill.pair}) foi "
                        f"forcado {self.MAX_DRILL_ATTEMPTS}x sem nunca resolver (vitoria ou "
                        f"{self.MAX_DRILL_ATTEMPTS} derrotas). Provavel que o sinal so retorna "
                        f"'hold' nesse par/cenario — precisa de revisao de codigo, nao mais treino.",
                        strategy_id=drill.strategy_id,
                        scenario=drill.scenario,
                        pair=drill.pair,
                    )
                )
            strat = next((s for s in all_strategies if s.id == drill.strategy_id), all_strategies[0])
            pair = drill.pair if drill.pair in all_pairs else random.choice(all_pairs)
            return pair, strat

        if self.remedial_mode:
            safe = [s for s in all_strategies if s.id in ("S09", "S05")]
            return random.choice(all_pairs), random.choice(safe or list(all_strategies))

        remedial_students = [p for p in self.students.values() if p.remedial]
        if remedial_students:
            student = random.choice(remedial_students)
            scenario = random.choice(student.weak_scenarios) if student.weak_scenarios else "ranging"
            best_ids = SCENARIO_BEST_PRACTICE.get(scenario, ("S09",))
            strat = next((s for s in all_strategies if s.id in best_ids), all_strategies[0])
            return random.choice(all_pairs), strat

        weak = weak_buckets or []
        if weak and random.random() < 0.7:
            bucket = random.choice(weak)
            sid = bucket.get("strategy_id", "")
            pair = bucket.get("pair") or random.choice(all_pairs)
            strat = next((s for s in all_strategies if s.id == sid), random.choice(all_strategies))
            return pair, strat

        return random.choice(all_pairs), random.choice(all_strategies)

    def weak_buckets_from_leaderboard(self, stats: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        # Fraco de verdade = perde com amostra significativa. Sem isso, o foco
        # de treino era guiado por ruido (buckets de 3 trades).
        return [
            b for b in stats.values()
            if b.get("trades", 0) >= self.MIN_TRADES_FOR_JUDGMENT and b.get("win_rate", 1) < self.LOSING_BAR
        ]

    GOOD_BAR = 0.60  # 60-80% = vantagem BOA (onde os fundos ganham dinheiro de verdade)

    def proven_edges(self, stats: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        """O PRODUTO REAL do aprendizado, em dois niveis (com amostra >= 30):
          - ELITE (>= 80%): o creme do creme, raro, o selo de excelencia.
          - BOM  (60-80%): onde o dinheiro REAL esta. Fundos bilionarios operam
            com 58-65% de acerto + gestao de risco. Nao ignore este nivel so
            porque nao chegou a 80% — e aqui que se ganha de forma consistente.
        Ambos exigem amostra significativa para nao serem sorte.

        Exige tambem expectancy_pct > 0 conhecida (mesmo criterio ja usado em
        decision_engine._vote_weight e backtester.run_backtest). Sem isto, um
        bucket so com win_rate alto podia entrar no Playbook mesmo perdendo
        dinheiro na pratica (ganha muitas vezes pouco, perde raro mas MUITO —
        exatamente o perfil de risco de BOOM/CRASH). Isto tambem separa por
        construcao o treino de tick (continuous_trainer, que nunca calcula
        expectancy_pct e por isso e ruido de microestrutura, achado real
        2026-07-09: um bucket la tinha 1325 trades e win_rate 0.08%) do
        backtest walk-forward real (M38, que sempre grava expectancy_pct) —
        so o segundo alimenta o Playbook que a Torre de Controle usa pra
        decidir OPERAR."""
        edges = []
        for b in stats.values():
            wr = b.get("win_rate", 0)
            if b.get("trades", 0) < self.MIN_TRADES_FOR_JUDGMENT or wr < self.GOOD_BAR:
                continue
            expectancy = b.get("expectancy_pct")
            if expectancy is None or expectancy <= 0:
                continue
            # DSR (Deflated Sharpe Ratio): passa junto por transparencia — mostra
            # se este edge sobrevive a correcao estatistica pelo numero de
            # combinacoes testadas no lote (protecao contra data snooping). O
            # gate de OPERAR (decision_engine.py) e quem efetivamente barra
            # edges com DSR baixo antes de arriscar stake; aqui so anota.
            dsr = b.get("dsr")
            edges.append({
                "strategy_id": b.get("strategy_id"), "scenario": b.get("scenario"),
                "pair": b.get("pair"), "win_rate": wr, "trades": b.get("trades"),
                "expectancy_pct": expectancy, "dsr": dsr,
                "nivel": "ELITE" if wr >= self.EDGE_BAR else "BOM",
            })
        edges.sort(key=lambda e: (e["win_rate"], e["trades"]), reverse=True)
        return edges

    def _read_playbook(self) -> list[dict[str, Any]]:
        if PLAYBOOK_PATH.exists():
            try:
                return json.loads(PLAYBOOK_PATH.read_text(encoding="utf-8")).get("edges", [])[:10]
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def report(self) -> dict[str, Any]:
        return {
            "remedial_mode": self.remedial_mode,
            "accuracy_goal": self.ACCURACY_GOAL,
            "pending_drills": len(self.pending_drills),
            "broken_combos": [list(c) for c in self.broken_combos],
            "recent_cycle_wr": list(self.recent_cycle_wr),
            "students": [p.to_dict() for p in self.students.values()],
            "wisdom_count": len(self.wisdom_rules),
            "top_wisdom": self.wisdom_rules[-10:],
            "playbook_edges": self._read_playbook(),
            "accuracy_leaders": sorted(
                [p.to_dict() for p in self.students.values()],
                key=lambda x: -x.get("accuracy_streak", 0),
            )[:5],
            "levels_summary": {
                LEVEL_NAMES[i]: sum(1 for p in self.students.values() if p.level == i + 1)
                for i in range(len(LEVEL_NAMES))
            },
        }
