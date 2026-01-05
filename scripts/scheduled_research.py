#!/usr/bin/env python3
"""
Scheduled Research Refresh for Epochal Capital.

Run this script twice weekly (recommended: Monday & Thursday mornings).

Usage:
    python scripts/scheduled_research.py              # Refresh all companies
    python scripts/scheduled_research.py --dry-run   # Show what would be refreshed
    python scripts/scheduled_research.py --force     # Force refresh all (ignore age)

Cron example (Mon & Thu at 6am):
    0 6 * * 1,4 cd /path/to/EpochalCapital && python scripts/scheduled_research.py
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from epochal.agents.deal_sourcing import TRACKED_AI_COMPANIES
from epochal.core.research_workflows import ResearchWorkflows, get_research_status


async def run_scheduled_refresh(dry_run: bool = False, force: bool = False):
    """Run the scheduled research refresh."""
    print("\n" + "=" * 70)
    print("  EPOCHAL CAPITAL - SCHEDULED RESEARCH REFRESH")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)

    # Get all tracked company names
    company_names = [c["name"] for c in TRACKED_AI_COMPANIES]
    print(f"\n[*] Total companies tracked: {len(company_names)}")

    # Show current research status
    status = get_research_status()
    print(f"[*] Recently researched (last 3 days): {status['recently_researched']}")
    print(f"[*] Needing refresh: {status['needs_refresh']}")
    print(f"[*] Last full refresh: {status['last_full_refresh'] or 'Never'}")

    if dry_run:
        print("\n[DRY RUN] Would refresh the following companies:")
        workflows = ResearchWorkflows()
        for name in company_names:
            last = workflows.get_last_research(name)
            if not last:
                print(f"  - {name} (never researched)")
            else:
                print(f"  - {name} (last: {last['research_date'][:10]})")
        return

    # Run the refresh
    workflows = ResearchWorkflows()

    if force:
        print("\n[FORCE] Refreshing ALL companies regardless of age...")
        max_age = 0  # Force refresh all
    else:
        max_age = 3  # Only refresh if older than 3 days

    print("\n[*] Starting research refresh...")
    print("[*] This will search for latest: funding, IPO, leadership, M&A news")
    print()

    results = await workflows.refresh_all_companies(
        company_names=company_names,
        max_age_days=max_age,
    )

    # Summary
    print("\n" + "=" * 70)
    print("  REFRESH COMPLETE")
    print("=" * 70)
    print(f"\n[+] Companies researched: {len(results)}")
    print(f"[+] Research history saved to: data/research_history.json")

    # Show updated status
    new_status = get_research_status()
    print(f"\n[*] New status:")
    print(f"    Recently researched: {new_status['recently_researched']}")
    print(f"    Needing refresh: {new_status['needs_refresh']}")


async def research_single_company(company_name: str):
    """Research a single company."""
    print(f"\n[*] Running comprehensive research for: {company_name}")

    workflows = ResearchWorkflows()
    result = await workflows.research_company_comprehensive(company_name)

    print(f"\n[+] Research complete")
    print(f"[+] Queries generated:")
    for q in workflows.generate_research_queries(company_name):
        print(f"    - {q}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Epochal Capital Scheduled Research Refresh"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be refreshed without doing it",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force refresh all companies regardless of age",
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Research a single company by name",
    )

    args = parser.parse_args()

    if args.company:
        asyncio.run(research_single_company(args.company))
    else:
        asyncio.run(run_scheduled_refresh(dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
