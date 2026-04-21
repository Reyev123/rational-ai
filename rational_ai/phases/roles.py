"""Role assignment and team management phase."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from rational_ai.ai.agents import RolesAgent
from rational_ai.ai.providers import AIProvider
from rational_ai.models.schema import PhaseStatus, Project, RolesPackage, TeamMember

console = Console()


def recommend_team(ai: AIProvider, project: Project) -> RolesPackage:
    """AI-driven team composition recommendation."""
    agent = RolesAgent(ai)

    console.print("[bold blue]👥 Analyzing project for team composition...[/]")
    package = agent.recommend_roles(project)
    console.print(f"[green]✓ Recommended {len(package.members)} team members[/]")

    return package


def add_member(package: RolesPackage, **kwargs) -> TeamMember:
    """Manually add a team member."""
    next_id = f"TM-{len(package.members) + 1:03d}"
    member = TeamMember(id=next_id, **kwargs)
    package.members.append(member)
    return member


def display_roles(package: RolesPackage) -> None:
    """Display team in a rich table."""
    table = Table(title="Team Composition", show_lines=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Name", style="bold")
    table.add_column("Role", style="magenta")
    table.add_column("Skills", style="dim")
    table.add_column("Components", style="yellow")

    for m in package.members:
        table.add_row(
            m.id, m.name, m.role.value,
            ", ".join(m.skills[:3]),
            ", ".join(m.assigned_components[:2]),
        )
    console.print(table)

    if package.raci_matrix:
        console.print("\n[bold]RACI Matrix:[/]")
        raci_table = Table(show_lines=True)
        raci_table.add_column("Activity", style="bold")
        roles = set()
        for v in package.raci_matrix.values():
            roles.update(v.keys())
        for role in sorted(roles):
            raci_table.add_column(role, style="cyan")

        for activity, mapping in package.raci_matrix.items():
            row = [activity] + [mapping.get(r, "-") for r in sorted(roles)]
            raci_table.add_row(*row)
        console.print(raci_table)


def save_roles(package: RolesPackage, rai_dir: Path) -> None:
    out_dir = rai_dir / "roles"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = package.model_dump(mode="json")
    (out_dir / "roles.yaml").write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8"
    )
    console.print(f"[dim]Saved to {out_dir / 'roles.yaml'}[/]")


def load_roles(rai_dir: Path) -> RolesPackage:
    path = rai_dir / "roles" / "roles.yaml"
    if not path.exists():
        return RolesPackage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return RolesPackage(**raw)
