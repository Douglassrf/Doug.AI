import os
import tempfile

from doug_os.memory.experience_store import ExperienceStore
from doug_os.memory.probability_engine_v2 import ProbabilityEngineV2


def test_weighted_probabilities_emphasise_recency(tmp_path):
    # Use a temporary database
    db_path = tmp_path / "exp.db"
    store = ExperienceStore(db_path=str(db_path))
    engine = ProbabilityEngineV2(store)
    context = {"scenario": 1}
    # Save three experiences with pattern context; results: WIN, LOSS, WIN
    store.save(context, regime="bull", decision="BUY", result="WIN", pnl=1.0)
    store.save(context, regime="bull", decision="SELL", result="LOSS", pnl=-1.0)
    store.save(context, regime="bull", decision="BUY", result="WIN", pnl=2.0)
    # Weighted: weights 1, 2, 3 -> win_weight=1*1 + 2*0 + 3*1 = 4; total=6 -> 4/6=0.6667
    stats = engine.estimate(context)
    assert abs(stats["win_probability"] - 0.6667) < 0.01
    # Recurrence weighted should be 6.0
    assert abs(stats["recurrence"] - 6.0) < 0.1
    # Confidence saturates at 6/5=1.2 -> 1.0
    assert stats["confidence"] == 1.0
    assert stats["recommendation"] == "WIN"


def test_regime_weighting_increases_influence(tmp_path):
    db_path = tmp_path / "exp2.db"
    store = ExperienceStore(db_path=str(db_path))
    engine = ProbabilityEngineV2(store)
    context = {"scenario": 2}
    # Save experiences with mixed regimes
    store.save(context, regime="bear", decision="BUY", result="WIN", pnl=1.0)  # id 1
    store.save(context, regime="bull", decision="SELL", result="LOSS", pnl=-1.0)  # id 2
    store.save(context, regime="bull", decision="BUY", result="WIN", pnl=2.0)  # id 3
    # Without regime param: weights 1,2,3 -> win_weight=1+0+3=4; total=6 -> 0.6667
    stats_no_reg = engine.estimate(context)
    # With regime 'bull': weight for id2 and id3 multiplied by 1.5 -> weights: id1=1, id2=2*1.5=3, id3=3*1.5=4.5 -> total=8.5; win_weight=1+0+4.5=5.5 -> 5.5/8.5=0.6471
    stats_bull = engine.estimate(context, regime="bull")
    assert abs(stats_no_reg["win_probability"] - 0.6667) < 0.01
    assert abs(stats_bull["win_probability"] - 0.6471) < 0.01
    # Weighted recurrence increases when matching regime
    assert stats_bull["recurrence"] > stats_no_reg["recurrence"]