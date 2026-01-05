"""
Agent system for Epochal Capital.

Provides a framework for creating specialized AI agents that can
handle different aspects of fund management autonomously.
"""

from epochal.agents.base import Agent, AgentRole, AgentTask, AgentResult
from epochal.agents.orchestrator import AgentOrchestrator
from epochal.agents.deal_sourcing import DealSourcingAgent
from epochal.agents.research import ResearchAgent
from epochal.agents.portfolio import PortfolioAgent

__all__ = [
    "Agent",
    "AgentRole",
    "AgentTask",
    "AgentResult",
    "AgentOrchestrator",
    "DealSourcingAgent",
    "ResearchAgent",
    "PortfolioAgent",
]
