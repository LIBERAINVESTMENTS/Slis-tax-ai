"""Master Agent — central assistant that routes intents to specialist agents."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent
from ai_accountant_backend.agents.registry import get_agent


class MasterAgent(BaseAgent):
    name = "master"
    role = "central assistant coordinating specialist finance agents"
    permitted_tools = ["route", "chat"]

    INTENT_TO_AGENT = {
        "accounting": "accountant",
        "bookkeeping": "accountant",
        "reconciliation": "accountant",
        "journal": "accountant",
        "transaction": "accountant",
        "tax": "tax",
        "vat": "tax",
        "filing": "tax",
        "deduction": "tax",
        "cfo": "cfo",
        "forecast": "cfo",
        "profit": "cfo",
        "break-even": "cfo",
        "margin": "cfo",
        "personal": "personal_finance",
        "budget": "personal_finance",
        "net worth": "personal_finance",
        "document": "document",
        "receipt": "document",
        "ocr": "document",
        "audit": "audit",
        "compliance": "audit",
        "verification": "audit",
    }

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        target = None
        for keyword, agent_type in self.INTENT_TO_AGENT.items():
            if keyword in msg:
                target = agent_type
                break
        if target:
            agent = get_agent(target)
            if agent:
                return await agent.run(message=message, context=context)
        # Default: answer from master context
        return AgentResult(
            text=f"[demo mock] Master Agent received: {message[:120]}... "
                 "I can route you to the Accountant, Tax, CFO, Personal Finance, Document, or Audit agent. "
                 "No live LLM key configured.",
            agent="master",
            model="mock-light",
            provider="mock",
        )

