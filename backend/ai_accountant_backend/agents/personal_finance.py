"""Personal Finance Agent — budgets, net worth, goals, forecasting (personal env)."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class PersonalFinanceAgent(BaseAgent):
    name = "personal_finance"
    role = "personal financial management"
    permitted_tools = ["net_worth", "budget", "goal", "recurring_expense"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "net worth" in msg:
            return AgentResult(
                text="[demo mock] Net worth = total assets − total liabilities (personal environment, strictly "
                     "separate from business companies).",
                agent="personal_finance", model="mock-light", provider="mock",
            )
        if "budget" in msg:
            return AgentResult(
                text="[demo mock] Budget tracking: planned vs actual spending by category, with alerts when a "
                     "category exceeds its limit.",
                agent="personal_finance", model="mock-light", provider="mock",
            )
        if "goal" in msg:
            return AgentResult(
                text="[demo mock] Financial goals: target amount, target date, and monthly savings needed. "
                     "Forecasts are labeled as assumptions, not actuals.",
                agent="personal_finance", model="mock-light", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] Personal Finance Agent: {message[:120]}... I manage income/expense, bank accounts, "
                 "budgets, savings, assets, debts, investments, and net worth.",
            agent="personal_finance", model="mock-light", provider="mock",
        )

