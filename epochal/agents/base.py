"""
Base agent framework for Epochal Capital.

Defines the core Agent class and supporting types that all
specialized agents inherit from.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class AgentRole(Enum):
    """Roles that agents can fulfill in the organization."""
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


class TaskPriority(Enum):
    """Priority levels for agent tasks."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Status of an agent task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """
    Represents a task to be executed by an agent.

    Attributes:
        id: Unique task identifier
        name: Human-readable task name
        description: Detailed task description
        agent_role: Which agent role should handle this
        priority: Task priority
        status: Current status
        input_data: Input data for the task
        output_data: Output data from the task
        dependencies: List of task IDs this depends on
        created_at: When task was created
        started_at: When task started execution
        completed_at: When task completed
        error: Error message if failed
        metadata: Additional metadata
    """
    name: str
    description: str
    agent_role: AgentRole
    id: str = field(default_factory=lambda: str(uuid4()))
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_role": self.agent_role.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """Result from an agent task execution."""
    task_id: str
    success: bool
    data: dict = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    follow_up_tasks: list[AgentTask] = field(default_factory=list)


@dataclass
class AgentCapability:
    """Defines a capability that an agent has."""
    name: str
    description: str
    handler: Callable
    required_inputs: list[str] = field(default_factory=list)
    output_schema: dict = field(default_factory=dict)


class Agent(ABC):
    """
    Base class for all Epochal Capital agents.

    Each agent has:
    - A specific role in the organization
    - A set of capabilities (actions it can perform)
    - Access to shared portfolio data
    - Ability to communicate with other agents via orchestrator
    """

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
        self.capabilities: dict[str, AgentCapability] = {}
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.tasks_completed = 0
        self.tasks_failed = 0

        # Register capabilities
        self._register_capabilities()

    @abstractmethod
    def _register_capabilities(self):
        """Register this agent's capabilities. Override in subclasses."""
        pass

    def register_capability(
        self,
        name: str,
        description: str,
        handler: Callable,
        required_inputs: list[str] = None,
    ):
        """Register a capability for this agent."""
        self.capabilities[name] = AgentCapability(
            name=name,
            description=description,
            handler=handler,
            required_inputs=required_inputs or [],
        )

    def get_capabilities(self) -> list[str]:
        """Get list of capability names."""
        return list(self.capabilities.keys())

    def can_handle(self, task: AgentTask) -> bool:
        """Check if this agent can handle a task."""
        return task.agent_role == self.role

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a task. Override in subclasses.

        Args:
            task: The task to execute

        Returns:
            AgentResult with task outcome
        """
        pass

    async def execute_capability(
        self,
        capability_name: str,
        **kwargs,
    ) -> Any:
        """Execute a specific capability."""
        if capability_name not in self.capabilities:
            raise ValueError(f"Unknown capability: {capability_name}")

        capability = self.capabilities[capability_name]

        # Validate required inputs
        for req_input in capability.required_inputs:
            if req_input not in kwargs:
                raise ValueError(f"Missing required input: {req_input}")

        # Execute handler
        return await capability.handler(**kwargs)

    def get_status(self) -> dict:
        """Get agent status information."""
        return {
            "id": self.id,
            "role": self.role.value,
            "name": self.name,
            "is_active": self.is_active,
            "capabilities": list(self.capabilities.keys()),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }

    def __repr__(self) -> str:
        return f"Agent({self.role.value}: {self.name})"
