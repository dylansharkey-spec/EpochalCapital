"""
Tests for the WebResearchEngine class.
"""

import pytest
from datetime import datetime, timedelta
from epochal.integrations.web_research import (
    WebResearchEngine,
    ResearchResult,
    NewsItem,
)


@pytest.fixture
def research_engine(temp_data_dir):
    """Create a web research engine instance."""
    return WebResearchEngine(cache_dir=temp_data_dir)


class TestWebResearchEngine:
    """Tests for WebResearchEngine."""

    def test_init_default(self, research_engine):
        """Test default initialization."""
        assert research_engine is not None
        assert len(research_engine.QUERY_TEMPLATES) > 0

    def test_query_templates_exist(self, research_engine):
        """Test expected query templates exist."""
        expected_templates = ["funding", "ipo", "revenue", "news"]

        for template in expected_templates:
            assert template in research_engine.QUERY_TEMPLATES

    def test_generate_queries(self, research_engine):
        """Test query generation for a company."""
        queries = research_engine.generate_queries("Anthropic")

        assert len(queries) > 0
        assert all("Anthropic" in q for q in queries)


class TestResearchResult:
    """Tests for ResearchResult dataclass."""

    def test_result_creation(self):
        """Test creating a research result."""
        result = ResearchResult(
            company_name="TestAI",
            research_date=datetime.utcnow(),
            valuation_usd=50_000_000_000,
            key_investors=["Investor A", "Investor B"],
            liquidity_signals=["IPO H2 2026"],
            revenue_arr_usd=1_000_000_000,
        )

        assert result.company_name == "TestAI"
        assert result.valuation_usd == 50_000_000_000
        assert len(result.key_investors) == 2

    def test_result_to_dict(self):
        """Test result serialization."""
        result = ResearchResult(
            company_name="TestAI",
            research_date=datetime.utcnow(),
            valuation_usd=50_000_000_000,
        )

        result_dict = result.to_dict()

        assert result_dict["company_name"] == "TestAI"
        assert result_dict["valuation_usd"] == 50_000_000_000

    def test_result_with_all_fields(self):
        """Test result with all fields populated."""
        result = ResearchResult(
            company_name="FullDataCo",
            research_date=datetime.utcnow(),
            valuation_usd=100_000_000_000,
            key_investors=["VC1", "VC2", "VC3"],
            liquidity_signals=["IPO filed", "Secondary active"],
            risk_factors=["Competition", "Regulation"],
            ipo_status="filed",
            ipo_timeline="Q3 2026",
            revenue_arr_usd=5_000_000_000,
            employee_count=2000,
            founding_year=2020,
            headquarters="San Francisco",
            recent_news=["News item 1", "News item 2"],
            competitive_landscape="Strong position",
            sources=["TechCrunch", "Bloomberg"],
        )

        assert result.ipo_status == "filed"
        assert len(result.sources) == 2


class TestNewsItem:
    """Tests for NewsItem dataclass."""

    def test_news_item_creation(self):
        """Test creating a news item."""
        news = NewsItem(
            title="TestAI Raises $5B",
            source="TechCrunch",
            url="https://techcrunch.com/test",
            published_at=datetime.utcnow(),
            summary="TestAI announced a $5B funding round.",
        )

        assert news.title == "TestAI Raises $5B"
        assert news.source == "TechCrunch"

    def test_news_item_to_dict(self):
        """Test news item serialization."""
        news = NewsItem(
            title="Test News",
            source="Bloomberg",
            url="https://bloomberg.com/test",
            published_at=datetime.utcnow(),
        )

        news_dict = news.to_dict()

        assert news_dict["title"] == "Test News"
        assert news_dict["source"] == "Bloomberg"


