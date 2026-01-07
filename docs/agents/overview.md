# Agent Framework

## Overview

Epochal Capital uses a multi-agent architecture where specialized AI agents handle different aspects of the investment process. Agents can work independently or coordinate through the orchestrator.

## Agent Roles

```python
class AgentRole(Enum):
    CIO = "chief_investment_officer"
    CHIEF_OF_STAFF = "chief_of_staff"
    DEAL_SOURCING = "deal_sourcing"
    RESEARCH_ANALYST = "research_analyst"
    DUE_DILIGENCE = "due_diligence"
    PORTFOLIO_MANAGER = "portfolio_manager"
    RISK_MANAGER = "risk_manager"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    INVESTOR_RELATIONS = "investor_relations"
    MARKET_INTELLIGENCE = "market_intelligence"
```

## Current Agents

| Agent | Role | Status | Description |
|-------|------|--------|-------------|
| Deal Sourcing | `DEAL_SOURCING` | ✅ Active | Market scanning, company evaluation, liquidity detection |
| Research | `RESEARCH_ANALYST` | ✅ Active | Company research, market analysis |
| Portfolio | `PORTFOLIO_MANAGER` | ✅ Active | Position tracking, performance reporting |
| Investor Relations | `INVESTOR_RELATIONS` | ✅ Active | Content generation, LP communications |
| Risk Manager | `RISK_MANAGER` | 🔜 Planned | Portfolio risk, concentration analysis |
| Compliance | `COMPLIANCE` | 🔜 Planned | Regulatory checks, documentation |

## Base Agent Class

All agents inherit from the abstract `Agent` class:

```python
class Agent(ABC):
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
    ):
        self.id = str(uuid4())
        self.role = role
        self.name = name
        self.description = description
        self.capabilities = {}
        self.is_active = True
        self.tasks_completed = 0
        self.tasks_failed = 0
        self._register_capabilities()

    @abstractmethod
    def _register_capabilities(self):
        """Register agent capabilities."""
        pass

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a task."""
        pass
```

## Capabilities

Agents expose functionality through registered capabilities:

```python
def _register_capabilities(self):
    self.register_capability(
        name="scan_market",
        description="Scan market for opportunities",
        handler=self._scan_market,
        required_inputs=["vertical"],
    )
```

## Task Execution

Tasks are structured units of work:

```python
@dataclass
class AgentTask:
    name: str
    description: str
    agent_role: AgentRole
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    input_data: dict = field(default_factory=dict)
```

Results are returned uniformly:

```python
@dataclass
class AgentResult:
    task_id: str
    success: bool
    data: dict
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
```

## Agent Orchestrator

The orchestrator coordinates multi-agent workflows:

```python
orchestrator = AgentOrchestrator(portfolio=portfolio)

# Register agents
orchestrator.register_agent(DealSourcingAgent())
orchestrator.register_agent(ResearchAgent())
orchestrator.register_agent(PortfolioAgent(portfolio))
orchestrator.register_agent(InvestorRelationsAgent(portfolio))

# Execute task
task = AgentTask(
    name="Scan Market",
    description="Find opportunities",
    agent_role=AgentRole.DEAL_SOURCING,
    input_data={"capability": "scan_market"},
)
result = await orchestrator.execute_task(task)
```

## Workflow Execution

Multi-step workflows can chain agent tasks:

```python
workflow = orchestrator.create_workflow(
    name="Due Diligence",
    steps=[
        {"agent_role": "deal_sourcing", "input_data": {"capability": "evaluate_company"}},
        {"agent_role": "research_analyst", "input_data": {"capability": "research"}, "depends_on": ["step_1"]},
    ]
)
await orchestrator.execute_workflow(workflow.id)
```

## Daily Briefing

The orchestrator provides a built-in daily briefing:

```python
briefing = await orchestrator.run_daily_briefing()
# Returns aggregated insights from all agents
```
