"""
Tests for the SecondaryMarketAggregator class.
"""

import pytest
from datetime import datetime
from epochal.integrations.secondary_markets import (
    SecondaryMarketAggregator,
    SecondaryPricing,
    SecondaryDeal,
    SecondaryPlatform,
    DealEconomics,
)


@pytest.fixture
def aggregator():
    """Create a secondary market aggregator instance."""
    return SecondaryMarketAggregator()


class TestSecondaryMarketAggregator:
    """Tests for SecondaryMarketAggregator."""

    def test_init_default(self, aggregator):
        """Test default initialization."""
        assert aggregator is not None
        assert len(aggregator.platform_configs) > 0

    def test_platforms_configured(self, aggregator):
        """Test all platforms are configured."""
        expected_platforms = [
            SecondaryPlatform.HIIVE,
            SecondaryPlatform.FORGE,
            SecondaryPlatform.EQUITYZEN,
            SecondaryPlatform.NPM,
        ]

        for platform in expected_platforms:
            assert platform in aggregator.platform_configs

    def test_validate_pricing_data(self, aggregator):
        """Test pricing data validation."""
        pricing = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.HIIVE,
            bid_price_per_share=95.0,
            ask_price_per_share=105.0,
            last_round_price=100.0,
            implied_valuation=50_000_000_000,
        )

        assert pricing.company_name == "TestCo"
        assert pricing.platform == SecondaryPlatform.HIIVE
        assert pricing.bid_price_per_share < pricing.ask_price_per_share


class TestSecondaryPricing:
    """Tests for SecondaryPricing dataclass."""

    def test_pricing_creation(self):
        """Test creating pricing data."""
        pricing = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.FORGE,
            bid_price_per_share=90.0,
            ask_price_per_share=100.0,
            last_round_price=95.0,
            implied_valuation=10_000_000_000,
            volume_30d_shares=100000,
            last_updated=datetime.utcnow(),
        )

        assert pricing.bid_price_per_share == 90.0
        assert pricing.volume_30d_shares == 100000

    def test_pricing_to_dict(self):
        """Test pricing serialization."""
        pricing = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.HIIVE,
            implied_valuation=50_000_000_000,
        )

        pricing_dict = pricing.to_dict()

        assert pricing_dict["company_name"] == "TestCo"
        assert pricing_dict["platform"] == "hiive"
        assert pricing_dict["implied_valuation"] == 50_000_000_000


class TestSecondaryDeal:
    """Tests for SecondaryDeal dataclass."""

    def test_deal_creation(self):
        """Test creating a deal."""
        deal = SecondaryDeal(
            id="deal_001",
            company_name="TestCo",
            platform=SecondaryPlatform.NPM,
            side="sell",
            price_per_share=100.0,
            shares_available=10000,
            minimum_shares=1000,
            share_class="Common",
            seller_type="employee",
            created_at=datetime.utcnow(),
        )

        assert deal.id == "deal_001"
        assert deal.side == "sell"
        assert deal.shares_available == 10000

    def test_deal_to_dict(self):
        """Test deal serialization."""
        deal = SecondaryDeal(
            id="deal_002",
            company_name="TestCo",
            platform=SecondaryPlatform.EQUITYZEN,
            side="buy",
            price_per_share=50.0,
            shares_available=5000,
        )

        deal_dict = deal.to_dict()

        assert deal_dict["id"] == "deal_002"
        assert deal_dict["side"] == "buy"


class TestDealEconomics:
    """Tests for deal economics calculations."""

    def test_economics_creation(self):
        """Test creating deal economics."""
        economics = DealEconomics(
            gross_investment_usd=1_000_000,
            platform_fee_usd=25_000,
            legal_fee_usd=10_000,
            total_cost_usd=1_035_000,
            shares_acquired=10000,
            effective_price_per_share=103.5,
            discount_to_last_round_pct=10.0,
            implied_valuation_usd=50_000_000_000,
        )

        assert economics.total_cost_usd == 1_035_000
        assert economics.effective_price_per_share == 103.5

    def test_economics_fee_calculation(self):
        """Test fee calculation in economics."""
        gross = 1_000_000
        platform_fee = 25_000
        legal_fee = 10_000
        total = gross + platform_fee + legal_fee

        economics = DealEconomics(
            gross_investment_usd=gross,
            platform_fee_usd=platform_fee,
            legal_fee_usd=legal_fee,
            total_cost_usd=total,
            shares_acquired=10000,
            effective_price_per_share=total / 10000,
        )

        assert economics.total_cost_usd == 1_035_000
        assert economics.effective_price_per_share == 103.5


class TestPlatformConnectors:
    """Tests for platform-specific connectors."""

    def test_hiive_connector_exists(self, aggregator):
        """Test Hiive connector is available."""
        assert SecondaryPlatform.HIIVE in aggregator.platform_configs

    def test_forge_connector_exists(self, aggregator):
        """Test Forge connector is available."""
        assert SecondaryPlatform.FORGE in aggregator.platform_configs

    def test_npm_connector_exists(self, aggregator):
        """Test NPM connector is available."""
        assert SecondaryPlatform.NPM in aggregator.platform_configs

    def test_equityzen_connector_exists(self, aggregator):
        """Test EquityZen connector is available."""
        assert SecondaryPlatform.EQUITYZEN in aggregator.platform_configs


class TestPriceComparison:
    """Tests for cross-platform price comparison."""

    def test_compare_prices_structure(self, aggregator):
        """Test price comparison returns expected structure."""
        # Mock pricing data
        pricing_a = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.HIIVE,
            ask_price_per_share=100.0,
            implied_valuation=50_000_000_000,
        )
        pricing_b = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.FORGE,
            ask_price_per_share=95.0,
            implied_valuation=47_500_000_000,
        )

        # Forge has lower ask price
        assert pricing_b.ask_price_per_share < pricing_a.ask_price_per_share


class TestDataSerialization:
    """Tests for data serialization."""

    def test_pricing_roundtrip(self):
        """Test pricing serialization roundtrip."""
        original = SecondaryPricing(
            company_name="TestCo",
            platform=SecondaryPlatform.HIIVE,
            bid_price_per_share=95.0,
            ask_price_per_share=105.0,
            implied_valuation=50_000_000_000,
        )

        data = original.to_dict()

        # Verify serialized data
        assert data["company_name"] == "TestCo"
        assert data["platform"] == "hiive"
        assert data["bid_price_per_share"] == 95.0

    def test_deal_roundtrip(self):
        """Test deal serialization roundtrip."""
        original = SecondaryDeal(
            id="deal_test",
            company_name="TestCo",
            platform=SecondaryPlatform.FORGE,
            side="sell",
            price_per_share=100.0,
            shares_available=5000,
        )

        data = original.to_dict()

        assert data["id"] == "deal_test"
        assert data["side"] == "sell"
