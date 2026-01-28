"""
SQLAlchemy ORM models for Epochal Capital.

Provides database schema for:
- Companies
- Deals
- Investments
- Alerts
- Research history
"""

from datetime import datetime
from typing import Optional

try:
    from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        Float,
        ForeignKey,
        Integer,
        String,
        Text,
        create_engine,
    )
    from sqlalchemy.orm import declarative_base, relationship
    from sqlalchemy.dialects.sqlite import JSON
except ImportError:
    # Provide stub classes if SQLAlchemy not installed
    class Column:
        def __init__(self, *args, **kwargs):
            pass

    class String:
        def __init__(self, *args):
            pass

    Text = String
    Integer = String
    Float = String
    Boolean = String
    DateTime = String
    JSON = String

    class ForeignKey:
        def __init__(self, *args):
            pass

    def relationship(*args, **kwargs):
        pass

    def declarative_base():
        class Base:
            pass
        return Base

    def create_engine(*args, **kwargs):
        return None


Base = declarative_base()


class CompanyDB(Base):
    """Database model for tracked companies."""

    __tablename__ = "companies"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    vertical = Column(String(50), index=True)
    stage = Column(String(50), index=True)
    founded_year = Column(Integer)
    headquarters = Column(String(200))
    website = Column(String(500))
    valuation_usd = Column(Float)
    last_round_usd = Column(Float)
    last_round_date = Column(DateTime)
    key_investors = Column(JSON)  # List of investor names
    employee_count = Column(Integer)
    revenue_arr_usd = Column(Float)
    growth_rate_pct = Column(Float)
    gross_margin_pct = Column(Float)
    ipo_timeline = Column(String(100))
    liquidity_signals = Column(JSON)  # List of signals
    risk_score = Column(Float)
    thesis_score = Column(Float)
    tags = Column(JSON)  # List of tags
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deals = relationship("DealDB", back_populates="company")
    investments = relationship("InvestmentDB", back_populates="company")
    research_history = relationship("ResearchDB", back_populates="company")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "vertical": self.vertical,
            "stage": self.stage,
            "founded_year": self.founded_year,
            "headquarters": self.headquarters,
            "website": self.website,
            "valuation_usd": self.valuation_usd,
            "last_round_usd": self.last_round_usd,
            "last_round_date": self.last_round_date.isoformat() if self.last_round_date else None,
            "key_investors": self.key_investors or [],
            "employee_count": self.employee_count,
            "revenue_arr_usd": self.revenue_arr_usd,
            "growth_rate_pct": self.growth_rate_pct,
            "gross_margin_pct": self.gross_margin_pct,
            "ipo_timeline": self.ipo_timeline,
            "liquidity_signals": self.liquidity_signals or [],
            "risk_score": self.risk_score,
            "thesis_score": self.thesis_score,
            "tags": self.tags or [],
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DealDB(Base):
    """Database model for deals in pipeline."""

    __tablename__ = "deals"

    id = Column(String(50), primary_key=True)
    company_id = Column(String(50), ForeignKey("companies.id"), index=True)
    deal_type = Column(String(50), index=True)  # secondary, primary, spv, fund
    status = Column(String(50), index=True)  # sourcing, diligence, negotiation, closed, passed
    source = Column(String(200))
    source_contact = Column(String(200))
    price_per_share_usd = Column(Float)
    total_available_usd = Column(Float)
    minimum_usd = Column(Float)
    our_target_usd = Column(Float)
    share_class = Column(String(50))
    valuation_implied_usd = Column(Float)
    discount_to_last_round_pct = Column(Float)
    thesis_score = Column(Float)
    risk_score = Column(Float)
    platform = Column(String(100))  # Hiive, Forge, NPM, etc.
    expiration_date = Column(DateTime)
    notes = Column(Text)
    terms = Column(JSON)  # Deal terms dict
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyDB", back_populates="deals")
    investment = relationship("InvestmentDB", back_populates="deal", uselist=False)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "deal_type": self.deal_type,
            "status": self.status,
            "source": self.source,
            "source_contact": self.source_contact,
            "price_per_share_usd": self.price_per_share_usd,
            "total_available_usd": self.total_available_usd,
            "minimum_usd": self.minimum_usd,
            "our_target_usd": self.our_target_usd,
            "share_class": self.share_class,
            "valuation_implied_usd": self.valuation_implied_usd,
            "discount_to_last_round_pct": self.discount_to_last_round_pct,
            "thesis_score": self.thesis_score,
            "risk_score": self.risk_score,
            "platform": self.platform,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "notes": self.notes,
            "terms": self.terms or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class InvestmentDB(Base):
    """Database model for investments."""

    __tablename__ = "investments"

    id = Column(String(50), primary_key=True)
    company_id = Column(String(50), ForeignKey("companies.id"), index=True)
    deal_id = Column(String(50), ForeignKey("deals.id"))
    investment_type = Column(String(50))  # direct, spv, fund
    status = Column(String(50), index=True)  # active, exited, written_off
    investment_date = Column(DateTime)
    shares = Column(Float)
    share_class = Column(String(50))
    price_per_share_usd = Column(Float)
    cost_basis_usd = Column(Float)
    current_value_usd = Column(Float)
    last_valuation_date = Column(DateTime)
    exit_date = Column(DateTime)
    exit_proceeds_usd = Column(Float)
    realized_gain_usd = Column(Float)
    irr_pct = Column(Float)
    multiple = Column(Float)
    spv_id = Column(String(50))
    fund_id = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyDB", back_populates="investments")
    deal = relationship("DealDB", back_populates="investment")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "deal_id": self.deal_id,
            "investment_type": self.investment_type,
            "status": self.status,
            "investment_date": self.investment_date.isoformat() if self.investment_date else None,
            "shares": self.shares,
            "share_class": self.share_class,
            "price_per_share_usd": self.price_per_share_usd,
            "cost_basis_usd": self.cost_basis_usd,
            "current_value_usd": self.current_value_usd,
            "last_valuation_date": self.last_valuation_date.isoformat() if self.last_valuation_date else None,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "exit_proceeds_usd": self.exit_proceeds_usd,
            "realized_gain_usd": self.realized_gain_usd,
            "irr_pct": self.irr_pct,
            "multiple": self.multiple,
            "spv_id": self.spv_id,
            "fund_id": self.fund_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertDB(Base):
    """Database model for alerts."""

    __tablename__ = "alerts"

    id = Column(String(50), primary_key=True)
    alert_type = Column(String(50), index=True)
    priority = Column(String(20), index=True)
    title = Column(String(500))
    message = Column(Text)
    company_name = Column(String(200), index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)
    acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    channels_sent = Column(JSON)  # List of channels
    tags = Column(JSON)  # List of tags

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "company_name": self.company_name,
            "data": self.data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "channels_sent": self.channels_sent or [],
            "tags": self.tags or [],
        }


