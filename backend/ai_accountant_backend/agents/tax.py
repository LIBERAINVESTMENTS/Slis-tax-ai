"""Tax Agent — tax legislation, preparation, deduction identification (Suriname first)."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class TaxAgent(BaseAgent):
    name = "tax"
    role = "tax legislation and preparation"
    permitted_tools = ["compute_tax", "list_deductions", "prepare_return"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "corporate" in msg:
            return AgentResult(
                text="[demo mock] Suriname corporate income tax: 36% flat on taxable profit "
                     "(Income Tax Act of 1922; verified against EITI Suriname/Ministry of Finance).",
                agent="tax", model="mock-light", provider="mock",
            )
        if "vat" in msg or "btw" in msg:
            return AgentResult(
                text="[demo mock] Suriname VAT (BTW): 10% standard since 2023-01-01; 25% luxury; "
                     "5% reduced; 0% exports. Registration threshold SRD 1,000,000/year (verified).",
                agent="tax", model="mock-light", provider="mock",
            )
        if "personal" in msg or "income tax" in msg:
            return AgentResult(
                text="[demo mock] Suriname personal income tax: tax-free threshold SRD 108,000; "
                     "progressive brackets from Staatsbesluit 11 Jan 2024. Brackets above SRD 192,000 "
                     "pending official verification — not used for live calculation.",
                agent="tax", model="mock-light", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] Tax Agent: {message[:120]}... I handle Suriname corporate/personal income tax, "
                 "VAT, wage tax, withholding, and tax-return preparation (approval-gated filing).",
            agent="tax", model="mock-light", provider="mock",
        )

