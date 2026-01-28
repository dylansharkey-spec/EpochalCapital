"""
Tests for the RiskScorer class.
"""

import pytest
from epochal.core.risk_scoring import (
    RiskScorer,
    RiskProfile,
    RiskDimension,
    RiskLevel,
    DimensionScore,
)


class TestRiskScorer:
    """Tests for RiskScorer."""

    def test_init_default(self, risk_scorer):
        """Test default initialization."""
        assert risk_scorer is not None
        assert len(risk_scorer.weights) == 8
        # Weights should sum to 1.0
        assert abs(sum(risk_scorer.weights.values()) - 1.0) < 0.001

    def test_init_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {
            RiskDimension.CONCENTRATION: 0.2,
            RiskDimension.REGULATORY: 0.2,
            RiskDimension.COMPETITION: 0.2,
            RiskDimension.EXECUTION: 0.1,
            RiskDimension.MARKET_TIMING: 0.1,
            RiskDimension.KEY_PERSON: 0.1,
            RiskDimension.CAP_TABLE: 0.05,
            RiskDimension.BURN_RATE: 0.05,
        }
        scorer = RiskScorer(weights=custom_weights)

        # Weights should be normalized
        assert abs(sum(scorer.weights.values()) - 1.0) < 0.001

    def test_score_to_level(self, risk_scorer):
        """Test score to level conversion."""
        assert risk_scorer.score_to_level(10) == RiskLevel.VERY_LOW
        assert risk_scorer.score_to_level(30) == RiskLevel.LOW
        assert risk_scorer.score_to_level(50) == RiskLevel.MODERATE
        assert risk_scorer.score_to_level(70) == RiskLevel.HIGH
        assert risk_scorer.score_to_level(90) == RiskLevel.VERY_HIGH


class TestConcentrationRisk:
    """Tests for concentration risk scoring."""

    def test_high_concentration(self, risk_scorer):
        """Test high customer concentration gets high score."""
        score = risk_scorer.score_concentration_risk(
            top_customer_revenue_pct=60,
            customer_count=5,
        )

        assert score.dimension == RiskDimension.CONCENTRATION
        assert score.score >= 60  # High risk
        assert len(score.factors) > 0

    def test_low_concentration(self, risk_scorer):
        """Test well-diversified customer base gets low score."""
        score = risk_scorer.score_concentration_risk(
            top_customer_revenue_pct=5,
            top_3_customers_pct=15,
            customer_count=5000,
            revenue_type="recurring",
            customer_churn_pct=3,
        )

        assert score.score <= 30  # Low risk
        assert len(score.mitigants) > 0

    def test_churn_impact(self, risk_scorer):
        """Test high churn increases risk score."""
        low_churn = risk_scorer.score_concentration_risk(customer_churn_pct=3)
        high_churn = risk_scorer.score_concentration_risk(customer_churn_pct=25)

        assert high_churn.score > low_churn.score


class TestRegulatoryRisk:
    """Tests for regulatory risk scoring."""

    def test_high_regulatory_exposure(self, risk_scorer):
        """Test multi-region high-reg exposure."""
        score = risk_scorer.score_regulatory_risk(
            primary_markets=["EU", "China", "California"],
            data_types=["healthcare", "financial"],
            ai_model_type="foundation",
            pending_investigations=2,
        )

        assert score.score >= 60
        assert len(score.factors) > 0

    def test_low_regulatory_exposure(self, risk_scorer):
        """Test US-focused narrow AI with certifications."""
        score = risk_scorer.score_regulatory_risk(
            primary_markets=["US"],
            ai_model_type="narrow",
            compliance_certifications=["SOC2", "ISO27001", "HIPAA"],
        )

        assert score.score <= 40
        assert len(score.mitigants) > 0


