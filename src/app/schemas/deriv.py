"""Pydantic schemas for Deriv API routes.

If Pydantic is not installed in a minimal test environment, a tiny compatible
fallback keeps the safe mock tests importable. Production installs should use
`pydantic>=2.0` from `requirements.txt`.
"""
from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover - exercised only in dependency-light envs
    def Field(default: Any = None, **_: Any) -> Any:
        return default

    class BaseModel:
        def __init__(self, **data: Any) -> None:
            annotations = getattr(self, "__annotations__", {})
            for name in annotations:
                setattr(self, name, getattr(type(self), name, None))
            for name, value in data.items():
                setattr(self, name, value)

        def model_dump(self) -> dict[str, Any]:
            return {name: getattr(self, name) for name in getattr(self, "__annotations__", {})}


class DerivStatusResponse(BaseModel):
    ok: bool
    mock_enabled: bool
    live_enabled: bool
    endpoint: str
    default_symbol: str
    currency: str
    has_token: bool


class DerivPingResponse(BaseModel):
    msg_type: str
    mock: bool | None = None
    ping: str | None = None
    request: dict[str, Any] | None = None


class DerivTicksRequest(BaseModel):
    symbol: str | None = None


class DerivProposalRequest(BaseModel):
    amount: float = Field(default=1.0, gt=0)
    contract_type: str = "CALL"
    duration: int = Field(default=5, gt=0)
    duration_unit: str = "t"
    symbol: str | None = None
    dry_run: bool = True


class DerivGenericResponse(BaseModel):
    data: dict[str, Any]
