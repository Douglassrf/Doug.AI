"""Testes offline do EWMA de volatilidade e do CUSUM de mudanca de regime
(training/volatility.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.volatility import cusum_change_points, ewma_volatility, regime_shift_alert  # noqa: E402


class TestEwmaVolatility:
    def test_weights_recent_shock_more_than_old_shock(self):
        # Choque grande no INICIO da serie, resto quieto
        shock_early = [0.05] + [0.001] * 30
        # Choque grande no FIM da serie, resto quieto
        shock_late = [0.001] * 30 + [0.05]
        vol_early = ewma_volatility(shock_early)
        vol_late = ewma_volatility(shock_late)
        assert vol_late > vol_early, "EWMA deve reagir mais a um choque recente do que a um choque antigo"

    def test_constant_returns_give_stable_volatility(self):
        returns = [0.001] * 20
        vol = ewma_volatility(returns)
        assert abs(vol - 0.001) < 1e-9

    def test_empty_or_single_return_is_zero(self):
        assert ewma_volatility([]) == 0.0
        assert ewma_volatility([0.01]) == 0.0


class TestCusum:
    def test_detects_clear_mean_shift(self):
        # 40 retornos em torno de 0, depois 20 retornos com deriva forte e persistente
        returns = [0.0001 if i % 2 == 0 else -0.0001 for i in range(40)] + [0.01] * 20
        points = cusum_change_points(returns)
        assert points, "CUSUM deveria detectar a quebra de regime"
        assert points[-1] >= 40, "o alarme deve cair dentro do trecho com deriva, nao antes"

    def test_no_false_alarm_on_pure_noise_like_pattern(self):
        returns = [0.0001 if i % 2 == 0 else -0.0001 for i in range(50)]
        points = cusum_change_points(returns)
        assert points == []

    def test_short_series_returns_no_points(self):
        assert cusum_change_points([0.001] * 5) == []


class TestRegimeShiftAlert:
    def test_flags_recent_shift(self):
        prices = [100.0]
        for _ in range(40):
            prices.append(prices[-1] * 1.0001)
        for _ in range(15):
            prices.append(prices[-1] * 1.01)  # quebra forte no final
        alert = regime_shift_alert(prices)
        assert alert["shift_detected"] is True

    def test_no_shift_on_smooth_series(self):
        prices = [100.0]
        for _ in range(60):
            prices.append(prices[-1] * 1.0001)
        alert = regime_shift_alert(prices)
        assert alert["shift_detected"] is False
