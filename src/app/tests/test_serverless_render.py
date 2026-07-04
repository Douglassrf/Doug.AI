def test_deriv_route_loaded():
    from app.api.safe_router import FAILED_ROUTES, LOADED_ROUTES

    assert "app.api.routes.deriv" in LOADED_ROUTES
    assert not FAILED_ROUTES
