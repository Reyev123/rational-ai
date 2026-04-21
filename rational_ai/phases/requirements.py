"""Requirements gathering and management phase."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from rational_ai.ai.agents import RequirementsAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import (
    PhaseStatus,
    Requirement,
    RequirementsPackage,
    UseCase,
)

console = Console()


def gather_requirements(
    ai: AIProvider,
    description: str,
    stakeholder_notes: str = "",
) -> RequirementsPackage:
    """AI-driven requirements extraction from project description."""
    agent = RequirementsAgent(ai)
    full_input = description
    if stakeholder_notes:
        full_input += f"\n\nStakeholder Notes:\n{stakeholder_notes}"

    console.print("[bold blue]🔍 Extracting requirements with AI...[/]")
    package = agent.extract_requirements(full_input)

    console.print(f"[green]✓ Extracted {len(package.requirements)} requirements[/]")

    # Generate use cases
    console.print("[bold blue]📋 Generating use cases...[/]")
    package.use_cases = agent.generate_use_cases(package)
    console.print(f"[green]✓ Generated {len(package.use_cases)} use cases[/]")

    # Run analysis
    console.print("[bold blue]🧠 Analyzing requirements quality...[/]")
    package.ai_summary = agent.analyze_requirements(package)
    package.stakeholder_notes = stakeholder_notes
    package.status = PhaseStatus.REVIEW

    return package


def add_requirement(package: RequirementsPackage, **kwargs) -> Requirement:
    """Manually add a requirement."""
    next_id = f"REQ-{len(package.requirements) + 1:03d}"
    req = Requirement(id=next_id, **kwargs)
    package.requirements.append(req)
    return req


def display_requirements(package: RequirementsPackage) -> None:
    """Display requirements in a rich table."""
    table = Table(title="Requirements", show_lines=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Title", style="bold")
    table.add_column("Type", style="magenta")
    table.add_column("Priority", style="yellow")
    table.add_column("Status", style="green")

    for r in package.requirements:
        table.add_row(r.id, r.title, r.type.value, r.priority.value, r.status.value)

    console.print(table)

    if package.use_cases:
        uc_table = Table(title="Use Cases", show_lines=True)
        uc_table.add_column("ID", style="cyan", width=10)
        uc_table.add_column("Title", style="bold")
        uc_table.add_column("Actor", style="magenta")
        uc_table.add_column("Related Reqs", style="dim")
        for uc in package.use_cases:
            uc_table.add_row(uc.id, uc.title, uc.actor, ", ".join(uc.related_requirements))
        console.print(uc_table)


def save_requirements(package: RequirementsPackage, rai_dir: Path) -> None:
    """Persist requirements to .rai/requirements/."""
    out_dir = rai_dir / "requirements"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = package.model_dump(mode="json")
    (out_dir / "requirements.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )
    console.print(f"[dim]Saved to {out_dir / 'requirements.yaml'}[/]")


def load_requirements(rai_dir: Path) -> RequirementsPackage:
    """Load requirements from .rai/requirements/."""
    path = rai_dir / "requirements" / "requirements.yaml"
    if not path.exists():
        return RequirementsPackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return RequirementsPackage(**raw)
