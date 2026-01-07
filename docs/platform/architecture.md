# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / API                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Orchestrator                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │Deal Sourcing│ │  Research   │ │  Portfolio  │ │     IR      ││
│  │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Core Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Models    │ │   Thesis    │ │  Portfolio  │ │  Research   ││
│  │             │ │             │ │             │ │  Workflows  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Persistence                            │
│              data/portfolio.json, data/research_history.json     │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
epochal/
├── agents/                    # AI agent implementations
│   ├── base.py               # Base agent framework & types
│   ├── orchestrator.py       # Multi-agent coordination
│   ├── deal_sourcing.py      # Deal sourcing agent
│   ├── research.py           # Research agent
│   ├── portfolio.py          # Portfolio management agent
│   └── investor_relations.py # IR/content agent
│
├── core/                      # Core business logic
│   ├── models.py             # Data models (Company, Deal, Investment)
│   ├── thesis.py             # Investment thesis & scoring
│   ├── portfolio.py          # Portfolio management
│   └── research_workflows.py # Automated research system
│
├── integrations/              # External integrations (planned)
│   ├── forge.py              # Forge Global
│   ├── equityzen.py          # EquityZen
│   └── carta.py              # Carta
│
├── utils/                     # Utilities
│   └── formatters.py         # Output formatting
│
└── cli.py                     # Command-line interface

scripts/
├── run_demo.py               # Demo script
└── scheduled_research.py     # Cron-based research refresh

data/
├── portfolio.json            # Portfolio state
└── research_history.json     # Research cache

content/
└── investor_letter_2026_01.md # Generated content

docs/                          # GitBook documentation
```

## Core Components

### Agent Framework

All agents inherit from the base `Agent` class:

```python
class Agent(ABC):
    role: AgentRole           # Agent's organizational role
    capabilities: dict        # Registered capabilities

    async def execute_task(task: AgentTask) -> AgentResult
```

### Agent Orchestrator

Coordinates multi-agent workflows:

```python
class AgentOrchestrator:
    def register_agent(agent: Agent)
    async def execute_task(task: AgentTask) -> AgentResult
    async def execute_workflow(workflow_id: str) -> dict
    async def run_daily_briefing() -> dict
```

### Data Models

Core entities in `epochal/core/models.py`:

| Model | Description |
|-------|-------------|
| `Company` | Tracked company with valuation, stage, investors |
| `Deal` | Investment opportunity with status and terms |
| `Investment` | Portfolio position with cost basis and returns |
| `Fund` | Fund vehicle with commitments and portfolio |
| `SPV` | Special purpose vehicle for single deals |

### Investment Thesis

Scoring engine in `epochal/core/thesis.py`:

```python
class InvestmentThesis:
    def score_company(company: Company) -> dict
    def get_thesis_summary() -> str
    def matches_thesis(company: Company) -> bool
```

## Data Flow

### Deal Sourcing Flow

```
Market Data → Deal Sourcing Agent → Thesis Scoring → Ranked Opportunities
                     │
                     ▼
              Research Agent → Comprehensive Analysis
                     │
                     ▼
              Portfolio Agent → Position Tracking
```

### Research Workflow

```
Trigger (manual/scheduled)
         │
         ▼
Generate Search Queries (funding, IPO, leadership, M&A)
         │
         ▼
Execute Research (web search, analysis)
         │
         ▼
Update Research History (data/research_history.json)
         │
         ▼
Available for Scoring & Reporting
```

### Content Generation Flow

```
Topic/Trigger → IR Agent → Template Selection → Content Draft
                    │
                    ▼
              Portfolio Context (metrics, positions)
                    │
                    ▼
              Formatted Output (Substack, LinkedIn, Twitter)
```
