"""Core modules for Epochal Capital platform."""

from epochal.core.models import Company, Deal, Investment, Fund, SPV
from epochal.core.thesis import InvestmentThesis
from epochal.core.portfolio import Portfolio
from epochal.core.valuation import (
    ValuationModel,
    ValuationResult,
    ComprehensiveValuation,
)
from epochal.core.risk_scoring import (
    RiskScorer,
    RiskProfile,
    RiskDimension,
    RiskLevel,
)
from epochal.core.alerts import (
    AlertManager,
    Alert,
    AlertType,
    AlertPriority,
    NotificationChannel,
)

__all__ = [
    "Company",
    "Deal",
    "Investment",
    "Fund",
    "SPV",
    "InvestmentThesis",
    "Portfolio",
    "ValuationModel",
    "ValuationResult",
    "ComprehensiveValuation",
    "RiskScorer",
    "RiskProfile",
    "RiskDimension",
    "RiskLevel",
    "AlertManager",
    "Alert",
    "AlertType",
    "AlertPriority",
    "NotificationChannel",
]
