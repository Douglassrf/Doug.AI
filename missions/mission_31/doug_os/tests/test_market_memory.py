import tempfile

from doug_os.memory.experience_store import ExperienceStore


def test_experience_store_save_and_similar():
    """ExperienceStore should save and retrieve experiences by pattern hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test.db"
        store = ExperienceStore(db_path=db_path)
        context = {"price": 10, "volume": 5}
        # save an experience
        store.save(context, regime="bull", decision="BUY", result="WIN", pnl=5.0)
        # retrieving similar experiences should return one record with matching fields
        experiences = store.similar(context)
        assert len(experiences) == 1
        exp = experiences[0]
        assert exp["context"] == context
        assert exp["regime"] == "bull"
        assert exp["decision"] == "BUY"
        assert exp["result"] == "WIN"
        assert exp["pnl"] == 5.0
        # unrelated context yields empty list
        assert store.similar({"price": 20}) == []