"""Tests for Whale Mirror Engine (Missão 29)."""

from doug_os.onchain import WhaleMirrorEngine


def test_whale_mirror_engine_processing_and_scores() -> None:
    engine = WhaleMirrorEngine(whale_threshold=100_000)
    txs_round1 = [
        {"sender": "0xWhaleA", "receiver": "0xX", "amount": 150_000},
        {"sender": "0xWhaleB", "receiver": "0xY", "amount": 250_000},
        {"sender": "0xSmall", "receiver": "0xZ", "amount": 10_000},  # ignored
    ]
    engine.process_transactions(txs_round1)
    scores = engine.get_influence_scores()
    assert set(scores.keys()) == {"0xwhalea", "0xwhaleb"}
    # after first round volumes: 150k and 250k → total 400k → scores 0.375 and 0.625
    assert abs(scores["0xwhalea"] - 0.375) < 1e-6
    assert abs(scores["0xwhaleb"] - 0.625) < 1e-6

    # second round adds more volume to WhaleA
    txs_round2 = [
        {"sender": "0xWhaleA", "receiver": "0xW", "amount": 200_000},
        {"sender": "0xWhaleC", "receiver": "0xZ", "amount": 500_000},
    ]
    engine.process_transactions(txs_round2)
    scores = engine.get_influence_scores()
    # volumes: WhaleA=350k, WhaleB=250k, WhaleC=500k → total=1.1M
    assert abs(scores["0xwhalea"] - 350_000 / 1_100_000) < 1e-6
    assert abs(scores["0xwhaleb"] - 250_000 / 1_100_000) < 1e-6
    assert abs(scores["0xwhalec"] - 500_000 / 1_100_000) < 1e-6
    # top 2 whales should be C then A
    top2 = engine.get_top_whales(n=2)
    assert top2[0][0] == "0xwhalec"
    assert top2[1][0] == "0xwhalea"