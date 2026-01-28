"""
Database layer for Epochal Capital.

Provides SQLite-based persistence with SQLAlchemy ORM.
"""

from epochal.database.models import (
    Base,
    CompanyDB,
    DealDB,
    InvestmentDB,
    AlertDB,
    ResearchDB,
)
from epochal.database.session import (
    get_engine,
    get_session,
    init_db,
    DatabaseManager,
)

__all__ = [
    "Base",
    "CompanyDB",
    "DealDB",
    "InvestmentDB",
    "AlertDB",
    "ResearchDB",
    "get_engine",
    "get_session",
    "init_db",
    "DatabaseManager",
]
