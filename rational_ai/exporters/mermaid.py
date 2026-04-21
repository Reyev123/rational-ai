"""Export architecture diagrams as Mermaid files."""

from __future__ import annotations

from pathlib import Path

from rational_ai.models.schema import ArchitecturePackage


def export_diagrams(package: ArchitecturePackage, output_dir: Path) -> list[Path]:
    """Write each diagram to a .mmd file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for diag in package.diagrams:
        p = output_dir / f"{diag.id}-{diag.type.value}.mmd"
        p.write_text(diag.mermaid_code, encoding="utf-8")
        paths.append(p)
    return paths


def generate_combined_html(package: ArchitecturePackage, output: Path) -> Path:
    """Generate a single HTML page with all Mermaid diagrams rendered."""
    diagrams_html = ""
    for diag in package.diagrams:
        diagrams_html += f"""
        <div class="diagram">
            <h3>{diag.id}: {diag.title}</h3>
            <p>{diag.description}</p>
            <div class="mermaid">
{diag.mermaid_code}
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Architecture Diagrams</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .diagram {{ margin: 2rem 0; padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; }}
        h3 {{ color: #1a73e8; }}
    </style>
</head>
<body>
    <h1>Architecture Diagrams</h1>
    {diagrams_html}
    <script>mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output
