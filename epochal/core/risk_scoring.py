"""
Risk Scoring Module for Epochal Capital.

Provides multi-dimensional risk assessment for AI company investments.
Evaluates 8 key risk dimensions with weighted scoring.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    """Risk level categories."""
    VERY_LOW = "very_low"      # 0-20
    LOW = "low"                # 21-40
    MODERATE = "moderate"      # 41-60
    HIGH = "high"              # 61-80
    VERY_HIGH = "very_high"    # 81-100


class RiskDimension(str, Enum):
    """The 8 risk dimensions evaluated."""
    CONCENTRATION = "concentration_risk"
    REGULATORY = "regulatory_risk"
    COMPETITION = "competition_risk"
    EXECUTION = "execution_risk"
    MARKET_TIMING = "market_timing_risk"
    KEY_PERSON = "key_person_risk"
    CAP_TABLE = "cap_table_risk"
    BURN_RATE = "burn_rate_risk"


@dataclass
class DimensionScore:
    """Score for a single risk dimension."""
    dimension: RiskDimension
    score: float  # 0-100, higher = riskier
    level: RiskLevel
    factors: list[str] = field(default_factory=list)
    mitigants: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class RiskProfile:
    """Complete risk profile for a company."""
    company_name: str
    assessment_date: datetime
    dimension_scores: dict[RiskDimension, DimensionScore]
    overall_score: float  # 0-100
    overall_level: RiskLevel
    weighted_score: float  # After applying dimension weights
    risk_adjusted_return: Optional[float] = None
    recommendation: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "assessment_date": self.assessment_date.isoformat(),
            "dimension_scores": {
                dim.value: {
                    "score": score.score,
                    "level": score.level.value,
                    "factors": score.factors,
                    "mitigants": score.mitigants,
                    "notes": score.notes,
                }
                for dim, score in self.dimension_scores.items()
            },
            "overall_score": self.overall_score,
            "overall_level": self.overall_level.value,
            "weighted_score": self.weighted_score,
            "risk_adjusted_return": self.risk_adjusted_return,
            "recommendation": self.recommendation,
        }


class RiskScorer:
    """
    Multi-dimensional risk scoring engine.

    Evaluates 8 risk dimensions:
    1. Concentration Risk - Revenue/customer concentration
    2. Regulatory Risk - AI regulation, antitrust, data privacy
    3. Competition Risk - Market dynamics, competitive moats
    4. Execution Risk - Team, technology, operational risks
    5. Market Timing Risk - IPO window, macro conditions
    6. Key Person Risk - Founder/exec dependency
    7. Cap Table Risk - Investor dynamics, governance
    8. Burn Rate Risk - Cash runway, capital efficiency
    """

    # Default weights for each dimension (sum to 1.0)
    DEFAULT_WEIGHTS = {
        RiskDimension.CONCENTRATION: 0.10,
        RiskDimension.REGULATORY: 0.15,
        RiskDimension.COMPETITION: 0.15,
        RiskDimension.EXECUTION: 0.15,
        RiskDimension.MARKET_TIMING: 0.10,
        RiskDimension.KEY_PERSON: 0.10,
        RiskDimension.CAP_TABLE: 0.10,
        RiskDimension.BURN_RATE: 0.15,
    }

    # AI vertical-specific risk adjustments
    VERTICAL_RISK_FACTORS = {
        "foundation_models": {
            RiskDimension.REGULATORY: 1.3,      # Higher regulatory scrutiny
            RiskDimension.COMPETITION: 1.2,     # Intense competition
            RiskDimension.BURN_RATE: 1.4,       # High compute costs
            RiskDimension.KEY_PERSON: 1.2,      # Talent wars
        },
        "infrastructure": {
            RiskDimension.EXECUTION: 1.2,       # Complex builds
            RiskDimension.COMPETITION: 1.1,
            RiskDimension.BURN_RATE: 1.2,
        },
        "enterprise_ai": {
            RiskDimension.CONCENTRATION: 1.3,   # Enterprise customer concentration
            RiskDimension.COMPETITION: 1.2,
        },
        "ai_agents": {
            RiskDimension.REGULATORY: 1.2,
            RiskDimension.EXECUTION: 1.3,       # Nascent technology
            RiskDimension.MARKET_TIMING: 1.2,
        },
        "vertical_ai": {
            RiskDimension.CONCENTRATION: 1.2,
            RiskDimension.COMPETITION: 0.9,     # More defensible
        },
        "robotics": {
            RiskDimension.EXECUTION: 1.4,       # Hardware complexity
            RiskDimension.BURN_RATE: 1.3,
            RiskDimension.REGULATORY: 1.2,
        },
        "defense_ai": {
            RiskDimension.REGULATORY: 1.1,
            RiskDimension.CONCENTRATION: 1.4,   # Government customer concentration
            RiskDimension.KEY_PERSON: 1.2,
        },
    }

    # Stage-specific base risk levels
    STAGE_BASE_RISK = {
        "seed": 75,
        "series_a": 65,
        "series_b": 55,
        "series_c": 45,
        "growth": 35,
        "pre_ipo": 25,
        "public": 15,
    }

    def __init__(self, weights: Optional[dict[RiskDimension, float]] = None):
        """Initialize with optional custom weights."""
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # Normalize weights to sum to 1.0
        weight_sum = sum(self.weights.values())
        if weight_sum != 1.0:
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}

    def score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score <= 20:
            return RiskLevel.VERY_LOW
        elif score <= 40:
            return RiskLevel.LOW
        elif score <= 60:
            return RiskLevel.MODERATE
        elif score <= 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def score_concentration_risk(
        self,
        top_customer_revenue_pct: Optional[float] = None,
        top_3_customers_pct: Optional[float] = None,
        customer_count: Optional[int] = None,
        revenue_type: str = "recurring",
        customer_churn_pct: Optional[float] = None,
    ) -> DimensionScore:
        """
        Score concentration risk.

        Factors:
        - Single customer dependency
        - Top customer concentration
        - Customer diversification
        - Revenue type (recurring vs transactional)
        - Churn rates
        """
        score = 30  # Base moderate-low score
        factors = []
        mitigants = []

        # Top customer concentration
        if top_customer_revenue_pct is not None:
            if top_customer_revenue_pct > 50:
                score += 40
                factors.append(f"Single customer represents {top_customer_revenue_pct:.0f}% of revenue")
            elif top_customer_revenue_pct > 30:
                score += 25
                factors.append(f"Top customer at {top_customer_revenue_pct:.0f}% of revenue")
            elif top_customer_revenue_pct > 20:
                score += 15
                factors.append(f"Top customer at {top_customer_revenue_pct:.0f}% of revenue")
            elif top_customer_revenue_pct < 10:
                score -= 10
                mitigants.append(f"No single customer >10% ({top_customer_revenue_pct:.0f}%)")

        # Top 3 customers
        if top_3_customers_pct is not None:
            if top_3_customers_pct > 70:
                score += 20
                factors.append(f"Top 3 customers = {top_3_customers_pct:.0f}% revenue")
            elif top_3_customers_pct < 30:
                score -= 10
                mitigants.append("Well-diversified customer base")

        # Customer count
        if customer_count is not None:
            if customer_count < 10:
                score += 25
                factors.append(f"Only {customer_count} customers")
            elif customer_count < 50:
                score += 10
                factors.append(f"Limited customer base ({customer_count})")
            elif customer_count > 1000:
                score -= 15
                mitigants.append(f"Large customer base ({customer_count:,})")
            elif customer_count > 100:
                score -= 5
                mitigants.append(f"Solid customer base ({customer_count})")

        # Revenue type
        if revenue_type == "recurring":
            score -= 10
            mitigants.append("Recurring revenue model")
        elif revenue_type == "transactional":
            score += 10
            factors.append("Transactional revenue model")
        elif revenue_type == "usage":
            score += 5
            factors.append("Usage-based revenue (variable)")

        # Churn
        if customer_churn_pct is not None:
            if customer_churn_pct > 20:
                score += 20
                factors.append(f"High churn rate ({customer_churn_pct:.0f}%)")
            elif customer_churn_pct > 10:
                score += 10
                factors.append(f"Elevated churn ({customer_churn_pct:.0f}%)")
            elif customer_churn_pct < 5:
                score -= 10
                mitigants.append(f"Low churn ({customer_churn_pct:.0f}%)")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.CONCENTRATION,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_regulatory_risk(
        self,
        primary_markets: Optional[list[str]] = None,
        data_types: Optional[list[str]] = None,
        ai_model_type: Optional[str] = None,
        has_government_contracts: bool = False,
        pending_investigations: int = 0,
        compliance_certifications: Optional[list[str]] = None,
    ) -> DimensionScore:
        """
        Score regulatory risk.

        Factors:
        - Geographic exposure (EU AI Act, US state laws, China)
        - Data sensitivity (healthcare, finance, children)
        - AI model type (foundation vs narrow)
        - Government exposure
        - Pending regulatory actions
        """
        score = 25  # Base low score
        factors = []
        mitigants = []

        # Geographic exposure
        high_reg_markets = ["eu", "china", "california"]
        moderate_reg_markets = ["uk", "canada", "australia"]

        if primary_markets:
            markets_lower = [m.lower() for m in primary_markets]
            high_exposure = sum(1 for m in high_reg_markets if m in markets_lower)
            mod_exposure = sum(1 for m in moderate_reg_markets if m in markets_lower)

            if high_exposure >= 2:
                score += 25
                factors.append("Multi-region high regulatory exposure")
            elif high_exposure == 1:
                score += 15
                factors.append(f"Exposure to high-regulation market")

            if "us" in markets_lower and "eu" not in markets_lower:
                score -= 5
                mitigants.append("US-focused (lower near-term AI regulation)")

        # Data sensitivity
        sensitive_data = ["healthcare", "financial", "children", "biometric", "pii"]
        if data_types:
            data_lower = [d.lower() for d in data_types]
            sensitive_count = sum(1 for d in sensitive_data if d in data_lower)
            if sensitive_count >= 2:
                score += 25
                factors.append("Multiple sensitive data categories")
            elif sensitive_count == 1:
                score += 15
                factors.append("Sensitive data handling")

        # AI model type
        if ai_model_type:
            model_lower = ai_model_type.lower()
            if "foundation" in model_lower or "general" in model_lower:
                score += 20
                factors.append("Foundation model - heightened regulatory scrutiny")
            elif "narrow" in model_lower or "specific" in model_lower:
                score -= 5
                mitigants.append("Narrow AI application (lower scrutiny)")

        # Government contracts
        if has_government_contracts:
            score += 10
            factors.append("Government contract compliance requirements")

        # Pending investigations
        if pending_investigations > 0:
            score += 15 * min(pending_investigations, 3)
            factors.append(f"{pending_investigations} pending regulatory investigation(s)")

        # Compliance certifications
        cert_value = {"soc2": 10, "iso27001": 10, "hipaa": 15, "fedramp": 15, "gdpr": 10}
        if compliance_certifications:
            certs_lower = [c.lower().replace(" ", "").replace("-", "") for c in compliance_certifications]
            cert_credit = sum(cert_value.get(c, 5) for c in certs_lower)
            score -= min(cert_credit, 25)
            mitigants.append(f"Compliance certifications: {', '.join(compliance_certifications)}")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.REGULATORY,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_competition_risk(
        self,
        market_position: Optional[str] = None,
        competitor_count: Optional[int] = None,
        big_tech_competition: bool = False,
        moat_strength: Optional[str] = None,
        switching_costs: Optional[str] = None,
        network_effects: bool = False,
        proprietary_data: bool = False,
    ) -> DimensionScore:
        """
        Score competition risk.

        Factors:
        - Market position (leader, challenger, niche)
        - Competitor landscape
        - Big tech exposure
        - Competitive moats (data, network, tech)
        - Switching costs
        """
        score = 40  # Base moderate score
        factors = []
        mitigants = []

        # Market position
        if market_position:
            pos_lower = market_position.lower()
            if "leader" in pos_lower or "dominant" in pos_lower:
                score -= 20
                mitigants.append("Market leader position")
            elif "challenger" in pos_lower:
                score += 10
                factors.append("Challenger position - must take share")
            elif "niche" in pos_lower:
                score -= 5
                mitigants.append("Defensible niche position")

        # Competitor count
        if competitor_count is not None:
            if competitor_count > 20:
                score += 20
                factors.append(f"Crowded market ({competitor_count}+ competitors)")
            elif competitor_count > 10:
                score += 10
                factors.append(f"Competitive market ({competitor_count} players)")
            elif competitor_count < 5:
                score -= 10
                mitigants.append("Limited direct competition")

        # Big tech competition
        if big_tech_competition:
            score += 25
            factors.append("Direct competition from Big Tech")

        # Moat strength
        if moat_strength:
            moat_lower = moat_strength.lower()
            if moat_lower == "strong":
                score -= 20
                mitigants.append("Strong competitive moat")
            elif moat_lower == "moderate":
                score -= 5
            elif moat_lower == "weak":
                score += 15
                factors.append("Weak competitive differentiation")

        # Switching costs
        if switching_costs:
            switch_lower = switching_costs.lower()
            if switch_lower == "high":
                score -= 15
                mitigants.append("High customer switching costs")
            elif switch_lower == "low":
                score += 15
                factors.append("Low switching costs")

        # Network effects
        if network_effects:
            score -= 15
            mitigants.append("Network effects present")

        # Proprietary data
        if proprietary_data:
            score -= 10
            mitigants.append("Proprietary data advantage")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.COMPETITION,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_execution_risk(
        self,
        team_experience_years: Optional[float] = None,
        prior_exits: int = 0,
        employee_count: Optional[int] = None,
        employee_growth_pct: Optional[float] = None,
        tech_debt_level: Optional[str] = None,
        product_market_fit: Optional[str] = None,
        recent_leadership_changes: int = 0,
        glassdoor_rating: Optional[float] = None,
    ) -> DimensionScore:
        """
        Score execution risk.

        Factors:
        - Team experience and track record
        - Organizational scale and growth
        - Technology/product maturity
        - Leadership stability
        - Employee satisfaction
        """
        score = 40  # Base moderate score
        factors = []
        mitigants = []

        # Team experience
        if team_experience_years is not None:
            if team_experience_years > 15:
                score -= 15
                mitigants.append(f"Highly experienced team ({team_experience_years:.0f}+ years avg)")
            elif team_experience_years > 10:
                score -= 10
                mitigants.append("Experienced leadership team")
            elif team_experience_years < 5:
                score += 15
                factors.append("Relatively inexperienced team")

        # Prior exits
        if prior_exits >= 3:
            score -= 20
            mitigants.append(f"Leadership with {prior_exits} prior exits")
        elif prior_exits >= 1:
            score -= 10
            mitigants.append("Leadership with prior exit experience")

        # Employee count and growth
        if employee_count is not None:
            if employee_count > 1000:
                score -= 10
                mitigants.append(f"Scale organization ({employee_count:,} employees)")
            elif employee_count < 50:
                score += 15
                factors.append(f"Small team ({employee_count} employees)")

        if employee_growth_pct is not None:
            if employee_growth_pct > 100:
                score += 15
                factors.append(f"Hypergrowth hiring ({employee_growth_pct:.0f}%) - integration risk")
            elif employee_growth_pct < 0:
                score += 20
                factors.append(f"Workforce contraction ({employee_growth_pct:.0f}%)")

        # Tech debt
        if tech_debt_level:
            tech_lower = tech_debt_level.lower()
            if tech_lower == "high":
                score += 20
                factors.append("High technical debt")
            elif tech_lower == "low":
                score -= 10
                mitigants.append("Well-managed technical infrastructure")

        # Product-market fit
        if product_market_fit:
            pmf_lower = product_market_fit.lower()
            if pmf_lower == "strong":
                score -= 15
                mitigants.append("Strong product-market fit")
            elif pmf_lower == "emerging":
                score += 5
            elif pmf_lower == "searching":
                score += 25
                factors.append("Still searching for PMF")

        # Leadership changes
        if recent_leadership_changes >= 3:
            score += 25
            factors.append(f"{recent_leadership_changes} recent C-suite departures")
        elif recent_leadership_changes >= 1:
            score += 10
            factors.append("Recent leadership turnover")

        # Glassdoor
        if glassdoor_rating is not None:
            if glassdoor_rating >= 4.0:
                score -= 10
                mitigants.append(f"Strong employee satisfaction ({glassdoor_rating}/5)")
            elif glassdoor_rating < 3.0:
                score += 15
                factors.append(f"Low employee satisfaction ({glassdoor_rating}/5)")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.EXECUTION,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_market_timing_risk(
        self,
        ipo_window_months: Optional[int] = None,
        macro_environment: Optional[str] = None,
        sector_sentiment: Optional[str] = None,
        recent_comparable_ipos: Optional[list[str]] = None,
        fed_rate_trajectory: Optional[str] = None,
        election_uncertainty: bool = False,
    ) -> DimensionScore:
        """
        Score market timing risk.

        Factors:
        - IPO window timing
        - Macro environment
        - Sector sentiment
        - Recent comparable transactions
        - Interest rate environment
        """
        score = 35  # Base moderate-low score
        factors = []
        mitigants = []

        # IPO window
        if ipo_window_months is not None:
            if ipo_window_months <= 6:
                score -= 15
                mitigants.append(f"Near-term liquidity ({ipo_window_months} months)")
            elif ipo_window_months <= 12:
                score -= 5
                mitigants.append("Reasonable liquidity timeline")
            elif ipo_window_months > 24:
                score += 20
                factors.append(f"Extended hold period ({ipo_window_months}+ months)")
            elif ipo_window_months > 18:
                score += 10
                factors.append("Longer liquidity timeline")

        # Macro environment
        if macro_environment:
            macro_lower = macro_environment.lower()
            if "recession" in macro_lower:
                score += 30
                factors.append("Recessionary environment")
            elif "slowdown" in macro_lower:
                score += 15
                factors.append("Economic slowdown")
            elif "expansion" in macro_lower or "strong" in macro_lower:
                score -= 15
                mitigants.append("Favorable macro conditions")

        # Sector sentiment
        if sector_sentiment:
            sent_lower = sector_sentiment.lower()
            if sent_lower == "hot" or sent_lower == "bullish":
                score -= 20
                mitigants.append("Strong AI sector sentiment")
            elif sent_lower == "neutral":
                pass
            elif sent_lower == "bearish" or sent_lower == "cold":
                score += 20
                factors.append("Weak sector sentiment")

        # Comparable IPOs
        if recent_comparable_ipos:
            if len(recent_comparable_ipos) >= 3:
                score -= 15
                mitigants.append(f"Active IPO market ({len(recent_comparable_ipos)} recent comps)")
            elif len(recent_comparable_ipos) == 0:
                score += 15
                factors.append("No recent comparable IPOs")

        # Fed rates
        if fed_rate_trajectory:
            rate_lower = fed_rate_trajectory.lower()
            if "cutting" in rate_lower or "easing" in rate_lower:
                score -= 15
                mitigants.append("Easing rate environment")
            elif "hiking" in rate_lower or "tightening" in rate_lower:
                score += 20
                factors.append("Rising rate environment")

        # Election
        if election_uncertainty:
            score += 10
            factors.append("Election-related uncertainty")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.MARKET_TIMING,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_key_person_risk(
        self,
        founder_led: bool = True,
        founder_ownership_pct: Optional[float] = None,
        key_person_insurance: bool = False,
        succession_plan: bool = False,
        co_founder_count: int = 1,
        key_departures_12mo: int = 0,
        founder_full_time: bool = True,
    ) -> DimensionScore:
        """
        Score key person risk.

        Factors:
        - Founder dependency
        - Ownership concentration
        - Succession planning
        - Recent departures
        """
        score = 35  # Base moderate-low score
        factors = []
        mitigants = []

        # Founder-led
        if founder_led:
            if founder_full_time:
                score -= 5
                mitigants.append("Founder actively leading")
            else:
                score += 20
                factors.append("Founder not full-time")
        else:
            score += 10
            factors.append("Professional management (founder departed)")

        # Co-founders
        if co_founder_count >= 3:
            score -= 15
            mitigants.append(f"Distributed leadership ({co_founder_count} co-founders)")
        elif co_founder_count == 1:
            score += 15
            factors.append("Single founder dependency")

        # Founder ownership
        if founder_ownership_pct is not None:
            if founder_ownership_pct > 30:
                score -= 10
                mitigants.append(f"Strong founder alignment ({founder_ownership_pct:.0f}%)")
            elif founder_ownership_pct < 10:
                score += 10
                factors.append(f"Low founder ownership ({founder_ownership_pct:.0f}%)")

        # Key person insurance
        if key_person_insurance:
            score -= 10
            mitigants.append("Key person insurance in place")

        # Succession plan
        if succession_plan:
            score -= 10
            mitigants.append("Succession plan documented")
        else:
            score += 5
            factors.append("No formal succession plan")

        # Recent departures
        if key_departures_12mo >= 3:
            score += 30
            factors.append(f"{key_departures_12mo} key departures in 12 months - CRITICAL")
        elif key_departures_12mo >= 1:
            score += 15
            factors.append(f"{key_departures_12mo} key departure(s) in 12 months")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.KEY_PERSON,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_cap_table_risk(
        self,
        investor_count: Optional[int] = None,
        has_strategic_investors: bool = False,
        down_round_history: int = 0,
        preference_stack_multiple: Optional[float] = None,
        board_composition: Optional[str] = None,
        anti_dilution_provisions: bool = False,
        secondary_restrictions: Optional[str] = None,
    ) -> DimensionScore:
        """
        Score cap table risk.

        Factors:
        - Investor complexity
        - Down round history
        - Preference stack
        - Governance/board dynamics
        - Secondary market restrictions
        """
        score = 30  # Base low-moderate score
        factors = []
        mitigants = []

        # Investor count
        if investor_count is not None:
            if investor_count > 50:
                score += 20
                factors.append(f"Complex cap table ({investor_count} investors)")
            elif investor_count > 20:
                score += 10
                factors.append(f"Many investors ({investor_count})")
            elif investor_count < 10:
                score -= 5
                mitigants.append("Clean cap table")

        # Strategic investors
        if has_strategic_investors:
            score += 10
            factors.append("Strategic investors (potential conflicts)")

        # Down rounds
        if down_round_history >= 2:
            score += 30
            factors.append(f"Multiple down rounds ({down_round_history})")
        elif down_round_history == 1:
            score += 15
            factors.append("Prior down round")

        # Preference stack
        if preference_stack_multiple is not None:
            if preference_stack_multiple > 2.0:
                score += 25
                factors.append(f"Heavy preference stack ({preference_stack_multiple:.1f}x)")
            elif preference_stack_multiple > 1.5:
                score += 15
                factors.append(f"Elevated preferences ({preference_stack_multiple:.1f}x)")
            elif preference_stack_multiple <= 1.0:
                score -= 10
                mitigants.append("1x non-participating preferred")

        # Board composition
        if board_composition:
            board_lower = board_composition.lower()
            if "founder" in board_lower or "balanced" in board_lower:
                score -= 10
                mitigants.append("Founder-friendly board")
            elif "investor" in board_lower:
                score += 15
                factors.append("Investor-controlled board")

        # Anti-dilution
        if anti_dilution_provisions:
            score += 10
            factors.append("Anti-dilution provisions present")

        # Secondary restrictions
        if secondary_restrictions:
            restrict_lower = secondary_restrictions.lower()
            if restrict_lower == "none" or restrict_lower == "minimal":
                score -= 10
                mitigants.append("Secondary trading allowed")
            elif restrict_lower == "rofr":
                score += 5
                factors.append("ROFR on secondary sales")
            elif restrict_lower == "strict":
                score += 15
                factors.append("Strict secondary restrictions")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.CAP_TABLE,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def score_burn_rate_risk(
        self,
        monthly_burn_usd: Optional[float] = None,
        cash_runway_months: Optional[int] = None,
        revenue_usd: Optional[float] = None,
        gross_margin_pct: Optional[float] = None,
        path_to_profitability_months: Optional[int] = None,
        last_funding_date_months_ago: Optional[int] = None,
        capital_intensity: Optional[str] = None,
    ) -> DimensionScore:
        """
        Score burn rate risk.

        Factors:
        - Cash runway
        - Burn multiple (burn/ARR growth)
        - Gross margins
        - Path to profitability
        - Capital needs
        """
        score = 40  # Base moderate score
        factors = []
        mitigants = []

        # Cash runway
        if cash_runway_months is not None:
            if cash_runway_months < 6:
                score += 40
                factors.append(f"Critical runway: {cash_runway_months} months")
            elif cash_runway_months < 12:
                score += 25
                factors.append(f"Short runway: {cash_runway_months} months")
            elif cash_runway_months < 18:
                score += 10
                factors.append(f"Limited runway: {cash_runway_months} months")
            elif cash_runway_months >= 36:
                score -= 20
                mitigants.append(f"Strong runway: {cash_runway_months}+ months")
            elif cash_runway_months >= 24:
                score -= 10
                mitigants.append(f"Healthy runway: {cash_runway_months} months")

        # Burn multiple (if we have both burn and revenue)
        if monthly_burn_usd and revenue_usd:
            annual_burn = monthly_burn_usd * 12
            burn_multiple = annual_burn / max(revenue_usd, 1)
            if burn_multiple > 3:
                score += 20
                factors.append(f"High burn multiple ({burn_multiple:.1f}x ARR)")
            elif burn_multiple > 2:
                score += 10
                factors.append(f"Elevated burn ({burn_multiple:.1f}x ARR)")
            elif burn_multiple < 1:
                score -= 15
                mitigants.append(f"Efficient burn ({burn_multiple:.1f}x ARR)")

        # Gross margins
        if gross_margin_pct is not None:
            if gross_margin_pct >= 80:
                score -= 15
                mitigants.append(f"Strong gross margins ({gross_margin_pct:.0f}%)")
            elif gross_margin_pct >= 60:
                score -= 5
                mitigants.append(f"Healthy margins ({gross_margin_pct:.0f}%)")
            elif gross_margin_pct < 40:
                score += 20
                factors.append(f"Low gross margins ({gross_margin_pct:.0f}%)")
            elif gross_margin_pct < 50:
                score += 10
                factors.append(f"Below-average margins ({gross_margin_pct:.0f}%)")

        # Path to profitability
        if path_to_profitability_months is not None:
            if path_to_profitability_months <= 12:
                score -= 15
                mitigants.append(f"Near-term profitability ({path_to_profitability_months} months)")
            elif path_to_profitability_months <= 24:
                score -= 5
            elif path_to_profitability_months > 48:
                score += 20
                factors.append(f"Extended path to profit ({path_to_profitability_months}+ months)")

        # Last funding
        if last_funding_date_months_ago is not None:
            if last_funding_date_months_ago > 18:
                score += 15
                factors.append(f"Aging last round ({last_funding_date_months_ago} months ago)")
            elif last_funding_date_months_ago < 6:
                score -= 10
                mitigants.append("Recently funded")

        # Capital intensity
        if capital_intensity:
            cap_lower = capital_intensity.lower()
            if cap_lower == "high":
                score += 15
                factors.append("Capital-intensive business model")
            elif cap_lower == "low":
                score -= 10
                mitigants.append("Capital-efficient model")

        score = max(0, min(100, score))

        return DimensionScore(
            dimension=RiskDimension.BURN_RATE,
            score=score,
            level=self.score_to_level(score),
            factors=factors,
            mitigants=mitigants,
        )

    def calculate_risk_profile(
        self,
        company_name: str,
        vertical: Optional[str] = None,
        stage: Optional[str] = None,
        expected_return_pct: Optional[float] = None,
        dimension_inputs: Optional[dict] = None,
    ) -> RiskProfile:
        """
        Calculate complete risk profile for a company.

        Args:
            company_name: Name of the company
            vertical: AI vertical (for risk adjustments)
            stage: Company stage
            expected_return_pct: Expected return for risk-adjusted calculation
            dimension_inputs: Dict with inputs for each dimension scorer

        Returns:
            Complete RiskProfile with all dimension scores
        """
        dimension_inputs = dimension_inputs or {}
        dimension_scores = {}

        # Score each dimension
        dimension_scorers = {
            RiskDimension.CONCENTRATION: self.score_concentration_risk,
            RiskDimension.REGULATORY: self.score_regulatory_risk,
            RiskDimension.COMPETITION: self.score_competition_risk,
            RiskDimension.EXECUTION: self.score_execution_risk,
            RiskDimension.MARKET_TIMING: self.score_market_timing_risk,
            RiskDimension.KEY_PERSON: self.score_key_person_risk,
            RiskDimension.CAP_TABLE: self.score_cap_table_risk,
            RiskDimension.BURN_RATE: self.score_burn_rate_risk,
        }

        for dimension, scorer in dimension_scorers.items():
            inputs = dimension_inputs.get(dimension.value, {})
            score = scorer(**inputs)

            # Apply vertical adjustment if applicable
            if vertical and vertical in self.VERTICAL_RISK_FACTORS:
                adjustment = self.VERTICAL_RISK_FACTORS[vertical].get(dimension, 1.0)
                if adjustment != 1.0:
                    score.score = min(100, score.score * adjustment)
                    score.level = self.score_to_level(score.score)
                    if adjustment > 1.0:
                        score.notes = f"Adjusted +{(adjustment-1)*100:.0f}% for {vertical}"

            dimension_scores[dimension] = score

        # Calculate overall score (simple average)
        overall_score = sum(s.score for s in dimension_scores.values()) / len(dimension_scores)

        # Calculate weighted score
        weighted_score = sum(
            dimension_scores[dim].score * self.weights[dim]
            for dim in dimension_scores
        )

        # Apply stage adjustment to weighted score
        if stage and stage in self.STAGE_BASE_RISK:
            stage_adjustment = self.STAGE_BASE_RISK[stage] / 50  # Normalize around 50
            weighted_score = weighted_score * stage_adjustment

        weighted_score = min(100, weighted_score)
        overall_level = self.score_to_level(weighted_score)

        # Calculate risk-adjusted return
        risk_adjusted_return = None
        if expected_return_pct is not None:
            # Simple Sharpe-like calculation
            # Penalize return by risk score (higher risk = lower adjusted return)
            risk_penalty = weighted_score / 100
            risk_adjusted_return = expected_return_pct * (1 - risk_penalty * 0.5)

        # Generate recommendation
        if weighted_score <= 30:
            recommendation = "LOW RISK - Suitable for core portfolio allocation"
        elif weighted_score <= 50:
            recommendation = "MODERATE RISK - Position size accordingly"
        elif weighted_score <= 70:
            recommendation = "ELEVATED RISK - Requires strong conviction and upside"
        else:
            recommendation = "HIGH RISK - Consider passing or minimal position"

        return RiskProfile(
            company_name=company_name,
            assessment_date=datetime.utcnow(),
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            overall_level=overall_level,
            weighted_score=weighted_score,
            risk_adjusted_return=risk_adjusted_return,
            recommendation=recommendation,
        )

    def generate_risk_report(self, profile: RiskProfile) -> str:
        """Generate human-readable risk report."""
        report = f"""
