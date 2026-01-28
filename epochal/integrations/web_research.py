"""
Web Research Engine for Epochal Capital.

Provides live web search and data aggregation capabilities for company research.
Integrates with multiple data sources to gather comprehensive intelligence.
"""

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus


@dataclass
class NewsItem:
    """A news item from web search."""
    title: str
    source: str
    url: str
    published_date: Optional[datetime] = None
    snippet: str = ""
    relevance_score: float = 0.0
    category: str = "general"  # funding, ipo, leadership, product, partnership


@dataclass
class ResearchResult:
    """Aggregated research result for a company."""
    company_name: str
    research_date: datetime
    valuation_usd: Optional[float] = None
    last_funding_round: Optional[str] = None
    funding_amount: Optional[float] = None
    stage: Optional[str] = None
    key_investors: list[str] = field(default_factory=list)
    liquidity_signals: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    ipo_status: Optional[str] = None
    ipo_timeline: Optional[str] = None
    revenue_arr_usd: Optional[float] = None
    employee_count: Optional[int] = None
    recent_news: list[NewsItem] = field(default_factory=list)
    executive_changes: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    confidence_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "research_date": self.research_date.isoformat(),
            "valuation_usd": self.valuation_usd,
            "last_funding_round": self.last_funding_round,
            "funding_amount": self.funding_amount,
            "stage": self.stage,
            "key_investors": self.key_investors,
            "liquidity_signals": self.liquidity_signals,
            "risk_factors": self.risk_factors,
            "ipo_status": self.ipo_status,
            "ipo_timeline": self.ipo_timeline,
            "revenue_arr_usd": self.revenue_arr_usd,
            "employee_count": self.employee_count,
            "recent_news": [
                {
                    "title": n.title,
                    "source": n.source,
                    "url": n.url,
                    "snippet": n.snippet,
                    "category": n.category,
                }
                for n in self.recent_news
            ],
            "executive_changes": self.executive_changes,
            "sources": self.sources,
            "confidence_score": self.confidence_score,
        }


