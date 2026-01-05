"""
Investment Thesis Configuration and Scoring System.

Defines the investment criteria for Epochal Capital and provides
scoring mechanisms to evaluate deals against the thesis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from epochal.core.models import (
    AIVertical,
    Company,
    CompanyStage,
    Deal,
    LiquidityEventType,
)


@dataclass
class ThesisCriteria:
    """
    Configurable investment criteria for the fund.

    Adjust these weights and thresholds to tune deal scoring.
    """
    # Target characteristics
    target_verticals: list[AIVertical] = field(default_factory=lambda: [
        AIVertical.FOUNDATION_MODELS,
        AIVertical.INFRASTRUCTURE,
        AIVertical.AI_AGENTS,
        AIVertical.DEVELOPER_TOOLS,
        AIVertical.ENTERPRISE_AI,
        AIVertical.DATA_INFRASTRUCTURE,
        AIVertical.MLOps,
    ])

    target_stages: list[CompanyStage] = field(default_factory=lambda: [
        CompanyStage.SERIES_B,
        CompanyStage.SERIES_C,
        CompanyStage.SERIES_D_PLUS,
        CompanyStage.PRE_IPO,
    ])

    # Valuation parameters
    min_valuation_usd: float = 100_000_000  # $100M minimum
    max_valuation_usd: float = 50_000_000_000  # $50B maximum
    preferred_valuation_range: tuple[float, float] = (500_000_000, 10_000_000_000)

    # Liquidity requirements
    max_time_to_liquidity_months: int = 36  # 3 years max
    preferred_time_to_liquidity_months: int = 18
    preferred_liquidity_events: list[LiquidityEventType] = field(default_factory=lambda: [
        LiquidityEventType.IPO,
        LiquidityEventType.DIRECT_LISTING,
        LiquidityEventType.ACQUISITION,
    ])

    # Financial metrics
    min_revenue_arr_usd: Optional[float] = 10_000_000  # $10M ARR minimum
    min_revenue_growth_yoy: float = 0.50  # 50% YoY growth

    # Discount requirements
    min_discount_to_last_round: float = 0.10  # At least 10% discount
    preferred_discount: float = 0.25  # Prefer 25%+ discount

    # Deal size
    min_check_size_usd: float = 100_000
    max_check_size_usd: float = 5_000_000
    target_check_size_usd: float = 500_000

    # Quality signals
    required_investor_quality: list[str] = field(default_factory=lambda: [
        "a]16z", "Sequoia", "Benchmark", "Greylock", "Index Ventures",
        "Founders Fund", "Thrive Capital", "Tiger Global", "Coatue",
        "General Catalyst", "Lightspeed", "Accel", "Bessemer",
        "Andreessen Horowitz", "NEA", "Insight Partners",
    ])

    # Scoring weights (should sum to 1.0)
    weight_vertical_fit: float = 0.15
    weight_stage_fit: float = 0.10
    weight_liquidity_timeline: float = 0.25
    weight_valuation_attractiveness: float = 0.15
    weight_discount: float = 0.15
    weight_investor_quality: float = 0.10
    weight_revenue_metrics: float = 0.10


@dataclass
class InvestmentThesis:
    """
    Core investment thesis for Epochal Capital.

    Focus: Private AI companies with potential upcoming liquidity events.

    Key criteria:
    1. AI-native or AI-first business model
    2. Series B+ stage with clear path to liquidity
    3. Strong revenue growth and unit economics
    4. Discount to last round valuation
    5. Backed by top-tier investors
    6. Expected liquidity within 18-36 months
    """
    name: str = "Epochal Capital AI Liquidity Strategy"
    version: str = "1.0"
    criteria: ThesisCriteria = field(default_factory=ThesisCriteria)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def score_company(self, company: Company) -> dict:
        """
        Score a company against thesis criteria.

        Returns a dict with component scores and total score (0-100).
        """
        scores = {}
        criteria = self.criteria

        # Vertical fit (0-100)
        if company.vertical in criteria.target_verticals:
            scores["vertical_fit"] = 100
        else:
            scores["vertical_fit"] = 30  # Some AI exposure

        # Stage fit (0-100)
        if company.stage in criteria.target_stages:
            scores["stage_fit"] = 100
        elif company.stage == CompanyStage.SERIES_A:
            scores["stage_fit"] = 50  # Too early but possible
        else:
            scores["stage_fit"] = 20

        # Investor quality (0-100)
        if company.key_investors:
            top_investor_count = sum(
                1 for inv in company.key_investors
                if any(top.lower() in inv.lower() for top in criteria.required_investor_quality)
            )
            scores["investor_quality"] = min(100, top_investor_count * 25)
        else:
            scores["investor_quality"] = 0

        # Revenue metrics (0-100)
        if company.revenue_arr_usd:
            if company.revenue_arr_usd >= criteria.min_revenue_arr_usd * 5:
                scores["revenue_metrics"] = 100
            elif company.revenue_arr_usd >= criteria.min_revenue_arr_usd:
                scores["revenue_metrics"] = 70
            else:
                scores["revenue_metrics"] = 30
        else:
            scores["revenue_metrics"] = 50  # Unknown, neutral

        # Liquidity signals (0-100)
        if company.liquidity_signals:
            signal_strength = min(100, len(company.liquidity_signals) * 20)
            scores["liquidity_signals"] = signal_strength
        else:
            scores["liquidity_signals"] = 20

        # Calculate weighted total
        total = (
            scores["vertical_fit"] * 0.25 +
            scores["stage_fit"] * 0.20 +
            scores["investor_quality"] * 0.20 +
            scores["revenue_metrics"] * 0.15 +
            scores["liquidity_signals"] * 0.20
        )

        scores["total"] = round(total, 1)
        return scores

    def score_deal(self, deal: Deal, company: Optional[Company] = None) -> dict:
        """
        Score a deal against thesis criteria.

        Returns a dict with component scores and total score (0-100).
        """
        scores = {}
        criteria = self.criteria

        # Start with company score if available
        if company:
            company_scores = self.score_company(company)
            scores["company_score"] = company_scores["total"]
        else:
            scores["company_score"] = 50  # Neutral if no company data

        # Valuation attractiveness (0-100)
        if deal.valuation_implied_usd:
            val = deal.valuation_implied_usd
            if criteria.preferred_valuation_range[0] <= val <= criteria.preferred_valuation_range[1]:
                scores["valuation"] = 100
            elif criteria.min_valuation_usd <= val <= criteria.max_valuation_usd:
                scores["valuation"] = 70
            else:
                scores["valuation"] = 30
        else:
            scores["valuation"] = 50

        # Discount score (0-100)
        if deal.discount_to_last_round:
            discount = deal.discount_to_last_round
            if discount >= criteria.preferred_discount:
                scores["discount"] = 100
            elif discount >= criteria.min_discount_to_last_round:
                scores["discount"] = 70
            else:
                scores["discount"] = 40
        else:
            scores["discount"] = 50

        # Liquidity timeline (0-100)
        if deal.liquidity_event and deal.liquidity_event.expected_date:
            months_to_liquidity = (
                deal.liquidity_event.expected_date - datetime.utcnow()
            ).days / 30
            if months_to_liquidity <= criteria.preferred_time_to_liquidity_months:
                scores["liquidity_timeline"] = 100
            elif months_to_liquidity <= criteria.max_time_to_liquidity_months:
                # Linear decay
                remaining = criteria.max_time_to_liquidity_months - months_to_liquidity
                scores["liquidity_timeline"] = 50 + (remaining / criteria.max_time_to_liquidity_months) * 50
            else:
                scores["liquidity_timeline"] = 20
        else:
            scores["liquidity_timeline"] = 40  # Unknown timeline

        # Liquidity event type (0-100)
        if deal.liquidity_event:
            if deal.liquidity_event.event_type in criteria.preferred_liquidity_events:
                scores["liquidity_type"] = 100
            else:
                scores["liquidity_type"] = 60
        else:
            scores["liquidity_type"] = 50

        # Confidence score
        if deal.liquidity_event:
            scores["liquidity_confidence"] = deal.liquidity_event.confidence * 100
        else:
            scores["liquidity_confidence"] = 0

        # Calculate weighted total
        total = (
            scores["company_score"] * criteria.weight_vertical_fit +
            scores["valuation"] * criteria.weight_valuation_attractiveness +
            scores["discount"] * criteria.weight_discount +
            scores["liquidity_timeline"] * criteria.weight_liquidity_timeline +
            scores["liquidity_type"] * 0.10 +
            scores["liquidity_confidence"] * 0.10
        )

        scores["total"] = round(total, 1)
        scores["recommendation"] = self._get_recommendation(scores["total"])

        return scores

    def _get_recommendation(self, score: float) -> str:
        """Get investment recommendation based on score."""
        if score >= 80:
            return "STRONG_BUY"
        elif score >= 65:
            return "BUY"
        elif score >= 50:
            return "HOLD_FOR_REVIEW"
        elif score >= 35:
            return "PASS_LIKELY"
        else:
            return "PASS"

    def get_thesis_summary(self) -> str:
        """Return a human-readable thesis summary."""
        return f"""
{self.name} (v{self.version})
{'=' * 50}

