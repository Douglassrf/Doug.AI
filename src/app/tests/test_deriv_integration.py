from app.core.config import DerivSettings
from app.integrations.deriv import DerivClient, DerivLivePurchaseBlocked
from app.schemas.deriv import DerivProposalRequest


def test_deriv_mock_status_is_safe_by_default():
    client = DerivClient(DerivSettings())
    status = client.status()
    assert status["mock_enabled"] is True
    assert status["live_enabled"] is False
    assert status["has_token"] is False


def test_deriv_mock_ping():
    assert DerivClient(DerivSettings()).ping()["msg_type"] == "ping"


def test_deriv_proposal_schema_defaults_to_dry_run():
    request = DerivProposalRequest()
    assert request.dry_run is True


def test_deriv_proposal_dry_run_blocks_purchase():
    response = DerivClient(DerivSettings()).proposal(amount=1, contract_type="CALL", duration=5, duration_unit="t")
    assert response["dry_run"] is True
    assert response["purchase_blocked"] is True


def test_deriv_real_purchase_blocked_when_live_disabled():
    client = DerivClient(DerivSettings(mock_enabled=True, live_enabled=False))
    try:
        client.proposal(amount=1, contract_type="CALL", duration=5, duration_unit="t", dry_run=False)
    except DerivLivePurchaseBlocked:
        pass
    else:
        raise AssertionError("purchase should be blocked")
