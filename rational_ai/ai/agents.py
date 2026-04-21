"""AI agents — specialized per-phase assistants for the software lifecycle."""

from __future__ import annotations

import json
from typing import Any

from rational_ai.ai import prompts
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import (
    ArchComponent,
    ArchDecision,
    ArchitecturePackage,
    DeploymentPackage,
    DeploymentStep,
    DevTask,
    DevelopmentPackage,
    Environment,
    Milestone,
    PhaseStatus,
    Project,
    Requirement,
    RequirementsPackage,
    RolesPackage,
    SchedulePackage,
    Sprint,
    TeamMember,
    UseCase,
)


class RequirementsAgent:
    """AI agent for requirements gathering and analysis."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def extract_requirements(self, description: str) -> RequirementsPackage:
        data = self.ai.chat_json(prompts.REQUIREMENTS_EXTRACT, description)
        reqs = [Requirement(**r) for r in data.get("requirements", [])]
        return RequirementsPackage(requirements=reqs, status=PhaseStatus.IN_PROGRESS)

    def generate_use_cases(self, package: RequirementsPackage) -> list[UseCase]:
        req_text = "\n".join(
            f"- {r.id}: {r.title} — {r.description}" for r in package.requirements
        )
        data = self.ai.chat_json(prompts.USE_CASE_GENERATE, req_text)
        return [UseCase(**uc) for uc in data.get("use_cases", [])]

    def analyze_requirements(self, package: RequirementsPackage) -> str:
        req_text = json.dumps([r.model_dump() for r in package.requirements], indent=2)
        resp = self.ai.chat(prompts.REQUIREMENTS_ANALYZE, req_text)
        return resp.content


class RolesAgent:
    """AI agent for team composition and role assignment."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def recommend_roles(self, project: Project) -> RolesPackage:
        context = json.dumps(
            {
                "project": project.name,
                "description": project.description,
                "requirements_count": len(project.requirements.requirements),
                "components": [c.model_dump() for c in project.architecture.components],
            },
            indent=2,
        )
        data = self.ai.chat_json(prompts.ROLES_RECOMMEND, context)
        members = []
        for i, r in enumerate(data.get("roles", []), start=1):
            members.append(
                TeamMember(
                    id=f"TM-{i:03d}",
                    name=f"{r.get('role', 'member').replace('_', ' ').title()} {i}",
                    role=r.get("role", "developer"),
                    skills=r.get("skills", []),
                    assigned_components=r.get("assigned_components", []),
                )
            )
        return RolesPackage(
            members=members,
            raci_matrix=data.get("raci_matrix", {}),
            ai_recommendations=json.dumps(data.get("roles", []), indent=2),
        )


