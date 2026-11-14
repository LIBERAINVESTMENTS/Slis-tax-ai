"""Agent registry — maps agent type to agent class."""
from __future__ import annotations

from typing import Optional

from ai_accountant_backend.agents.base import BaseAgent

_REGISTRY: dict[str, BaseAgent] = {}


def register(agent: BaseAgent) -> None:
    _REGISTRY[agent.name.lower()] = agent


def get_agent(agent_type: str) -> Optional[BaseAgent]:
    return _REGISTRY.get(agent_type.lower())


def all_agents() -> list[BaseAgent]:
    return list(_REGISTRY.values())


def available_agent_types() -> list[str]:
    return sorted(_REGISTRY.keys())