RISK ASSESSMENT REPORT
======================
Company: {profile.company_name}
Date: {profile.assessment_date.strftime('%Y-%m-%d %H:%M UTC')}

OVERALL RISK SCORE
------------------
Weighted Score: {profile.weighted_score:.1f}/100 ({profile.overall_level.value.upper()})
Raw Score: {profile.overall_score:.1f}/100

{profile.recommendation}
"""

        if profile.risk_adjusted_return is not None:
            report += f"\nRisk-Adjusted Return: {profile.risk_adjusted_return:.1f}%\n"

        report += "\nDIMENSION BREAKDOWN\n"
        report += "-" * 40 + "\n"

        # Sort by score (highest risk first)
        sorted_dims = sorted(
            profile.dimension_scores.items(),
            key=lambda x: x[1].score,
            reverse=True,
        )

        for dimension, score in sorted_dims:
            dim_name = dimension.value.replace("_", " ").title()
            report += f"\n{dim_name}: {score.score:.0f}/100 ({score.level.value})\n"

            if score.factors:
                report += "  Risk Factors:\n"
                for factor in score.factors:
                    report += f"    - {factor}\n"

            if score.mitigants:
                report += "  Mitigants:\n"
                for mitigant in score.mitigants:
                    report += f"    + {mitigant}\n"

        return report

    def compare_companies(
        self,
        profiles: list[RiskProfile],
    ) -> str:
        """Compare risk profiles across multiple companies."""
        if not profiles:
            return "No profiles to compare"

        report = "RISK COMPARISON\n"
        report += "=" * 60 + "\n\n"
        report += f"{'Company':<25} {'Score':>8} {'Level':<12} {'Recommendation'}\n"
        report += "-" * 60 + "\n"

        sorted_profiles = sorted(profiles, key=lambda p: p.weighted_score)

        for profile in sorted_profiles:
            short_rec = profile.recommendation.split(" - ")[0]
            report += (
                f"{profile.company_name:<25} "
                f"{profile.weighted_score:>7.1f} "
                f"{profile.overall_level.value:<12} "
                f"{short_rec}\n"
            )

        report += "\n\nDIMENSION COMPARISON\n"
        report += "-" * 60 + "\n"

        for dimension in RiskDimension:
            dim_name = dimension.value.replace("_", " ").title()
            report += f"\n{dim_name}:\n"

            for profile in sorted_profiles:
                score = profile.dimension_scores[dimension]
                report += f"  {profile.company_name}: {score.score:.0f} ({score.level.value})\n"

        return report
