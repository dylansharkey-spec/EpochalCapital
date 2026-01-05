"""
Command-line interface for Epochal Capital.

Provides interactive access to the investment platform.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional

from epochal.agents.deal_sourcing import DealSourcingAgent
from epochal.agents.research import ResearchAgent
from epochal.agents.portfolio import PortfolioAgent
from epochal.agents.orchestrator import AgentOrchestrator
from epochal.agents.base import AgentRole
from epochal.core.portfolio import Portfolio
from epochal.core.thesis import InvestmentThesis
from epochal.core.models import (
    Company,
    Deal,
    DealSource,
    DealStatus,
    AIVertical,
    CompanyStage,
)
from epochal.utils.formatters import format_currency, format_report
from epochal.core.research_workflows import ResearchWorkflows, get_research_status


class EpochalCLI:
    """Command-line interface for Epochal Capital platform."""

    def __init__(self, data_dir: str = "data"):
        self.portfolio = Portfolio(data_dir=data_dir)
        self.thesis = InvestmentThesis()

        # Initialize orchestrator with agents
        self.orchestrator = AgentOrchestrator(portfolio=self.portfolio)

        # Register agents
        self.deal_sourcing_agent = DealSourcingAgent()
        self.research_agent = ResearchAgent()
        self.portfolio_agent = PortfolioAgent(portfolio=self.portfolio)

        self.orchestrator.register_agent(self.deal_sourcing_agent)
        self.orchestrator.register_agent(self.research_agent)
        self.orchestrator.register_agent(self.portfolio_agent)

        # Initialize research workflows
        self.research_workflows = ResearchWorkflows(data_dir=data_dir)

    def print_header(self):
        """Print CLI header."""
        print("\n" + "=" * 60)
        print("  EPOCHAL CAPITAL - AI Investment Platform")
        print("  Private AI Companies with Liquidity Potential")
        print("=" * 60 + "\n")

    def print_thesis(self):
        """Print investment thesis."""
        print(self.thesis.get_thesis_summary())

    async def scan_opportunities(self) -> dict:
        """Scan for investment opportunities."""
        print("\n[*] Scanning market for AI investment opportunities...")

        from epochal.agents.base import AgentTask

        task = AgentTask(
            name="Market Scan",
            description="Scan market for AI companies matching thesis",
            agent_role=AgentRole.DEAL_SOURCING,
            input_data={"capability": "scan_market"},
        )

        result = await self.orchestrator.execute_task(task)

        if result.success:
            data = result.data
            print(f"\n[+] Scanned {data['companies_scanned']} companies")
            print(f"[+] Found {data['companies_matching']} matching opportunities\n")

            print("TOP OPPORTUNITIES:")
            print("-" * 80)

            for i, opp in enumerate(data["top_opportunities"], 1):
                print(f"\n{i}. {opp['name']}")
                print(f"   Vertical: {opp['vertical']}")
                print(f"   Stage: {opp['stage']}")
                print(f"   Valuation: {format_currency(opp['valuation_usd'])}")
                print(f"   Thesis Score: {opp['thesis_score']}/100")
                print(f"   Key Investors: {', '.join(opp['key_investors'][:3])}")
                if opp['liquidity_signals']:
                    print(f"   Liquidity Signals: {', '.join(opp['liquidity_signals'])}")

            return data
        else:
            print(f"[!] Error: {result.error}")
            return {}

    async def find_liquidity_events(self) -> dict:
        """Find companies with upcoming liquidity events."""
        print("\n[*] Analyzing liquidity event potential...")

        from epochal.agents.base import AgentTask

        task = AgentTask(
            name="Liquidity Analysis",
            description="Find companies with liquidity events",
            agent_role=AgentRole.DEAL_SOURCING,
            input_data={"capability": "find_liquidity_events"},
        )

        result = await self.orchestrator.execute_task(task)

        if result.success:
            data = result.data
            print(f"\n[+] Found {data['candidates_found']} liquidity candidates\n")

            print("TOP LIQUIDITY CANDIDATES:")
            print("-" * 80)

            for i, candidate in enumerate(data["top_liquidity_candidates"], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   Stage: {candidate['stage']}")
                print(f"   Valuation: {format_currency(candidate['valuation_usd'])}")
                print(f"   Liquidity Score: {candidate['liquidity_score']}/100")
                print(f"   Likely Event: {candidate['likely_event_type']}")
                print(f"   Signals: {', '.join(candidate['signals'])}")

            return data
        else:
            print(f"[!] Error: {result.error}")
            return {}

    async def evaluate_company(self, company_name: str) -> dict:
        """Evaluate a specific company against thesis."""
        print(f"\n[*] Evaluating {company_name}...")

        from epochal.agents.base import AgentTask

        task = AgentTask(
            name=f"Evaluate {company_name}",
            description=f"Evaluate {company_name} against investment thesis",
            agent_role=AgentRole.DEAL_SOURCING,
            input_data={
                "capability": "evaluate_company",
                "company_name": company_name,
            },
        )

        result = await self.orchestrator.execute_task(task)

        if result.success:
            data = result.data
            if "error" in data:
                print(f"\n[!] {data['error']}")
                return data

            print(f"\nCOMPANY EVALUATION: {data['company']}")
            print("-" * 60)
            print(f"Vertical: {data['vertical']}")
            print(f"Stage: {data['stage']}")
            print(f"Valuation: {format_currency(data['valuation_usd'])}")
            print(f"\nSCORES:")
            for key, value in data['scores'].items():
                if key != 'total':
                    print(f"  {key}: {value}/100")
            print(f"\n  TOTAL SCORE: {data['scores']['total']}/100")
            print(f"\nRECOMMENDATION: {data['recommendation']}")
            print(f"\nANALYSIS: {data['analysis']}")

            return data
        else:
            print(f"[!] Error: {result.error}")
            return {}

    async def portfolio_summary(self) -> dict:
        """Get portfolio summary."""
        print("\n[*] Generating portfolio summary...")

        from epochal.agents.base import AgentTask

        task = AgentTask(
            name="Portfolio Summary",
            description="Generate portfolio summary",
            agent_role=AgentRole.PORTFOLIO_MANAGER,
            input_data={"capability": "portfolio_summary"},
        )

        result = await self.orchestrator.execute_task(task)

        if result.success:
            print(result.data.get("report", "No report available"))
            return result.data
        else:
            print(f"[!] Error: {result.error}")
            return {}

    async def run_daily_briefing(self) -> dict:
        """Run comprehensive daily briefing."""
        print("\n[*] Running daily briefing across all agents...")
        print("[*] This may take a moment...\n")

        briefing = await self.orchestrator.run_daily_briefing()

        print("\n" + "=" * 60)
        print("  EPOCHAL CAPITAL DAILY BRIEFING")
        print(f"  {briefing['date']}")
        print("=" * 60)

        # Deal Sourcing Section
        if "deal_sourcing" in briefing["sections"]:
            sourcing = briefing["sections"]["deal_sourcing"]
            if "results" in sourcing:
                opportunities = sourcing["results"].get("generate_opportunities", {})
                if opportunities.get("opportunities"):
                    print("\n📊 TOP OPPORTUNITIES:")
                    for opp in opportunities["opportunities"][:5]:
                        print(f"  • {opp['company']} ({opp['vertical']}) - Score: {opp['thesis_score']}")

        # Research Section
        if "research" in briefing["sections"]:
            research = briefing["sections"]["research"]
            if research.get("executive_summary"):
                print("\n📈 MARKET OUTLOOK:")
                print(f"  {research['executive_summary'].get('market_outlook', 'N/A')}")

        # Portfolio Section
        if "portfolio_review" in briefing["sections"]:
            portfolio = briefing["sections"]["portfolio_review"]
            if "results" in portfolio:
                recs = portfolio["results"].get("recommendations", {})
                if recs.get("recommendations"):
                    print("\n📋 RECOMMENDATIONS:")
                    for rec in recs["recommendations"]:
                        print(f"  • [{rec['priority'].upper()}] {rec['description']}")

        print("\n" + "=" * 60 + "\n")

        return briefing

    def show_agent_status(self):
        """Show status of all agents."""
        print("\n[*] Agent Status:")
        print("-" * 60)

        for agent_status in self.orchestrator.list_agents():
            print(f"\n  {agent_status['name']}")
            print(f"    Role: {agent_status['role']}")
            print(f"    Active: {agent_status['is_active']}")
            print(f"    Capabilities: {', '.join(agent_status['capabilities'])}")
            print(f"    Tasks Completed: {agent_status['tasks_completed']}")

    def add_company_to_watchlist(
        self,
        name: str,
        description: str,
        vertical: str,
        stage: str,
        valuation_usd: Optional[float] = None,
    ) -> Company:
        """Add a company to the watchlist."""
        company = Company(
            name=name,
            description=description,
            vertical=AIVertical(vertical),
            stage=CompanyStage(stage),
            valuation_usd=valuation_usd,
        )

        self.portfolio.add_company(company)
        print(f"\n[+] Added {name} to watchlist")

        # Also add to deal sourcing agent's tracking
        self.deal_sourcing_agent.add_company_to_track({
            "name": name,
            "description": description,
            "vertical": AIVertical(vertical),
            "stage": CompanyStage(stage),
            "valuation_usd": valuation_usd,
            "key_investors": [],
            "liquidity_signals": [],
        })

        return company

    async def research_company(self, company_name: str) -> dict:
        """Run comprehensive research on a company."""
        print(f"\n[*] Running comprehensive research on {company_name}...")
        print("[*] Generating search queries for: funding, IPO, leadership, M&A news")

        # Show the queries that would be run
        queries = self.research_workflows.generate_research_queries(company_name)
        print("\n[*] Research queries:")
        for q in queries:
            print(f"    → {q}")

        # Run the research workflow
        result = await self.research_workflows.research_company_comprehensive(company_name)

        print(f"\n[+] Research recorded for {company_name}")
        print(f"[+] Research date: {result.research_date.strftime('%Y-%m-%d %H:%M UTC')}")

        # Show last research if available
        last = self.research_workflows.get_last_research(company_name)
        if last:
            print(f"\n[*] Research history saved")
            if last.get("sources"):
                print(f"[*] Sources: {len(last['sources'])} found")

        return result.to_dict()

    async def refresh_research(self, force: bool = False) -> dict:
        """Refresh research for all tracked companies."""
        from epochal.agents.deal_sourcing import TRACKED_AI_COMPANIES

        company_names = [c["name"] for c in TRACKED_AI_COMPANIES]

        print(f"\n[*] Scheduled Research Refresh")
        print(f"[*] Companies tracked: {len(company_names)}")

        # Show status
        status = get_research_status()
        print(f"[*] Recently researched (last 3 days): {status['recently_researched']}")
        print(f"[*] Needing refresh: {status['needs_refresh']}")

        if not force and status['needs_refresh'] == 0:
            print("\n[+] All companies recently researched. Use 'refresh --force' to force update.")
            return status

        print(f"\n[*] Starting refresh...")
        max_age = 0 if force else 3

        results = await self.research_workflows.refresh_all_companies(
            company_names=company_names,
            max_age_days=max_age,
        )

        print(f"\n[+] Refreshed {len(results)} companies")
        return {"refreshed": len(results), "status": get_research_status()}

    def show_research_status(self):
        """Show research status."""
        status = get_research_status()

        print("\n[*] Research Status:")
        print("-" * 50)
        print(f"    Total companies tracked:  {status['total_companies_tracked']}")
        print(f"    Recently researched:      {status['recently_researched']}")
        print(f"    Needing refresh:          {status['needs_refresh']}")
        print(f"    Last full refresh:        {status['last_full_refresh'] or 'Never'}")

        # Show schedule recommendation
        print("\n[*] Recommended schedule: Run 'refresh' Monday & Thursday")
        print("    Cron: 0 6 * * 1,4 python scripts/scheduled_research.py")

    def get_commands(self) -> dict:
        """Get available commands."""
        return {
            "scan": "Scan market for AI investment opportunities",
            "liquidity": "Find companies with upcoming liquidity events",
            "evaluate <company>": "Evaluate a specific company",
            "research <company>": "Run comprehensive research on a company",
            "refresh": "Refresh research for all tracked companies",
            "research-status": "Show research workflow status",
            "portfolio": "View portfolio summary",
            "briefing": "Run comprehensive daily briefing",
            "agents": "Show agent status",
            "thesis": "Show investment thesis",
            "add <company>": "Add company to watchlist",
            "help": "Show this help message",
            "exit": "Exit the CLI",
        }

    def print_help(self):
        """Print help message."""
        print("\nAVAILABLE COMMANDS:")
        print("-" * 40)
        for cmd, desc in self.get_commands().items():
            print(f"  {cmd:25} {desc}")
        print()


async def main():
    """Main CLI entry point."""
    cli = EpochalCLI()
    cli.print_header()

    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1].lower()

        if command == "scan":
            await cli.scan_opportunities()
        elif command == "liquidity":
            await cli.find_liquidity_events()
        elif command == "evaluate" and len(sys.argv) > 2:
            company = " ".join(sys.argv[2:])
            await cli.evaluate_company(company)
        elif command == "research" and len(sys.argv) > 2:
            company = " ".join(sys.argv[2:])
            await cli.research_company(company)
        elif command == "refresh":
            force = "--force" in sys.argv
            await cli.refresh_research(force=force)
        elif command == "research-status":
            cli.show_research_status()
        elif command == "portfolio":
            await cli.portfolio_summary()
        elif command == "briefing":
            await cli.run_daily_briefing()
        elif command == "agents":
            cli.show_agent_status()
        elif command == "thesis":
            cli.print_thesis()
        elif command == "help":
            cli.print_help()
        else:
            print(f"Unknown command: {command}")
            cli.print_help()
    else:
        # Interactive mode
        cli.print_help()

        while True:
            try:
                user_input = input("\nepochal> ").strip()

                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()

                if command == "exit" or command == "quit":
                    print("\nGoodbye!")
                    break
                elif command == "scan":
                    await cli.scan_opportunities()
                elif command == "liquidity":
                    await cli.find_liquidity_events()
                elif command == "evaluate":
                    if len(parts) > 1:
                        company = " ".join(parts[1:])
                        await cli.evaluate_company(company)
                    else:
                        print("Usage: evaluate <company_name>")
                elif command == "research":
                    if len(parts) > 1:
                        company = " ".join(parts[1:])
                        await cli.research_company(company)
                    else:
                        print("Usage: research <company_name>")
                elif command == "refresh":
                    force = "--force" in parts
                    await cli.refresh_research(force=force)
                elif command == "research-status":
                    cli.show_research_status()
                elif command == "portfolio":
                    await cli.portfolio_summary()
                elif command == "briefing":
                    await cli.run_daily_briefing()
                elif command == "agents":
                    cli.show_agent_status()
                elif command == "thesis":
                    cli.print_thesis()
                elif command == "help":
                    cli.print_help()
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def run():
    """Entry point for the CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
