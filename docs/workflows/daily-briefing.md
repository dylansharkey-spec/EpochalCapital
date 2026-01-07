# Daily Briefing

## Overview

The daily briefing aggregates insights from all agents into a comprehensive morning report.

## Usage

```bash
python -m epochal.cli briefing
```

## Briefing Sections

### 1. Top Opportunities

From Deal Sourcing Agent:
- Highest-scoring companies
- Thesis alignment scores
- Key signals

### 2. Market Outlook

From Research Agent:
- Sector trends
- Funding environment
- IPO pipeline status

### 3. Portfolio Recommendations

From Portfolio Agent:
- Position updates
- Rebalancing suggestions
- Risk alerts

## Sample Output

```
============================================================
  EPOCHAL CAPITAL DAILY BRIEFING
  2026-01-07
============================================================

📊 TOP OPPORTUNITIES:
  • Anthropic (Foundation Models) - Score: 92.5
  • Glean (Enterprise AI) - Score: 79.5
  • Mistral AI (Foundation Models) - Score: 79.5
  • Lambda Labs (AI Infrastructure) - Score: 78.0
  • Perplexity AI (AI Agents) - Score: 77.0

📈 MARKET OUTLOOK:
  Enterprise AI adoption accelerating. Multiple companies
  preparing for 2026 IPOs. Valuations stabilizing.

📋 RECOMMENDATIONS:
  • [HIGH] Review Lambda Labs IPO timeline
  • [MEDIUM] Update Lightmatter research
  • [LOW] Monitor Stability AI restructuring

============================================================
```

## Programmatic Usage

```python
from epochal.cli import EpochalCLI

cli = EpochalCLI()
briefing = await cli.run_daily_briefing()

# Access sections
opportunities = briefing["sections"]["deal_sourcing"]
research = briefing["sections"]["research"]
portfolio = briefing["sections"]["portfolio_review"]
```

## Scheduling

Run daily briefing automatically:

```bash
# Cron: Every weekday at 7am
0 7 * * 1-5 python -m epochal.cli briefing >> /var/log/epochal/briefing.log
```
