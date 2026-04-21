"""Export project artifacts to Markdown documentation."""

from __future__ import annotations

from pathlib import Path

from rational_ai.models.schema import Project


def export_project_markdown(project: Project, output_dir: Path) -> Path:
    """Generate a full Markdown document for the project."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{_slug(project.name)}-report.md"

    sections: list[str] = []
    sections.append(f"# {project.name}\n")
    sections.append(f"_{project.description}_\n")
    sections.append(f"**Version:** {project.version}  \n")
    sections.append(f"**Generated:** {project.updated_at.strftime('%Y-%m-%d %H:%M')}\n")

    # ── Requirements ──
    sections.append("\n---\n## 1. Requirements\n")
    if project.requirements.requirements:
        sections.append("| ID | Title | Type | Priority | Status |")
        sections.append("|---|---|---|---|---|")
        for r in project.requirements.requirements:
            sections.append(
                f"| {r.id} | {r.title} | {r.type.value} | {r.priority.value} | {r.status.value} |"
            )
        sections.append("")

    if project.requirements.use_cases:
        sections.append("\n### Use Cases\n")
        for uc in project.requirements.use_cases:
            sections.append(f"#### {uc.id}: {uc.title}\n")
            sections.append(f"- **Actor:** {uc.actor}")
            if uc.preconditions:
                sections.append(f"- **Preconditions:** {'; '.join(uc.preconditions)}")
            sections.append("- **Main Flow:**")
            for i, step in enumerate(uc.main_flow, 1):
                sections.append(f"  {i}. {step}")
            sections.append("")

    if project.requirements.ai_summary:
        sections.append(f"\n### AI Analysis\n\n{project.requirements.ai_summary}\n")

    # ── Team & Roles ──
    sections.append("\n---\n## 2. Team & Roles\n")
    if project.roles.members:
        sections.append("| ID | Name | Role | Skills |")
        sections.append("|---|---|---|---|")
        for m in project.roles.members:
            sections.append(f"| {m.id} | {m.name} | {m.role.value} | {', '.join(m.skills[:3])} |")
        sections.append("")

    # ── Architecture ──
    sections.append("\n---\n## 3. Architecture\n")
    if project.architecture.components:
        sections.append("### Components\n")
        sections.append("| ID | Name | Type | Technology | Dependencies |")
        sections.append("|---|---|---|---|---|")
        for c in project.architecture.components:
            sections.append(
                f"| {c.id} | {c.name} | {c.type} | {c.technology} | {', '.join(c.dependencies)} |"
            )
        sections.append("")

    if project.architecture.tech_stack:
        sections.append("### Tech Stack\n")
        for layer, tech in project.architecture.tech_stack.items():
            sections.append(f"- **{layer}:** {tech}")
        sections.append("")

    if project.architecture.decisions:
        sections.append("### Architecture Decision Records\n")
        for d in project.architecture.decisions:
            sections.append(f"#### {d.id}: {d.title}\n")
            sections.append(f"- **Context:** {d.context}")
            sections.append(f"- **Decision:** {d.decision}")
            sections.append(f"- **Consequences:** {d.consequences}")
            sections.append(f"- **Status:** {d.status}\n")

    if project.architecture.diagrams:
        sections.append("### Diagrams\n")
        for diag in project.architecture.diagrams:
            sections.append(f"#### {diag.title}\n")
            sections.append(f"```mermaid\n{diag.mermaid_code}\n```\n")

    if project.architecture.ai_analysis:
        sections.append(f"\n### Architecture Review\n\n{project.architecture.ai_analysis}\n")

    # ── Development ──
    sections.append("\n---\n## 4. Development\n")
    if project.development.tasks:
        sections.append("| ID | Title | Component | Priority | Hours | Status |")
        sections.append("|---|---|---|---|---|---|")
        for t in project.development.tasks:
            sections.append(
                f"| {t.id} | {t.title} | {t.component} | {t.priority.value} "
                f"| {t.estimated_hours} | {t.status.value} |"
            )
        sections.append("")

    if project.development.coding_standards:
        sections.append(f"\n### Coding Standards\n\n{project.development.coding_standards}\n")
    if project.development.branching_strategy:
        sections.append(f"\n### Branching Strategy\n\n{project.development.branching_strategy}\n")

    # ── Deployment ──
    sections.append("\n---\n## 5. Deployment\n")
    if project.deployment.environments:
        sections.append("### Environments\n")
        sections.append("| Name | Type | URL |")
        sections.append("|---|---|---|")
        for e in project.deployment.environments:
            sections.append(f"| {e.name} | {e.type} | {e.url} |")
        sections.append("")

    if project.deployment.pipeline_steps:
        sections.append("### CI/CD Pipeline\n")
        for s in sorted(project.deployment.pipeline_steps, key=lambda x: x.order):
            sections.append(f"{s.order}. **{s.name}** — {s.description}")
        sections.append("")

    # ── Schedule ──
    sections.append("\n---\n## 6. Schedule\n")
    if project.schedule.milestones:
        sections.append("### Milestones\n")
        sections.append("| ID | Name | Target Date | Deliverables |")
        sections.append("|---|---|---|---|")
        for m in project.schedule.milestones:
            sections.append(
                f"| {m.id} | {m.name} | {m.target_date or 'TBD'} "
                f"| {', '.join(m.deliverables[:3])} |"
            )
        sections.append("")

    if project.schedule.sprints:
        sections.append("### Sprint Plan\n")
        for s in project.schedule.sprints:
            sections.append(f"#### {s.name}\n")
            sections.append(f"- **Tasks:** {', '.join(s.tasks[:5])}")
            sections.append(f"- **Goals:** {', '.join(s.goals[:3])}")
            sections.append("")

    if project.schedule.estimated_duration_weeks:
        sections.append(
            f"\n**Estimated Duration:** {project.schedule.estimated_duration_weeks} weeks\n"
        )

    content = "\n".join(sections)
    out.write_text(content, encoding="utf-8")
    return out


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")
