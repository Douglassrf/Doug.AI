import pytest
from discovery.autonomous_api_gateway import AutonomousAPIGateway, APIRequest


def test_register_client_returns_key():
    gw = AutonomousAPIGateway()
    key = gw.register_client("client1")
    assert isinstance(key, str)
    assert len(key) == 32


def test_authenticate_valid_key():
    gw = AutonomousAPIGateway()
    key = gw.register_client("c1")
    assert gw.authenticate(key) is True


def test_authenticate_invalid_key():
    gw = AutonomousAPIGateway()
    assert gw.authenticate("badkey") is False


def test_authorize_registered_client():
    gw = AutonomousAPIGateway()
    gw.register_client("c1")
    assert gw.authorize("c1", "/api/data") is True


def test_handle_request_success():
    gw = AutonomousAPIGateway()
    key = gw.register_client("c1")
    gw.register_handler("/data", "GET", lambda body: {"result": "ok"})
    req = gw.handle_request("/data", "GET", {}, {}, key)
    assert req.status == "success"
    assert req.response == {"result": "ok"}


def test_handle_request_auth_fail():
    gw = AutonomousAPIGateway()
    req = gw.handle_request("/data", "GET", {}, {}, "invalid_key")
    assert req.status == "failed"
    assert "auth" in (req.error or "").lower()


def test_handle_request_endpoint_not_found():
    gw = AutonomousAPIGateway()
    key = gw.register_client("c1")
    req = gw.handle_request("/unknown", "GET", {}, {}, key)
    assert req.status == "failed"


def test_rate_limit():
    gw = AutonomousAPIGateway(rate_limit_max=2)
    key = gw.register_client("c1")
    gw.register_handler("/limited", "GET", lambda b: {})
    gw.handle_request("/limited", "GET", {}, {}, key)
    gw.handle_request("/limited", "GET", {}, {}, key)
    req = gw.handle_request("/limited", "GET", {}, {}, key)
    assert req.status == "failed"
    assert "rate" in (req.error or "").lower()


def test_get_metrics():
    gw = AutonomousAPIGateway()
    m = gw.get_metrics()
    assert "total_requests" in m
    assert m["total_requests"] == 0


def test_api_request_to_dict():
    r = APIRequest(endpoint="/x", method="POST", client_id="c1")
    d = r.to_dict()
    assert d["endpoint"] == "/x"
    assert d["method"] == "POST"