class WebResearchEngine:
    """
    Engine for conducting live web research on companies.

    Capabilities:
    - Web search aggregation
    - News monitoring
    - Financial data extraction
    - IPO signal detection
    - Leadership change tracking
    """

    # Research query templates
    QUERY_TEMPLATES = {
        "funding": "{company} funding round valuation 2026",
        "ipo": "{company} IPO timeline filing 2026",
        "revenue": "{company} revenue ARR annual recurring 2026",
        "leadership": "{company} CEO executive leadership changes",
        "news": "{company} AI latest news",
        "investors": "{company} investors funding investors",
        "acquisition": "{company} acquisition M&A deal",
    }

    # Patterns for extracting data from text
    VALUATION_PATTERNS = [
        r"\$(\d+(?:\.\d+)?)\s*(?:billion|B)\s*valuation",
        r"valued\s+at\s+\$(\d+(?:\.\d+)?)\s*(?:billion|B)",
        r"valuation\s+(?:of\s+)?\$(\d+(?:\.\d+)?)\s*(?:billion|B)",
        r"\$(\d+(?:\.\d+)?)\s*(?:billion|B)\s*(?:post-money|pre-money)",
    ]

    REVENUE_PATTERNS = [
        r"\$(\d+(?:\.\d+)?)\s*(?:billion|B)\s*(?:ARR|revenue|run.?rate)",
        r"(\d+(?:\.\d+)?)\s*(?:billion|B)\s*(?:in\s+)?(?:ARR|revenue)",
        r"ARR\s*(?:of\s*)?\$(\d+(?:\.\d+)?)\s*(?:billion|B|million|M)",
        r"revenue\s*(?:of\s*)?\$(\d+(?:\.\d+)?)\s*(?:billion|B|million|M)",
    ]

    IPO_KEYWORDS = [
        "ipo", "public offering", "going public", "direct listing",
        "s-1 filing", "sec filing", "ipo timeline", "ipo preparation",
        "confidential filing", "wilson sonsini", "morgan stanley ipo",
    ]

    RISK_KEYWORDS = [
        "lawsuit", "investigation", "regulatory", "layoffs",
        "ceo departure", "leadership exodus", "restructuring",
        "cash burn", "runway", "competition", "antitrust",
    ]

    def __init__(self, cache_dir: str = "data/research_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=24)

    def generate_research_queries(self, company_name: str) -> list[str]:
        """Generate search queries for comprehensive research."""
        queries = []
        for query_type, template in self.QUERY_TEMPLATES.items():
            queries.append({
                "type": query_type,
                "query": template.format(company=company_name),
            })
        return queries

    async def research_company(
        self,
        company_name: str,
        use_cache: bool = True,
    ) -> ResearchResult:
        """
        Conduct comprehensive research on a company.

        This method would integrate with actual web search APIs.
        Currently provides a framework that can be connected to:
        - Google Custom Search API
        - Bing Search API
        - SerpAPI
        - News APIs (NewsAPI, Google News)
        """
        # Check cache first
        if use_cache:
            cached = self._load_from_cache(company_name)
            if cached:
                return cached

        # Generate queries
        queries = self.generate_research_queries(company_name)

        # Initialize result
        result = ResearchResult(
            company_name=company_name,
            research_date=datetime.utcnow(),
        )

        # In a production system, these would be actual API calls
        # For now, we provide the framework for integration
        result.sources = [q["query"] for q in queries]

        # Extract any data from tracked companies (as baseline)
        result = self._enrich_from_tracked_companies(company_name, result)

        # Cache the result
        self._save_to_cache(company_name, result)

        return result

    def _enrich_from_tracked_companies(
        self,
        company_name: str,
        result: ResearchResult,
    ) -> ResearchResult:
        """Enrich research result from tracked companies data."""
        try:
            from epochal.agents.deal_sourcing import TRACKED_AI_COMPANIES

            for company in TRACKED_AI_COMPANIES:
                if company["name"].lower() == company_name.lower():
                    result.valuation_usd = company.get("valuation_usd")
                    result.stage = company.get("stage").value if company.get("stage") else None
                    result.key_investors = company.get("key_investors", [])
                    result.liquidity_signals = company.get("liquidity_signals", [])
                    result.revenue_arr_usd = company.get("revenue_arr_usd")

                    # Extract IPO signals
                    for signal in result.liquidity_signals:
                        signal_lower = signal.lower()
                        if any(kw in signal_lower for kw in self.IPO_KEYWORDS):
                            result.ipo_status = "Preparing"
                            # Try to extract timeline
                            if "h1 2026" in signal_lower:
                                result.ipo_timeline = "H1 2026"
                            elif "h2 2026" in signal_lower:
                                result.ipo_timeline = "H2 2026"
                            elif "q1 2026" in signal_lower:
                                result.ipo_timeline = "Q1 2026"
                            elif "q2 2026" in signal_lower:
                                result.ipo_timeline = "Q2 2026"
                            elif "2026" in signal_lower:
                                result.ipo_timeline = "2026"

                    # Check for risk factors from tags
                    tags = company.get("tags", [])
                    if "leadership_exodus" in tags or "ceo_departed" in tags:
                        result.risk_factors.append("Leadership exodus - key executives departed")
                    if "restructuring" in tags:
                        result.risk_factors.append("Company undergoing restructuring")
                    if "acquired" in tags:
                        result.liquidity_signals = ["ACQUIRED - Liquidity event complete"]
                    if "valuation_risk" in tags:
                        result.risk_factors.append("High valuation multiple - premium to last round")

                    result.confidence_score = 0.9  # High confidence from internal data
                    break

        except ImportError:
            pass

        return result

    def extract_valuation(self, text: str) -> Optional[float]:
        """Extract valuation from text."""
        for pattern in self.VALUATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                # Assume billions if > 0.1
                if value < 1000:
                    return value * 1_000_000_000
                return value * 1_000_000  # millions
        return None

    def extract_revenue(self, text: str) -> Optional[float]:
        """Extract revenue/ARR from text."""
        for pattern in self.REVENUE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                text_lower = text.lower()
                if "billion" in text_lower or "b" in match.group(0).lower():
                    return value * 1_000_000_000
                return value * 1_000_000  # millions
        return None

    def detect_ipo_signals(self, text: str) -> list[str]:
        """Detect IPO-related signals in text."""
        signals = []
        text_lower = text.lower()

        if "s-1" in text_lower or "s1" in text_lower:
            signals.append("S-1 filing mentioned")
        if "confidential" in text_lower and "filing" in text_lower:
            signals.append("Confidential IPO filing")
        if "wilson sonsini" in text_lower:
            signals.append("Wilson Sonsini engaged (IPO counsel)")
        if "morgan stanley" in text_lower and "ipo" in text_lower:
            signals.append("Morgan Stanley as IPO advisor")
        if "goldman" in text_lower and "ipo" in text_lower:
            signals.append("Goldman Sachs as IPO advisor")
        if "direct listing" in text_lower:
            signals.append("Direct listing considered")
        if "roadshow" in text_lower:
            signals.append("IPO roadshow mentioned")

        return signals

    def detect_risk_factors(self, text: str) -> list[str]:
        """Detect risk factors in text."""
        risks = []
        text_lower = text.lower()

        if "layoff" in text_lower or "cut" in text_lower and "job" in text_lower:
            risks.append("Layoffs or job cuts reported")
        if "ceo" in text_lower and ("depart" in text_lower or "left" in text_lower or "resign" in text_lower):
            risks.append("CEO departure")
        if "investigation" in text_lower or "probe" in text_lower:
            risks.append("Regulatory investigation")
        if "lawsuit" in text_lower or "litigation" in text_lower:
            risks.append("Legal proceedings")
        if "burn rate" in text_lower or "cash burn" in text_lower:
            risks.append("Cash burn concerns")
        if "restructur" in text_lower:
            risks.append("Restructuring")

        return risks

    def _cache_key(self, company_name: str) -> str:
        """Generate cache key for company."""
        return hashlib.md5(company_name.lower().encode()).hexdigest()

    def _load_from_cache(self, company_name: str) -> Optional[ResearchResult]:
        """Load research from cache if fresh."""
        cache_file = self.cache_dir / f"{self._cache_key(company_name)}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            # Check freshness
            research_date = datetime.fromisoformat(data["research_date"])
            if datetime.utcnow() - research_date > self.cache_ttl:
                return None

            # Reconstruct result
            return ResearchResult(
                company_name=data["company_name"],
                research_date=research_date,
                valuation_usd=data.get("valuation_usd"),
                stage=data.get("stage"),
                key_investors=data.get("key_investors", []),
                liquidity_signals=data.get("liquidity_signals", []),
                risk_factors=data.get("risk_factors", []),
                ipo_status=data.get("ipo_status"),
                ipo_timeline=data.get("ipo_timeline"),
                revenue_arr_usd=data.get("revenue_arr_usd"),
                sources=data.get("sources", []),
                confidence_score=data.get("confidence_score", 0.0),
            )
        except Exception:
            return None

    def _save_to_cache(self, company_name: str, result: ResearchResult):
        """Save research to cache."""
        cache_file = self.cache_dir / f"{self._cache_key(company_name)}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
        except Exception:
            pass

    async def batch_research(
        self,
        company_names: list[str],
        max_concurrent: int = 5,
    ) -> list[ResearchResult]:
        """Research multiple companies concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def research_with_semaphore(name: str) -> ResearchResult:
            async with semaphore:
                return await self.research_company(name)

        tasks = [research_with_semaphore(name) for name in company_names]
        return await asyncio.gather(*tasks)

    def get_research_summary(self, results: list[ResearchResult]) -> dict:
        """Generate summary of research results."""
        summary = {
            "total_companies": len(results),
            "with_ipo_signals": 0,
            "with_risk_factors": 0,
            "total_market_cap": 0,
            "avg_confidence": 0,
            "by_stage": {},
            "top_opportunities": [],
        }

        for result in results:
            if result.ipo_status:
                summary["with_ipo_signals"] += 1
            if result.risk_factors:
                summary["with_risk_factors"] += 1
            if result.valuation_usd:
                summary["total_market_cap"] += result.valuation_usd
            summary["avg_confidence"] += result.confidence_score

            if result.stage:
                summary["by_stage"][result.stage] = summary["by_stage"].get(result.stage, 0) + 1

        if results:
            summary["avg_confidence"] /= len(results)

        # Sort by confidence for top opportunities
        sorted_results = sorted(results, key=lambda r: r.confidence_score, reverse=True)
        summary["top_opportunities"] = [r.company_name for r in sorted_results[:5]]

        return summary
