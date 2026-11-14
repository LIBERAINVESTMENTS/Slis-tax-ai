"""CFO Agent — business analysis, forecasting, break-even, margins, scenarios."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class CFOAgent(BaseAgent):
    name = "cfo"
    role = "business analysis and forecasting"
    permitted_tools = ["forecast", "break_even", "margin_analysis", "scenario_simulate"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "break-even" in msg or "breakeven" in msg:
            return AgentResult(
                text="[demo mock] Break-even analysis: break-even revenue = fixed costs ÷ contribution margin "
                     "ratio. Provide fixed costs and margin to compute.",
                agent="cfo", model="mock-heavy", provider="mock",
            )
        if "forecast" in msg or "cash flow" in msg:
            return AgentResult(
                text="[demo mock] Cash-flow forecast: projected revenue minus projected expenses over the next "
                     "12 weeks, distinguished from actuals. Provide historical data to compute.",
                agent="cfo", model="mock-heavy", provider="mock",
            )
        if "margin" in msg or "profit" in msg:
            return AgentResult(
                text="[demo mock] Profit margin = net income ÷ revenue. I compute actual margins from posted "
                     "journal entries (never LLM arithmetic).",
                agent="cfo", model="mock-heavy", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] CFO Agent: {message[:120]}... I analyze profitability, forecast cash flow, "
                 "calculate break-even/margins, and simulate scenarios. Actuals vs forecasts are clearly labeled.",
            agent="cfo", model="mock-heavy", provider="mock",
        )

