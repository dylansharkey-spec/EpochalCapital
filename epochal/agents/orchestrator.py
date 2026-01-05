"""
Agent Orchestrator for Epochal Capital.

Coordinates multiple AI agents to work together on complex tasks.
Manages task queues, dependencies, and agent communication.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from epochal.agents.base import (
    Agent,
    AgentRole,
    AgentTask,
    AgentResult,
    TaskPriority,
    TaskStatus,
)
from epochal.core.portfolio import Portfolio


@dataclass
class WorkflowStep:
    """A step in a multi-agent workflow."""
    task: AgentTask
    agent_role: AgentRole
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    """A multi-step workflow coordinating multiple agents."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    results: dict = field(default_factory=dict)


class AgentOrchestrator:
    """
    Coordinates multiple AI agents for Epochal Capital.

    Features:
    - Agent registration and management
    - Task queue management
    - Workflow orchestration
    - Inter-agent communication
    - Result aggregation
    """

    def __init__(self, portfolio: Optional[Portfolio] = None):
        self.agents: dict[AgentRole, Agent] = {}
        self.task_queue: list[AgentTask] = []
        self.completed_tasks: dict[str, AgentResult] = {}
        self.workflows: dict[str, Workflow] = {}
        self.portfolio = portfolio or Portfolio()
        self.is_running = False

    def register_agent(self, agent: Agent):
        """Register an agent with the orchestrator."""
        self.agents[agent.role] = agent

    def get_agent(self, role: AgentRole) -> Optional[Agent]:
        """Get an agent by role."""
        return self.agents.get(role)

    def list_agents(self) -> list[dict]:
        """List all registered agents and their status."""
        return [agent.get_status() for agent in self.agents.values()]

    def create_task(
        self,
        name: str,
        description: str,
        agent_role: AgentRole,
        priority: TaskPriority = TaskPriority.MEDIUM,
        input_data: Optional[dict] = None,
        dependencies: Optional[list[str]] = None,
    ) -> AgentTask:
        """Create a new task."""
        task = AgentTask(
            name=name,
            description=description,
            agent_role=agent_role,
            priority=priority,
            input_data=input_data or {},
            dependencies=dependencies or [],
        )
        return task

    def queue_task(self, task: AgentTask):
        """Add a task to the queue."""
        self.task_queue.append(task)
        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority.value)

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a single task."""
        agent = self.get_agent(task.agent_role)

        if not agent:
            return AgentResult(
                task_id=task.id,
                success=False,
                error=f"No agent registered for role: {task.agent_role.value}",
            )

        # Check dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return AgentResult(
                    task_id=task.id,
                    success=False,
                    error=f"Dependency not met: {dep_id}",
                )

        # Execute task
        result = await agent.execute_task(task)

        # Store result
        self.completed_tasks[task.id] = result
        task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        task.output_data = result.data

        return result

    async def run_queue(self) -> list[AgentResult]:
        """Process all tasks in the queue."""
        self.is_running = True
        results = []

        while self.task_queue:
            task = self.task_queue.pop(0)
            result = await self.execute_task(task)
            results.append(result)

        self.is_running = False
        return results

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict],
    ) -> Workflow:
        """
        Create a multi-agent workflow.

        Args:
            name: Workflow name
            description: What this workflow does
            steps: List of step definitions with:
                - name: Step name
                - agent_role: Which agent handles this
                - input_data: Input for the task
                - depends_on: List of step names this depends on
        """
        workflow = Workflow(name=name, description=description)
        step_id_map = {}

        for step_def in steps:
            task = self.create_task(
                name=step_def["name"],
                description=step_def.get("description", ""),
                agent_role=AgentRole(step_def["agent_role"]),
                input_data=step_def.get("input_data", {}),
            )

            # Resolve dependencies
            depends_on = []
            for dep_name in step_def.get("depends_on", []):
                if dep_name in step_id_map:
                    depends_on.append(step_id_map[dep_name])

            task.dependencies = depends_on
            step_id_map[step_def["name"]] = task.id

            workflow.steps.append(WorkflowStep(
                task=task,
                agent_role=task.agent_role,
                depends_on=depends_on,
            ))

        self.workflows[workflow.id] = workflow
        return workflow

    async def execute_workflow(self, workflow_id: str) -> dict:
        """Execute a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow not found: {workflow_id}"}

        workflow.status = "running"
        results = {}

        # Execute steps respecting dependencies
        pending_steps = list(workflow.steps)
        completed_step_ids = set()

        while pending_steps:
            # Find steps with satisfied dependencies
            ready_steps = [
                step for step in pending_steps
                if all(dep in completed_step_ids for dep in step.depends_on)
            ]

            if not ready_steps:
                # Deadlock or all done
                break

            # Execute ready steps (could be parallelized)
            for step in ready_steps:
                result = await self.execute_task(step.task)
                results[step.task.name] = result.data if result.success else {"error": result.error}
                completed_step_ids.add(step.task.id)
                pending_steps.remove(step)

        workflow.status = "completed" if not pending_steps else "failed"
        workflow.completed_at = datetime.utcnow()
        workflow.results = results

        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "results": results,
        }

    # Pre-built workflows for common operations

    def create_sourcing_workflow(self) -> Workflow:
        """Create a workflow for deal sourcing."""
        return self.create_workflow(
            name="Deal Sourcing Workflow",
            description="Scan market, identify opportunities, and score against thesis",
            steps=[
                {
                    "name": "market_scan",
                    "agent_role": "deal_sourcing",
                    "description": "Scan market for AI companies",
                    "input_data": {"capability": "scan_market"},
                },
                {
                    "name": "liquidity_analysis",
                    "agent_role": "deal_sourcing",
                    "description": "Find companies with liquidity events",
                    "input_data": {"capability": "find_liquidity_events"},
                    "depends_on": ["market_scan"],
                },
                {
                    "name": "generate_opportunities",
                    "agent_role": "deal_sourcing",
                    "description": "Generate opportunity list",
                    "input_data": {"capability": "generate_opportunities"},
                    "depends_on": ["liquidity_analysis"],
                },
            ],
        )

    def create_due_diligence_workflow(self, company_name: str) -> Workflow:
        """Create a workflow for due diligence on a company."""
        return self.create_workflow(
            name=f"Due Diligence: {company_name}",
            description=f"Comprehensive due diligence on {company_name}",
            steps=[
                {
                    "name": "company_research",
                    "agent_role": "research_analyst",
                    "description": f"Research {company_name}",
                    "input_data": {
                        "capability": "research_company",
                        "company_name": company_name,
                    },
                },
                {
                    "name": "company_evaluation",
                    "agent_role": "deal_sourcing",
                    "description": f"Evaluate {company_name} against thesis",
                    "input_data": {
                        "capability": "evaluate_company",
                        "company_name": company_name,
                    },
                    "depends_on": ["company_research"],
                },
            ],
        )

    def create_portfolio_review_workflow(self) -> Workflow:
        """Create a workflow for portfolio review."""
        return self.create_workflow(
            name="Portfolio Review Workflow",
            description="Comprehensive portfolio review and recommendations",
            steps=[
                {
                    "name": "portfolio_summary",
                    "agent_role": "portfolio_manager",
                    "description": "Generate portfolio summary",
                    "input_data": {"capability": "portfolio_summary"},
                },
                {
                    "name": "risk_analysis",
                    "agent_role": "portfolio_manager",
                    "description": "Analyze portfolio risks",
                    "input_data": {"capability": "risk_analysis"},
                    "depends_on": ["portfolio_summary"],
                },
                {
                    "name": "pipeline_status",
                    "agent_role": "portfolio_manager",
                    "description": "Review deal pipeline",
                    "input_data": {"capability": "pipeline_status"},
                },
                {
                    "name": "recommendations",
                    "agent_role": "portfolio_manager",
                    "description": "Generate recommendations",
                    "input_data": {"capability": "recommendations"},
                    "depends_on": ["risk_analysis", "pipeline_status"],
                },
            ],
        )

    async def run_daily_briefing(self) -> dict:
        """Run a daily briefing workflow combining all agents."""
        briefing = {
            "date": datetime.utcnow().isoformat(),
            "sections": {},
        }

        # Run sourcing workflow
        sourcing_workflow = self.create_sourcing_workflow()
        sourcing_result = await self.execute_workflow(sourcing_workflow.id)
        briefing["sections"]["deal_sourcing"] = sourcing_result

        # Run portfolio review
        portfolio_workflow = self.create_portfolio_review_workflow()
        portfolio_result = await self.execute_workflow(portfolio_workflow.id)
        briefing["sections"]["portfolio_review"] = portfolio_result

        # Generate research report
        research_agent = self.get_agent(AgentRole.RESEARCH_ANALYST)
        if research_agent:
            research_task = self.create_task(
                name="Generate Research Report",
                description="Generate market research report",
                agent_role=AgentRole.RESEARCH_ANALYST,
                input_data={"capability": "generate_research_report"},
            )
            research_result = await self.execute_task(research_task)
            briefing["sections"]["research"] = research_result.data

        return briefing

    def get_orchestrator_status(self) -> dict:
        """Get orchestrator status."""
        return {
            "is_running": self.is_running,
            "registered_agents": len(self.agents),
            "agents": self.list_agents(),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "workflows": len(self.workflows),
        }
