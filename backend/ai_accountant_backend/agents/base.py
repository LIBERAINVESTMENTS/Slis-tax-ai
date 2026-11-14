"""Base agent: permission-gated tool use, deterministic financial math delegated to engines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentResult:
    text: str
    agent: str
    model: str
    provider: str
    requires_approval: bool = False
    approval_payload: Optional[dict] = None
    citations: list[dict] = field(default_factory=list)


class BaseAgent:
    name: str = "base"
    role: str = "base agent"
    # Tools this agent is permitted to call
    permitted_tools: list[str] = field(default_factory=list)

    def can_call(self, tool_name: str) -> bool:
        return tool_name in self.permitted_tools

    async def run(self, *, message: str, context: dict) -> AgentResult:
        raise NotImplementedError
