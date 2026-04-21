"""Rational AI CLI — AI-powered software engineering lifecycle tool."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from rational_ai.config import load_config, save_config
from rational_ai.project import ProjectOrchestrator

app = typer.Typer(
    name="rai",
    help="Rational AI — AI-powered software engineering lifecycle platform",
    no_args_is_help=True,
)
console = Console()


def _get_orchestrator(project_dir: Path | None = None) -> ProjectOrchestrator:
    cfg = load_config(project_dir)
    return ProjectOrchestrator(cfg)


# ── Init ──────────────────────────────────────────────────────────────────────

@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    description: str = typer.Option("", "--desc", "-d", help="Project description"),
    provider: str = typer.Option("openai", "--provider", "-p", help="AI provider"),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="AI model"),
):
    """Initialize a new Rational AI project."""
    orch = _get_orchestrator()
    orch.config.ai.provider = provider
    orch.config.ai.model = model
    save_config(orch.config)
    orch.init_project(name, description)


# ── Phase Commands ───────────────────────────────────────────────────────────

@app.command()
def requirements(
    description: str = typer.Option("", "--desc", "-d", help="Additional description"),
    notes: str = typer.Option("", "--notes", "-n", help="Stakeholder notes"),
):
    """Run the requirements gathering phase."""
    orch = _get_orchestrator()
    orch.run_requirements(description, notes)


@app.command()
def team():
    """Run the team/roles recommendation phase."""
    orch = _get_orchestrator()
    orch.run_roles()


@app.command()
def architecture():
    """Run the architecture design phase."""
    orch = _get_orchestrator()
    orch.run_architecture()


@app.command()
def review():
    """Run AI architecture review."""
    orch = _get_orchestrator()
    result = orch.review_architecture()
    console.print(result)


@app.command()
def development():
    """Run the development planning phase."""
    orch = _get_orchestrator()
    orch.run_development()


@app.command()
def deployment():
    """Run the deployment planning phase."""
    orch = _get_orchestrator()
    orch.run_deployment()


@app.command()
def schedule():
    """Run the scheduling phase."""
    orch = _get_orchestrator()
    orch.run_schedule()


@app.command()
def full(
    description: str = typer.Option("", "--desc", "-d", help="Additional context"),
    notes: str = typer.Option("", "--notes", "-n", help="Stakeholder notes"),
):
    """Run ALL phases sequentially (full lifecycle)."""
    orch = _get_orchestrator()
    orch.run_all(description, notes)


# ── Scaffold ─────────────────────────────────────────────────────────────────

@app.command()
def scaffold(
    component: str = typer.Argument(..., help="Component ID to scaffold"),
):
    """Generate code scaffold for an architecture component."""
    orch = _get_orchestrator()
    code = orch.scaffold(component)
    console.print(code)


# ── Export ───────────────────────────────────────────────────────────────────

@app.command()
def export(
    fmt: str = typer.Argument("all", help="Export format: markdown | html | diagrams | all"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Export project artifacts."""
    orch = _get_orchestrator()

    if fmt in ("markdown", "md", "all"):
        orch.export_markdown(output)
    if fmt in ("html", "all"):
        orch.export_html(output)
    if fmt in ("diagrams", "mermaid", "all"):
        orch.export_diagrams(output)


# ── Status ───────────────────────────────────────────────────────────────────

@app.command()
def status():
    """Show project phase status."""
    orch = _get_orchestrator()
    orch.load()

    table = Table(title=f"Project: {orch.project.name}", show_lines=True)
    table.add_column("Phase", style="bold")
    table.add_column("Status", style="cyan")

    status_colors = {
        "not_started": "[dim]not started[/]",
        "in_progress": "[yellow]in progress[/]",
        "review": "[blue]review[/]",
        "completed": "[green]completed[/]",
        "configured": "[green]configured[/]",
    }

    for phase, st in orch.status().items():
        table.add_row(phase, status_colors.get(st, st))
    console.print(table)

    # Summary counts
    proj = orch.project
    console.print(f"\n  Requirements: {len(proj.requirements.requirements)}")
    console.print(f"  Use Cases:    {len(proj.requirements.use_cases)}")
    console.print(f"  Team Members: {len(proj.roles.members)}")
    console.print(f"  Components:   {len(proj.architecture.components)}")
    console.print(f"  ADRs:         {len(proj.architecture.decisions)}")
    console.print(f"  Diagrams:     {len(proj.architecture.diagrams)}")
    console.print(f"  Dev Tasks:    {len(proj.development.tasks)}")
    console.print(f"  Environments: {len(proj.deployment.environments)}")
    console.print(f"  Milestones:   {len(proj.schedule.milestones)}")
    console.print(f"  Sprints:      {len(proj.schedule.sprints)}")


# ── Show ─────────────────────────────────────────────────────────────────────

@app.command()
def show(
    phase: str = typer.Argument(..., help="Phase to display: requirements | team | architecture | development | deployment | schedule"),
):
    """Display artifacts for a specific phase."""
    orch = _get_orchestrator()
    orch.load()
    proj = orch.project

    display_map = {
        "requirements": lambda: __import__("rational_ai.phases.requirements", fromlist=["display_requirements"]).display_requirements(proj.requirements),
        "team": lambda: __import__("rational_ai.phases.roles", fromlist=["display_roles"]).display_roles(proj.roles),
        "roles": lambda: __import__("rational_ai.phases.roles", fromlist=["display_roles"]).display_roles(proj.roles),
        "architecture": lambda: __import__("rational_ai.phases.architecture", fromlist=["display_architecture"]).display_architecture(proj.architecture),
        "development": lambda: __import__("rational_ai.phases.development", fromlist=["display_development"]).display_development(proj.development),
        "deployment": lambda: __import__("rational_ai.phases.deployment", fromlist=["display_deployment"]).display_deployment(proj.deployment),
        "schedule": lambda: __import__("rational_ai.phases.scheduling", fromlist=["display_schedule"]).display_schedule(proj.schedule),
    }

    if phase in display_map:
        display_map[phase]()
    else:
        console.print(f"[red]Unknown phase: {phase}[/]")
        console.print(f"Available: {', '.join(display_map.keys())}")


if __name__ == "__main__":
    app()
