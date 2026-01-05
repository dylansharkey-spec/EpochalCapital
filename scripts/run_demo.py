#!/usr/bin/env python3
"""
Demo script for Epochal Capital platform.

This script demonstrates the key capabilities of the platform:
1. Market scanning for AI companies
2. Thesis scoring and evaluation
3. Liquidity event identification
4. Multi-agent workflow orchestration
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from epochal.cli import EpochalCLI


async def run_demo():
    """Run a demonstration of the Epochal Capital platform."""
    print("\n" + "=" * 70)
    print("  EPOCHAL CAPITAL - Platform Demonstration")
    print("  Private AI Companies with Liquidity Potential")
    print("=" * 70)

    # Initialize CLI
    cli = EpochalCLI(data_dir="data")

    # Step 1: Show Investment Thesis
    print("\n\n📋 STEP 1: Investment Thesis")
    print("-" * 50)
    cli.print_thesis()

    # Step 2: Scan for opportunities
    print("\n\n🔍 STEP 2: Market Scan")
    print("-" * 50)
    await cli.scan_opportunities()

    # Step 3: Find liquidity events
    print("\n\n💰 STEP 3: Liquidity Event Analysis")
    print("-" * 50)
    await cli.find_liquidity_events()

    # Step 4: Evaluate specific companies
    print("\n\n📊 STEP 4: Company Evaluations")
    print("-" * 50)

    companies_to_evaluate = ["Anthropic", "Databricks", "Perplexity AI"]

    for company in companies_to_evaluate:
        await cli.evaluate_company(company)
        print()

    # Step 5: Show agent status
    print("\n\n🤖 STEP 5: Multi-Agent System Status")
    print("-" * 50)
    cli.show_agent_status()

    # Step 6: Run daily briefing
    print("\n\n📰 STEP 6: Daily Briefing (Full Multi-Agent Workflow)")
    print("-" * 50)
    await cli.run_daily_briefing()

    print("\n\n✅ Demo complete!")
    print("=" * 70)
    print("\nThe Epochal Capital platform is ready for use.")
    print("Run 'python -m epochal.cli' for interactive mode.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
