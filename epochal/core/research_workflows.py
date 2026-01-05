"""
Research Workflows for Epochal Capital.

Automated research workflows that:
1. Trigger comprehensive research when new companies are added
2. Refresh research on all tracked companies twice weekly
3. Update scores based on latest intelligence
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json
from pathlib import Path


@dataclass
class ResearchResult:
    """Result from a company research workflow."""
    company_name: str
    research_date: datetime
    valuation_usd: Optional[float] = None
    stage: Optional[str] = None
    key_investors: list[str] = field(default_factory=list)
    liquidity_signals: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    ipo_status: Optional[str] = None
    ipo_timeline: Optional[str] = None
    revenue_arr_usd: Optional[float] = None
    recent_news: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    score_before: Optional[float] = None
    score_after: Optional[float] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "research_date": self.research_date.isoformat(),
            "valuation_usd": self.valuation_usd,
            "stage": self.stage,
            "key_investors": self.key_investors,
            "liquidity_signals": self.liquidity_signals,
            "risk_factors": self.risk_factors,
            "ipo_status": self.ipo_status,
            "ipo_timeline": self.ipo_timeline,
            "revenue_arr_usd": self.revenue_arr_usd,
            "recent_news": self.recent_news,
            "sources": self.sources,
            "score_before": self.score_before,
            "score_after": self.score_after,
            "tags": self.tags,
        }


class ResearchWorkflows:
    """
    Manages automated research workflows for Epochal Capital.

    Workflows:
    - on_company_added: Comprehensive research when new company added
    - refresh_all: Twice-weekly refresh of all tracked companies
    - research_single: Deep research on a single company
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.research_history_file = self.data_dir / "research_history.json"
        self.research_history: dict = self._load_research_history()

    def _load_research_history(self) -> dict:
        """Load research history from disk."""
        if self.research_history_file.exists():
            with open(self.research_history_file) as f:
                return json.load(f)
        return {"companies": {}, "last_full_refresh": None}

    def _save_research_history(self):
        """Save research history to disk."""
        with open(self.research_history_file, "w") as f:
            json.dump(self.research_history, f, indent=2, default=str)

    def record_research(self, result: ResearchResult):
        """Record a research result."""
        company_name = result.company_name
        if company_name not in self.research_history["companies"]:
            self.research_history["companies"][company_name] = []

        self.research_history["companies"][company_name].append(result.to_dict())
        self._save_research_history()

    def get_last_research(self, company_name: str) -> Optional[dict]:
        """Get the most recent research for a company."""
        history = self.research_history["companies"].get(company_name, [])
        return history[-1] if history else None

    def get_companies_needing_refresh(self, max_age_days: int = 3) -> list[str]:
        """Get companies that haven't been researched recently."""
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        needs_refresh = []

        for company_name, history in self.research_history["companies"].items():
            if not history:
                needs_refresh.append(company_name)
            else:
                last_research = datetime.fromisoformat(history[-1]["research_date"])
                if last_research < cutoff:
                    needs_refresh.append(company_name)

        return needs_refresh

    def generate_research_queries(self, company_name: str) -> list[str]:
        """Generate search queries for comprehensive company research."""
        current_year = datetime.utcnow().year

        return [
            f"{company_name} {current_year} funding valuation IPO news",
            f"{company_name} {current_year} Series funding round investors",
            f"{company_name} IPO plans timeline {current_year}",
            f"{company_name} CEO leadership changes {current_year}",
            f"{company_name} acquisition merger news {current_year}",
        ]

    def parse_research_findings(
        self,
        company_name: str,
        search_results: list[dict],
    ) -> ResearchResult:
        """
        Parse search results into structured research findings.

        This is a template - in practice, an LLM would analyze the results.
        """
        result = ResearchResult(
            company_name=company_name,
            research_date=datetime.utcnow(),
        )

        # Extract sources
        for search in search_results:
            if "sources" in search:
                result.sources.extend(search["sources"])

        return result

    async def research_company_comprehensive(
        self,
        company_name: str,
        search_function=None,
    ) -> ResearchResult:
        """
        Run comprehensive research workflow for a company.

        Steps:
        1. Generate search queries
        2. Execute searches (funding, IPO, leadership, M&A)
        3. Parse and structure findings
        4. Update company data
        5. Recalculate score
        6. Record research history

        Args:
            company_name: Name of company to research
            search_function: Async function to execute searches (injected for testing)

        Returns:
            ResearchResult with findings
        """
        print(f"\n[Research] Starting comprehensive research: {company_name}")
        print(f"[Research] Generated queries:")

        queries = self.generate_research_queries(company_name)
        for q in queries:
            print(f"  - {q}")

        result = ResearchResult(
            company_name=company_name,
            research_date=datetime.utcnow(),
        )

        # If search function provided, execute searches
        if search_function:
            search_results = []
            for query in queries:
                try:
                    search_result = await search_function(query)
                    search_results.append(search_result)
                except Exception as e:
                    print(f"[Research] Search failed for '{query}': {e}")

            # Parse results
            result = self.parse_research_findings(company_name, search_results)

        # Record research
        self.record_research(result)

        print(f"[Research] Completed research for {company_name}")
        return result

    async def on_company_added(
        self,
        company_name: str,
        search_function=None,
    ) -> ResearchResult:
        """
        Workflow triggered when a new company is added to watchlist.

        Performs comprehensive research and updates company data.
        """
        print(f"\n{'='*60}")
        print(f"  NEW COMPANY ADDED: {company_name}")
        print(f"  Triggering comprehensive research workflow...")
        print(f"{'='*60}")

        result = await self.research_company_comprehensive(
            company_name,
            search_function=search_function,
        )

        print(f"\n[Workflow] Research complete for new company: {company_name}")
        return result

    async def refresh_all_companies(
        self,
        company_names: list[str],
        search_function=None,
        max_age_days: int = 3,
    ) -> list[ResearchResult]:
        """
        Refresh research for all tracked companies.

        This should be run twice weekly (e.g., Monday and Thursday).
        Only refreshes companies not researched within max_age_days.
        """
        print(f"\n{'='*60}")
        print(f"  SCHEDULED RESEARCH REFRESH")
        print(f"  Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  Companies to check: {len(company_names)}")
        print(f"{'='*60}")

        # Find companies needing refresh
        needs_refresh = []
        for name in company_names:
            last = self.get_last_research(name)
            if not last:
                needs_refresh.append(name)
            else:
                last_date = datetime.fromisoformat(last["research_date"])
                if datetime.utcnow() - last_date > timedelta(days=max_age_days):
                    needs_refresh.append(name)

        print(f"[Refresh] {len(needs_refresh)} companies need refresh")

        results = []
        for i, company_name in enumerate(needs_refresh, 1):
            print(f"\n[{i}/{len(needs_refresh)}] Researching {company_name}...")
            result = await self.research_company_comprehensive(
                company_name,
                search_function=search_function,
            )
            results.append(result)

        # Update last full refresh timestamp
        self.research_history["last_full_refresh"] = datetime.utcnow().isoformat()
        self._save_research_history()

        print(f"\n[Refresh] Completed refresh of {len(results)} companies")
        return results

    def get_research_summary(self) -> dict:
        """Get summary of research status."""
        total_companies = len(self.research_history["companies"])

        needs_refresh = 0
        recently_researched = 0
        cutoff = datetime.utcnow() - timedelta(days=3)

        for company_name, history in self.research_history["companies"].items():
            if history:
                last_date = datetime.fromisoformat(history[-1]["research_date"])
                if last_date >= cutoff:
                    recently_researched += 1
                else:
                    needs_refresh += 1
            else:
                needs_refresh += 1

        return {
            "total_companies_tracked": total_companies,
            "recently_researched": recently_researched,
            "needs_refresh": needs_refresh,
            "last_full_refresh": self.research_history.get("last_full_refresh"),
        }


# Convenience functions for CLI integration

async def research_new_company(company_name: str) -> ResearchResult:
    """Research a newly added company."""
    workflows = ResearchWorkflows()
    return await workflows.on_company_added(company_name)


async def refresh_all_research(company_names: list[str]) -> list[ResearchResult]:
    """Refresh research for all companies."""
    workflows = ResearchWorkflows()
    return await workflows.refresh_all_companies(company_names)


def get_research_status() -> dict:
    """Get current research status."""
    workflows = ResearchWorkflows()
    return workflows.get_research_summary()
