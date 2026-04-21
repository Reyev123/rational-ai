"""Export full project report as HTML."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from rational_ai.models.schema import Project

_HTML_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ project.name }} — Rational AI Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root { --primary: #1a73e8; --bg: #f8f9fa; --card: #fff; --border: #e0e0e0; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: #333; }
        .container { max-width: 1100px; margin: 0 auto; padding: 2rem; }
        h1 { color: var(--primary); margin-bottom: 0.5rem; }
        h2 { color: var(--primary); margin: 2rem 0 1rem; border-bottom: 2px solid var(--primary); padding-bottom: 0.3rem; }
        h3 { margin: 1.5rem 0 0.5rem; }
        .meta { color: #666; margin-bottom: 2rem; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        th, td { padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: var(--bg); font-weight: 600; }
        tr:hover { background: #f0f4ff; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
        .badge-critical { background: #fce4ec; color: #c62828; }
        .badge-high { background: #fff3e0; color: #e65100; }
        .badge-medium { background: #e3f2fd; color: #1565c0; }
        .badge-low { background: #e8f5e9; color: #2e7d32; }
        .diagram { margin: 1.5rem 0; }
        .mermaid { background: #fff; padding: 1rem; border-radius: 8px; }
        .adr { border-left: 4px solid var(--primary); padding-left: 1rem; margin: 1rem 0; }
        ul, ol { padding-left: 1.5rem; margin: 0.5rem 0; }
        .phase-nav { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 1rem 0; }
        .phase-nav a { padding: 0.5rem 1rem; background: var(--primary); color: #fff; border-radius: 4px; text-decoration: none; }
        .phase-nav a:hover { opacity: 0.85; }
    </style>
</head>
<body>
<div class="container">
    <h1>{{ project.name }}</h1>
    <p class="meta">{{ project.description }}<br>Version {{ project.version }} — Generated {{ project.updated_at.strftime('%Y-%m-%d %H:%M') }}</p>

    <div class="phase-nav">
        <a href="#requirements">Requirements</a>
        <a href="#team">Team</a>
        <a href="#architecture">Architecture</a>
        <a href="#development">Development</a>
        <a href="#deployment">Deployment</a>
        <a href="#schedule">Schedule</a>
    </div>

    <!-- REQUIREMENTS -->
    <h2 id="requirements">1. Requirements</h2>
    {% if project.requirements.requirements %}
    <table>
        <tr><th>ID</th><th>Title</th><th>Type</th><th>Priority</th><th>Status</th></tr>
        {% for r in project.requirements.requirements %}
        <tr>
            <td>{{ r.id }}</td><td>{{ r.title }}</td><td>{{ r.type.value }}</td>
            <td><span class="badge badge-{{ r.priority.value }}">{{ r.priority.value }}</span></td>
            <td>{{ r.status.value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    {% if project.requirements.use_cases %}
    <h3>Use Cases</h3>
    {% for uc in project.requirements.use_cases %}
    <div class="card">
        <h4>{{ uc.id }}: {{ uc.title }}</h4>
        <p><strong>Actor:</strong> {{ uc.actor }}</p>
        {% if uc.main_flow %}
        <p><strong>Main Flow:</strong></p>
        <ol>{% for step in uc.main_flow %}<li>{{ step }}</li>{% endfor %}</ol>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if project.requirements.ai_summary %}
    <div class="card"><h4>AI Analysis</h4><p>{{ project.requirements.ai_summary | replace('\\n', '<br>') }}</p></div>
    {% endif %}

    <!-- TEAM -->
    <h2 id="team">2. Team & Roles</h2>
    {% if project.roles.members %}
    <table>
        <tr><th>ID</th><th>Name</th><th>Role</th><th>Skills</th><th>Components</th></tr>
        {% for m in project.roles.members %}
        <tr>
            <td>{{ m.id }}</td><td>{{ m.name }}</td><td>{{ m.role.value }}</td>
            <td>{{ m.skills[:3] | join(', ') }}</td><td>{{ m.assigned_components[:2] | join(', ') }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <!-- ARCHITECTURE -->
    <h2 id="architecture">3. Architecture</h2>
    {% if project.architecture.components %}
    <table>
        <tr><th>ID</th><th>Name</th><th>Type</th><th>Technology</th><th>Dependencies</th></tr>
        {% for c in project.architecture.components %}
        <tr>
            <td>{{ c.id }}</td><td>{{ c.name }}</td><td>{{ c.type }}</td>
            <td>{{ c.technology }}</td><td>{{ c.dependencies | join(', ') }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    {% if project.architecture.tech_stack %}
    <h3>Tech Stack</h3>
    <div class="card">
    <ul>{% for layer, tech in project.architecture.tech_stack.items() %}<li><strong>{{ layer }}:</strong> {{ tech }}</li>{% endfor %}</ul>
    </div>
    {% endif %}

    {% if project.architecture.decisions %}
    <h3>Architecture Decision Records</h3>
    {% for d in project.architecture.decisions %}
    <div class="adr">
        <h4>{{ d.id }}: {{ d.title }}</h4>
        <p><strong>Context:</strong> {{ d.context }}</p>
        <p><strong>Decision:</strong> {{ d.decision }}</p>
        <p><strong>Consequences:</strong> {{ d.consequences }}</p>
    </div>
    {% endfor %}
    {% endif %}

    {% if project.architecture.diagrams %}
    <h3>Diagrams</h3>
    {% for diag in project.architecture.diagrams %}
    <div class="diagram">
        <h4>{{ diag.title }}</h4>
        <div class="mermaid">{{ diag.mermaid_code }}</div>
    </div>
    {% endfor %}
    {% endif %}

    <!-- DEVELOPMENT -->
    <h2 id="development">4. Development</h2>
    {% if project.development.tasks %}
    <table>
        <tr><th>ID</th><th>Title</th><th>Component</th><th>Priority</th><th>Hours</th><th>Status</th></tr>
        {% for t in project.development.tasks %}
        <tr>
            <td>{{ t.id }}</td><td>{{ t.title }}</td><td>{{ t.component }}</td>
            <td><span class="badge badge-{{ t.priority.value }}">{{ t.priority.value }}</span></td>
            <td>{{ t.estimated_hours }}</td><td>{{ t.status.value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <!-- DEPLOYMENT -->
    <h2 id="deployment">5. Deployment</h2>
    {% if project.deployment.environments %}
    <table>
        <tr><th>Name</th><th>Type</th><th>URL</th></tr>
        {% for e in project.deployment.environments %}
        <tr><td>{{ e.name }}</td><td>{{ e.type }}</td><td>{{ e.url }}</td></tr>
        {% endfor %}
    </table>
    {% endif %}

    {% if project.deployment.pipeline_steps %}
    <h3>CI/CD Pipeline</h3>
    <ol>{% for s in project.deployment.pipeline_steps | sort(attribute='order') %}
    <li><strong>{{ s.name }}</strong> — {{ s.description }}</li>
    {% endfor %}</ol>
    {% endif %}

    <!-- SCHEDULE -->
    <h2 id="schedule">6. Schedule</h2>
    {% if project.schedule.milestones %}
    <table>
        <tr><th>ID</th><th>Milestone</th><th>Target</th><th>Status</th></tr>
        {% for m in project.schedule.milestones %}
        <tr><td>{{ m.id }}</td><td>{{ m.name }}</td><td>{{ m.target_date or 'TBD' }}</td><td>{{ m.status.value }}</td></tr>
        {% endfor %}
    </table>
    {% endif %}

    {% if project.schedule.sprints %}
    <h3>Sprint Plan</h3>
    {% for s in project.schedule.sprints %}
    <div class="card"><h4>{{ s.name }}</h4>
    <p><strong>Tasks:</strong> {{ s.tasks | join(', ') }}</p>
    <p><strong>Goals:</strong> {{ s.goals | join(', ') }}</p></div>
    {% endfor %}
    {% endif %}

    {% if project.schedule.estimated_duration_weeks %}
    <p><strong>Estimated Duration:</strong> {{ project.schedule.estimated_duration_weeks }} weeks</p>
    {% endif %}

</div>
<script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
</body>
</html>
""")


def export_project_html(project: Project, output_dir: Path) -> Path:
    """Render full project report as a self-contained HTML file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = project.name.lower().replace(" ", "-").replace("/", "-")
    out = output_dir / f"{slug}-report.html"
    html = _HTML_TEMPLATE.render(project=project)
    out.write_text(html, encoding="utf-8")
    return out
