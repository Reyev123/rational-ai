"""Rational AI — Comprehensive Dash Web GUI.

Usage:
    python -m gui.app                     # default port 8050
    python -m gui.app --port 9000         # custom port
    python -m gui.app --project /path     # custom project dir
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from dash import Dash, Input, Output, callback, dcc, html

from gui.theme import COLORS, EXTERNAL_CSS, MERMAID_JS
from gui.pages import (
    build_overview_page,
    build_requirements_page,
    build_roles_page,
    build_architecture_page,
    build_development_page,
    build_deployment_page,
    build_schedule_page,
    build_report_page,
    build_diagrams_page,
)

# ── Load project data ────────────────────────────────────────────────────────


def load_project(project_dir: Path) -> dict:
    """Load project.yaml from the .rai folder."""
    proj_file = project_dir / ".rai" / "project.yaml"
    if not proj_file.exists():
        print(f"ERROR: No project found at {proj_file}")
        print("Run 'rai init' and 'rai full' first.")
        sys.exit(1)
    return yaml.safe_load(proj_file.read_text(encoding="utf-8"))


# ── Navigation ────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    {"label": "Overview", "value": "overview", "icon": "📊"},
    {"label": "Requirements", "value": "requirements", "icon": "📋"},
    {"label": "Team & Roles", "value": "roles", "icon": "👥"},
    {"label": "Architecture", "value": "architecture", "icon": "🏗️"},
    {"label": "Development", "value": "development", "icon": "⚙️"},
    {"label": "Deployment", "value": "deployment", "icon": "🚀"},
    {"label": "Schedule", "value": "schedule", "icon": "📅"},
    {"label": "Diagrams", "value": "diagrams", "icon": "📐"},
    {"label": "Full Report", "value": "report", "icon": "📄"},
]


def build_sidebar(project: dict) -> html.Div:
    """Build the left sidebar with navigation."""
    nav_links = []
    for item in NAV_ITEMS:
        nav_links.append(
            html.Div(
                [
                    html.Span(item["icon"], style={"marginRight": "10px", "fontSize": "18px"}),
                    html.Span(item["label"]),
                ],
                id={"type": "nav-link", "index": item["value"]},
                className="nav-link",
                n_clicks=0,
                style={
                    "padding": "12px 20px",
                    "cursor": "pointer",
                    "borderRadius": "8px",
                    "marginBottom": "4px",
                    "display": "flex",
                    "alignItems": "center",
                    "transition": "all 0.2s ease",
                    "color": COLORS["text"],
                    "fontSize": "14px",
                },
            )
        )

    return html.Div(
        [
            # Logo / Title
            html.Div(
                [
                    html.H2(
                        "🧠 Rational AI",
                        style={
                            "color": COLORS["primary"],
                            "margin": "0",
                            "fontSize": "22px",
                            "fontWeight": "700",
                        },
                    ),
                    html.P(
                        "AI-Powered Lifecycle",
                        style={
                            "color": COLORS["text_secondary"],
                            "margin": "4px 0 0 0",
                            "fontSize": "11px",
                            "letterSpacing": "1px",
                            "textTransform": "uppercase",
                        },
                    ),
                ],
                style={"padding": "24px 20px", "borderBottom": f"1px solid {COLORS['border']}"},
            ),
            # Project name
            html.Div(
                [
                    html.P(
                        "PROJECT",
                        style={
                            "color": COLORS["text_secondary"],
                            "fontSize": "10px",
                            "letterSpacing": "1.5px",
                            "margin": "0 0 4px 0",
                        },
                    ),
                    html.P(
                        project.get("name", "Untitled"),
                        style={
                            "color": COLORS["text"],
                            "fontSize": "13px",
                            "fontWeight": "600",
                            "margin": "0",
                            "wordBreak": "break-word",
                        },
                    ),
                ],
                style={"padding": "16px 20px", "borderBottom": f"1px solid {COLORS['border']}"},
            ),
            # Navigation
            html.Div(
                nav_links,
                style={"padding": "12px 12px"},
            ),
            # Version
            html.Div(
                html.P(
                    f"v{project.get('version', '0.1.0')}",
                    style={"color": COLORS["text_secondary"], "fontSize": "11px", "margin": "0"},
                ),
                style={
                    "padding": "16px 20px",
                    "borderTop": f"1px solid {COLORS['border']}",
                    "position": "absolute",
                    "bottom": "0",
                    "width": "100%",
                    "boxSizing": "border-box",
                },
            ),
        ],
        style={
            "width": "260px",
            "minWidth": "260px",
            "height": "100vh",
            "background": COLORS["sidebar_bg"],
            "borderRight": f"1px solid {COLORS['border']}",
            "position": "fixed",
            "top": "0",
            "left": "0",
            "overflowY": "auto",
            "zIndex": "100",
        },
    )


# ── App Layout ────────────────────────────────────────────────────────────────


def create_app(project_dir: Path) -> Dash:
    """Create and configure the Dash application."""
    project = load_project(project_dir)

    app = Dash(
        __name__,
        title=f"Rational AI — {project.get('name', 'Project')}",
        suppress_callback_exceptions=True,
        external_stylesheets=EXTERNAL_CSS,
    )

    app.layout = html.Div(
        [
            dcc.Store(id="current-page", data="overview"),
            dcc.Store(id="project-data", data=project),
            # Sidebar
            build_sidebar(project),
            # Main content
            html.Div(
                id="page-content",
                style={
                    "marginLeft": "260px",
                    "padding": "32px 40px",
                    "minHeight": "100vh",
                    "background": COLORS["bg"],
                },
            ),
            # Mermaid.js for diagrams
            html.Script(src=MERMAID_JS),
            html.Script("mermaid.initialize({startOnLoad: false, theme: 'default'});"),
        ],
        style={
            "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "margin": "0",
            "padding": "0",
            "background": COLORS["bg"],
            "color": COLORS["text"],
        },
    )

    # ── Callbacks ─────────────────────────────────────────────────────────

    @app.callback(
        Output("current-page", "data"),
        [Input({"type": "nav-link", "index": item["value"]}, "n_clicks") for item in NAV_ITEMS],
        prevent_initial_call=True,
    )
    def navigate(*args):
        from dash import ctx

        if not ctx.triggered_id:
            return "overview"
        return ctx.triggered_id["index"]

    @app.callback(
        Output("page-content", "children"),
        Input("current-page", "data"),
        Input("project-data", "data"),
    )
    def render_page(page, proj):
        builders = {
            "overview": build_overview_page,
            "requirements": build_requirements_page,
            "roles": build_roles_page,
            "architecture": build_architecture_page,
            "development": build_development_page,
            "deployment": build_deployment_page,
            "schedule": build_schedule_page,
            "diagrams": build_diagrams_page,
            "report": build_report_page,
        }
        builder = builders.get(page, build_overview_page)
        return builder(proj)

    return app


# ── Entry Point ───────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Rational AI Web GUI")
    parser.add_argument("--port", type=int, default=8050, help="Port to run on")
    parser.add_argument("--project", type=str, default=".", help="Project directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    app = create_app(project_dir)

    print(f"\n🧠 Rational AI Web GUI")
    print(f"   Project: {project_dir}")
    print(f"   URL:     http://localhost:{args.port}")
    print(f"   Press Ctrl+C to stop\n")

    app.run(debug=args.debug, port=args.port, host="0.0.0.0")


if __name__ == "__main__":
    main()
