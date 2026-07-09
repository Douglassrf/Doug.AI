"""Testes offline (sem rede) do DSR (training/stats_validation.py) e do livro-razao
de paper trading / kill-switch / veredito protetor (training/paper_ledger.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training import paper_ledger  # noqa: E402
from training.stats_validation import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402


class TestDeflatedSharpeRatio:
    def test_more_trials_deflates_same_sharpe(self):
        few = deflated_sharpe_ratio(0.3, trials=10, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=300)
        many = deflated_sharpe_ratio(0.3, trials=500, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=300)
        assert many < few, "testar mais combinacoes deve reduzir a confianca no mesmo Sharpe observado"

    def test_zero_sharpe_is_never_significant(self):
        dsr = deflated_sharpe_ratio(0.0, trials=50, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=300)
        assert dsr < 0.05

    def test_small_sample_deflates_more_than_large_sample(self):
        small_n = deflated_sharpe_ratio(0.3, trials=10, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=20)
        large_n = deflated_sharpe_ratio(0.3, trials=10, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=300)
        assert small_n < large_n

    def test_expected_max_sharpe_grows_with_trials(self):
        assert expected_max_sharpe(500, 0.1) > expected_max_sharpe(10, 0.1)

    def test_no_sample_returns_zero(self):
        assert deflated_sharpe_ratio(0.5, trials=10, sharpe_std=0.1, skew=0.0, kurtosis=3.0, n_obs=1) == 0.0


class TestPaperLedger:
    def _use_tmp_paths(self, tmp_path, monkeypatch):
        monkeypatch.setattr(paper_ledger, "TRAINING_DIR", tmp_path)
        monkeypatch.setattr(paper_ledger, "OPEN_POSITIONS_PATH", tmp_path / "paper_open_positions.json")
        monkeypatch.setattr(paper_ledger, "LEDGER_PATH", tmp_path / "paper_trades.jsonl")
        monkeypatch.setattr(paper_ledger, "EQUITY_PATH", tmp_path / "paper_equity.json")

    def test_record_and_resolve_winning_position(self, tmp_path, monkeypatch):
        self._use_tmp_paths(tmp_path, monkeypatch)
        paper_ledger.record_open_position(
            pair="TEST", scenario="ranging", strategy_id="S01",
            direction="buy", entry=100.0, stake_pct=2.0,
        )
        # forca o horizonte ja ter passado
        import json as _json
        positions = _json.loads(paper_ledger.OPEN_POSITIONS_PATH.read_text(encoding="utf-8"))
        from datetime import datetime, timedelta, timezone
        positions[0]["opened_at"] = (
            datetime.now(timezone.utc) - timedelta(seconds=paper_ledger.HORIZON_SECONDS + 5)
        ).isoformat()
        paper_ledger._save_json(paper_ledger.OPEN_POSITIONS_PATH, positions)

        resolved = paper_ledger.resolve_pending_positions(lambda pair: 105.0)
        assert len(resolved) == 1
        assert resolved[0]["won"] is True
        equity = paper_ledger.equity_snapshot()
        assert equity["equity_pct"] > 100.0
        assert equity["resolved_trades"] == 1

    def test_position_not_resolved_before_horizon(self, tmp_path, monkeypatch):
        self._use_tmp_paths(tmp_path, monkeypatch)
        paper_ledger.record_open_position(
            pair="TEST", scenario="ranging", strategy_id="S01",
            direction="buy", entry=100.0, stake_pct=2.0,
        )
        resolved = paper_ledger.resolve_pending_positions(lambda pair: 999.0)
        assert resolved == []

    def test_kill_switch_trips_on_drawdown_and_resets_with_hysteresis(self, tmp_path, monkeypatch):
        self._use_tmp_paths(tmp_path, monkeypatch)
        paper_ledger._save_json(paper_ledger.EQUITY_PATH, {
            "equity_pct": 100.0, "peak_pct": 100.0, "drawdown_pct": 0.0,
            "kill_switch_active": False, "resolved_trades": 0, "updated_at": None,
        })
        # Uma posicao perdedora GIGANTE o suficiente pra estourar 15% de drawdown
        paper_ledger.record_open_position(
            pair="TEST", scenario="ranging", strategy_id="S01",
            direction="buy", entry=100.0, stake_pct=100.0,
        )
        import json as _json
        from datetime import datetime, timedelta, timezone
        positions = _json.loads(paper_ledger.OPEN_POSITIONS_PATH.read_text(encoding="utf-8"))
        positions[0]["opened_at"] = (
            datetime.now(timezone.utc) - timedelta(seconds=paper_ledger.HORIZON_SECONDS + 5)
        ).isoformat()
        paper_ledger._save_json(paper_ledger.OPEN_POSITIONS_PATH, positions)

        paper_ledger.resolve_pending_positions(lambda pair: 80.0)  # -20% move, buy = perda grande
        assert paper_ledger.is_kill_switch_active() is True

        # Drawdown ainda alto (nao recuperou abaixo do reset) -> continua ativo
        equity = paper_ledger.equity_snapshot()
        assert equity["drawdown_pct"] >= paper_ledger.KILL_SWITCH_DRAWDOWN_PCT

    def test_rolling_bucket_health_trips_on_recent_losses(self, tmp_path, monkeypatch):
        self._use_tmp_paths(tmp_path, monkeypatch)
        import json as _json
        with paper_ledger.LEDGER_PATH.open("w", encoding="utf-8") as f:
            for i in range(10):
                won = i < 3  # 3 wins (i=0..2), 7 losses (i=3..9) -> tripped
                f.write(_json.dumps({
                    "strategy_id": "S01", "pair": "TEST", "scenario": "ranging", "won": won,
                }) + "\n")
        health = paper_ledger.rolling_bucket_health("S01", "TEST", "ranging")
        assert health["n"] == 10
        assert health["losses"] == 7
        assert health["tripped"] is True

    def test_rolling_bucket_health_not_tripped_with_good_recent_record(self, tmp_path, monkeypatch):
        self._use_tmp_paths(tmp_path, monkeypatch)
        import json as _json
        with paper_ledger.LEDGER_PATH.open("w", encoding="utf-8") as f:
            for i in range(10):
                won = i < 6  # 6 wins, 4 losses -> nao tripped
                f.write(_json.dumps({
                    "strategy_id": "S01", "pair": "TEST", "scenario": "ranging", "won": won,
                }) + "\n")
        health = paper_ledger.rolling_bucket_health("S01", "TEST", "ranging")
        assert health["tripped"] is False
