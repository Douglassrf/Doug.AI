"""Testes offline da deteccao de tendencia por regressao (training/strategy_trend.py).
Os limiares (DECLINE_SLOPE/GROWTH_SLOPE) e a validacao preditiva real deste
modulo foram checados por simulacao walk-forward contra
data/training/sessions.jsonl (ver conversa/commit): buckets rotulados
"declining" na 1a metade do historico tiveram win rate medio de 35.9% na 2a
metade (fora da amostra), contra 62.8% dos "stable" -- este arquivo so cobre a
matematica pura da regressao em si."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.strategy_trend import (  # noqa: E402
    MIN_SAMPLES_FOR_TREND,
    bucket_trend,
    trend_label,
    trend_slope,
)


class TestTrendSlope:
    def test_insufficient_samples_is_none(self):
        assert trend_slope([1.0] * (MIN_SAMPLES_FOR_TREND - 1)) is None

    def test_clear_decline_has_negative_slope(self):
        history = [float(20 - i) for i in range(20)]  # 20,19,...,1
        slope = trend_slope(history)
        assert slope is not None and slope < 0

    def test_clear_growth_has_positive_slope(self):
        history = [float(i) for i in range(20)]  # 0,1,...,19
        slope = trend_slope(history)
        assert slope is not None and slope > 0

    def test_flat_history_has_near_zero_slope(self):
        history = [0.5] * 20
        slope = trend_slope(history)
        assert slope is not None and abs(slope) < 1e-9

    def test_only_uses_recent_window(self):
        # 100 valores caindo, seguidos de 20 estaveis -- so a janela recente conta
        declining_tail = [float(100 - i) for i in range(80)]
        flat_tail = [10.0] * 20
        history = declining_tail + flat_tail
        slope = trend_slope(history)
        assert slope is not None and abs(slope) < 1e-9


class TestTrendLabel:
    def test_none_slope_is_insufficient_data(self):
        assert trend_label(None) == "insufficient_data"

    def test_decline_threshold(self):
        assert trend_label(-0.02) == "declining"

    def test_growth_threshold(self):
        assert trend_label(0.02) == "improving"

    def test_neutral_zone_is_stable(self):
        assert trend_label(0.0) == "stable"


class TestBucketTrend:
    def test_reports_slope_label_and_sample_size(self):
        history = [float(i) for i in range(30)]  # crescendo, 30 amostras
        result = bucket_trend(history)
        assert result["label"] == "improving"
        assert result["samples"] == 20  # RECENT_WINDOW, nao o total de 30
        assert result["slope"] > 0
