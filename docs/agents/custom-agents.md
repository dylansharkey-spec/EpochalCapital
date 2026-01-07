# Creating Custom Agents

## Overview

Extend the platform by creating custom agents for new functions.

## Step 1: Define the Agent

```python
from epochal.agents.base import Agent, AgentRole, AgentTask, AgentResult, TaskStatus
from datetime import datetime

class CustomAgent(Agent):
    def __init__(self):
        super().__init__(
            role=AgentRole.CUSTOM,  # Add to AgentRole enum first
            name="Custom Agent",
            description="Description of what this agent does",
        )

    def _register_capabilities(self):
        self.register_capability(
            name="custom_action",
            description="What this capability does",
            handler=self._custom_handler,
            required_inputs=["input_param"],
        )

    async def execute_task(self, task: AgentTask) -> AgentResult:
        start_time = datetime.utcnow()
        task.status = TaskStatus.IN_PROGRESS

        try:
            capability = task.input_data.get("capability")
            if capability == "custom_action":
                result = await self._custom_handler(**task.input_data)
            else:
                raise ValueError(f"Unknown capability: {capability}")

            self.tasks_completed += 1
            return AgentResult(
                task_id=task.id,
                success=True,
                data=result,
                execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )
        except Exception as e:
            self.tasks_failed += 1
            return AgentResult(
                task_id=task.id,
                success=False,
                error=str(e),
            )

    async def _custom_handler(self, input_param: str, **kwargs) -> dict:
        # Implementation
        return {"result": f"Processed {input_param}"}
```

## Step 2: Add Agent Role

In `epochal/agents/base.py`:

```python
class AgentRole(Enum):
    # ... existing roles
    CUSTOM = "custom"
```

## Step 3: Register with Orchestrator

In `epochal/cli.py`:

```python
from epochal.agents.custom import CustomAgent

# In EpochalCLI.__init__
self.custom_agent = CustomAgent()
self.orchestrator.register_agent(self.custom_agent)
```

## Step 4: Add CLI Commands

```python
# In get_commands()
"custom <param>": "Run custom action"

# In main() command handling
elif command == "custom":
    param = parts[1] if len(parts) > 1 else "default"
    await cli.run_custom(param)
```

## Step 5: Export Agent

In `epochal/agents/__init__.py`:

```python
from epochal.agents.custom import CustomAgent

__all__ = [
    # ... existing
    "CustomAgent",
]
```

## Example: Risk Manager Agent

```python
class RiskManagerAgent(Agent):
    def __init__(self, portfolio: Portfolio):
        super().__init__(
            role=AgentRole.RISK_MANAGER,
            name="Risk Manager Agent",
            description="Portfolio risk analysis and monitoring",
        )
        self.portfolio = portfolio

    def _register_capabilities(self):
        self.register_capability(
            name="concentration_analysis",
            description="Analyze portfolio concentration risk",
            handler=self._analyze_concentration,
        )
        self.register_capability(
            name="liquidity_risk",
            description="Assess liquidity risk across positions",
            handler=self._assess_liquidity_risk,
        )

    async def _analyze_concentration(self) -> dict:
        positions = self.portfolio.get_positions()
        # Calculate concentration metrics
        return {
            "top_position_pct": 45.2,
            "top_3_pct": 78.5,
            "sector_concentration": {...},
            "risk_score": 65,
        }
```
