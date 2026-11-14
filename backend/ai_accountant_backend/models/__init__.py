"""Import all models so Alembic autogenerate and `Base.metadata` see them."""
from ai_accountant_backend.models.ai_cost_record import AICostRecord
from ai_accountant_backend.models.audit import AuditLog
from ai_accountant_backend.models.company import Company
from ai_accountant_backend.models.journal import JournalEntry, JournalLine
from ai_accountant_backend.models.shared import Base
from ai_accountant_backend.models.tax_return import TaxReturn
from ai_accountant_backend.models.tax_rule import TaxRule
from ai_accountant_backend.models.tenant import Tenant, User
from ai_accountant_backend.models.chart_of_accounts import Account
from ai_accountant_backend.models.transaction import Transaction

__all__ = [
    "Base",
    "Tenant",
    "User",
    "Company",
    "Account",
    "JournalEntry",
    "JournalLine",
    "Transaction",
    "AuditLog",
    "TaxRule",
    "TaxReturn",
    "AICostRecord",
]