class TestCompetitionRisk:
    """Tests for competition risk scoring."""

    def test_crowded_market_big_tech(self, risk_scorer):
        """Test crowded market with Big Tech competition."""
        score = risk_scorer.score_competition_risk(
            market_position="challenger",
            competitor_count=30,
            big_tech_competition=True,
            moat_strength="weak",
        )

        assert score.score >= 70

    def test_market_leader_with_moat(self, risk_scorer):
        """Test market leader with strong moat."""
        score = risk_scorer.score_competition_risk(
            market_position="leader",
            competitor_count=3,
            moat_strength="strong",
            network_effects=True,
            proprietary_data=True,
        )

        assert score.score <= 30


class TestExecutionRisk:
    """Tests for execution risk scoring."""

    def test_experienced_team_pmf(self, risk_scorer, execution_risk_inputs):
        """Test experienced team with strong PMF."""
        score = risk_scorer.score_execution_risk(**execution_risk_inputs)

        assert score.score <= 40
        assert len(score.mitigants) > 0

    def test_leadership_exodus(self, risk_scorer):
        """Test multiple leadership departures."""
        score = risk_scorer.score_execution_risk(
            recent_leadership_changes=4,
            employee_growth_pct=-20,
            glassdoor_rating=2.5,
        )

        assert score.score >= 60
        assert "departure" in " ".join(score.factors).lower()


class TestMarketTimingRisk:
    """Tests for market timing risk scoring."""

    def test_favorable_timing(self, risk_scorer):
        """Test favorable market conditions."""
        score = risk_scorer.score_market_timing_risk(
            ipo_window_months=6,
            macro_environment="expansion",
            sector_sentiment="hot",
            recent_comparable_ipos=["CompA", "CompB", "CompC"],
            fed_rate_trajectory="cutting",
        )

        assert score.score <= 30

    def test_unfavorable_timing(self, risk_scorer):
        """Test unfavorable market conditions."""
        score = risk_scorer.score_market_timing_risk(
            ipo_window_months=36,
            macro_environment="recession",
            sector_sentiment="bearish",
            recent_comparable_ipos=[],
            fed_rate_trajectory="hiking",
            election_uncertainty=True,
        )

        assert score.score >= 70


class TestKeyPersonRisk:
    """Tests for key person risk scoring."""

    def test_distributed_leadership(self, risk_scorer):
        """Test multiple co-founders with insurance."""
        score = risk_scorer.score_key_person_risk(
            founder_led=True,
            founder_ownership_pct=35,
            co_founder_count=3,
            key_person_insurance=True,
            succession_plan=True,
            key_departures_12mo=0,
        )

        assert score.score <= 30

    def test_single_founder_risk(self, risk_scorer):
        """Test single founder with departures."""
        score = risk_scorer.score_key_person_risk(
            founder_led=True,
            co_founder_count=1,
            key_departures_12mo=3,
            founder_ownership_pct=5,
        )

        assert score.score >= 60


class TestCapTableRisk:
    """Tests for cap table risk scoring."""

    def test_clean_cap_table(self, risk_scorer):
        """Test clean cap table structure."""
        score = risk_scorer.score_cap_table_risk(
            investor_count=8,
            down_round_history=0,
            preference_stack_multiple=1.0,
            board_composition="founder",
            secondary_restrictions="none",
        )

        assert score.score <= 30

    def test_messy_cap_table(self, risk_scorer):
        """Test problematic cap table."""
        score = risk_scorer.score_cap_table_risk(
            investor_count=60,
            has_strategic_investors=True,
            down_round_history=2,
            preference_stack_multiple=2.5,
            board_composition="investor",
            anti_dilution_provisions=True,
            secondary_restrictions="strict",
        )

        assert score.score >= 70


