"""
Secondary Market Integration for Epochal Capital.

Provides connectivity to secondary market platforms for:
- Live pricing data
- Deal discovery
- Transaction execution support
- Market depth analysis
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class SecondaryPlatform(str, Enum):
    """Supported secondary market platforms."""
    HIIVE = "hiive"
    FORGE = "forge"
    EQUITYZEN = "equityzen"
    NPM = "nasdaq_private_market"
    CARTA_X = "carta_x"
    ZANBATO = "zanbato"


class DealType(str, Enum):
    """Types of secondary deals."""
    SINGLE_ASSET_FUND = "single_asset_fund"
    DIRECT_SHARE = "direct_share"
    SPV = "spv"
    FORWARD_CONTRACT = "forward_contract"
    TENDER_OFFER = "tender_offer"


@dataclass
class SecondaryPricing:
    """Pricing data from secondary market."""
    company_name: str
    platform: SecondaryPlatform
    bid_price_per_share: Optional[float] = None
    ask_price_per_share: Optional[float] = None
    last_trade_price: Optional[float] = None
    last_trade_date: Optional[datetime] = None
    implied_valuation: Optional[float] = None
    shares_outstanding: Optional[int] = None
    volume_30d: Optional[float] = None
    spread_pct: Optional[float] = None
    last_round_price: Optional[float] = None
    premium_to_last_round: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def calculate_spread(self) -> Optional[float]:
        """Calculate bid-ask spread percentage."""
        if self.bid_price_per_share and self.ask_price_per_share:
            mid = (self.bid_price_per_share + self.ask_price_per_share) / 2
            spread = self.ask_price_per_share - self.bid_price_per_share
            return (spread / mid) * 100
        return None

    def calculate_premium_to_last_round(self) -> Optional[float]:
        """Calculate premium/discount to last funding round."""
        if self.last_trade_price and self.last_round_price:
            return ((self.last_trade_price / self.last_round_price) - 1) * 100
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "platform": self.platform.value,
            "bid_price": self.bid_price_per_share,
            "ask_price": self.ask_price_per_share,
            "last_trade": self.last_trade_price,
            "last_trade_date": self.last_trade_date.isoformat() if self.last_trade_date else None,
            "implied_valuation": self.implied_valuation,
            "volume_30d": self.volume_30d,
            "spread_pct": self.spread_pct or self.calculate_spread(),
            "premium_to_last_round": self.premium_to_last_round,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SecondaryDeal:
    """A secondary market deal opportunity."""
    id: str
    company_name: str
    platform: SecondaryPlatform
    deal_type: DealType
    price_per_share: Optional[float] = None
    implied_valuation: Optional[float] = None
    minimum_investment: float = 0.0
    total_available: float = 0.0
    management_fee_pct: float = 0.0
    carry_pct: float = 0.0
    setup_fee_pct: float = 0.0
    discount_to_ipo: Optional[float] = None  # For convertible notes
    share_class: str = "Common"
    lock_up_months: int = 0
    accreditation_required: bool = True
    closing_date: Optional[datetime] = None
    description: str = ""
    source_url: str = ""
    discovered_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_total_fees(self) -> float:
        """Calculate total fee load."""
        return self.management_fee_pct + self.setup_fee_pct

    def calculate_effective_price(self) -> Optional[float]:
        """Calculate effective price after fees."""
        if self.price_per_share:
            fee_multiplier = 1 + (self.calculate_total_fees() / 100)
            return self.price_per_share * fee_multiplier
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "platform": self.platform.value,
            "deal_type": self.deal_type.value,
            "price_per_share": self.price_per_share,
            "implied_valuation": self.implied_valuation,
            "minimum_investment": self.minimum_investment,
            "total_available": self.total_available,
            "management_fee_pct": self.management_fee_pct,
            "carry_pct": self.carry_pct,
            "setup_fee_pct": self.setup_fee_pct,
            "total_fees_pct": self.calculate_total_fees(),
            "effective_price": self.calculate_effective_price(),
            "discount_to_ipo": self.discount_to_ipo,
            "share_class": self.share_class,
            "lock_up_months": self.lock_up_months,
            "closing_date": self.closing_date.isoformat() if self.closing_date else None,
            "discovered_at": self.discovered_at.isoformat(),
        }


class PlatformConnector:
    """Base class for platform-specific connectors."""

    platform: SecondaryPlatform

    async def get_pricing(self, company_name: str) -> Optional[SecondaryPricing]:
        """Get current pricing for a company."""
        raise NotImplementedError

    async def get_available_deals(self) -> list[SecondaryDeal]:
        """Get all available deals."""
        raise NotImplementedError

    async def search_company(self, company_name: str) -> list[SecondaryDeal]:
        """Search for deals by company name."""
        raise NotImplementedError


class HiiveConnector(PlatformConnector):
    """Connector for Hiive secondary market."""

    platform = SecondaryPlatform.HIIVE

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.hiive.com"  # Placeholder

    async def get_pricing(self, company_name: str) -> Optional[SecondaryPricing]:
        """
        Get Hiive pricing for a company.

        In production, this would call the Hiive API.
        """
        # Placeholder - would integrate with actual API
        return SecondaryPricing(
            company_name=company_name,
            platform=self.platform,
        )

    async def get_available_deals(self) -> list[SecondaryDeal]:
        """Get available Hiive single-asset funds."""
        return []

    async def search_company(self, company_name: str) -> list[SecondaryDeal]:
        """Search Hiive for company deals."""
        return []


class ForgeConnector(PlatformConnector):
    """Connector for Forge Global secondary market."""

    platform = SecondaryPlatform.FORGE

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.forgeglobal.com"  # Placeholder

    async def get_pricing(self, company_name: str) -> Optional[SecondaryPricing]:
        """Get Forge pricing data."""
        return SecondaryPricing(
            company_name=company_name,
            platform=self.platform,
        )

    async def get_available_deals(self) -> list[SecondaryDeal]:
        """Get available Forge deals."""
        return []

    async def search_company(self, company_name: str) -> list[SecondaryDeal]:
        """Search Forge for company deals."""
        return []


class NPMConnector(PlatformConnector):
    """Connector for Nasdaq Private Market."""

    platform = SecondaryPlatform.NPM

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.nasdaqprivatemarket.com"  # Placeholder

    async def get_pricing(self, company_name: str) -> Optional[SecondaryPricing]:
        """Get NPM pricing data."""
        return SecondaryPricing(
            company_name=company_name,
            platform=self.platform,
        )

    async def get_available_deals(self) -> list[SecondaryDeal]:
        """Get available NPM tender offers and SPVs."""
        return []

    async def search_company(self, company_name: str) -> list[SecondaryDeal]:
        """Search NPM for company deals."""
        return []


class EquityZenConnector(PlatformConnector):
    """Connector for EquityZen."""

    platform = SecondaryPlatform.EQUITYZEN

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def get_pricing(self, company_name: str) -> Optional[SecondaryPricing]:
        """Get EquityZen pricing."""
        return SecondaryPricing(
            company_name=company_name,
            platform=self.platform,
        )

    async def get_available_deals(self) -> list[SecondaryDeal]:
        """Get available EquityZen SPVs."""
        return []

    async def search_company(self, company_name: str) -> list[SecondaryDeal]:
        """Search EquityZen for company deals."""
        return []


class SecondaryMarketAggregator:
    """
    Aggregates data from multiple secondary market platforms.

    Provides:
    - Cross-platform pricing comparison
    - Deal discovery across all platforms
    - Best execution analysis
    - Market depth assessment
    """

    def __init__(self):
        self.connectors: list[PlatformConnector] = [
            HiiveConnector(),
            ForgeConnector(),
            NPMConnector(),
            EquityZenConnector(),
        ]
        self._pricing_cache: dict[str, dict[SecondaryPlatform, SecondaryPricing]] = {}
        self._cache_ttl = timedelta(minutes=15)

    async def get_aggregated_pricing(
        self,
        company_name: str,
        refresh: bool = False,
    ) -> dict[str, SecondaryPricing]:
        """
        Get pricing from all platforms for a company.

        Returns dict mapping platform name to pricing data.
        """
        if not refresh and company_name in self._pricing_cache:
            # Check cache freshness
            first_pricing = next(iter(self._pricing_cache[company_name].values()))
            if datetime.utcnow() - first_pricing.timestamp < self._cache_ttl:
                return self._pricing_cache[company_name]

        pricing_results = {}

        # Query all platforms concurrently
        tasks = [
            connector.get_pricing(company_name)
            for connector in self.connectors
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for connector, result in zip(self.connectors, results):
            if isinstance(result, SecondaryPricing) and result is not None:
                pricing_results[connector.platform.value] = result

        # Cache results
        self._pricing_cache[company_name] = pricing_results

        return pricing_results

    async def find_best_price(
        self,
        company_name: str,
        side: str = "buy",  # "buy" or "sell"
    ) -> Optional[tuple[SecondaryPlatform, float]]:
        """
        Find best price across all platforms.

        For buying: lowest ask price
        For selling: highest bid price
        """
        pricing = await self.get_aggregated_pricing(company_name)

        best_platform = None
        best_price = None

        for platform_name, price_data in pricing.items():
            if side == "buy" and price_data.ask_price_per_share:
                if best_price is None or price_data.ask_price_per_share < best_price:
                    best_price = price_data.ask_price_per_share
                    best_platform = SecondaryPlatform(platform_name)
            elif side == "sell" and price_data.bid_price_per_share:
                if best_price is None or price_data.bid_price_per_share > best_price:
                    best_price = price_data.bid_price_per_share
                    best_platform = SecondaryPlatform(platform_name)

        if best_platform and best_price:
            return (best_platform, best_price)
        return None

    async def get_all_available_deals(
        self,
        min_valuation: Optional[float] = None,
        max_valuation: Optional[float] = None,
        companies: Optional[list[str]] = None,
    ) -> list[SecondaryDeal]:
        """
        Get all available deals from all platforms.

        Optionally filter by valuation range or specific companies.
        """
        all_deals = []

        # Query all platforms concurrently
        tasks = [connector.get_available_deals() for connector in self.connectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_deals.extend(result)

        # Apply filters
        filtered_deals = all_deals

        if min_valuation:
            filtered_deals = [
                d for d in filtered_deals
                if d.implied_valuation and d.implied_valuation >= min_valuation
            ]

        if max_valuation:
            filtered_deals = [
                d for d in filtered_deals
                if d.implied_valuation and d.implied_valuation <= max_valuation
            ]

        if companies:
            company_names_lower = [c.lower() for c in companies]
            filtered_deals = [
                d for d in filtered_deals
                if d.company_name.lower() in company_names_lower
            ]

        # Sort by implied valuation
        filtered_deals.sort(
            key=lambda d: d.implied_valuation or 0,
            reverse=True,
        )

        return filtered_deals

    async def search_deals(
        self,
        company_name: str,
    ) -> list[SecondaryDeal]:
        """Search for deals across all platforms for a specific company."""
        all_deals = []

        tasks = [
            connector.search_company(company_name)
            for connector in self.connectors
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_deals.extend(result)

        return all_deals

    async def compare_deal_economics(
        self,
        deals: list[SecondaryDeal],
    ) -> list[dict]:
        """
        Compare economics across multiple deals.

        Returns ranked list with analysis.
        """
        comparisons = []

        for deal in deals:
            analysis = {
                "deal_id": deal.id,
                "company": deal.company_name,
                "platform": deal.platform.value,
                "deal_type": deal.deal_type.value,
                "price_per_share": deal.price_per_share,
                "total_fees_pct": deal.calculate_total_fees(),
                "effective_price": deal.calculate_effective_price(),
                "minimum_investment": deal.minimum_investment,
                "liquidity_score": self._calculate_liquidity_score(deal),
                "fee_efficiency_score": self._calculate_fee_efficiency(deal),
                "overall_score": 0,
            }

            # Calculate overall score (lower is better for fees, higher for liquidity)
            if analysis["fee_efficiency_score"] and analysis["liquidity_score"]:
                analysis["overall_score"] = (
                    analysis["fee_efficiency_score"] * 0.4 +
                    analysis["liquidity_score"] * 0.6
                )

            comparisons.append(analysis)

        # Sort by overall score (higher is better)
        comparisons.sort(key=lambda x: x["overall_score"], reverse=True)

        return comparisons

    def _calculate_liquidity_score(self, deal: SecondaryDeal) -> float:
        """Calculate liquidity score for a deal (0-100)."""
        score = 50  # Base score

        # Prefer shorter lock-ups
        if deal.lock_up_months == 0:
            score += 20
        elif deal.lock_up_months <= 6:
            score += 10
        elif deal.lock_up_months > 12:
            score -= 10

        # Prefer direct shares over funds
        if deal.deal_type == DealType.DIRECT_SHARE:
            score += 15
        elif deal.deal_type == DealType.TENDER_OFFER:
            score += 10

        # Prefer common shares
        if deal.share_class.lower() == "common":
            score += 5

        return min(100, max(0, score))

    def _calculate_fee_efficiency(self, deal: SecondaryDeal) -> float:
        """Calculate fee efficiency score (0-100, higher is better = lower fees)."""
        total_fees = deal.calculate_total_fees()

        # Score inversely proportional to fees
        if total_fees <= 2:
            return 100
        elif total_fees <= 5:
            return 80
        elif total_fees <= 8:
            return 60
        elif total_fees <= 12:
            return 40
        else:
            return 20

    def get_market_summary(self, pricing_data: dict[str, dict]) -> dict:
        """
        Generate market summary across all tracked companies.

        Args:
            pricing_data: Dict mapping company names to platform pricing
        """
        summary = {
            "total_companies": len(pricing_data),
            "platforms_active": set(),
            "avg_spread": 0,
            "avg_premium_to_last_round": 0,
            "most_liquid": [],
            "widest_spreads": [],
        }

        spreads = []
        premiums = []

        for company, platforms in pricing_data.items():
            for platform, pricing in platforms.items():
                summary["platforms_active"].add(platform)

                if pricing.spread_pct:
                    spreads.append((company, pricing.spread_pct))
                if pricing.premium_to_last_round:
                    premiums.append((company, pricing.premium_to_last_round))

        if spreads:
            summary["avg_spread"] = sum(s[1] for s in spreads) / len(spreads)
            spreads.sort(key=lambda x: x[1])
            summary["most_liquid"] = [s[0] for s in spreads[:5]]
            summary["widest_spreads"] = [s[0] for s in spreads[-5:]]

        if premiums:
            summary["avg_premium_to_last_round"] = sum(p[1] for p in premiums) / len(premiums)

        summary["platforms_active"] = list(summary["platforms_active"])

        return summary
