"""Architecture design phase."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rational_ai.ai.agents import ArchitectureAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import (
    ArchitecturePackage,
    PhaseStatus,
    Project,
)

console = Console()


def design_architecture(ai: AIProvider, project: Project) -> ArchitecturePackage:
    """AI-driven architecture design."""
    agent = ArchitectureAgent(ai)

    console.print("[bold blue]🏗️  Designing system architecture with AI...[/]")
    package = agent.design_architecture(project)
    console.print(f"[green]✓ Designed {len(package.components)} components[/]")
    console.print(f"[green]✓ Created {len(package.diagrams)} diagrams[/]")
    console.print(f"[green]✓ Recorded {len(package.decisions)} architecture decisions[/]")

    return package


def review_architecture(ai: AIProvider, package: ArchitecturePackage) -> str:
    """AI-driven architecture review."""
    agent = ArchitectureAgent(ai)

    console.print("[bold blue]🔎 Reviewing architecture...[/]")
    review = agent.review_architecture(package)
    package.ai_analysis = review
    console.print("[green]✓ Architecture review complete[/]")

    return review


def display_architecture(package: ArchitecturePackage) -> None:
    """Display architecture in rich format."""
    # Components
    table = Table(title="Architecture Components", show_lines=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="magenta")
    table.add_column("Technology", style="yellow")
    table.add_column("Dependencies", style="dim")

    for c in package.components:
        table.add_row(c.id, c.name, c.type, c.technology, ", ".join(c.dependencies))
    console.print(table)

    # Tech stack
    if package.tech_stack:
        console.print("\n[bold]Tech Stack:[/]")
        for layer, tech in package.tech_stack.items():
            console.print(f"  [cyan]{layer}:[/] {tech}")

    # ADRs
    if package.decisions:
        console.print("\n[bold]Architecture Decision Records:[/]")
        for d in package.decisions:
            console.print(Panel(
                f"[bold]{d.title}[/]\n\n"
                f"[dim]Context:[/] {d.context}\n"
                f"[dim]Decision:[/] {d.decision}\n"
                f"[dim]Consequences:[/] {d.consequences}",
                title=d.id,
                border_style="blue",
            ))

    # Diagrams
    if package.diagrams:
        console.print("\n[bold]Diagrams:[/]")
        for diag in package.diagrams:
            console.print(Panel(
                f"```mermaid\n{diag.mermaid_code}\n```",
                title=f"{diag.id}: {diag.title}",
                border_style="green",
            ))


def save_architecture(package: ArchitecturePackage, rai_dir: Path) -> None:
    out_dir = rai_dir / "architecture"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = package.model_dump(mode="json")
    (out_dir / "architecture.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )

    # Save diagrams as individual files
    for diag in package.diagrams:
        (out_dir / f"{diag.id}.mmd").write_text(diag.mermaid_code, encoding="utf-8")

    console.print(f"[dim]Saved to {out_dir}[/]")


def load_architecture(rai_dir: Path) -> ArchitecturePackage:
    path = rai_dir / "architecture" / "architecture.yaml"
    if not path.exists():
        return ArchitecturePackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ArchitecturePackage(**raw)
