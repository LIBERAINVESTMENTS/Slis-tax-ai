"""Audit Agent — independent verification, compliance checks, tamper detection."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class AuditAgent(BaseAgent):
    name = "audit"
    role = "independent verification and compliance checks"
    permitted_tools = ["verify_journal", "check_period_lock", "detect_tampering"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "tamper" in msg or "verify" in msg:
            return AgentResult(
                text="[demo mock] Audit Agent: every journal entry has a tamper-evident hash chain "
                     "(SHA-256 of prev_hash || payload). Posted entries are immutable; corrections use reversing entries.",
                agent="audit", model="mock-light", provider="mock",
            )
        if "compliance" in msg:
            return AgentResult(
                text="[demo mock] Compliance check: period locking, tax-rule verification status, and "
                     "approval-gated filing are enforced. No silent edits to historical records.",
                agent="audit", model="mock-light", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] Audit Agent: {message[:120]}... I independently verify bookkeeping, tax "
                 "calculations, and filing compliance.",
            agent="audit", model="mock-light", provider="mock",
        )

