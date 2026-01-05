"""
Portfolio Management System.

Tracks all investments, deals in pipeline, and portfolio analytics.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from epochal.core.models import (
    Company,
    Deal,
    DealStatus,
    Fund,
    Investment,
    SPV,
)
from epochal.core.thesis import InvestmentThesis


@dataclass
class PortfolioSummary:
    """Summary statistics for the portfolio."""
    total_invested_usd: float = 0.0
    current_value_usd: float = 0.0
    realized_gains_usd: float = 0.0
    unrealized_gains_usd: float = 0.0
    total_return_pct: float = 0.0
    active_positions: int = 0
    exited_positions: int = 0
    deals_in_pipeline: int = 0
    companies_tracked: int = 0


class Portfolio:
    """
    Central portfolio management system.

    Manages:
    - Companies being tracked
    - Active deals in pipeline
    - Investments (direct and via SPVs/funds)
    - Portfolio analytics
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.companies: dict[str, Company] = {}
        self.deals: dict[str, Deal] = {}
        self.investments: dict[str, Investment] = {}
        self.spvs: dict[str, SPV] = {}
        self.funds: dict[str, Fund] = {}
        self.thesis = InvestmentThesis()

        self._load_data()

    def _load_data(self):
        """Load portfolio data from disk."""
        for entity_type, entity_dict, entity_class in [
            ("companies", self.companies, Company),
            ("deals", self.deals, Deal),
            ("investments", self.investments, Investment),
        ]:
            file_path = self.data_dir / f"{entity_type}.json"
            if file_path.exists():
                with open(file_path) as f:
                    data = json.load(f)
                    for item in data:
                        try:
                            if entity_type == "companies":
                                entity = Company.from_dict(item)
                            else:
                                # For now, skip complex deserialization
                                continue
                            entity_dict[entity.id] = entity
                        except Exception:
                            pass  # Skip malformed entries

    def save_data(self):
        """Save portfolio data to disk."""
        # Save companies
        companies_data = [c.to_dict() for c in self.companies.values()]
        with open(self.data_dir / "companies.json", "w") as f:
            json.dump(companies_data, f, indent=2)

        # Save deals
        deals_data = [d.to_dict() for d in self.deals.values()]
        with open(self.data_dir / "deals.json", "w") as f:
            json.dump(deals_data, f, indent=2)

        # Save investments
        investments_data = [i.to_dict() for i in self.investments.values()]
        with open(self.data_dir / "investments.json", "w") as f:
            json.dump(investments_data, f, indent=2)

        # Save SPVs
        spvs_data = [s.to_dict() for s in self.spvs.values()]
        with open(self.data_dir / "spvs.json", "w") as f:
            json.dump(spvs_data, f, indent=2)

        # Save funds
        funds_data = [fund.to_dict() for fund in self.funds.values()]
        with open(self.data_dir / "funds.json", "w") as f:
            json.dump(funds_data, f, indent=2)

    # Company Management
    def add_company(self, company: Company) -> Company:
        """Add a company to track."""
        self.companies[company.id] = company
        self.save_data()
        return company

    def get_company(self, company_id: str) -> Optional[Company]:
        """Get a company by ID."""
        return self.companies.get(company_id)

    def find_company_by_name(self, name: str) -> Optional[Company]:
        """Find a company by name (case-insensitive)."""
        name_lower = name.lower()
        for company in self.companies.values():
            if company.name.lower() == name_lower:
                return company
        return None

    def list_companies(self, vertical: Optional[str] = None) -> list[Company]:
        """List all tracked companies, optionally filtered by vertical."""
        companies = list(self.companies.values())
        if vertical:
            companies = [c for c in companies if c.vertical.value == vertical]
        return sorted(companies, key=lambda c: c.name)

    def update_company(self, company_id: str, updates: dict) -> Optional[Company]:
        """Update a company's information."""
        if company_id not in self.companies:
            return None

        company = self.companies[company_id]
        for key, value in updates.items():
            if hasattr(company, key):
                setattr(company, key, value)
        company.updated_at = datetime.utcnow()
        self.save_data()
        return company

    # Deal Management
    def add_deal(self, deal: Deal) -> Deal:
        """Add a deal to the pipeline."""
        # Score the deal against thesis
        company = self.get_company(deal.company_id)
        scores = self.thesis.score_deal(deal, company)
        deal.thesis_score = scores["total"]

        self.deals[deal.id] = deal
        self.save_data()
        return deal

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Get a deal by ID."""
        return self.deals.get(deal_id)

    def list_deals(
        self,
        status: Optional[DealStatus] = None,
        min_score: Optional[float] = None,
    ) -> list[Deal]:
        """List deals, optionally filtered."""
        deals = list(self.deals.values())

        if status:
            deals = [d for d in deals if d.status == status]

        if min_score is not None:
            deals = [d for d in deals if d.thesis_score and d.thesis_score >= min_score]

        return sorted(deals, key=lambda d: d.thesis_score or 0, reverse=True)

    def update_deal_status(self, deal_id: str, status: DealStatus) -> Optional[Deal]:
        """Update a deal's status."""
        if deal_id not in self.deals:
            return None

        self.deals[deal_id].status = status
        self.deals[deal_id].updated_at = datetime.utcnow()
        self.save_data()
        return self.deals[deal_id]

    def get_pipeline_summary(self) -> dict:
        """Get summary of deal pipeline."""
        pipeline = {}
        for status in DealStatus:
            deals = [d for d in self.deals.values() if d.status == status]
            pipeline[status.value] = {
                "count": len(deals),
                "total_value": sum(d.total_available_usd or 0 for d in deals),
            }
        return pipeline

    # Investment Management
    def record_investment(self, investment: Investment) -> Investment:
        """Record a new investment."""
        self.investments[investment.id] = investment

        # Update deal status if linked
        if investment.deal_id and investment.deal_id in self.deals:
            self.deals[investment.deal_id].status = DealStatus.CLOSED

        self.save_data()
        return investment

    def get_investment(self, investment_id: str) -> Optional[Investment]:
        """Get an investment by ID."""
        return self.investments.get(investment_id)

    def list_investments(self, status: str = "active") -> list[Investment]:
        """List investments by status."""
        return [
            inv for inv in self.investments.values()
            if inv.status == status
        ]

    def update_investment_value(
        self,
        investment_id: str,
        current_value_usd: float,
    ) -> Optional[Investment]:
        """Update an investment's current value."""
        if investment_id not in self.investments:
            return None

        self.investments[investment_id].current_value_usd = current_value_usd
        self.save_data()
        return self.investments[investment_id]

    def record_exit(
        self,
        investment_id: str,
        exit_proceeds_usd: float,
        exit_date: Optional[datetime] = None,
    ) -> Optional[Investment]:
        """Record an investment exit."""
        if investment_id not in self.investments:
            return None

        inv = self.investments[investment_id]
        inv.status = "exited"
        inv.exit_date = exit_date or datetime.utcnow()
        inv.exit_proceeds_usd = exit_proceeds_usd
        inv.realized_gain_usd = exit_proceeds_usd - inv.cost_basis_usd
        self.save_data()
        return inv

    # SPV Management
    def add_spv(self, spv: SPV) -> SPV:
        """Add an SPV."""
        self.spvs[spv.id] = spv
        self.save_data()
        return spv

    def list_spvs(self, status: str = "open") -> list[SPV]:
        """List SPVs by status."""
        return [s for s in self.spvs.values() if s.status == status]

    # Fund Management
    def add_fund(self, fund: Fund) -> Fund:
        """Add a fund commitment."""
        self.funds[fund.id] = fund
        self.save_data()
        return fund

    def list_funds(self, status: str = "active") -> list[Fund]:
        """List funds by status."""
        return [f for f in self.funds.values() if f.status == status]

    # Analytics
    def get_portfolio_summary(self) -> PortfolioSummary:
        """Calculate portfolio summary statistics."""
        summary = PortfolioSummary()

        # Active investments
        active_investments = self.list_investments("active")
        summary.active_positions = len(active_investments)
        summary.total_invested_usd = sum(i.cost_basis_usd for i in active_investments)
        summary.current_value_usd = sum(
            i.current_value_usd or i.cost_basis_usd for i in active_investments
        )

        # Exited investments
        exited_investments = self.list_investments("exited")
        summary.exited_positions = len(exited_investments)
        summary.realized_gains_usd = sum(
            i.realized_gain_usd or 0 for i in exited_investments
        )

        # Unrealized gains
        summary.unrealized_gains_usd = (
            summary.current_value_usd - summary.total_invested_usd
        )

        # Total return
        if summary.total_invested_usd > 0:
            total_gains = summary.realized_gains_usd + summary.unrealized_gains_usd
            summary.total_return_pct = (total_gains / summary.total_invested_usd) * 100

        # Pipeline and tracking
        summary.deals_in_pipeline = len([
            d for d in self.deals.values()
            if d.status not in [DealStatus.CLOSED, DealStatus.PASSED, DealStatus.LOST]
        ])
        summary.companies_tracked = len(self.companies)

        return summary

    def get_portfolio_by_vertical(self) -> dict:
        """Get portfolio breakdown by AI vertical."""
        by_vertical = {}

        for inv in self.list_investments("active"):
            company = self.get_company(inv.company_id)
            if company:
                vertical = company.vertical.value
                if vertical not in by_vertical:
                    by_vertical[vertical] = {
                        "count": 0,
                        "invested": 0.0,
                        "current_value": 0.0,
                    }
                by_vertical[vertical]["count"] += 1
                by_vertical[vertical]["invested"] += inv.cost_basis_usd
                by_vertical[vertical]["current_value"] += (
                    inv.current_value_usd or inv.cost_basis_usd
                )

        return by_vertical

    def export_portfolio_report(self) -> str:
        """Generate a text portfolio report."""
        summary = self.get_portfolio_summary()
        by_vertical = self.get_portfolio_by_vertical()
        pipeline = self.get_pipeline_summary()

        report = f"""
EPOCHAL CAPITAL PORTFOLIO REPORT
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
{'=' * 60}

PORTFOLIO SUMMARY
-----------------
Total Invested:     ${summary.total_invested_usd:,.0f}
Current Value:      ${summary.current_value_usd:,.0f}
Unrealized Gain:    ${summary.unrealized_gains_usd:,.0f}
Realized Gain:      ${summary.realized_gains_usd:,.0f}
Total Return:       {summary.total_return_pct:.1f}%

Active Positions:   {summary.active_positions}
Exited Positions:   {summary.exited_positions}
Companies Tracked:  {summary.companies_tracked}

DEAL PIPELINE
-------------
"""
        for status, data in pipeline.items():
            report += f"{status:20} {data['count']:3} deals  ${data['total_value']:,.0f}\n"

        if by_vertical:
            report += "\nPORTFOLIO BY VERTICAL\n"
            report += "-" * 20 + "\n"
            for vertical, data in sorted(by_vertical.items()):
                report += (
                    f"{vertical:20} {data['count']:3} positions  "
                    f"${data['invested']:,.0f} invested  "
                    f"${data['current_value']:,.0f} current\n"
                )

        return report
