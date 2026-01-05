"""
Epochal Capital - AI-Powered Investment Platform

A multi-agent system for sourcing, evaluating, and managing investments
in private AI companies with potential upcoming liquidity events.
"""

__version__ = "0.1.0"
__author__ = "Epochal Capital"

from epochal.core.models import Company, Deal, Investment, Fund, SPV
from epochal.core.thesis import InvestmentThesis
from epochal.core.portfolio import Portfolio
from epochal.agents.base import Agent, AgentRole
from epochal.agents.orchestrator import AgentOrchestrator

__all__ = [
    "Company",
    "Deal",
    "Investment",
    "Fund",
    "SPV",
    "InvestmentThesis",
    "Portfolio",
    "Agent",
    "AgentRole",
    "AgentOrchestrator",
]
