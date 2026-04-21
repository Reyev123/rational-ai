"""Pydantic data models for all Rational AI artifacts."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enumerations ──────────────────────────────────────────────────────────────

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementType(str, Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    INTERFACE = "interface"


class PhaseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"


class RoleType(str, Enum):
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS = "devops"
    DESIGNER = "designer"
    STAKEHOLDER = "stakeholder"
    DATA_ENGINEER = "data_engineer"
    SECURITY = "security"


class DiagramType(str, Enum):
    CLASS = "class"
    SEQUENCE = "sequence"
    COMPONENT = "component"
    DEPLOYMENT = "deployment"
    USE_CASE = "use_case"
    ACTIVITY = "activity"
    STATE = "state"
    ER = "er"
    FLOWCHART = "flowchart"
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


# ── Requirements ──────────────────────────────────────────────────────────────

class Requirement(BaseModel):
    id: str = Field(..., description="Unique requirement ID, e.g. REQ-001")
    title: str
    description: str
    type: RequirementType = RequirementType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    acceptance_criteria: list[str] = Field(default_factory=list)
    source: str = ""  # stakeholder, interview, document, etc.
    depends_on: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    ai_analysis: str = ""  # AI-generated analysis/suggestions


class UseCase(BaseModel):
    id: str = Field(..., description="Unique use case ID, e.g. UC-001")
    title: str
    actor: str
    preconditions: list[str] = Field(default_factory=list)
    main_flow: list[str] = Field(default_factory=list)
    alternative_flows: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    related_requirements: list[str] = Field(default_factory=list)


class RequirementsPackage(BaseModel):
    requirements: list[Requirement] = Field(default_factory=list)
    use_cases: list[UseCase] = Field(default_factory=list)
    stakeholder_notes: str = ""
    ai_summary: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED


# ── Roles & Team ──────────────────────────────────────────────────────────────

class TeamMember(BaseModel):
    id: str
    name: str
    role: RoleType
    email: str = ""
    skills: list[str] = Field(default_factory=list)
    availability: float = 1.0  # 0.0 to 1.0 (fraction of full-time)
    assigned_components: list[str] = Field(default_factory=list)


class RolesPackage(BaseModel):
    members: list[TeamMember] = Field(default_factory=list)
    raci_matrix: dict[str, dict[str, str]] = Field(default_factory=dict)
    ai_recommendations: str = ""


# ── Architecture ──────────────────────────────────────────────────────────────

class ArchComponent(BaseModel):
    id: str
    name: str
    type: str  # service, library, database, queue, gateway, etc.
    description: str = ""
    technology: str = ""
    interfaces: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ArchDiagram(BaseModel):
    id: str
    title: str
    type: DiagramType
    mermaid_code: str = ""
    description: str = ""


class ArchDecision(BaseModel):
    id: str = Field(..., description="ADR-001 etc.")
    title: str
    context: str
    decision: str
    consequences: str = ""
    status: str = "proposed"  # proposed | accepted | deprecated | superseded
    date: str = ""


class ArchitecturePackage(BaseModel):
    components: list[ArchComponent] = Field(default_factory=list)
    diagrams: list[ArchDiagram] = Field(default_factory=list)
    decisions: list[ArchDecision] = Field(default_factory=list)
    tech_stack: dict[str, str] = Field(default_factory=dict)
    ai_analysis: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED


# ── Development ───────────────────────────────────────────────────────────────

class DevTask(BaseModel):
    id: str
    title: str
    description: str = ""
    component: str = ""
    assigned_to: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    priority: Priority = Priority.MEDIUM
    estimated_hours: float = 0
    requirements: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CodeModule(BaseModel):
    name: str
    path: str
    language: str = ""
    description: str = ""
    ai_generated: bool = False


class DevelopmentPackage(BaseModel):
    tasks: list[DevTask] = Field(default_factory=list)
    modules: list[CodeModule] = Field(default_factory=list)
    coding_standards: str = ""
    branching_strategy: str = ""
    ai_suggestions: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED


# ── Deployment ────────────────────────────────────────────────────────────────

class Environment(BaseModel):
    name: str  # dev, staging, production
    type: str  # kubernetes, docker-compose, vm, serverless, bare-metal
    config: dict[str, Any] = Field(default_factory=dict)
    url: str = ""


class DeploymentStep(BaseModel):
    order: int
    name: str
    description: str = ""
    command: str = ""
    environment: str = ""


class DeploymentPackage(BaseModel):
    environments: list[Environment] = Field(default_factory=list)
    pipeline_steps: list[DeploymentStep] = Field(default_factory=list)
    infrastructure_as_code: str = ""  # terraform, pulumi, etc.
    monitoring: dict[str, str] = Field(default_factory=dict)
    ai_suggestions: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED


# ── Scheduling ────────────────────────────────────────────────────────────────

class Milestone(BaseModel):
    id: str
    name: str
    target_date: date | None = None
    deliverables: list[str] = Field(default_factory=list)
    status: PhaseStatus = PhaseStatus.NOT_STARTED


class Sprint(BaseModel):
    id: str
    name: str
    start_date: date | None = None
    end_date: date | None = None
    tasks: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)


class SchedulePackage(BaseModel):
    milestones: list[Milestone] = Field(default_factory=list)
    sprints: list[Sprint] = Field(default_factory=list)
    estimated_duration_weeks: int = 0
    ai_schedule: str = ""
    status: PhaseStatus = PhaseStatus.NOT_STARTED


# ── Unified Project ──────────────────────────────────────────────────────────

class Project(BaseModel):
    name: str
    description: str = ""
    version: str = "0.1.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    requirements: RequirementsPackage = Field(default_factory=RequirementsPackage)
    roles: RolesPackage = Field(default_factory=RolesPackage)
    architecture: ArchitecturePackage = Field(default_factory=ArchitecturePackage)
    development: DevelopmentPackage = Field(default_factory=DevelopmentPackage)
    deployment: DeploymentPackage = Field(default_factory=DeploymentPackage)
    schedule: SchedulePackage = Field(default_factory=SchedulePackage)
    metadata: dict[str, Any] = Field(default_factory=dict)