class TestBurnRateRisk:
    """Tests for burn rate risk scoring."""

    def test_healthy_burn(self, risk_scorer, burn_rate_inputs):
        """Test healthy burn rate profile."""
        score = risk_scorer.score_burn_rate_risk(**burn_rate_inputs)

        assert score.score <= 40

    def test_critical_runway(self, risk_scorer):
        """Test critical cash runway."""
        score = risk_scorer.score_burn_rate_risk(
            cash_runway_months=4,
            monthly_burn_usd=50_000_000,
            revenue_usd=100_000_000,
            gross_margin_pct=30,
            path_to_profitability_months=60,
            last_funding_date_months_ago=24,
            capital_intensity="high",
        )

        assert score.score >= 70


class TestComprehensiveRiskProfile:
    """Tests for comprehensive risk profiling."""

    def test_calculate_risk_profile(self, risk_scorer, full_dimension_inputs):
        """Test complete risk profile calculation."""
        profile = risk_scorer.calculate_risk_profile(
            company_name="TestCo",
            vertical="foundation_models",
            stage="pre_ipo",
            expected_return_pct=50.0,
            dimension_inputs=full_dimension_inputs,
        )

        assert isinstance(profile, RiskProfile)
        assert profile.company_name == "TestCo"
        assert len(profile.dimension_scores) == 8
        assert profile.overall_score >= 0 and profile.overall_score <= 100
        assert profile.weighted_score >= 0 and profile.weighted_score <= 100
        assert profile.risk_adjusted_return is not None

    def test_risk_profile_to_dict(self, risk_scorer, full_dimension_inputs):
        """Test risk profile serialization."""
        profile = risk_scorer.calculate_risk_profile(
            company_name="TestCo",
            dimension_inputs=full_dimension_inputs,
        )

        profile_dict = profile.to_dict()

        assert "company_name" in profile_dict
        assert "dimension_scores" in profile_dict
        assert "overall_score" in profile_dict
        assert "recommendation" in profile_dict

    def test_generate_risk_report(self, risk_scorer, full_dimension_inputs):
        """Test risk report generation."""
        profile = risk_scorer.calculate_risk_profile(
            company_name="TestCo",
            vertical="infrastructure",
            dimension_inputs=full_dimension_inputs,
        )

        report = risk_scorer.generate_risk_report(profile)

        assert "RISK ASSESSMENT REPORT" in report
        assert "TestCo" in report
        assert "DIMENSION BREAKDOWN" in report

    def test_compare_companies(self, risk_scorer, full_dimension_inputs):
        """Test company risk comparison."""
        profiles = []
        for name in ["CompA", "CompB", "CompC"]:
            profile = risk_scorer.calculate_risk_profile(
                company_name=name,
                dimension_inputs=full_dimension_inputs,
            )
            profiles.append(profile)

        comparison = risk_scorer.compare_companies(profiles)

        assert "RISK COMPARISON" in comparison
        assert "CompA" in comparison
        assert "CompB" in comparison
        assert "CompC" in comparison


class TestVerticalAdjustments:
    """Tests for vertical-specific risk adjustments."""

    def test_foundation_model_adjustments(self, risk_scorer):
        """Test foundation models get higher regulatory/burn risk."""
        # Score regulatory risk for foundation model company
        profile_fm = risk_scorer.calculate_risk_profile(
            company_name="FoundationCo",
            vertical="foundation_models",
            dimension_inputs={
                RiskDimension.REGULATORY.value: {
                    "primary_markets": ["US"],
                    "ai_model_type": "foundation",
                }
            },
        )

        # Score regulatory risk for narrow AI company
        profile_narrow = risk_scorer.calculate_risk_profile(
            company_name="NarrowCo",
            vertical="vertical_ai",
            dimension_inputs={
                RiskDimension.REGULATORY.value: {
                    "primary_markets": ["US"],
                    "ai_model_type": "narrow",
                }
            },
        )

        # Foundation model should have higher regulatory risk after adjustment
        fm_reg = profile_fm.dimension_scores[RiskDimension.REGULATORY].score
        narrow_reg = profile_narrow.dimension_scores[RiskDimension.REGULATORY].score

        assert fm_reg > narrow_reg
