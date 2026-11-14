"""Accountant Agent — bookkeeping, reconciliation, suggested entries, duplicate/error detection."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class AccountantAgent(BaseAgent):
    name = "accountant"
    role = "bookkeeping and reconciliation"
    permitted_tools = ["post_journal", "list_accounts", "detect_duplicates", "reconcile"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "duplicate" in msg:
            return AgentResult(
                text="[demo mock] Duplicate-transaction scan: no exact duplicates found in the sample period. "
                     "Provide a bank statement import to run a full match.",
                agent="accountant", model="mock-light", provider="mock",
            )
        if "reconcil" in msg:
            return AgentResult(
                text="[demo mock] Bank reconciliation: import a statement (CSV/OFX) and I'll match each line to an "
                     "invoice, bill, or journal entry. Unmatched items go to review.",
                agent="accountant", model="mock-light", provider="mock",
            )
        if "entry" in msg or "journal" in msg:
            return AgentResult(
                text="[demo mock] I can suggest balanced double-entry journal entries. Specify accounts, amounts, "
                     "and date; I'll validate that debits equal credits before posting.",
                agent="accountant", model="mock-light", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] Accountant Agent: {message[:120]}... I handle bookkeeping, journal entries, "
                 "reconciliation, and duplicate/error detection.",
            agent="accountant", model="mock-light", provider="mock",
        )

