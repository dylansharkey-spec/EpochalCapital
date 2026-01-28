"""
Pytest fixtures for Epochal Capital tests.
"""

import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from epochal.core.models import (
    Company,
    Deal,
    AIVertical,
    CompanyStage,
    DealStatus,
    DealType,
)
from epochal.core.portfolio import Portfolio
from epochal.core.valuation import ValuationModel
from epochal.core.risk_scoring import RiskScorer, RiskDimension
from epochal.core.alerts import AlertManager, AlertType, AlertPriority


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_company():
    """Create a sample AI company for testing."""
    return Company(
        id="company_001",
        name="TestAI Labs",
        description="AI safety research company building large language models",
        vertical=AIVertical.FOUNDATION_MODELS,
        stage=CompanyStage.PRE_IPO,
        founded_year=2021,
        headquarters="San Francisco, CA",
        website="https://testai.com",
        valuation_usd=50_000_000_000,  # $50B
        last_round_usd=2_000_000_000,  # $2B
        key_investors=["Top VC", "Big Tech Co", "Growth Fund"],
        employee_count=1000,
        revenue_arr_usd=500_000_000,  # $500M ARR
        tags=["foundation_models", "ai_safety", "pre_ipo"],
    )


@pytest.fixture
def sample_companies():
    """Create multiple sample companies for comparison tests."""
    return [
        Company(
            id="company_001",
            name="FoundationAI",
            description="Foundation model company",
            vertical=AIVertical.FOUNDATION_MODELS,
            stage=CompanyStage.PRE_IPO,
            valuation_usd=100_000_000_000,
            revenue_arr_usd=2_000_000_000,
        ),
        Company(
            id="company_002",
            name="InfraML",
            description="ML infrastructure",
            vertical=AIVertical.INFRASTRUCTURE,
            stage=CompanyStage.GROWTH,
            valuation_usd=10_000_000_000,
            revenue_arr_usd=500_000_000,
        ),
        Company(
            id="company_003",
            name="EnterpriseBot",
            description="Enterprise AI platform",
            vertical=AIVertical.ENTERPRISE_AI,
            stage=CompanyStage.SERIES_C,
            valuation_usd=5_000_000_000,
            revenue_arr_usd=200_000_000,
        ),
    ]


@pytest.fixture
def sample_deal(sample_company):
    """Create a sample deal for testing."""
    return Deal(
        id="deal_001",
        company_id=sample_company.id,
        deal_type=DealType.SECONDARY,
        status=DealStatus.SOURCING,
        price_per_share_usd=100.0,
        total_available_usd=10_000_000,  # $10M
        minimum_usd=250_000,
        source="Secondary Platform",
        valuation_implied_usd=50_000_000_000,
        discount_to_last_round_pct=10.0,
        thesis_score=85.0,
    )


@pytest.fixture
def portfolio(temp_data_dir):
    """Create a portfolio instance with temp directory."""
    return Portfolio(data_dir=temp_data_dir)


@pytest.fixture
def valuation_model():
    """Create a valuation model instance."""
    return ValuationModel()


@pytest.fixture
def risk_scorer():
    """Create a risk scorer instance."""
    return RiskScorer()


@pytest.fixture
def alert_manager(temp_data_dir):
    """Create an alert manager instance with temp directory."""
    return AlertManager(data_dir=temp_data_dir)


@pytest.fixture
def concentration_risk_inputs():
    """Sample inputs for concentration risk scoring."""
    return {
        "top_customer_revenue_pct": 15.0,
        "top_3_customers_pct": 40.0,
        "customer_count": 500,
        "revenue_type": "recurring",
        "customer_churn_pct": 5.0,
    }


@pytest.fixture
def execution_risk_inputs():
    """Sample inputs for execution risk scoring."""
    return {
        "team_experience_years": 12.0,
        "prior_exits": 2,
        "employee_count": 500,
        "employee_growth_pct": 30.0,
        "tech_debt_level": "low",
        "product_market_fit": "strong",
        "recent_leadership_changes": 0,
        "glassdoor_rating": 4.2,
    }


@pytest.fixture
def burn_rate_inputs():
    """Sample inputs for burn rate risk scoring."""
    return {
        "monthly_burn_usd": 10_000_000,
        "cash_runway_months": 24,
        "revenue_usd": 200_000_000,
        "gross_margin_pct": 75.0,
        "path_to_profitability_months": 18,
        "last_funding_date_months_ago": 6,
        "capital_intensity": "low",
    }


@pytest.fixture
def full_dimension_inputs(concentration_risk_inputs, execution_risk_inputs, burn_rate_inputs):
    """Full set of dimension inputs for comprehensive risk scoring."""
    return {
        RiskDimension.CONCENTRATION.value: concentration_risk_inputs,
        RiskDimension.EXECUTION.value: execution_risk_inputs,
        RiskDimension.BURN_RATE.value: burn_rate_inputs,
        RiskDimension.REGULATORY.value: {
            "primary_markets": ["us"],
            "ai_model_type": "narrow",
            "compliance_certifications": ["SOC2", "ISO27001"],
        },
        RiskDimension.COMPETITION.value: {
            "market_position": "leader",
            "moat_strength": "strong",
            "network_effects": True,
        },
        RiskDimension.MARKET_TIMING.value: {
            "ipo_window_months": 12,
            "sector_sentiment": "hot",
        },
        RiskDimension.KEY_PERSON.value: {
            "founder_led": True,
            "co_founder_count": 3,
            "key_departures_12mo": 0,
        },
        RiskDimension.CAP_TABLE.value: {
            "investor_count": 15,
            "down_round_history": 0,
            "preference_stack_multiple": 1.0,
        },
    }
