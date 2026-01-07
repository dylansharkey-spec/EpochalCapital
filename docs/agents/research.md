# Research Agent

## Overview

The Research Agent conducts company research, market analysis, and competitive intelligence.

**Role:** `AgentRole.RESEARCH_ANALYST`

## Capabilities

| Capability | Description |
|------------|-------------|
| `research_company` | Deep-dive on specific company |
| `generate_research_report` | Formatted research output |
| `analyze_market` | Sector/market analysis |

## Usage

```bash
# Research a company
python -m epochal.cli research "Anthropic"
```

## Research Queries

The agent generates structured queries:

- `{company} funding round 2026`
- `{company} IPO filing news`
- `{company} CEO leadership changes`
- `{company} acquisition M&A rumors`
- `{company} revenue ARR growth`

## Integration with Research Workflows

The Research Agent is enhanced by the automated Research Workflows system:

```python
from epochal.core.research_workflows import ResearchWorkflows

workflows = ResearchWorkflows()

# Research on company add
await workflows.on_company_added("New Company")

# Scheduled refresh
await workflows.refresh_all_companies(company_names, max_age_days=3)
```

See [Research Workflows](../workflows/research.md) for automation details.
