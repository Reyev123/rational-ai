"""Project scheduling and milestone planning phase."""

from __future__ import annotations

from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from rational_ai.ai.agents import ScheduleAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import Project, SchedulePackage

console = Console()


def generate_schedule(ai: AIProvider, project: Project) -> SchedulePackage:
    """AI-driven schedule generation."""
    agent = ScheduleAgent(ai)

    console.print("[bold blue]📅 Generating project schedule with AI...[/]")
    package = agent.generate_schedule(project)
    console.print(f"[green]✓ Created {len(package.milestones)} milestones[/]")
    console.print(f"[green]✓ Planned {len(package.sprints)} sprints[/]")
    console.print(f"[green]✓ Estimated duration: {package.estimated_duration_weeks} weeks[/]")

    return package


def display_schedule(package: SchedulePackage) -> None:
    """Display schedule."""
    # Milestones
    ms_table = Table(title="Milestones", show_lines=True)
    ms_table.add_column("ID", style="cyan", width=10)
    ms_table.add_column("Name", style="bold")
    ms_table.add_column("Target Date", style="yellow")
    ms_table.add_column("Deliverables", style="dim")
    ms_table.add_column("Status", style="green")

    for m in package.milestones:
        ms_table.add_row(
            m.id, m.name,
            str(m.target_date) if m.target_date else "TBD",
            ", ".join(m.deliverables[:3]),
            m.status.value,
        )
    console.print(ms_table)

    # Sprints
    if package.sprints:
        sp_table = Table(title="Sprint Plan", show_lines=True)
        sp_table.add_column("ID", style="cyan", width=10)
        sp_table.add_column("Name", style="bold")
        sp_table.add_column("Tasks", style="dim")
        sp_table.add_column("Goals", style="yellow")

        for s in package.sprints:
            sp_table.add_row(
                s.id, s.name,
                ", ".join(s.tasks[:4]),
                ", ".join(s.goals[:2]),
            )
        console.print(sp_table)

    if package.estimated_duration_weeks:
        console.print(
            f"\n[bold]Estimated Duration:[/] {package.estimated_duration_weeks} weeks"
        )


def save_schedule(package: SchedulePackage, rai_dir: Path) -> None:
    out_dir = rai_dir / "schedule"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = package.model_dump(mode="json")
    (out_dir / "schedule.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    console.print(f"[dim]Saved to {out_dir / 'schedule.yaml'}[/]")


def load_schedule(rai_dir: Path) -> SchedulePackage:
    path = rai_dir / "schedule" / "schedule.yaml"
    if not path.exists():
        return SchedulePackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return SchedulePackage(**raw)