class ResearchDB(Base):
    """Database model for research history."""

    __tablename__ = "research_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("companies.id"), index=True)
    research_date = Column(DateTime, default=datetime.utcnow, index=True)
    research_type = Column(String(50))  # valuation, news, ipo, funding
    valuation_usd = Column(Float)
    revenue_arr_usd = Column(Float)
    key_findings = Column(JSON)  # List of findings
    sources = Column(JSON)  # List of sources
    risk_signals = Column(JSON)  # List of risk signals
    liquidity_signals = Column(JSON)  # List of liquidity signals
    raw_data = Column(JSON)  # Full research data
    agent_id = Column(String(50))  # Which agent performed research

    # Relationships
    company = relationship("CompanyDB", back_populates="research_history")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "research_date": self.research_date.isoformat() if self.research_date else None,
            "research_type": self.research_type,
            "valuation_usd": self.valuation_usd,
            "revenue_arr_usd": self.revenue_arr_usd,
            "key_findings": self.key_findings or [],
            "sources": self.sources or [],
            "risk_signals": self.risk_signals or [],
            "liquidity_signals": self.liquidity_signals or [],
            "agent_id": self.agent_id,
        }


class SecondaryPricingDB(Base):
    """Database model for secondary market pricing history."""

    __tablename__ = "secondary_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), index=True)
    platform = Column(String(50), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    bid_price = Column(Float)
    ask_price = Column(Float)
    last_price = Column(Float)
    implied_valuation = Column(Float)
    volume_shares = Column(Integer)
    spread_pct = Column(Float)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "platform": self.platform,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "last_price": self.last_price,
            "implied_valuation": self.implied_valuation,
            "volume_shares": self.volume_shares,
            "spread_pct": self.spread_pct,
        }


class RiskAssessmentDB(Base):
    """Database model for risk assessment history."""

    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), ForeignKey("companies.id"), index=True)
    assessment_date = Column(DateTime, default=datetime.utcnow, index=True)
    overall_score = Column(Float)
    weighted_score = Column(Float)
    overall_level = Column(String(20))
    concentration_score = Column(Float)
    regulatory_score = Column(Float)
    competition_score = Column(Float)
    execution_score = Column(Float)
    market_timing_score = Column(Float)
    key_person_score = Column(Float)
    cap_table_score = Column(Float)
    burn_rate_score = Column(Float)
    recommendation = Column(Text)
    risk_factors = Column(JSON)  # List of factors
    mitigants = Column(JSON)  # List of mitigants

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "assessment_date": self.assessment_date.isoformat() if self.assessment_date else None,
            "overall_score": self.overall_score,
            "weighted_score": self.weighted_score,
            "overall_level": self.overall_level,
            "dimension_scores": {
                "concentration": self.concentration_score,
                "regulatory": self.regulatory_score,
                "competition": self.competition_score,
                "execution": self.execution_score,
                "market_timing": self.market_timing_score,
                "key_person": self.key_person_score,
                "cap_table": self.cap_table_score,
                "burn_rate": self.burn_rate_score,
            },
            "recommendation": self.recommendation,
            "risk_factors": self.risk_factors or [],
            "mitigants": self.mitigants or [],
        }
