from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import json
import hashlib
import os


@dataclass
class ConfigEntry:
    id: str = field(default_factory=lambda: f"cfg_{uuid.uuid4().hex[:12]}")
    key: str = ""
    value: Any = None
    version: int = 1
    environment: str = "production"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: str = ""
    sensitive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "value": "***" if self.sensitive else self.value,
            "version": self.version,
            "environment": self.environment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "checksum": self.checksum,
            "sensitive": self.sensitive,
        }


@dataclass
class ConfigVersion:
    id: str = field(default_factory=lambda: f"cv_{uuid.uuid4().hex[:12]}")
    config_id: str = ""
    version: int = 1
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "config_id": self.config_id,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum,
        }


class AutonomousConfigurationManager:
    """Gerenciador autônomo de configuração com versionamento, rollback e listeners."""

    def __init__(self) -> None:
        self._configs: Dict[str, ConfigEntry] = {}
        self._versions: Dict[str, List[ConfigVersion]] = {}
        self._environment = os.environ.get("DOUG_ENV", "production")
        self._listeners: List[Callable] = []

    def set_config(self, key: str, value: Any, sensitive: bool = False) -> ConfigEntry:
        if key in self._configs:
            config = self._configs[key]
            config.value = value
            config.version += 1
            config.updated_at = datetime.now(timezone.utc)
            config.sensitive = sensitive
            config.checksum = self._checksum({key: value})

            version = ConfigVersion(
                config_id=config.id,
                version=config.version,
                data={key: value},
                checksum=config.checksum,
            )
            self._versions.setdefault(config.id, []).append(version)
        else:
            config = ConfigEntry(
                key=key,
                value=value,
                environment=self._environment,
                sensitive=sensitive,
                checksum=self._checksum({key: value}),
            )
            self._configs[key] = config
            self._versions[config.id] = []

        self._notify(key, value)
        return config

    def get_config(self, key: str) -> Optional[Any]:
        config = self._configs.get(key)
        return config.value if config else None

    def rollback(self, key: str, version: int) -> bool:
        config = self._configs.get(key)
        if not config:
            return False
        for v in self._versions.get(config.id, []):
            if v.version == version:
                config.value = v.data.get(key)
                config.version = version + 1
                config.updated_at = datetime.now(timezone.utc)
                config.checksum = v.checksum
                self._notify(key, config.value)
                return True
        return False

    def add_listener(self, callback: Callable) -> None:
        self._listeners.append(callback)

    def _notify(self, key: str, value: Any) -> None:
        for cb in self._listeners:
            try:
                cb(key, value)
            except Exception:
                pass

    @staticmethod
    def _checksum(data: Dict) -> str:
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "total_configs": len(self._configs),
            "environment": self._environment,
            "configs": {k: v.to_dict() for k, v in self._configs.items()},
        }
