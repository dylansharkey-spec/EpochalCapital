# Research Workflows

## Overview

The Research Workflows system automates comprehensive research across all tracked companies.

## Features

- **On-add research**: Automatic research when new companies are added
- **Scheduled refresh**: Twice-weekly research updates
- **Query generation**: Structured research queries for funding, IPO, leadership, M&A
- **History tracking**: Persistent research cache

## Usage

### CLI Commands

```bash
# Research specific company
python -m epochal.cli research "Lambda Labs"

# Check research status
python -m epochal.cli research-status

# Refresh stale research
python -m epochal.cli refresh

# Force refresh all
python -m epochal.cli refresh --force
```

### Research Status Output

```
[*] Research Status:
--------------------------------------------------
    Total companies tracked:  22
    Recently researched:      18
    Needing refresh:          4
    Last full refresh:        2026-01-05

[*] Recommended schedule: Run 'refresh' Monday & Thursday
    Cron: 0 6 * * 1,4 python scripts/scheduled_research.py
```

## Automated Scheduling

### Cron Setup

```bash
# Add to crontab
crontab -e

# Monday and Thursday at 6am
0 6 * * 1,4 cd /path/to/EpochalCapital && python scripts/scheduled_research.py
```

### Scheduled Script

```bash
# Dry run (preview what would be refreshed)
python scripts/scheduled_research.py --dry-run

# Normal run (refresh stale research)
python scripts/scheduled_research.py

# Force refresh all companies
python scripts/scheduled_research.py --force
```

## Research Queries

For each company, the system generates queries:

```python
queries = [
    f"{company} funding round 2026",
    f"{company} IPO filing news",
    f"{company} CEO leadership changes",
    f"{company} acquisition M&A rumors",
    f"{company} revenue ARR growth",
]
```

## API Usage

```python
from epochal.core.research_workflows import ResearchWorkflows, get_research_status

workflows = ResearchWorkflows(data_dir="data")

# Research single company
result = await workflows.research_company_comprehensive("Anthropic")

# Refresh all companies
results = await workflows.refresh_all_companies(
    company_names=["Anthropic", "Mistral"],
    max_age_days=3,
)

# Check status
status = get_research_status()
```

## Data Storage

Research history stored in `data/research_history.json`:

```json
{
  "Anthropic": {
    "last_research": "2026-01-06T10:30:00",
    "queries": ["Anthropic funding...", "Anthropic IPO..."],
    "sources": [...],
    "summary": "..."
  }
}
```
