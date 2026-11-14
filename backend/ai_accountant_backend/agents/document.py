"""Document Agent — upload, metadata, OCR framework, extraction."""
from __future__ import annotations

from ai_accountant_backend.agents.base import AgentResult, BaseAgent


class DocumentAgent(BaseAgent):
    name = "document"
    role = "OCR and document extraction"
    permitted_tools = ["upload", "extract", "ocr"]

    async def run(self, *, message: str, context: dict) -> AgentResult:
        msg = message.lower()
        if "ocr" in msg or "receipt" in msg or "invoice" in msg:
            return AgentResult(
                text="[demo mock] Document Agent: upload receipts/invoices/bank statements. OCR extraction "
                     "requires an external service (AWS Textract / Azure Form Recognizer / Google Document AI) — "
                     "configure credentials to enable. Extracted transactions are suggested entries pending approval.",
                agent="document", model="mock-light", provider="mock",
            )
        return AgentResult(
            text=f"[demo mock] Document Agent: {message[:120]}... I store financial documents, extract fields, "
                 "and flag missing documents for tax preparation.",
            agent="document", model="mock-light", provider="mock",
        )

