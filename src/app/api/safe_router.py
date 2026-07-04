"""Safe route discovery for Doug.AI API modules."""
from __future__ import annotations

from importlib import import_module

ROUTE_MODULES = ("app.api.routes.deriv",)
LOADED_ROUTES: list[str] = []
FAILED_ROUTES: list[dict[str, str]] = []

for module_name in ROUTE_MODULES:
    try:
        module = import_module(module_name)
        if getattr(module, "router", None) is not None:
            LOADED_ROUTES.append(module_name)
    except Exception as exc:  # pragma: no cover
        FAILED_ROUTES.append({"module": module_name, "error": str(exc)})