class ArchitectureAgent:
    """AI agent for system architecture design."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def design_architecture(self, project: Project) -> ArchitecturePackage:
        context = json.dumps(
            {
                "project": project.name,
                "description": project.description,
                "requirements": [r.model_dump() for r in project.requirements.requirements],
            },
            indent=2,
        )
        data = self.ai.chat_json(prompts.ARCHITECTURE_DESIGN, context)

        components = [ArchComponent(**c) for c in data.get("components", [])]
        decisions = [ArchDecision(**d) for d in data.get("decisions", [])]
        tech_stack = data.get("tech_stack", {})

        pkg = ArchitecturePackage(
            components=components,
            decisions=decisions,
            tech_stack=tech_stack,
            status=PhaseStatus.IN_PROGRESS,
        )

        # Generate diagrams from descriptions
        for desc in data.get("diagram_descriptions", []):
            if isinstance(desc, dict):
                dtype = desc.get("type", "flowchart")
                text = desc.get("description", "")
            else:
                dtype, text = "flowchart", str(desc)
            mermaid = self.ai.generate_mermaid(text, dtype)
            from rational_ai.models.schema import ArchDiagram, DiagramType

            pkg.diagrams.append(
                ArchDiagram(
                    id=f"DIA-{len(pkg.diagrams) + 1:03d}",
                    title=f"{dtype} diagram",
                    type=getattr(DiagramType, dtype.upper(), DiagramType.FLOWCHART),
                    mermaid_code=mermaid,
                    description=text,
                )
            )

        return pkg

    def review_architecture(self, package: ArchitecturePackage) -> str:
        arch_text = json.dumps(
            {
                "components": [c.model_dump() for c in package.components],
                "tech_stack": package.tech_stack,
                "decisions": [d.model_dump() for d in package.decisions],
            },
            indent=2,
        )
        resp = self.ai.chat(prompts.ARCHITECTURE_REVIEW, arch_text)
        return resp.content


class DevelopmentAgent:
    """AI agent for development task planning and code scaffolding."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def generate_tasks(self, project: Project) -> DevelopmentPackage:
        context = json.dumps(
            {
                "components": [c.model_dump() for c in project.architecture.components],
                "requirements": [r.model_dump() for r in project.requirements.requirements],
                "tech_stack": project.architecture.tech_stack,
            },
            indent=2,
        )
        data = self.ai.chat_json(prompts.DEV_TASKS_GENERATE, context)
        tasks = [DevTask(**t) for t in data.get("tasks", [])]
        return DevelopmentPackage(
            tasks=tasks,
            coding_standards=data.get("coding_standards", ""),
            branching_strategy=data.get("branching_strategy", ""),
            status=PhaseStatus.IN_PROGRESS,
        )

    def scaffold_component(self, component: ArchComponent, tech_stack: dict) -> str:
        context = json.dumps(
            {"component": component.model_dump(), "tech_stack": tech_stack}, indent=2
        )
        resp = self.ai.chat(prompts.CODE_SCAFFOLD, context)
        return resp.content


class DeploymentAgent:
    """AI agent for deployment planning."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def plan_deployment(self, project: Project) -> DeploymentPackage:
        context = json.dumps(
            {
                "components": [c.model_dump() for c in project.architecture.components],
                "tech_stack": project.architecture.tech_stack,
                "team_size": len(project.roles.members),
            },
            indent=2,
        )
        data = self.ai.chat_json(prompts.DEPLOYMENT_PLAN, context)

        environments = [Environment(**e) for e in data.get("environments", [])]
        steps = [DeploymentStep(**s) for s in data.get("pipeline_steps", [])]

        return DeploymentPackage(
            environments=environments,
            pipeline_steps=steps,
            infrastructure_as_code=data.get("infrastructure", ""),
            monitoring=data.get("monitoring", {}),
            ai_suggestions=json.dumps(data.get("security_checklist", []), indent=2),
            status=PhaseStatus.IN_PROGRESS,
        )


class ScheduleAgent:
    """AI agent for project scheduling."""

    def __init__(self, ai: AIProvider):
        self.ai = ai

    def generate_schedule(self, project: Project) -> SchedulePackage:
        context = json.dumps(
            {
                "tasks": [t.model_dump() for t in project.development.tasks],
                "team": [m.model_dump() for m in project.roles.members],
                "milestones_hint": [
                    m.model_dump() for m in project.schedule.milestones
                ],
            },
            indent=2,
            default=str,
        )
        data = self.ai.chat_json(prompts.SCHEDULE_GENERATE, context)

        milestones = []
        for m in data.get("milestones", []):
            m.pop("target_date", None)  # avoid date parse issues from LLM
            milestones.append(Milestone(**m))

        sprints = []
        for s in data.get("sprints", []):
            s.pop("start_date", None)
            s.pop("end_date", None)
            sprints.append(Sprint(**s))

        return SchedulePackage(
            milestones=milestones,
            sprints=sprints,
            estimated_duration_weeks=data.get("estimated_duration_weeks", 0),
            ai_schedule=json.dumps(
                {"critical_path": data.get("critical_path", []), "risks": data.get("risks", [])},
                indent=2,
            ),
            status=PhaseStatus.IN_PROGRESS,
        )
