# Epochal Capital

AI-Powered Investment Platform for Private AI Companies with Liquidity Potential

## Overview

Epochal Capital is a multi-agent investment platform designed to:

- **Source deals** in private AI companies with upcoming liquidity events
- **Score opportunities** against a configurable investment thesis
- **Track portfolio** investments across direct positions, SPVs, and funds
- **Automate workflows** through coordinated AI agents

## Investment Thesis

Focus: Private AI companies with potential upcoming liquidity events (IPO, acquisition, secondary)

Target Profile:
- **Verticals**: Foundation models, AI infrastructure, AI agents, developer tools, enterprise AI
- **Stages**: Series B through Pre-IPO
- **Valuation**: $100M - $50B (preferred: $500M - $10B)
- **Liquidity Timeline**: 18-36 months
- **Discount**: Minimum 10% to last round (preferred: 25%+)

## Architecture

### Multi-Agent System

The platform uses specialized AI agents that can work independently or in coordinated workflows:

| Agent | Role | Capabilities |
|-------|------|--------------|
| Deal Sourcing Agent | Find opportunities | Market scan, company evaluation, liquidity analysis |
| Research Agent | Due diligence | Company research, market analysis, competitive analysis |
| Portfolio Agent | Portfolio management | Tracking, risk analysis, performance reporting |

### Core Modules

```
epochal/
├── agents/           # AI agent implementations
│   ├── base.py       # Base agent framework
│   ├── deal_sourcing.py
│   ├── research.py
│   ├── portfolio.py
│   └── orchestrator.py
├── core/             # Core business logic
│   ├── models.py     # Data models (Company, Deal, Investment, etc.)
│   ├── thesis.py     # Investment thesis and scoring
│   └── portfolio.py  # Portfolio management
├── integrations/     # External platform integrations
├── utils/            # Utilities and formatters
└── cli.py            # Command-line interface
```

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/EpochalCapital.git
cd EpochalCapital

# Install in development mode
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

```bash
# Run interactive CLI
python -m epochal.cli

# Or use individual commands
python -m epochal.cli scan        # Scan for opportunities
python -m epochal.cli liquidity   # Find liquidity events
python -m epochal.cli evaluate Anthropic  # Evaluate a company
python -m epochal.cli briefing    # Run daily briefing
python -m epochal.cli portfolio   # View portfolio
```

### Demo Script

```bash
python scripts/run_demo.py
```

### Programmatic Usage

```python
import asyncio
from epochal.cli import EpochalCLI

async def main():
    cli = EpochalCLI()

    # Scan for opportunities
    opportunities = await cli.scan_opportunities()

    # Evaluate a specific company
    evaluation = await cli.evaluate_company("Anthropic")

    # Run daily briefing
    briefing = await cli.run_daily_briefing()

asyncio.run(main())
```

## Tracked Companies

The platform tracks major private AI companies including:

- **Foundation Models**: Anthropic, OpenAI, Mistral AI, Cohere
- **Infrastructure**: Databricks, Cerebras, Groq, Together AI
- **AI Agents**: Perplexity AI, Adept AI
- **Developer Tools**: Hugging Face, Replit
- **Enterprise AI**: Glean, Scale AI
- **Creative AI**: Runway, Stability AI

## Extending the Platform

### Adding New Agents

Create a new agent by extending the base `Agent` class:

```python
from epochal.agents.base import Agent, AgentRole, AgentTask, AgentResult

class CustomAgent(Agent):
    def __init__(self):
        super().__init__(
            role=AgentRole.CUSTOM,  # Add to AgentRole enum
            name="Custom Agent",
            description="Description of what this agent does",
        )

    def _register_capabilities(self):
        self.register_capability(
            name="custom_action",
            description="What this capability does",
            handler=self._custom_handler,
        )

    async def execute_task(self, task: AgentTask) -> AgentResult:
        # Implementation
        pass

    async def _custom_handler(self, **kwargs):
        # Capability implementation
        pass
```

### Creating Workflows

Use the orchestrator to create multi-agent workflows:

```python
from epochal.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Create custom workflow
workflow = orchestrator.create_workflow(
    name="Custom Workflow",
    description="Multi-step workflow",
    steps=[
        {
            "name": "step_1",
            "agent_role": "deal_sourcing",
            "input_data": {"capability": "scan_market"},
        },
        {
            "name": "step_2",
            "agent_role": "research_analyst",
            "input_data": {"capability": "generate_research_report"},
            "depends_on": ["step_1"],
        },
    ],
)

# Execute workflow
result = await orchestrator.execute_workflow(workflow.id)
```

## Configuration

Edit `config/thesis.yaml` to customize investment criteria:

```yaml
valuation_criteria:
  min_valuation: 100_000_000
  max_valuation: 50_000_000_000

liquidity_requirements:
  max_months: 36
  preferred_months: 18

scoring_weights:
  vertical_fit: 0.15
  liquidity_timeline: 0.25
  # ... etc
```

## Future Roadmap

- [ ] Integration with secondary market platforms (Forge, EquityZen)
- [ ] Real-time news and intelligence feeds
- [ ] Automated deal flow ingestion
- [ ] LP reporting and communications
- [ ] Risk management agent
- [ ] Compliance and regulatory agent

## License

Proprietary - Epochal Capital
