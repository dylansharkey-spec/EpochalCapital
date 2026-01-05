"""
Portfolio Management Agent for Epochal Capital.

Responsible for:
- Portfolio monitoring and reporting
- Investment tracking
- Risk management
- Performance analytics
"""

from datetime import datetime
from typing import Optional

from epochal.agents.base import Agent, AgentRole, AgentTask, AgentResult, TaskStatus
from epochal.core.portfolio import Portfolio, PortfolioSummary


class PortfolioAgent(Agent):
    """
    Agent responsible for portfolio management and monitoring.

    Capabilities:
    - portfolio_summary: Generate portfolio summary
    - investment_report: Detailed investment report
    - risk_analysis: Analyze portfolio risks
    - performance_tracking: Track performance metrics
    - rebalancing_suggestions: Suggest portfolio rebalancing
    """

    def __init__(self, portfolio: Optional[Portfolio] = None):
        super().__init__(
            role=AgentRole.PORTFOLIO_MANAGER,
            name="Portfolio Management Agent",
            description="Manages and monitors the investment portfolio",
        )
        self.portfolio = portfolio or Portfolio()

    def _register_capabilities(self):
        """Register portfolio management capabilities."""
        self.register_capability(
            name="portfolio_summary",
            description="Generate portfolio summary and key metrics",
            handler=self._portfolio_summary,
        )
        self.register_capability(
            name="investment_report",
            description="Generate detailed investment report",
            handler=self._investment_report,
        )
        self.register_capability(
            name="risk_analysis",
            description="Analyze portfolio concentration and risks",
            handler=self._risk_analysis,
        )
        self.register_capability(
            name="pipeline_status",
            description="Get current deal pipeline status",
            handler=self._pipeline_status,
        )
        self.register_capability(
            name="recommendations",
            description="Generate portfolio action recommendations",
            handler=self._recommendations,
        )

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a portfolio management task."""
        start_time = datetime.utcnow()
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = start_time

        try:
            capability_name = task.input_data.get("capability", "portfolio_summary")

            if capability_name == "portfolio_summary":
                result_data = await self._portfolio_summary()
            elif capability_name == "investment_report":
                result_data = await self._investment_report()
            elif capability_name == "risk_analysis":
                result_data = await self._risk_analysis()
            elif capability_name == "pipeline_status":
                result_data = await self._pipeline_status()
            elif capability_name == "recommendations":
                result_data = await self._recommendations()
            else:
                raise ValueError(f"Unknown capability: {capability_name}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.tasks_completed += 1

            return AgentResult(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            self.tasks_failed += 1
            return AgentResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _portfolio_summary(self) -> dict:
        """Generate portfolio summary."""
        summary = self.portfolio.get_portfolio_summary()

        return {
            "summary_date": datetime.utcnow().isoformat(),
            "metrics": {
                "total_invested_usd": summary.total_invested_usd,
                "current_value_usd": summary.current_value_usd,
                "unrealized_gains_usd": summary.unrealized_gains_usd,
                "realized_gains_usd": summary.realized_gains_usd,
                "total_return_pct": summary.total_return_pct,
            },
            "positions": {
                "active": summary.active_positions,
                "exited": summary.exited_positions,
            },
            "pipeline": {
                "companies_tracked": summary.companies_tracked,
                "deals_in_pipeline": summary.deals_in_pipeline,
            },
            "report": self.portfolio.export_portfolio_report(),
        }

    async def _investment_report(self) -> dict:
        """Generate detailed investment report."""
        active_investments = self.portfolio.list_investments("active")
        exited_investments = self.portfolio.list_investments("exited")

        investments_data = []
        for inv in active_investments:
            company = self.portfolio.get_company(inv.company_id)
            investments_data.append({
                "id": inv.id,
                "company": inv.company_name,
                "vertical": company.vertical.value if company else "Unknown",
                "vehicle_type": inv.vehicle_type,
                "cost_basis_usd": inv.cost_basis_usd,
                "current_value_usd": inv.current_value_usd or inv.cost_basis_usd,
                "unrealized_gain_pct": (
                    ((inv.current_value_usd or inv.cost_basis_usd) - inv.cost_basis_usd)
                    / inv.cost_basis_usd * 100
                ) if inv.cost_basis_usd > 0 else 0,
                "investment_date": inv.investment_date.isoformat(),
            })

        exits_data = []
        for inv in exited_investments:
            exits_data.append({
                "id": inv.id,
                "company": inv.company_name,
                "cost_basis_usd": inv.cost_basis_usd,
                "exit_proceeds_usd": inv.exit_proceeds_usd,
                "realized_gain_usd": inv.realized_gain_usd,
                "realized_return_pct": (
                    (inv.realized_gain_usd / inv.cost_basis_usd * 100)
                    if inv.cost_basis_usd > 0 and inv.realized_gain_usd
                    else 0
                ),
                "exit_date": inv.exit_date.isoformat() if inv.exit_date else None,
            })

        return {
            "report_date": datetime.utcnow().isoformat(),
            "active_investments": investments_data,
            "exited_investments": exits_data,
            "total_active": len(investments_data),
            "total_exited": len(exits_data),
        }

    async def _risk_analysis(self) -> dict:
        """Analyze portfolio risks."""
        by_vertical = self.portfolio.get_portfolio_by_vertical()
        summary = self.portfolio.get_portfolio_summary()

        # Calculate concentration metrics
        concentrations = []
        total_value = summary.current_value_usd or 1

        for vertical, data in by_vertical.items():
            concentration_pct = (data["current_value"] / total_value * 100) if total_value > 0 else 0
            concentrations.append({
                "vertical": vertical,
                "concentration_pct": round(concentration_pct, 1),
                "position_count": data["count"],
            })

        # Sort by concentration
        concentrations.sort(key=lambda x: x["concentration_pct"], reverse=True)

        # Identify risks
        risks = []
        if concentrations and concentrations[0]["concentration_pct"] > 40:
            risks.append({
                "type": "concentration_risk",
                "severity": "high",
                "description": f"Over 40% concentrated in {concentrations[0]['vertical']}",
            })

        if summary.active_positions < 5:
            risks.append({
                "type": "diversification_risk",
                "severity": "medium",
                "description": "Portfolio has fewer than 5 positions",
            })

        return {
            "analysis_date": datetime.utcnow().isoformat(),
            "concentration_by_vertical": concentrations,
            "identified_risks": risks,
            "risk_score": len(risks) * 25,  # Simple risk score
            "recommendations": self._generate_risk_recommendations(risks),
        }

    def _generate_risk_recommendations(self, risks: list) -> list:
        """Generate recommendations based on risks."""
        recommendations = []

        for risk in risks:
            if risk["type"] == "concentration_risk":
                recommendations.append("Consider diversifying into other AI verticals")
            elif risk["type"] == "diversification_risk":
                recommendations.append("Look to add more positions to improve diversification")

        return recommendations

    async def _pipeline_status(self) -> dict:
        """Get deal pipeline status."""
        pipeline = self.portfolio.get_pipeline_summary()

        # Get top deals
        active_deals = self.portfolio.list_deals(min_score=50)

        deals_data = []
        for deal in active_deals[:10]:
            deals_data.append({
                "id": deal.id,
                "company": deal.company_name,
                "status": deal.status.value,
                "thesis_score": deal.thesis_score,
                "source": deal.source.value,
                "valuation_implied_usd": deal.valuation_implied_usd,
            })

        return {
            "pipeline_date": datetime.utcnow().isoformat(),
            "status_summary": pipeline,
            "top_deals": deals_data,
            "total_pipeline_value": sum(
                d.get("valuation_implied_usd", 0) or 0 for d in deals_data
            ),
        }

    async def _recommendations(self) -> dict:
        """Generate portfolio action recommendations."""
        summary = self.portfolio.get_portfolio_summary()
        risk_analysis = await self._risk_analysis()

        recommendations = []

        # Check portfolio deployment
        if summary.total_invested_usd == 0:
            recommendations.append({
                "priority": "high",
                "action": "deploy_capital",
                "description": "Portfolio has no active investments - review deal pipeline",
            })

        # Check deal pipeline
        if summary.deals_in_pipeline < 5:
            recommendations.append({
                "priority": "medium",
                "action": "expand_sourcing",
                "description": "Deal pipeline is thin - increase sourcing activity",
            })

        # Add risk-based recommendations
        for rec in risk_analysis.get("recommendations", []):
            recommendations.append({
                "priority": "medium",
                "action": "risk_mitigation",
                "description": rec,
            })

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "portfolio_health": "healthy" if len(recommendations) <= 2 else "needs_attention",
        }
