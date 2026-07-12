import tempfile

from doug_os.memory.experience_store import ExperienceStore
from doug_os.memory.probability_engine import ProbabilityEngine


def test_probability_engine_no_data():
    """When no experiences exist for a context, probabilities should default to zero."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ExperienceStore(db_path=f"{tmpdir}/test.db")
        engine = ProbabilityEngine(store)
        result = engine.estimate({"price": 1})
        assert result["win_probability"] == 0.0
        assert result["recurrence"] == 0
        assert result["confidence"] == 0.0
        assert result["recommendation"] == "UNSURE"


def test_probability_engine_with_data():
    """ProbabilityEngine should compute win probability, recurrence and confidence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ExperienceStore(db_path=f"{tmpdir}/test.db")
        # same context repeated with different results
        ctx = {"price": 10, "volume": 5}
        # two wins and one loss
        store.save(ctx, regime="bull", decision="BUY", result="WIN", pnl=5)
        store.save(ctx, regime="bull", decision="BUY", result="WIN", pnl=8)
        store.save(ctx, regime="bull", decision="SELL", result="LOSS", pnl=-3)
        engine = ProbabilityEngine(store)
        res = engine.estimate(ctx)
        # 2 wins out of 3 -> win prob ~ 0.6667
        assert abs(res["win_probability"] - 0.6667) < 1e-4
        # recurrence equals 3
        assert res["recurrence"] == 3
        # confidence = 3/10 = 0.3
        assert abs(res["confidence"] - 0.3) < 1e-6
        # recommendation should be WIN (>= 0.6)
        assert res["recommendation"] == "WIN"