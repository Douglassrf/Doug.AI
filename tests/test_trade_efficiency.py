"""Testes offline do MFE/MAE de eficiencia de saida (training/trade_efficiency.py).
Nao testa fetch_trade_path (rede) -- mesmo criterio ja usado para
training.backtester.fetch_candles_sync (tests/test_backtester_decision.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.trade_efficiency import analyze_trade, exit_efficiency, mfe_mae  # noqa: E402


class TestMfeMae:
    def test_buy_mfe_is_best_high_above_entry(self):
        result = mfe_mae("buy", entry=100.0, path_highs=[100.5, 102.0, 101.0], path_lows=[99.5, 99.0, 100.2])
        assert abs(result["mfe_pct"] - 2.0) < 1e-9  # (102-100)/100
        assert abs(result["mae_pct"] - 1.0) < 1e-9  # (100-99)/100

    def test_sell_mfe_is_best_low_below_entry(self):
        result = mfe_mae("sell", entry=100.0, path_highs=[100.5, 101.5, 100.2], path_lows=[99.0, 98.5, 99.8])
        assert abs(result["mfe_pct"] - 1.5) < 1e-9  # (100-98.5)/100
        assert abs(result["mae_pct"] - 1.5) < 1e-9  # (101.5-100)/100

    def test_no_path_data_returns_zero(self):
        result = mfe_mae("buy", entry=100.0, path_highs=[], path_lows=[])
        assert result == {"mfe_pct": 0.0, "mae_pct": 0.0}


class TestExitEfficiency:
    def test_perfect_exit_at_the_peak(self):
        assert exit_efficiency(realized_move_pct=2.0, mfe_pct=2.0) == 1.0

    def test_partial_capture(self):
        assert exit_efficiency(realized_move_pct=1.0, mfe_pct=2.0) == 0.5

    def test_no_favorable_excursion_is_zero_not_negative(self):
        assert exit_efficiency(realized_move_pct=0.5, mfe_pct=0.0) == 0.0

    def test_clamped_at_one_even_if_realized_exceeds_mfe(self):
        # nao deveria acontecer na pratica (mfe e por definicao o maximo), mas a
        # funcao nao deve estourar 1.0 por causa de arredondamento externo
        assert exit_efficiency(realized_move_pct=3.0, mfe_pct=2.0) == 1.0


class TestAnalyzeTrade:
    def test_full_report_matches_components(self):
        report = analyze_trade(
            direction="buy", entry=100.0, exit_price=101.0, realized_move_pct=1.0,
            path_highs=[100.5, 102.0], path_lows=[99.5, 100.0],
        )
        assert report["mfe_pct"] == 2.0
        assert report["exit_efficiency"] == 0.5
        assert report["gave_back_pct"] == 1.0  # deixou 1.0% na mesa (2.0 - 1.0)
