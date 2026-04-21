"""Deployment planning phase."""

from __future__ import annotations

from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from rational_ai.ai.agents import DeploymentAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import DeploymentPackage, Project

console = Console()


def plan_deployment(ai: AIProvider, project: Project) -> DeploymentPackage:
    """AI-driven deployment planning."""
    agent = DeploymentAgent(ai)

    console.print("[bold blue]🚀 Planning deployment with AI...[/]")
    package = agent.plan_deployment(project)
    console.print(f"[green]✓ Planned {len(package.environments)} environments[/]")
    console.print(f"[green]✓ Defined {len(package.pipeline_steps)} pipeline steps[/]")

    return package


def display_deployment(package: DeploymentPackage) -> None:
    """Display deployment plan."""
    # Environments
    env_table = Table(title="Deployment Environments", show_lines=True)
    env_table.add_column("Name", style="bold")
    env_table.add_column("Type", style="magenta")
    env_table.add_column("URL", style="dim")

    for e in package.environments:
        env_table.add_row(e.name, e.type, e.url)
    console.print(env_table)

    # Pipeline
    if package.pipeline_steps:
        pipe_table = Table(title="CI/CD Pipeline", show_lines=True)
        pipe_table.add_column("#", style="cyan", width=5)
        pipe_table.add_column("Step", style="bold")
        pipe_table.add_column("Description", style="dim")
        pipe_table.add_column("Environment", style="yellow")

        for s in sorted(package.pipeline_steps, key=lambda x: x.order):
            pipe_table.add_row(str(s.order), s.name, s.description, s.environment)
        console.print(pipe_table)

    if package.monitoring:
        console.print("\n[bold]Monitoring Stack:[/]")
        for k, v in package.monitoring.items():
            console.print(f"  [cyan]{k}:[/] {v}")


def save_deployment(package: DeploymentPackage, rai_dir: Path) -> None:
    out_dir = rai_dir / "deployment"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = package.model_dump(mode="json")
    (out_dir / "deployment.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )
    console.print(f"[dim]Saved to {out_dir / 'deployment.yaml'}[/]")


def load_deployment(rai_dir: Path) -> DeploymentPackage:
    path = rai_dir / "deployment" / "deployment.yaml"
    if not path.exists():
        return DeploymentPackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return DeploymentPackage(**raw)
