"""Mission 338 — Defensive Mode Controller: adapta parâmetros ao regime de mercado."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


# Cenários de mercado detectáveis
SCENARIO_STRESS = "STRESS"       # VIX > 30 ou volatilidade extrema
SCENARIO_LATERAL = "LATERAL"     # range < 0.5%, sem direção
SCENARIO_TRENDING = "TRENDING"   # momentum > 2σ, tendência forte
SCENARIO_NORMAL = "NORMAL"       # condições médias


@dataclass
class MarketScenario:
    name: str = SCENARIO_NORMAL
    vix: float = 0.0
    range_pct: float = 1.0
    momentum_sigma: float = 0.0
    volatility: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "vix": round(self.vix, 2),
            "range_pct": round(self.range_pct, 4),
            "momentum_sigma": round(self.momentum_sigma, 3),
            "volatility": round(self.volatility, 4),
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class DefensiveConfig:
    scenario: str = SCENARIO_NORMAL
    stop_loss_pct: float = 1.5
    max_position_size: float = 1.0      # fração do capital máximo
    active_agents: List[str] = field(default_factory=list)
    max_open_positions: int = 3
    description: str = ""
    applied_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "stop_loss_pct": round(self.stop_loss_pct, 3),
            "max_position_size": round(self.max_position_size, 3),
            "active_agents": self.active_agents,
            "max_open_positions": self.max_open_positions,
            "description": self.description,
            "applied_at": self.applied_at.isoformat(),
        }


# Configurações pré-definidas por cenário
_SCENARIO_CONFIGS: Dict[str, Dict[str, Any]] = {
    SCENARIO_STRESS: {
        "stop_loss_pct": 0.5,
        "max_position_size": 0.25,
        "active_agents": ["RiskAgent"],
        "max_open_positions": 1,
        "description": "Modo máxima proteção: apenas RiskAgent, stop 0.5%, tamanho 25%",
    },
    SCENARIO_LATERAL: {
        "stop_loss_pct": 1.0,
        "max_position_size": 0.50,
        "active_agents": ["MarketAgent", "DiscoveryAgent"],
        "max_open_positions": 2,
        "description": "Modo conservador: MarketAgent + Discovery, stop 1%, tamanho 50%",
    },
    SCENARIO_TRENDING: {
        "stop_loss_pct": 2.0,
        "max_position_size": 1.0,
        "active_agents": ["MarketAgent", "RiskAgent", "DiscoveryAgent",
                          "LearningAgent", "AuditAgent", "ResearchAgent"],
        "max_open_positions": 3,
        "description": "Modo agressivo: todos os agentes, stop 2%, tamanho 100%",
    },
    SCENARIO_NORMAL: {
        "stop_loss_pct": 1.5,
        "max_position_size": 0.75,
        "active_agents": ["MarketAgent", "RiskAgent", "DiscoveryAgent", "LearningAgent"],
        "max_open_positions": 3,
        "description": "Modo padrão: 4 agentes, stop 1.5%, tamanho 75%",
    },
}


class DefensiveModeController:
    """
    Detecta o cenário de mercado a partir de métricas e ativa automaticamente
    o perfil de configuração correspondente.

    Hierarquia de prioridade: STRESS > LATERAL > TRENDING > NORMAL
    """

    STRESS_VIX_THRESHOLD = 30.0
    STRESS_VOL_THRESHOLD = 0.04
    LATERAL_RANGE_THRESHOLD = 0.005     # 0.5%
    TRENDING_MOMENTUM_SIGMA = 2.0

    def __init__(self, custom_configs: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self._configs = {**_SCENARIO_CONFIGS, **(custom_configs or {})}
        self._history: List[DefensiveConfig] = []
        self._current: Optional[DefensiveConfig] = None

    # ------------------------------------------------------------------ #
    #  Detection                                                           #
    # ------------------------------------------------------------------ #

    def detect_scenario(self, market_data: Dict[str, Any]) -> MarketScenario:
        vix = float(market_data.get("vix", 0.0))
        range_pct = float(market_data.get("range_pct", 1.0))
        momentum_sigma = float(market_data.get("momentum_sigma", 0.0))
        volatility = float(market_data.get("volatility", 0.0))

        if vix > self.STRESS_VIX_THRESHOLD or volatility > self.STRESS_VOL_THRESHOLD:
            name = SCENARIO_STRESS
        elif range_pct < self.LATERAL_RANGE_THRESHOLD:
            name = SCENARIO_LATERAL
        elif abs(momentum_sigma) > self.TRENDING_MOMENTUM_SIGMA:
            name = SCENARIO_TRENDING
        else:
            name = SCENARIO_NORMAL

        return MarketScenario(
            name=name, vix=vix, range_pct=range_pct,
            momentum_sigma=momentum_sigma, volatility=volatility,
        )

    # ------------------------------------------------------------------ #
    #  Apply                                                               #
    # ------------------------------------------------------------------ #

    def apply(self, market_data: Dict[str, Any]) -> DefensiveConfig:
        """Detecta cenário e aplica configuração defensiva correspondente."""
        scenario = self.detect_scenario(market_data)
        cfg_data = self._configs.get(scenario.name, self._configs[SCENARIO_NORMAL])

        config = DefensiveConfig(
            scenario=scenario.name,
            stop_loss_pct=cfg_data["stop_loss_pct"],
            max_position_size=cfg_data["max_position_size"],
            active_agents=list(cfg_data["active_agents"]),
            max_open_positions=cfg_data["max_open_positions"],
            description=cfg_data["description"],
        )
        self._current = config
        self._history.append(config)
        return config

    def apply_scenario(self, scenario_name: str) -> DefensiveConfig:
        """Aplica um cenário específico diretamente (para testes ou override manual)."""
        cfg_data = self._configs.get(scenario_name, self._configs[SCENARIO_NORMAL])
        config = DefensiveConfig(
            scenario=scenario_name,
            stop_loss_pct=cfg_data["stop_loss_pct"],
            max_position_size=cfg_data["max_position_size"],
            active_agents=list(cfg_data["active_agents"]),
            max_open_positions=cfg_data["max_open_positions"],
            description=cfg_data["description"],
        )
        self._current = config
        self._history.append(config)
        return config

    @property
    def current_config(self) -> Optional[DefensiveConfig]:
        return self._current

    def is_agent_active(self, agent_id: str) -> bool:
        if self._current is None:
            return True
        return agent_id in self._current.active_agents

    # ------------------------------------------------------------------ #
    #  Custom config                                                       #
    # ------------------------------------------------------------------ #

    def register_custom_config(
        self, scenario: str, stop_loss_pct: float,
        max_position_size: float, active_agents: List[str],
        max_open_positions: int = 3, description: str = "",
    ) -> None:
        self._configs[scenario] = {
            "stop_loss_pct": stop_loss_pct,
            "max_position_size": max_position_size,
            "active_agents": active_agents,
            "max_open_positions": max_open_positions,
            "description": description,
        }

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self._history[-limit:]]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._history)
        if total == 0:
            return {"total_switches": 0, "current_scenario": None}
        by_scenario: Dict[str, int] = {}
        for c in self._history:
            by_scenario[c.scenario] = by_scenario.get(c.scenario, 0) + 1
        return {
            "total_switches": total,
            "current_scenario": self._current.scenario if self._current else None,
            "by_scenario": by_scenario,
        }
