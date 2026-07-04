# ============================================================
# MISSÃO 318 — DOUG OPERATING SYSTEM (DougOS)
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import asyncio
import logging


@dataclass
class DougOSModule:
    """Módulo do DougOS."""

    id: str = field(default_factory=lambda: f"dosm_{uuid.uuid4().hex[:12]}")
    name: str = ""
    module_type: str = ""
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    status: str = "registered"
    instance: Any = None
    health_check: Optional[Callable] = None
    start_priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "module_type": self.module_type,
            "version": self.version,
            "dependencies": self.dependencies,
            "status": self.status,
            "start_priority": self.start_priority,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
        }


@dataclass
class DougOSState:
    """Estado do DougOS."""

    status: str = "initializing"
    modules: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    uptime_seconds: float = 0.0
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "modules": self.modules,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
        }


class DougOperatingSystem:
    """
    Sistema Operacional Central do Doug.AI.

    Coordena módulos core, intelligence, risk, discovery, learning e governance.
    """

    _instance: Optional["DougOperatingSystem"] = None

    def __new__(cls) -> "DougOperatingSystem":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._modules: Dict[str, DougOSModule] = {}
        self._state = DougOSState()
        self._config: Dict[str, Any] = {}
        self._is_running = False
        self._logger = logging.getLogger("DougOS")
        self._shutdown_hooks: List[Callable] = []
        self._health_check_task: Optional[asyncio.Task] = None
        self._initialized = True

    @classmethod
    def reset_singleton(cls) -> None:
        """Reseta singleton para testes."""
        cls._instance = None

    def register_module(
        self,
        name: str,
        module_type: str,
        instance: Any,
        dependencies: Optional[List[str]] = None,
        version: str = "1.0.0",
        start_priority: int = 5,
        health_check: Optional[Callable] = None,
    ) -> DougOSModule:
        """Registra módulo no sistema."""
        if name in [m.name for m in self._modules.values()]:
            raise ValueError(f"Module {name} already registered")

        module = DougOSModule(
            name=name,
            module_type=module_type,
            version=version,
            dependencies=dependencies or [],
            instance=instance,
            start_priority=start_priority,
            health_check=health_check,
        )

        self._modules[module.id] = module
        self._logger.info("Module registered: %s (%s)", name, module_type)
        return module

    def set_config(self, key: str, value: Any) -> None:
        """Define configuração global."""
        self._config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Recupera configuração global."""
        return self._config.get(key, default)

    async def start(self) -> bool:
        """Inicia o sistema operacional."""
        self._state.status = "initializing"
        self._logger.info("Starting DougOS...")

        if not self._check_dependencies():
            self._state.status = "error"
            return False

        sorted_modules = sorted(
            self._modules.values(),
            key=lambda m: (m.start_priority, len(m.dependencies)),
        )

        for module in sorted_modules:
            try:
                if hasattr(module.instance, "initialize"):
                    await module.instance.initialize()
                module.status = "loading"
            except Exception as exc:
                self._logger.error("Failed to initialize module %s: %s", module.name, exc)
                module.status = "error"
                self._state.status = "error"
                return False

        for module in sorted_modules:
            try:
                if hasattr(module.instance, "start"):
                    await module.instance.start()
                module.status = "active"
            except Exception as exc:
                self._logger.error("Failed to start module %s: %s", module.name, exc)
                module.status = "error"
                self._state.status = "error"
                return False

        self._state.status = "running"
        self._state.started_at = datetime.now(timezone.utc)
        self._is_running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._logger.info("DougOS started successfully")
        return True

    def _check_dependencies(self) -> bool:
        """Verifica dependências dos módulos."""
        module_names = {m.name for m in self._modules.values()}

        for module in self._modules.values():
            for dep in module.dependencies:
                if dep not in module_names:
                    self._logger.error(
                        "Missing dependency: %s for module %s", dep, module.name
                    )
                    return False

        return True

    async def _health_check_loop(self) -> None:
        """Loop de health check."""
        while self._is_running:
            try:
                for module in self._modules.values():
                    if module.health_check:
                        try:
                            healthy = module.health_check()
                            module.status = "active" if healthy else "error"
                            module.last_heartbeat = datetime.now(timezone.utc)
                        except Exception as exc:
                            self._logger.warning(
                                "Health check failed for %s: %s", module.name, exc
                            )
                            module.status = "error"
                    else:
                        module.last_heartbeat = datetime.now(timezone.utc)

                await asyncio.sleep(30)

            except Exception as exc:
                self._logger.error("Health check loop error: %s", exc)
                await asyncio.sleep(60)

    async def stop(self) -> None:
        """Encerra o sistema com segurança."""
        self._logger.info("Stopping DougOS...")
        self._state.status = "stopping"
        self._is_running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        for hook in self._shutdown_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as exc:
                self._logger.error("Shutdown hook error: %s", exc)

        for module in reversed(list(self._modules.values())):
            try:
                if hasattr(module.instance, "stop"):
                    await module.instance.stop()
                module.status = "stopped"
            except Exception as exc:
                self._logger.error("Failed to stop module %s: %s", module.name, exc)

        self._state.status = "stopped"
        self._state.stopped_at = datetime.now(timezone.utc)
        self._logger.info("DougOS stopped")

    def get_state(self) -> DougOSState:
        """Retorna estado do sistema."""
        self._state.modules = [m.name for m in self._modules.values()]
        if self._state.started_at:
            self._state.uptime_seconds = (
                datetime.now(timezone.utc) - self._state.started_at
            ).total_seconds()
        return self._state

    def get_module(self, name: str) -> Optional[DougOSModule]:
        """Recupera módulo por nome."""
        for module in self._modules.values():
            if module.name == name:
                return module
        return None

    def get_modules_by_type(self, module_type: str) -> List[DougOSModule]:
        """Recupera módulos por tipo."""
        return [m for m in self._modules.values() if m.module_type == module_type]

    def add_shutdown_hook(self, hook: Callable) -> None:
        """Adiciona hook de shutdown."""
        self._shutdown_hooks.append(hook)

    def get_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do DougOS."""
        return {
            "state": self._state.to_dict(),
            "modules": [m.to_dict() for m in self._modules.values()],
            "config_keys": list(self._config.keys()),
            "total_modules": len(self._modules),
            "active_modules": sum(1 for m in self._modules.values() if m.status == "active"),
            "healthy_modules": sum(1 for m in self._modules.values() if m.status == "active"),
            "uptime_hours": self._state.uptime_seconds / 3600 if self._state.started_at else 0,
            "module_types": {
                mt: sum(1 for m in self._modules.values() if m.module_type == mt)
                for mt in set(m.module_type for m in self._modules.values())
            },
        }
