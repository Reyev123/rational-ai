"""Development planning and code scaffolding phase."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from rational_ai.ai.agents import DevelopmentAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import (
    DevelopmentPackage,
    PhaseStatus,
    Project,
)

console = Console()


def plan_development(ai: AIProvider, project: Project) -> DevelopmentPackage:
    """AI-driven development task breakdown."""
    agent = DevelopmentAgent(ai)

    console.print("[bold blue]⚙️  Generating development tasks with AI...[/]")
    package = agent.generate_tasks(project)
    console.print(f"[green]✓ Generated {len(package.tasks)} development tasks[/]")

    return package


def scaffold_code(ai: AIProvider, project: Project, component_id: str) -> str:
    """Generate code scaffold for a specific component."""
    agent = DevelopmentAgent(ai)

    comp = next((c for c in project.architecture.components if c.id == component_id), None)
    if not comp:
        console.print(f"[red]Component {component_id} not found[/]")
        return ""

    console.print(f"[bold blue]🔨 Scaffolding code for {comp.name}...[/]")
    scaffold = agent.scaffold_component(comp, project.architecture.tech_stack)
    console.print("[green]✓ Code scaffold generated[/]")

    return scaffold


def display_development(package: DevelopmentPackage) -> None:
    """Display development tasks."""
    table = Table(title="Development Tasks", show_lines=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Title", style="bold")
    table.add_column("Component", style="magenta")
    table.add_column("Priority", style="yellow")
    table.add_column("Est. Hours", justify="right")
    table.add_column("Status", style="green")

    for t in package.tasks:
        table.add_row(
            t.id, t.title, t.component, t.priority.value,
            str(t.estimated_hours), t.status.value,
        )
    console.print(table)

    if package.coding_standards:
        console.print(f"\n[bold]Coding Standards:[/]\n{package.coding_standards}")
    if package.branching_strategy:
        console.print(f"\n[bold]Branching Strategy:[/]\n{package.branching_strategy}")


def save_development(package: DevelopmentPackage, rai_dir: Path) -> None:
    out_dir = rai_dir / "development"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = package.model_dump(mode="json")
    (out_dir / "development.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )
    console.print(f"[dim]Saved to {out_dir / 'development.yaml'}[/]")


def load_development(rai_dir: Path) -> DevelopmentPackage:
    path = rai_dir / "development" / "development.yaml"
    if not path.exists():
        return DevelopmentPackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return DevelopmentPackage(**raw)