INVESTMENT FOCUS:
Private AI companies with potential upcoming liquidity events

TARGET PROFILE:
- Verticals: {', '.join(v.value for v in self.criteria.target_verticals)}
- Stages: {', '.join(s.value for s in self.criteria.target_stages)}
- Valuation Range: ${self.criteria.min_valuation_usd/1e6:.0f}M - ${self.criteria.max_valuation_usd/1e9:.0f}B
- Preferred Range: ${self.criteria.preferred_valuation_range[0]/1e6:.0f}M - ${self.criteria.preferred_valuation_range[1]/1e9:.0f}B

LIQUIDITY REQUIREMENTS:
- Max Time to Liquidity: {self.criteria.max_time_to_liquidity_months} months
- Preferred Timeline: {self.criteria.preferred_time_to_liquidity_months} months
- Preferred Events: {', '.join(e.value for e in self.criteria.preferred_liquidity_events)}

FINANCIAL CRITERIA:
- Min ARR: ${self.criteria.min_revenue_arr_usd/1e6:.0f}M
- Min YoY Growth: {self.criteria.min_revenue_growth_yoy*100:.0f}%
- Min Discount: {self.criteria.min_discount_to_last_round*100:.0f}%
- Preferred Discount: {self.criteria.preferred_discount*100:.0f}%

CHECK SIZE:
- Range: ${self.criteria.min_check_size_usd/1e3:.0f}K - ${self.criteria.max_check_size_usd/1e6:.1f}M
- Target: ${self.criteria.target_check_size_usd/1e3:.0f}K
"""

    def to_dict(self) -> dict:
        """Convert thesis to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "criteria": {
                "target_verticals": [v.value for v in self.criteria.target_verticals],
                "target_stages": [s.value for s in self.criteria.target_stages],
                "min_valuation_usd": self.criteria.min_valuation_usd,
                "max_valuation_usd": self.criteria.max_valuation_usd,
                "preferred_valuation_range": self.criteria.preferred_valuation_range,
                "max_time_to_liquidity_months": self.criteria.max_time_to_liquidity_months,
                "preferred_time_to_liquidity_months": self.criteria.preferred_time_to_liquidity_months,
                "min_revenue_arr_usd": self.criteria.min_revenue_arr_usd,
                "min_discount_to_last_round": self.criteria.min_discount_to_last_round,
                "min_check_size_usd": self.criteria.min_check_size_usd,
                "max_check_size_usd": self.criteria.max_check_size_usd,
                "target_check_size_usd": self.criteria.target_check_size_usd,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
