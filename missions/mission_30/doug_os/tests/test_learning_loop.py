import tempfile

from doug_os.memory.experience_store import ExperienceStore
from doug_os.memory.probability_engine import ProbabilityEngine
from doug_os.memory.learning_loop import LearningLoop


def test_learning_loop_updates_probabilities():
    """LearningLoop should save experiences and return updated metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ExperienceStore(db_path=f"{tmpdir}/store.db")
        engine = ProbabilityEngine(store)
        loop = LearningLoop(store, engine)
        ctx = {"price": 100}
        # First experience: WIN
        metrics1 = loop.process_experience(ctx, regime="bull", decision="BUY", result="WIN", pnl=10.0)
        assert metrics1["win_probability"] == 1.0
        assert metrics1["recurrence"] == 1
        assert metrics1["confidence"] == 0.1  # 1/10
        assert metrics1["recommendation"] == "WIN"
        assert metrics1["original_decision"] == "BUY"
        # Second experience: LOSS
        metrics2 = loop.process_experience(ctx, regime="bull", decision="BUY", result="LOSS", pnl=-5.0)
        assert metrics2["win_probability"] == 0.5
        assert metrics2["recurrence"] == 2
        # confidence should now be 0.2
        assert metrics2["confidence"] == 0.2
        # recommendation becomes UNSURE as prob is between 0.4 and 0.6
        assert metrics2["recommendation"] == "UNSURE"