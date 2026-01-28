"""
External integrations for Epochal Capital.

This module provides integrations with:
- Secondary market platforms (Forge, EquityZen, Nasdaq Private Market, Hiive)
- Data providers (PitchBook, Crunchbase)
- News and intelligence sources
- Broker networks
- Web research engines
"""

from epochal.integrations.web_research import (
    WebResearchEngine,
    ResearchResult,
    NewsItem,
)
from epochal.integrations.secondary_markets import (
    SecondaryMarketAggregator,
    SecondaryPricing,
    SecondaryDeal,
)
from epochal.integrations.news_feed import (
    NewsFeedMonitor,
    MaterialEvent,
)

__all__ = [
    "WebResearchEngine",
    "ResearchResult",
    "NewsItem",
    "SecondaryMarketAggregator",
    "SecondaryPricing",
    "SecondaryDeal",
    "NewsFeedMonitor",
    "MaterialEvent",
]

SECONDARY_PLATFORMS = [
    {
        "name": "Forge Global",
        "type": "secondary_market",
        "url": "https://forgeglobal.com",
        "capabilities": ["price_discovery", "deal_flow", "secondary_trades"],
    },
    {
        "name": "EquityZen",
        "type": "secondary_market",
        "url": "https://equityzen.com",
        "capabilities": ["spv_investment", "deal_flow"],
    },
    {
        "name": "Nasdaq Private Market",
        "type": "secondary_market",
        "url": "https://nasdaqprivatemarket.com",
        "capabilities": ["tender_offers", "liquidity_programs"],
    },
    {
        "name": "Hiive",
        "type": "secondary_market",
        "url": "https://hiive.com",
        "capabilities": ["price_discovery", "deal_flow"],
    },
    {
        "name": "Zanbato",
        "type": "secondary_market",
        "url": "https://zanbato.com",
        "capabilities": ["institutional_secondary"],
    },
]

DATA_PROVIDERS = [
    {
        "name": "PitchBook",
        "type": "data_provider",
        "capabilities": ["valuations", "funding_rounds", "investor_data"],
    },
    {
        "name": "Crunchbase",
        "type": "data_provider",
        "capabilities": ["company_data", "funding_rounds", "news"],
    },
    {
        "name": "CB Insights",
        "type": "data_provider",
        "capabilities": ["market_analysis", "company_rankings"],
    },
]
