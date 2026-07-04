import pytest
from discovery.capital_router import CapitalRouter, AssetOpportunity, CapitalAllocation


def _candidate(asset, cluster, conf=0.7, rq=0.7, liq=1.0, action="BUY"):
    return {"asset": asset, "cluster": cluster, "confidence": conf,
            "regime_quality": rq, "liquidity_score": liq, "action": action}


def test_route_empty():
    router = CapitalRouter()
    alloc = router.route([])
    assert alloc.used_slots == 0
    assert alloc.top_assets == []


def test_route_selects_top_k():
    router = CapitalRouter(top_k=3)
    candidates = [
        _candidate("BTC", "crypto", 0.90, 0.90),
        _candidate("ETH", "crypto", 0.80, 0.85),
        _candidate("EUR", "fx", 0.75, 0.80),
        _candidate("GOLD", "commodities", 0.70, 0.75),
        _candidate("SOL", "crypto", 0.65, 0.70),
    ]
    alloc = router.route(candidates)
    assert alloc.used_slots == 3
    assert len(alloc.top_assets) == 3


def test_max_per_cluster_respected():
    router = CapitalRouter(top_k=3, max_per_cluster=2)
    candidates = [
        _candidate("BTC", "crypto", 0.90, 0.90),
        _candidate("ETH", "crypto", 0.88, 0.90),
        _candidate("SOL", "crypto", 0.85, 0.88),  # 3rd crypto — should be rejected
        _candidate("EUR", "fx", 0.70, 0.75),
    ]
    alloc = router.route(candidates)
    clusters = [a.cluster for a in alloc.top_assets]
    assert clusters.count("crypto") <= 2


def test_opportunity_score_range():
    router = CapitalRouter()
    candidates = [_candidate("BTC", "crypto", 0.80, 0.80)]
    alloc = router.route(candidates)
    for asset in alloc.top_assets:
        assert 0.0 <= asset.opportunity_score <= 1.0


def test_win_rate_default_neutral():
    router = CapitalRouter()
    assert router.get_win_rate("UNKNOWN") == 0.50


def test_record_and_use_win_rate():
    router = CapitalRouter()
    for _ in range(8):
        router.record_result("BTC", won=True)
    for _ in range(2):
        router.record_result("BTC", won=False)
    wr = router.get_win_rate("BTC")
    assert abs(wr - 0.80) < 0.01


def test_daily_loss_reduces_later_slots():
    router = CapitalRouter(top_k=3, daily_loss_budget_r=2.0)
    router.record_loss(3.0)  # excede budget
    candidates = [
        _candidate("BTC", "crypto", 0.90, 0.90),
        _candidate("ETH", "crypto", 0.80, 0.85),
        _candidate("EUR", "fx", 0.75, 0.80),
    ]
    alloc = router.route(candidates)
    assert alloc.budget_ok is False
    # slots 1,2 devem ter fraction reduzida
    if len(alloc.top_assets) >= 2:
        assert alloc.top_assets[1].allocated_fraction <= alloc.top_assets[0].allocated_fraction


def test_reset_daily_loss():
    router = CapitalRouter(daily_loss_budget_r=3.0)
    router.record_loss(5.0)
    router.reset_daily_loss()
    assert router._daily_loss_used == 0.0


def test_get_ranking():
    router = CapitalRouter()
    candidates = [
        _candidate("BTC", "crypto", 0.90, 0.90),
        _candidate("EUR", "fx", 0.50, 0.60),
    ]
    ranking = router.get_ranking(candidates)
    assert ranking[0]["opportunity_score"] >= ranking[1]["opportunity_score"]


def test_get_stats():
    router = CapitalRouter()
    router.route([_candidate("BTC", "crypto")])
    stats = router.get_stats()
    assert stats["total_allocations"] == 1
    assert "avg_slots_used" in stats
