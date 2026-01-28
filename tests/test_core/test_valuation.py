"""
Tests for the ValuationModel class.
"""

import pytest
from epochal.core.valuation import (
    ValuationModel,
    ValuationResult,
    ComprehensiveValuation,
    ValuationMethod,
)


class TestValuationModel:
    """Tests for ValuationModel."""

    def test_init_default(self, valuation_model):
        """Test default initialization."""
        assert valuation_model is not None
        assert len(valuation_model.VERTICAL_MULTIPLES) > 0
        assert len(valuation_model.PUBLIC_COMPARABLES) > 0

    def test_get_vertical_multiples(self, valuation_model):
        """Test getting vertical-specific multiples."""
        # Foundation models should have highest multiples
        fm_multiples = valuation_model.VERTICAL_MULTIPLES["foundation_models"]
        infra_multiples = valuation_model.VERTICAL_MULTIPLES["infrastructure"]

        assert fm_multiples["median"] > infra_multiples["median"]

    def test_calculate_revenue_multiple_value(self, valuation_model):
        """Test revenue multiple valuation."""
        result = valuation_model.calculate_revenue_multiple_value(
            company_name="TestCo",
            revenue_usd=500_000_000,  # $500M
            vertical="foundation_models",
            stage="pre_ipo",
        )

        assert isinstance(result, ValuationResult)
        assert result.method == ValuationMethod.REVENUE_MULTIPLE
        assert result.value_usd > 0
        assert result.confidence >= 0.0 and result.confidence <= 1.0

    def test_calculate_growth_adjusted_value(self, valuation_model):
        """Test growth-adjusted valuation."""
        result = valuation_model.calculate_growth_adjusted_value(
            company_name="TestCo",
            revenue_usd=500_000_000,
            growth_rate_pct=100.0,  # 100% growth
            vertical="foundation_models",
            stage="pre_ipo",
        )

        assert isinstance(result, ValuationResult)
        assert result.method == ValuationMethod.GROWTH_ADJUSTED
        # High growth should result in premium valuation
        assert result.value_usd > 500_000_000

    def test_growth_premium_calculation(self, valuation_model):
        """Test that higher growth gets premium valuation."""
        # Low growth scenario
        low_growth = valuation_model.calculate_growth_adjusted_value(
            company_name="SlowCo",
            revenue_usd=500_000_000,
            growth_rate_pct=20.0,
            vertical="infrastructure",
            stage="growth",
        )

        # High growth scenario
        high_growth = valuation_model.calculate_growth_adjusted_value(
            company_name="FastCo",
            revenue_usd=500_000_000,
            growth_rate_pct=150.0,
            vertical="infrastructure",
            stage="growth",
        )

        assert high_growth.value_usd > low_growth.value_usd

    def test_stage_discount_applied(self, valuation_model):
        """Test that earlier stages get discounts."""
        # Pre-IPO company
        pre_ipo = valuation_model.calculate_revenue_multiple_value(
            company_name="PreIPOCo",
            revenue_usd=500_000_000,
            vertical="infrastructure",
            stage="pre_ipo",
        )

        # Series B company (earlier stage)
        series_b = valuation_model.calculate_revenue_multiple_value(
            company_name="SeriesBCo",
            revenue_usd=500_000_000,
            vertical="infrastructure",
            stage="series_b",
        )

        # Pre-IPO should have higher valuation (less discount)
        assert pre_ipo.value_usd > series_b.value_usd

    def test_comparable_transaction_valuation(self, valuation_model):
        """Test comparable transaction valuation."""
        result = valuation_model.calculate_comparable_transaction_value(
            company_name="TestCo",
            revenue_usd=500_000_000,
            comparable_transactions=[
                {"name": "CompA", "revenue": 400_000_000, "valuation": 20_000_000_000},
                {"name": "CompB", "revenue": 600_000_000, "valuation": 30_000_000_000},
            ],
        )

        assert isinstance(result, ValuationResult)
        assert result.method == ValuationMethod.COMPARABLE_TRANSACTIONS
        assert result.value_usd > 0

    def test_public_comparables_valuation(self, valuation_model):
        """Test public company comparables valuation."""
        result = valuation_model.calculate_public_comparables_value(
            company_name="TestCo",
            revenue_usd=500_000_000,
            vertical="infrastructure",
            growth_rate_pct=50.0,
        )

        assert isinstance(result, ValuationResult)
        assert result.method == ValuationMethod.PUBLIC_COMPARABLES
        assert result.value_usd > 0

    def test_comprehensive_valuation(self, valuation_model):
        """Test comprehensive multi-method valuation."""
        result = valuation_model.calculate_comprehensive_valuation(
            company_name="TestCo",
            revenue_usd=500_000_000,
            growth_rate_pct=80.0,
            vertical="foundation_models",
            stage="pre_ipo",
        )

        assert isinstance(result, ComprehensiveValuation)
        assert len(result.valuations) > 0
        assert result.weighted_value_usd > 0
        assert result.value_range_low < result.value_range_high

    def test_analyze_deal_valuation(self, valuation_model):
        """Test deal valuation analysis."""
        result = valuation_model.analyze_deal_valuation(
            company_name="TestCo",
            deal_price_per_share=100.0,
            shares_outstanding=100_000_000,
            revenue_usd=500_000_000,
            growth_rate_pct=80.0,
            vertical="foundation_models",
            stage="pre_ipo",
        )

        assert "deal_valuation" in result
        assert "fair_value_estimate" in result
        assert "discount_to_fair_value_pct" in result
        assert "recommendation" in result

    def test_deal_recommendation_buy(self, valuation_model):
        """Test that significant discount generates BUY recommendation."""
        result = valuation_model.analyze_deal_valuation(
            company_name="CheapCo",
            deal_price_per_share=50.0,  # Low price
            shares_outstanding=100_000_000,
            revenue_usd=1_000_000_000,  # $1B revenue
            growth_rate_pct=100.0,
            vertical="foundation_models",
            stage="pre_ipo",
        )

        # With $1B revenue at 100% growth, fair value should be much higher
        # than $5B implied valuation, generating a BUY
        assert "BUY" in result["recommendation"] or "STRONG BUY" in result["recommendation"]


class TestValuationMethods:
    """Tests for individual valuation method calculations."""

    def test_vertical_multiples_exist(self, valuation_model):
        """Test all expected verticals have multiples."""
        expected_verticals = [
            "foundation_models",
            "infrastructure",
            "enterprise_ai",
            "ai_agents",
            "vertical_ai",
            "robotics",
            "defense_ai",
        ]
        for vertical in expected_verticals:
            assert vertical in valuation_model.VERTICAL_MULTIPLES

    def test_public_comparables_exist(self, valuation_model):
        """Test public comparables data is populated."""
        comparables = valuation_model.PUBLIC_COMPARABLES
        assert len(comparables) > 0

        # Check structure
        for comp in comparables:
            assert "ticker" in comp
            assert "revenue_multiple" in comp

    def test_stage_discounts_order(self, valuation_model):
        """Test stage discounts are properly ordered."""
        discounts = valuation_model.STAGE_DISCOUNTS

        # Earlier stages should have higher discounts
        assert discounts.get("seed", 0) > discounts.get("series_a", 0)
        assert discounts.get("series_a", 0) > discounts.get("series_c", 0)
        assert discounts.get("series_c", 0) > discounts.get("pre_ipo", 0)
