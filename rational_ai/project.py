"""Unified project orchestrator — manages the full lifecycle."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console

from rational_ai.ai.providers import AIProvider
from rational_ai.config import Config
from rational_ai.exporters.html import export_project_html
from rational_ai.exporters.markdown import export_project_markdown
from rational_ai.exporters.mermaid import export_diagrams, generate_combined_html
from rational_ai.models.schema import PhaseStatus, Project
from rational_ai.phases import (
    architecture,
    deployment,
    development,
    requirements,
    roles,
    scheduling,
)

console = Console()


class ProjectOrchestrator:
    """Orchestrates the full software engineering lifecycle."""

    def __init__(self, config: Config):
        self.config = config
        self.ai = AIProvider(config.ai)
        self.project: Project | None = None

    # ── Project CRUD ──────────────────────────────────────────────────────────

    def init_project(self, name: str, description: str = "") -> Project:
        """Initialize a new project."""
        self.config.ensure_dirs()
        self.project = Project(name=name, description=description)
        self.save()
        console.print(f"[green]✓ Project '{name}' initialized in {self.config.rai_dir}[/]")
        return self.project

    def load(self) -> Project:
        """Load project from disk."""
        if not self.config.project_file.exists():
            raise FileNotFoundError(f"No project found at {self.config.project_file}")

        raw = yaml.safe_load(self.config.project_file.read_text(encoding="utf-8"))
        self.project = Project(**raw)
        return self.project

    def save(self) -> None:
        """Persist project state."""
        if not self.project:
            raise RuntimeError("No project loaded")

        self.project.updated_at = datetime.now()
        self.config.ensure_dirs()
        data = self.project.model_dump(mode="json")
        self.config.project_file.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    def _ensure_project(self) -> Project:
        if not self.project:
            self.load()
        assert self.project is not None
        return self.project

    # ── Phase Execution ──────────────────────────────────────────────────────

    def run_requirements(self, description: str = "", stakeholder_notes: str = "") -> None:
        """Execute the requirements phase."""
        proj = self._ensure_project()
        desc = description or proj.description
        proj.requirements = requirements.gather_requirements(self.ai, desc, stakeholder_notes)
        requirements.display_requirements(proj.requirements)
        requirements.save_requirements(proj.requirements, self.config.rai_dir)
        self.save()

    def run_roles(self) -> None:
        """Execute the roles/team phase."""
        proj = self._ensure_project()
        proj.roles = roles.recommend_team(self.ai, proj)
        roles.display_roles(proj.roles)
        roles.save_roles(proj.roles, self.config.rai_dir)
        self.save()

    def run_architecture(self) -> None:
        """Execute the architecture phase."""
        proj = self._ensure_project()
        proj.architecture = architecture.design_architecture(self.ai, proj)
        architecture.display_architecture(proj.architecture)
        architecture.save_architecture(proj.architecture, self.config.rai_dir)
        self.save()

    def review_architecture(self) -> str:
        """Run architecture review."""
        proj = self._ensure_project()
        review = architecture.review_architecture(self.ai, proj.architecture)
        architecture.save_architecture(proj.architecture, self.config.rai_dir)
        self.save()
        return review

    def run_development(self) -> None:
        """Execute the development planning phase."""
        proj = self._ensure_project()
        proj.development = development.plan_development(self.ai, proj)
        development.display_development(proj.development)
        development.save_development(proj.development, self.config.rai_dir)
        self.save()

    def run_deployment(self) -> None:
        """Execute the deployment planning phase."""
        proj = self._ensure_project()
        proj.deployment = deployment.plan_deployment(self.ai, proj)
        deployment.display_deployment(proj.deployment)
        deployment.save_deployment(proj.deployment, self.config.rai_dir)
        self.save()

    def run_schedule(self) -> None:
        """Execute the scheduling phase."""
        proj = self._ensure_project()
        proj.schedule = scheduling.generate_schedule(self.ai, proj)
        scheduling.display_schedule(proj.schedule)
        scheduling.save_schedule(proj.schedule, self.config.rai_dir)
        self.save()

    def run_all(self, description: str = "", stakeholder_notes: str = "") -> None:
        """Run all phases sequentially."""
        console.print("[bold]═══ RATIONAL AI — Full Lifecycle ═══[/]\n")

        console.print("\n[bold yellow]Phase 1/6: Requirements[/]")
        self.run_requirements(description, stakeholder_notes)

        console.print("\n[bold yellow]Phase 2/6: Team & Roles[/]")
        self.run_roles()

        console.print("\n[bold yellow]Phase 3/6: Architecture[/]")
        self.run_architecture()

        console.print("\n[bold yellow]Phase 4/6: Development Planning[/]")
        self.run_development()

        console.print("\n[bold yellow]Phase 5/6: Deployment Planning[/]")
        self.run_deployment()

        console.print("\n[bold yellow]Phase 6/6: Scheduling[/]")
        self.run_schedule()

        console.print("\n[bold green]═══ All phases complete ═══[/]")

    # ── Scaffold Code ─────────────────────────────────────────────────────────

    def scaffold(self, component_id: str) -> str:
        """Generate code scaffold for a component."""
        proj = self._ensure_project()
        return development.scaffold_code(self.ai, proj, component_id)

    # ── Export ────────────────────────────────────────────────────────────────

    def export_markdown(self, output_dir: Path | None = None) -> Path:
        proj = self._ensure_project()
        out = output_dir or (self.config.rai_dir / "exports")
        path = export_project_markdown(proj, out)
        console.print(f"[green]✓ Markdown report: {path}[/]")
        return path

    def export_html(self, output_dir: Path | None = None) -> Path:
        proj = self._ensure_project()
        out = output_dir or (self.config.rai_dir / "exports")
        path = export_project_html(proj, out)
        console.print(f"[green]✓ HTML report: {path}[/]")
        return path

    def export_diagrams(self, output_dir: Path | None = None) -> list[Path]:
        proj = self._ensure_project()
        out = output_dir or (self.config.rai_dir / "exports" / "diagrams")
        paths = export_diagrams(proj.architecture, out)
        html = generate_combined_html(proj.architecture, out / "diagrams.html")
        paths.append(html)
        console.print(f"[green]✓ Exported {len(paths)} diagram files to {out}[/]")
        return paths

    # ── Status ───────────────────────────────────────────────────────────────

    def status(self) -> dict[str, str]:
        """Get status of all phases."""
        proj = self._ensure_project()
        return {
            "Requirements": proj.requirements.status.value,
            "Roles": "configured" if proj.roles.members else "not_started",
            "Architecture": proj.architecture.status.value,
            "Development": proj.development.status.value,
            "Deployment": proj.deployment.status.value,
            "Schedule": proj.schedule.status.value,
        }
