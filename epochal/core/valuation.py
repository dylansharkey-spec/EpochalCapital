"""
Valuation Model for Epochal Capital.

Provides multi-method valuation analysis for private AI companies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ValuationMethod(str, Enum):
    """Valuation methodologies."""
    REVENUE_MULTIPLE = "revenue_multiple"
    GROWTH_ADJUSTED = "growth_adjusted"
    COMPARABLE_TRANSACTIONS = "comparable_transactions"
    PUBLIC_COMP_REGRESSION = "public_comp_regression"
    LAST_ROUND_ANALYSIS = "last_round_analysis"
    DCF_SIMPLIFIED = "dcf_simplified"


@dataclass
class Comparable:
    """A comparable company for valuation."""
    name: str
    is_public: bool
    valuation_usd: float
    revenue_usd: float
    revenue_multiple: float
    growth_rate_yoy: float
    vertical: str
    stage: str
    as_of_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValuationResult:
    """Result from valuation analysis."""
    company_name: str
    method: ValuationMethod
    estimated_value_usd: float
    confidence: float  # 0-1
    key_assumptions: list[str]
    comparable_used: Optional[str] = None
    details: dict = field(default_factory=dict)


@dataclass
class ComprehensiveValuation:
    """Comprehensive valuation across all methods."""
    company_name: str
    valuation_date: datetime
    method_results: list[ValuationResult]
    weighted_average_usd: float
    fair_value_range_low: float
    fair_value_range_high: float
    current_market_price: Optional[float] = None
    premium_discount_to_fair: Optional[float] = None
    recommendation: str = ""
    confidence_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "valuation_date": self.valuation_date.isoformat(),
            "method_results": [
                {
                    "method": r.method.value,
                    "value": r.estimated_value_usd,
                    "confidence": r.confidence,
                }
                for r in self.method_results
            ],
            "weighted_average": self.weighted_average_usd,
            "fair_value_range": {
                "low": self.fair_value_range_low,
                "high": self.fair_value_range_high,
            },
            "current_market_price": self.current_market_price,
            "premium_discount": self.premium_discount_to_fair,
            "recommendation": self.recommendation,
            "confidence": self.confidence_score,
        }


class ValuationModel:
    """
    Multi-method valuation model for AI companies.

    Methods:
    - Revenue multiple analysis
    - Growth-adjusted multiple (PEG-style)
    - Comparable transactions
    - Public company regression
    - Last round analysis
    """

    # Public AI company comparables (as of Jan 2026)
    PUBLIC_COMPARABLES = [
        Comparable(
            name="Palantir",
            is_public=True,
            valuation_usd=200_000_000_000,
            revenue_usd=3_500_000_000,
            revenue_multiple=57.0,
            growth_rate_yoy=0.30,
            vertical="enterprise_ai",
            stage="public",
        ),
        Comparable(
            name="Snowflake",
            is_public=True,
            valuation_usd=80_000_000_000,
            revenue_usd=4_000_000_000,
            revenue_multiple=20.0,
            growth_rate_yoy=0.25,
            vertical="data_infrastructure",
            stage="public",
        ),
        Comparable(
            name="MongoDB",
            is_public=True,
            valuation_usd=35_000_000_000,
            revenue_usd=2_200_000_000,
            revenue_multiple=16.0,
            growth_rate_yoy=0.20,
            vertical="data_infrastructure",
            stage="public",
        ),
        Comparable(
            name="CrowdStrike",
            is_public=True,
            valuation_usd=100_000_000_000,
            revenue_usd=4_500_000_000,
            revenue_multiple=22.0,
            growth_rate_yoy=0.25,
            vertical="enterprise_ai",
            stage="public",
        ),
        Comparable(
            name="Datadog",
            is_public=True,
            valuation_usd=55_000_000_000,
            revenue_usd=2_800_000_000,
            revenue_multiple=19.6,
            growth_rate_yoy=0.22,
            vertical="infrastructure",
            stage="public",
        ),
    ]

    # Vertical-specific revenue multiple benchmarks
    VERTICAL_MULTIPLES = {
        "foundation_models": {"median": 50.0, "high": 100.0, "low": 25.0},
        "infrastructure": {"median": 20.0, "high": 40.0, "low": 10.0},
        "enterprise_ai": {"median": 25.0, "high": 50.0, "low": 12.0},
        "developer_tools": {"median": 18.0, "high": 35.0, "low": 10.0},
        "data_infrastructure": {"median": 15.0, "high": 25.0, "low": 8.0},
        "ai_agents": {"median": 40.0, "high": 80.0, "low": 20.0},
        "creative_ai": {"median": 15.0, "high": 30.0, "low": 8.0},
        "mlops": {"median": 12.0, "high": 20.0, "low": 6.0},
        "robotics": {"median": 10.0, "high": 20.0, "low": 5.0},
    }

    # Growth rate adjustments
    GROWTH_PREMIUM_FACTORS = {
        (0, 25): 0.8,      # <25% growth: 20% discount
        (25, 50): 1.0,     # 25-50% growth: baseline
        (50, 100): 1.3,    # 50-100% growth: 30% premium
        (100, 200): 1.6,   # 100-200% growth: 60% premium
        (200, 500): 2.0,   # 200-500% growth: 100% premium
        (500, 10000): 2.5, # >500% growth: 150% premium
    }

    # Stage adjustments (private company discount)
    STAGE_DISCOUNTS = {
        "series_a": 0.50,      # 50% discount to public comps
        "series_b": 0.40,      # 40% discount
        "series_c": 0.30,      # 30% discount
        "series_d_plus": 0.20, # 20% discount
        "pre_ipo": 0.10,       # 10% discount
    }

    def __init__(self):
        self.comparables = self.PUBLIC_COMPARABLES.copy()

    def add_comparable(self, comparable: Comparable):
        """Add a comparable company."""
        self.comparables.append(comparable)

    def calculate_revenue_multiple_value(
        self,
        company_name: str,
        revenue_usd: float,
        vertical: str,
        stage: str,
    ) -> ValuationResult:
        """
        Calculate value using revenue multiple method.

        Uses vertical-specific median multiples adjusted for stage.
        """
        # Get vertical multiple
        vertical_data = self.VERTICAL_MULTIPLES.get(
            vertical.lower(),
            {"median": 15.0, "high": 30.0, "low": 8.0}
        )
        base_multiple = vertical_data["median"]

        # Apply stage discount
        stage_discount = self.STAGE_DISCOUNTS.get(stage.lower(), 0.20)
        adjusted_multiple = base_multiple * (1 - stage_discount)

        # Calculate value
        estimated_value = revenue_usd * adjusted_multiple

        return ValuationResult(
            company_name=company_name,
            method=ValuationMethod.REVENUE_MULTIPLE,
            estimated_value_usd=estimated_value,
            confidence=0.7,
            key_assumptions=[
                f"Vertical median multiple: {base_multiple}x",
                f"Stage discount: {stage_discount*100:.0f}%",
                f"Adjusted multiple: {adjusted_multiple:.1f}x",
            ],
            details={
                "revenue": revenue_usd,
                "base_multiple": base_multiple,
                "adjusted_multiple": adjusted_multiple,
                "stage_discount": stage_discount,
            }
        )

    def calculate_growth_adjusted_value(
        self,
        company_name: str,
        revenue_usd: float,
        growth_rate_pct: float,
        vertical: str,
        stage: str,
    ) -> ValuationResult:
        """
        Calculate value using growth-adjusted multiple (PEG-style).

        Higher growth rates command higher multiples.
        """
        # Start with base revenue multiple
        base_result = self.calculate_revenue_multiple_value(
            company_name, revenue_usd, vertical, stage
        )
        base_multiple = base_result.details["adjusted_multiple"]

        # Find growth premium factor
        growth_premium = 1.0
        for (low, high), factor in self.GROWTH_PREMIUM_FACTORS.items():
            if low <= growth_rate_pct < high:
                growth_premium = factor
                break

        # Adjusted multiple
        growth_adjusted_multiple = base_multiple * growth_premium

        # Calculate value
        estimated_value = revenue_usd * growth_adjusted_multiple

        return ValuationResult(
            company_name=company_name,
            method=ValuationMethod.GROWTH_ADJUSTED,
            estimated_value_usd=estimated_value,
            confidence=0.75,
            key_assumptions=[
                f"Base multiple: {base_multiple:.1f}x",
                f"Growth rate: {growth_rate_pct:.0f}%",
                f"Growth premium factor: {growth_premium:.1f}x",
                f"Growth-adjusted multiple: {growth_adjusted_multiple:.1f}x",
            ],
            details={
                "revenue": revenue_usd,
                "growth_rate": growth_rate_pct,
                "base_multiple": base_multiple,
                "growth_premium": growth_premium,
                "adjusted_multiple": growth_adjusted_multiple,
            }
        )

    def calculate_comparable_value(
        self,
        company_name: str,
        revenue_usd: float,
        growth_rate_pct: float,
        vertical: str,
    ) -> ValuationResult:
        """
        Calculate value using comparable public companies.

        Finds most similar public comps and applies their multiples.
        """
        # Find best comparable
        best_comp = None
        best_score = -1

        for comp in self.comparables:
            if not comp.is_public:
                continue

            score = 0

            # Vertical match
            if comp.vertical.lower() == vertical.lower():
                score += 2

            # Growth similarity
            growth_diff = abs(comp.growth_rate_yoy * 100 - growth_rate_pct)
            if growth_diff < 10:
                score += 2
            elif growth_diff < 25:
                score += 1

            # Size similarity (log scale)
            if revenue_usd > 0 and comp.revenue_usd > 0:
                size_ratio = max(revenue_usd, comp.revenue_usd) / min(revenue_usd, comp.revenue_usd)
                if size_ratio < 5:
                    score += 1

            if score > best_score:
                best_score = score
                best_comp = comp

        if not best_comp:
            # Fallback to median
            return ValuationResult(
                company_name=company_name,
                method=ValuationMethod.COMPARABLE_TRANSACTIONS,
                estimated_value_usd=revenue_usd * 20,  # Default 20x
                confidence=0.4,
                key_assumptions=["No suitable comparable found, using default 20x"],
            )

        # Apply comparable multiple with adjustment for private status
        private_discount = 0.15  # 15% private company discount
        adjusted_multiple = best_comp.revenue_multiple * (1 - private_discount)
        estimated_value = revenue_usd * adjusted_multiple

        return ValuationResult(
            company_name=company_name,
            method=ValuationMethod.COMPARABLE_TRANSACTIONS,
            estimated_value_usd=estimated_value,
            confidence=0.65,
            key_assumptions=[
                f"Comparable: {best_comp.name}",
                f"Comp multiple: {best_comp.revenue_multiple:.1f}x",
                f"Private discount: {private_discount*100:.0f}%",
                f"Applied multiple: {adjusted_multiple:.1f}x",
            ],
            comparable_used=best_comp.name,
            details={
                "comparable": best_comp.name,
                "comp_multiple": best_comp.revenue_multiple,
                "comp_growth": best_comp.growth_rate_yoy,
                "adjusted_multiple": adjusted_multiple,
            }
        )

    def calculate_last_round_analysis(
        self,
        company_name: str,
        last_round_valuation: float,
        last_round_date: datetime,
        current_revenue: Optional[float] = None,
        last_round_revenue: Optional[float] = None,
    ) -> ValuationResult:
        """
        Analyze current value based on last funding round.

        Adjusts for time passed and revenue growth if available.
        """
        months_since_round = (datetime.utcnow() - last_round_date).days / 30

        # Base appreciation assumption: 2% per month for high-growth companies
        monthly_appreciation = 0.02
        time_adjustment = 1 + (months_since_round * monthly_appreciation)

        # Revenue growth adjustment
        revenue_adjustment = 1.0
        if current_revenue and last_round_revenue and last_round_revenue > 0:
            revenue_growth = current_revenue / last_round_revenue
            # Weight revenue growth heavily
            revenue_adjustment = revenue_growth ** 0.7  # Diminishing returns

        # Combined adjustment
        total_adjustment = time_adjustment * revenue_adjustment

        # Cap adjustment at 3x (300% appreciation)
        total_adjustment = min(3.0, total_adjustment)

        estimated_value = last_round_valuation * total_adjustment

        return ValuationResult(
            company_name=company_name,
            method=ValuationMethod.LAST_ROUND_ANALYSIS,
            estimated_value_usd=estimated_value,
            confidence=0.8,
            key_assumptions=[
                f"Last round valuation: ${last_round_valuation/1e9:.1f}B",
                f"Months since round: {months_since_round:.0f}",
                f"Time adjustment: {time_adjustment:.2f}x",
                f"Revenue adjustment: {revenue_adjustment:.2f}x",
                f"Total adjustment: {total_adjustment:.2f}x",
            ],
            details={
                "last_round_valuation": last_round_valuation,
                "months_since_round": months_since_round,
                "time_adjustment": time_adjustment,
                "revenue_adjustment": revenue_adjustment,
                "total_adjustment": total_adjustment,
            }
        )

    def calculate_comprehensive_valuation(
        self,
        company_name: str,
        revenue_usd: Optional[float] = None,
        growth_rate_pct: Optional[float] = None,
        vertical: str = "enterprise_ai",
        stage: str = "series_d_plus",
        last_round_valuation: Optional[float] = None,
        last_round_date: Optional[datetime] = None,
        current_market_price: Optional[float] = None,
    ) -> ComprehensiveValuation:
        """
        Calculate comprehensive valuation using all applicable methods.

        Weights each method and provides fair value range.
        """
        results = []
        weights = {}

        # Revenue-based methods (if revenue available)
        if revenue_usd and revenue_usd > 0:
            # Revenue multiple
            rev_result = self.calculate_revenue_multiple_value(
                company_name, revenue_usd, vertical, stage
            )
            results.append(rev_result)
            weights[ValuationMethod.REVENUE_MULTIPLE] = 0.25

            # Growth-adjusted (if growth rate available)
            if growth_rate_pct is not None:
                growth_result = self.calculate_growth_adjusted_value(
                    company_name, revenue_usd, growth_rate_pct, vertical, stage
                )
                results.append(growth_result)
                weights[ValuationMethod.GROWTH_ADJUSTED] = 0.30

            # Comparable analysis
            comp_result = self.calculate_comparable_value(
                company_name, revenue_usd, growth_rate_pct or 50, vertical
            )
            results.append(comp_result)
            weights[ValuationMethod.COMPARABLE_TRANSACTIONS] = 0.20

        # Last round analysis (if available)
        if last_round_valuation and last_round_date:
            last_round_result = self.calculate_last_round_analysis(
                company_name,
                last_round_valuation,
                last_round_date,
                current_revenue=revenue_usd,
            )
            results.append(last_round_result)
            weights[ValuationMethod.LAST_ROUND_ANALYSIS] = 0.25

        if not results:
            # No data available
            return ComprehensiveValuation(
                company_name=company_name,
                valuation_date=datetime.utcnow(),
                method_results=[],
                weighted_average_usd=0,
                fair_value_range_low=0,
                fair_value_range_high=0,
                recommendation="Insufficient data for valuation",
                confidence_score=0,
            )

        # Normalize weights
        total_weight = sum(weights.get(r.method, 0.2) for r in results)
        normalized_weights = {
            r.method: weights.get(r.method, 0.2) / total_weight
            for r in results
        }

        # Calculate weighted average
        weighted_sum = sum(
            r.estimated_value_usd * normalized_weights[r.method]
            for r in results
        )

        # Calculate range (±20% of weighted average, adjusted by confidence)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        range_factor = 0.20 / avg_confidence  # Wider range for lower confidence

        fair_low = weighted_sum * (1 - range_factor)
        fair_high = weighted_sum * (1 + range_factor)

        # Determine recommendation
        premium_discount = None
        recommendation = ""

        if current_market_price:
            premium_discount = ((current_market_price / weighted_sum) - 1) * 100

            if premium_discount < -20:
                recommendation = "STRONG BUY - Significant discount to fair value"
            elif premium_discount < -10:
                recommendation = "BUY - Trading below fair value"
            elif premium_discount < 10:
                recommendation = "HOLD - Trading near fair value"
            elif premium_discount < 25:
                recommendation = "REDUCE - Trading above fair value"
            else:
                recommendation = "SELL - Significant premium to fair value"
        else:
            recommendation = f"Fair value estimate: ${weighted_sum/1e9:.1f}B"

        return ComprehensiveValuation(
            company_name=company_name,
            valuation_date=datetime.utcnow(),
            method_results=results,
            weighted_average_usd=weighted_sum,
            fair_value_range_low=fair_low,
            fair_value_range_high=fair_high,
            current_market_price=current_market_price,
            premium_discount_to_fair=premium_discount,
            recommendation=recommendation,
            confidence_score=avg_confidence,
        )

    def analyze_deal_valuation(
        self,
        company_name: str,
        deal_price_per_share: float,
        shares_outstanding: int,
        revenue_usd: Optional[float] = None,
        growth_rate_pct: Optional[float] = None,
        vertical: str = "enterprise_ai",
        stage: str = "series_d_plus",
        last_round_valuation: Optional[float] = None,
        last_round_date: Optional[datetime] = None,
    ) -> dict:
        """
        Analyze if a deal price represents good value.

        Returns deal analysis with buy/pass recommendation.
        """
        implied_valuation = deal_price_per_share * shares_outstanding

        # Get comprehensive valuation
        fair_value = self.calculate_comprehensive_valuation(
            company_name=company_name,
            revenue_usd=revenue_usd,
            growth_rate_pct=growth_rate_pct,
            vertical=vertical,
            stage=stage,
            last_round_valuation=last_round_valuation,
            last_round_date=last_round_date,
            current_market_price=implied_valuation,
        )

        # Calculate discount/premium
        discount_pct = None
        if fair_value.weighted_average_usd > 0:
            discount_pct = ((fair_value.weighted_average_usd / implied_valuation) - 1) * 100

        # Revenue multiple if available
        implied_multiple = None
        if revenue_usd and revenue_usd > 0:
            implied_multiple = implied_valuation / revenue_usd

        # Generate recommendation
        if discount_pct and discount_pct > 20:
            decision = "STRONG BUY"
            rationale = f"{discount_pct:.0f}% discount to fair value"
        elif discount_pct and discount_pct > 10:
            decision = "BUY"
            rationale = f"{discount_pct:.0f}% discount to fair value"
        elif discount_pct and discount_pct > -10:
            decision = "CONSIDER"
            rationale = "Trading near fair value"
        elif discount_pct and discount_pct > -25:
            decision = "PASS"
            rationale = f"{-discount_pct:.0f}% premium to fair value"
        else:
            decision = "STRONG PASS"
            rationale = "Significant premium to fair value"

        return {
            "company": company_name,
            "deal_price_per_share": deal_price_per_share,
            "implied_valuation": implied_valuation,
            "fair_value_estimate": fair_value.weighted_average_usd,
            "fair_value_range": {
                "low": fair_value.fair_value_range_low,
                "high": fair_value.fair_value_range_high,
            },
            "discount_to_fair_value_pct": discount_pct,
            "implied_revenue_multiple": implied_multiple,
            "decision": decision,
            "rationale": rationale,
            "confidence": fair_value.confidence_score,
            "method_breakdown": [
                {
                    "method": r.method.value,
                    "value": r.estimated_value_usd,
                    "confidence": r.confidence,
                }
                for r in fair_value.method_results
            ],
        }
