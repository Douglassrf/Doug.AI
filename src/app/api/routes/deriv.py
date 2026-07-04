"""FastAPI routes for the safe Deriv integration."""
from __future__ import annotations

try:
    from fastapi import APIRouter
except ImportError:  # pragma: no cover - dependency-light env fallback
    class APIRouter:  # type: ignore[no-redef]
        def __init__(self, *_: object, **__: object) -> None:
            self.routes = []

        def get(self, path: str, **_: object):
            def decorator(func):
                self.routes.append(("GET", path, func))
                return func
            return decorator

        def post(self, path: str, **_: object):
            def decorator(func):
                self.routes.append(("POST", path, func))
                return func
            return decorator

from app.integrations.deriv import DerivClient
from app.schemas.deriv import DerivGenericResponse, DerivPingResponse, DerivProposalRequest, DerivStatusResponse, DerivTicksRequest

router = APIRouter(prefix="/api/v1/deriv", tags=["deriv"])


@router.get("/status", response_model=DerivStatusResponse)
def status() -> dict[str, object]:
    return DerivClient().status()


@router.get("/ping", response_model=DerivPingResponse)
def ping() -> dict[str, object]:
    return DerivClient().ping()


@router.post("/ticks", response_model=DerivGenericResponse)
def ticks(request: DerivTicksRequest) -> dict[str, object]:
    return {"data": DerivClient().ticks(request.symbol)}


@router.post("/proposal", response_model=DerivGenericResponse)
def proposal(request: DerivProposalRequest) -> dict[str, object]:
    return {"data": DerivClient().proposal(**request.model_dump())}