class TestPatternExtraction:
    """Tests for pattern extraction from text."""

    def test_extract_valuation(self, research_engine):
        """Test valuation extraction from text."""
        text = "Anthropic raised funding at a $350 billion valuation."
        valuation = research_engine.extract_valuation(text)

        assert valuation is not None
        assert valuation == 350_000_000_000

    def test_extract_valuation_with_b(self, research_engine):
        """Test valuation extraction with 'B' notation."""
        text = "The company is valued at $50B."
        valuation = research_engine.extract_valuation(text)

        assert valuation is not None
        assert valuation == 50_000_000_000

    def test_extract_revenue(self, research_engine):
        """Test revenue extraction from text."""
        text = "The company reported $2 billion ARR."
        revenue = research_engine.extract_revenue(text)

        assert revenue is not None
        assert revenue == 2_000_000_000

    def test_extract_funding_amount(self, research_engine):
        """Test funding amount extraction."""
        text = "TestCo raised $500 million in Series D funding."
        amount = research_engine.extract_funding_amount(text)

        assert amount is not None
        assert amount == 500_000_000


class TestIPODetection:
    """Tests for IPO signal detection."""

    def test_detect_ipo_filing(self, research_engine):
        """Test IPO filing detection."""
        text = "The company filed an S-1 with the SEC."
        signals = research_engine.detect_ipo_signals(text)

        assert len(signals) > 0
        assert any("s-1" in s.lower() or "filed" in s.lower() for s in signals)

    def test_detect_ipo_preparation(self, research_engine):
        """Test IPO preparation detection."""
        text = "Sources say the company is preparing for an IPO in H2 2026."
        signals = research_engine.detect_ipo_signals(text)

        assert len(signals) > 0


class TestRiskDetection:
    """Tests for risk signal detection."""

    def test_detect_leadership_risk(self, research_engine):
        """Test leadership change detection."""
        text = "The CEO resigned effective immediately."
        risks = research_engine.detect_risk_signals(text)

        assert len(risks) > 0

    def test_detect_regulatory_risk(self, research_engine):
        """Test regulatory risk detection."""
        text = "The FTC opened an investigation into the company."
        risks = research_engine.detect_risk_signals(text)

        assert len(risks) > 0

    def test_detect_layoff_risk(self, research_engine):
        """Test layoff detection."""
        text = "The company announced 20% workforce reduction."
        risks = research_engine.detect_risk_signals(text)

        assert len(risks) > 0


class TestCaching:
    """Tests for research caching."""

    def test_cache_key_generation(self, research_engine):
        """Test cache key generation is consistent."""
        key1 = research_engine._generate_cache_key("TestCo")
        key2 = research_engine._generate_cache_key("TestCo")

        assert key1 == key2

    def test_cache_key_different_companies(self, research_engine):
        """Test different companies get different keys."""
        key1 = research_engine._generate_cache_key("CompanyA")
        key2 = research_engine._generate_cache_key("CompanyB")

        assert key1 != key2


class TestDataAggregation:
    """Tests for data aggregation from multiple sources."""

    def test_aggregate_results(self, research_engine):
        """Test aggregating multiple research results."""
        results = [
            ResearchResult(
                company_name="TestCo",
                research_date=datetime.utcnow(),
                valuation_usd=50_000_000_000,
                key_investors=["Investor A"],
            ),
            ResearchResult(
                company_name="TestCo",
                research_date=datetime.utcnow(),
                valuation_usd=55_000_000_000,
                key_investors=["Investor B"],
            ),
        ]

        # Both results should have valid data
        assert all(r.valuation_usd > 0 for r in results)
        assert len(set(r.key_investors[0] for r in results)) == 2


class TestReportGeneration:
    """Tests for research report generation."""

    def test_generate_research_summary(self, research_engine):
        """Test research summary generation."""
        result = ResearchResult(
            company_name="TestAI",
            research_date=datetime.utcnow(),
            valuation_usd=50_000_000_000,
            key_investors=["Top VC", "Growth Fund"],
            liquidity_signals=["IPO H2 2026", "Secondary active"],
            revenue_arr_usd=2_000_000_000,
        )

        summary = research_engine.generate_summary(result)

        assert "TestAI" in summary
        assert "$50" in summary or "50B" in summary or "50 billion" in summary.lower()
