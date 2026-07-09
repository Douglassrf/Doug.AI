"""Testes offline (sem rede) do backtester M38 e do cerebro de decisao."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.backtester import BucketStats, walk_forward_pair  # noqa: E402
from training.decision_engine import _kelly_stake, _vote_weight, apply_news_filter  # noqa: E402
from training.news_feed import _score_impact, _score_sentiment, summarize_topic, topic_for_pair  # noqa: E402


def _trending_up_closes(n: int = 120, start: float = 100.0, step: float = 0.05) -> list[float]:
    # Tendencia clara com micro-oscillacao deterministica (sem aleatoriedade nos testes)
    return [start + i * step + (0.01 if i % 2 else -0.01) for i in range(n)]


class TestWalkForward:
    def test_generates_many_trades_from_one_series(self):
        closes = _trending_up_closes()
        stats = walk_forward_pair("TEST_PAIR", closes, horizon=3)
        total = sum(b.trades for b in stats.values())
        assert total > 50, "walk-forward deve extrair dezenas de trades de uma serie"

    def test_no_lookahead_window(self):
        # Serie curta demais para o primeiro sinal nao deve gerar trade algum
        closes = _trending_up_closes(n=15)
        stats = walk_forward_pair("TEST_PAIR", closes, horizon=3)
        assert stats == {}

    def test_trend_strategies_win_in_clean_uptrend(self):
        closes = _trending_up_closes()
        stats = walk_forward_pair("TEST_PAIR", closes, horizon=3)
        # Momentum (S01) em tendencia limpa de alta deve ter WR alto e expectancy > 0
        s01 = [b for k, b in stats.items() if k.startswith("S01|")]
        assert s01, "S01 deve operar em tendencia de alta"
        agg_wins = sum(b.wins for b in s01)
        agg_trades = sum(b.trades for b in s01)
        assert agg_wins / agg_trades > 0.8
        assert all(b.expectancy_pct > 0 for b in s01 if b.trades >= 5)

    def test_bucket_stats_consistency(self):
        closes = _trending_up_closes()
        stats = walk_forward_pair("TEST_PAIR", closes, horizon=2)
        for bucket in stats.values():
            assert bucket.trades == bucket.wins + bucket.losses
            assert 0.0 <= bucket.win_rate <= 1.0
            assert math.isfinite(bucket.expectancy_pct)

    def test_accumulates_into_existing_stats(self):
        closes = _trending_up_closes()
        stats = walk_forward_pair("PAIR_A", closes, horizon=3)
        n_keys = len(stats)
        stats = walk_forward_pair("PAIR_B", closes, horizon=3, stats=stats)
        assert len(stats) > n_keys
        assert any(k.split("|")[1] == "PAIR_A" for k in stats)
        assert any(k.split("|")[1] == "PAIR_B" for k in stats)


class TestVoteWeight:
    def test_no_history_means_zero_weight(self):
        assert _vote_weight(None, 0, None) == 0.0

    def test_edge_scales_with_sample(self):
        small = _vote_weight(0.70, 10, 0.01)
        large = _vote_weight(0.70, 50, 0.01)
        assert 0 < small < large

    def test_bad_history_gives_negative_weight(self):
        assert _vote_weight(0.40, 50, None) < 0

    def test_positive_wr_with_negative_expectancy_is_zeroed(self):
        # Ganha com frequencia mas perde mais quando perde: sem vantagem real
        assert _vote_weight(0.70, 50, -0.05) == 0.0

    def test_coin_flip_is_zero(self):
        assert _vote_weight(0.50, 100, 0.0) == 0.0


class TestKellyStake:
    def test_no_edge_no_stake(self):
        assert _kelly_stake(0.50) == 0.0
        assert _kelly_stake(0.40) == 0.0

    def test_stake_grows_with_edge_but_is_capped(self):
        s52 = _kelly_stake(0.52)  # edge pequeno: abaixo do teto
        s53 = _kelly_stake(0.53)
        assert 0 < s52 < s53
        # Edges grandes batem no teto duro de 2% do capital
        assert _kelly_stake(0.75) == 2.0
        assert _kelly_stake(0.99) == 2.0


class TestNewsScoring:
    def test_bullish_headline_positive(self):
        assert _score_sentiment("Bitcoin surges to record high after ETF approval") > 0

    def test_bearish_headline_negative(self):
        assert _score_sentiment("Crypto crash deepens as panic selloff hits exchanges") < 0

    def test_neutral_headline_zero(self):
        assert _score_sentiment("Company announces quarterly meeting schedule") == 0.0

    def test_impact_detects_fed_and_hack(self):
        assert _score_impact("Federal Reserve rate decision looms") > 0
        assert _score_impact("Exchange hack drains wallets") > 0
        assert _score_impact("Local bakery opens new branch") == 0.0

    def test_topic_mapping(self):
        assert topic_for_pair("cryBTCUSD") == "crypto"
        assert topic_for_pair("frxEURUSD") == "macro"
        assert topic_for_pair("R_25") is None  # sintetico: imune a noticias

    def test_summarize_topic_empty(self):
        s = summarize_topic([])
        assert s["risk"] == 0.0 and s["bias"] == 0.0


class TestNewsFilter:
    def _snap(self, topic: str, bias: float, risk: float) -> dict:
        return {"summary": {topic: {"bias": bias, "risk": risk, "top_headline": "manchete X"}}}

    def test_synthetic_pair_immune(self):
        level, reasons = apply_news_filter("OPERAR", "buy", "R_25", self._snap("crypto", -1.0, 1.0))
        assert level == "OPERAR" and reasons == []

    def test_hot_news_downgrades_operar(self):
        level, reasons = apply_news_filter("OPERAR", "buy", "cryBTCUSD", self._snap("crypto", 0.0, 0.9))
        assert level == "OBSERVAR"
        assert any("erratico" in r or "QUENTE" in r for r in reasons)

    def test_strong_contrary_sentiment_blocks(self):
        level, _ = apply_news_filter("OPERAR", "buy", "cryBTCUSD", self._snap("crypto", -0.6, 0.2))
        assert level == "FICAR_DE_FORA"
        # Sentimento negativo NAO barra um sell (esta a favor)
        level2, _ = apply_news_filter("OPERAR", "sell", "cryBTCUSD", self._snap("crypto", -0.6, 0.2))
        assert level2 == "OPERAR"

    def test_calm_news_keeps_level(self):
        level, _ = apply_news_filter("OPERAR", "buy", "cryBTCUSD", self._snap("crypto", 0.1, 0.2))
        assert level == "OPERAR"

    def test_no_snapshot_is_neutral(self):
        level, reasons = apply_news_filter("OPERAR", "buy", "cryBTCUSD", None)
        assert level == "OPERAR"
        assert reasons  # avisa que o radar esta sem snapshot


class TestBucketStats:
    def test_expectancy_math(self):
        b = BucketStats("S01", "X", "ranging")
        b.trades, b.wins, b.losses = 4, 3, 1
        b.sum_move_pct = 0.8
        assert b.win_rate == 0.75
        assert abs(b.expectancy_pct - 0.2) < 1e-9
        d = b.to_dict()
        assert d["win_rate"] == 0.75
        assert d["expectancy_pct"] == 0.2
