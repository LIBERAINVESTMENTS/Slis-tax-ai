"""Agent service: registers all agents and provides master routing."""
from __future__ import annotations

from ai_accountant_backend.agents.accountant import AccountantAgent
from ai_accountant_backend.agents.audit import AuditAgent
from ai_accountant_backend.agents.cfo import CFOAgent
from ai_accountant_backend.agents.document import DocumentAgent
from ai_accountant_backend.agents.master import MasterAgent
from ai_accountant_backend.agents.personal_finance import PersonalFinanceAgent
from ai_accountant_backend.agents.registry import register
from ai_accountant_backend.agents.tax import TaxAgent


def register_all() -> None:
    register(MasterAgent())
    register(AccountantAgent())
    register(TaxAgent())
    register(CFOAgent())
    register(PersonalFinanceAgent())
    register(DocumentAgent())
    register(AuditAgent())


# Ensure registration on import
register_all()

