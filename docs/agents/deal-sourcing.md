# Deal Sourcing Agent

## Overview

The Deal Sourcing Agent is responsible for identifying and evaluating investment opportunities in private AI companies.

**Role:** `AgentRole.DEAL_SOURCING`

## Capabilities

| Capability | Description |
|------------|-------------|
| `scan_market` | Scan market for AI companies matching thesis |
| `find_liquidity_events` | Identify companies with upcoming liquidity |
| `evaluate_company` | Score specific company against thesis |
| `generate_opportunities` | Generate ranked opportunity list |

## Tracked Companies

The agent maintains a list of 22 tracked AI companies:

### Foundation Models
- Anthropic ($60B, Series D)
- OpenAI ($157B, Series E)
- Mistral AI ($6.2B, Series B)
- Cohere ($5.5B, Series D)

### AI Infrastructure
- Databricks ($62B, Series I)
- Cerebras Systems ($4.3B, Series F)
- Together AI ($3B, Series B)
- Lambda Labs ($12B, Pre-IPO)
- Lightmatter ($4.4B, Series D)

### AI Agents
- Perplexity AI ($9B, Series B)
- Adept AI ($1B, Series B)

### Developer Tools
- Hugging Face ($4.5B, Series D)
- Replit ($1.2B, Series B)

### Enterprise AI
- Glean ($4.6B, Series D)
- Scale AI ($13.8B, Series F)

### Creative AI
- Runway ($1.5B, Series C)
- Stability AI ($1B, Series B)

## Usage

### CLI Commands

```bash
# Scan for opportunities
python -m epochal.cli scan

# Find liquidity events
python -m epochal.cli liquidity

# Evaluate a company
python -m epochal.cli evaluate Anthropic
```

### Programmatic Usage

```python
from epochal.agents.deal_sourcing import DealSourcingAgent
from epochal.agents.base import AgentTask, AgentRole

agent = DealSourcingAgent()

# Scan market
task = AgentTask(
    name="Scan",
    description="Scan market",
    agent_role=AgentRole.DEAL_SOURCING,
    input_data={"capability": "scan_market"},
)
result = await agent.execute_task(task)

# Evaluate company
task = AgentTask(
    name="Evaluate",
    description="Evaluate company",
    agent_role=AgentRole.DEAL_SOURCING,
    input_data={
        "capability": "evaluate_company",
        "company_name": "Anthropic",
    },
)
result = await agent.execute_task(task)
```

## Scoring Output

The agent returns detailed scoring:

```python
{
    "company": "Anthropic",
    "vertical": "Foundation Models",
    "stage": "Series D",
    "valuation_usd": 60000000000,
    "scores": {
        "vertical_fit": 100,
        "stage_fit": 75,
        "liquidity_signals": 95,
        "investor_quality": 95,
        "valuation_attractiveness": 65,
        "total": 92.5,
    },
    "recommendation": "Strong Buy",
    "analysis": "..."
}
```

## Adding Companies

Add new companies to track:

```python
agent.add_company_to_track({
    "name": "New Company",
    "description": "Description",
    "vertical": AIVertical.AI_INFRASTRUCTURE,
    "stage": CompanyStage.SERIES_C,
    "valuation_usd": 5_000_000_000,
    "key_investors": ["Sequoia"],
    "liquidity_signals": ["IPO discussions"],
})
```

Or edit `TRACKED_AI_COMPANIES` in `epochal/agents/deal_sourcing.py`.
