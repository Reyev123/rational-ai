"""Rational AI — Interactive Platform GUI.

A web-based GUI that replaces the CLI for:
  - Creating / opening projects
  - Configuring AI provider settings
  - Running lifecycle phases interactively
  - Viewing all generated artifacts
  - Exporting reports

Usage:
    python -m gui.app                             # default
    python -m gui.app --port 9000                  # custom port
    python -m gui.app --project /path/to/project   # open existing project
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import traceback
from pathlib import Path

import yaml
from dash import Dash, Input, Output, State, callback_context, dcc, html, no_update

from gui.theme import (
    BTN_DANGER, BTN_PHASE, BTN_PRIMARY, BTN_SECONDARY, BTN_SUCCESS,
    CARD_STYLE, COLORS, EXTERNAL_CSS, FORM_GROUP, INPUT_STYLE,
    LABEL_STYLE, MERMAID_JS, SELECT_STYLE, TEXTAREA_STYLE,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    {"label": "Dashboard",      "value": "dashboard",     "icon": "📊"},
    {"label": "Create / Open",   "value": "project",       "icon": "📁"},
    {"label": "Configuration",   "value": "config",        "icon": "⚙️"},
    {"label": "Run Phases",      "value": "run",           "icon": "▶️"},
    {"label": "Requirements",    "value": "requirements",  "icon": "📋"},
    {"label": "Team & Roles",    "value": "roles",         "icon": "👥"},
    {"label": "Architecture",    "value": "architecture",  "icon": "🏗️"},
    {"label": "Development",     "value": "development",   "icon": "💻"},
    {"label": "Deployment",      "value": "deployment",    "icon": "🚀"},
    {"label": "Schedule",        "value": "schedule",      "icon": "📅"},
    {"label": "Diagrams",        "value": "diagrams",      "icon": "📐"},
    {"label": "Export",          "value": "export",        "icon": "📤"},
]


def _sidebar() -> html.Div:
    nav_links = []
    for item in NAV_ITEMS:
        nav_links.append(
            html.Div(
                [
                    html.Span(item["icon"], style={"marginRight": "10px", "fontSize": "16px"}),
                    html.Span(item["label"], style={"fontSize": "13px"}),
                ],
                id={"type": "nav-link", "index": item["value"]},
                n_clicks=0,
                style={
                    "padding": "10px 18px",
                    "cursor": "pointer",
                    "borderRadius": "8px",
                    "marginBottom": "2px",
                    "display": "flex",
                    "alignItems": "center",
                    "color": COLORS["sidebar_text"],
                    "transition": "all 0.15s",
                },
            )
        )

    return html.Div([
        html.Div([
            html.H2("🧠 Rational AI", style={"color": "#FFF", "margin": "0", "fontSize": "20px", "fontWeight": "700"}),
            html.P("Platform GUI", style={"color": COLORS["sidebar_text"], "margin": "2px 0 0", "fontSize": "10px", "letterSpacing": "1.5px", "textTransform": "uppercase"}),
        ], style={"padding": "22px 18px", "borderBottom": f"1px solid {COLORS['sidebar_hover']}"}),

        # Project indicator
        html.Div(id="sidebar-project-name", style={"padding": "12px 18px", "borderBottom": f"1px solid {COLORS['sidebar_hover']}"}),

        html.Div(nav_links, style={"padding": "10px 8px", "flex": "1", "overflowY": "auto"}),

        html.Div(
            html.P("v0.1.0", style={"color": COLORS["sidebar_text"], "fontSize": "10px", "margin": "0"}),
            style={"padding": "12px 18px", "borderTop": f"1px solid {COLORS['sidebar_hover']}"},
        ),
    ], style={
        "width": "240px", "minWidth": "240px", "height": "100vh",
        "background": COLORS["sidebar_bg"], "position": "fixed", "top": 0, "left": 0,
        "display": "flex", "flexDirection": "column", "zIndex": 100,
    })


# ── App Factory ──────────────────────────────────────────────────────────────

def create_app(project_dir: Path) -> Dash:
    app = Dash(
        __name__,
        title="Rational AI — Platform",
        suppress_callback_exceptions=True,
        external_stylesheets=EXTERNAL_CSS,
    )

    app.layout = html.Div([
        # Stores
        dcc.Store(id="store-page", data="dashboard"),
        dcc.Store(id="store-project-dir", data=str(project_dir)),
        dcc.Store(id="store-project-data", data=None),
        dcc.Store(id="store-refresh", data=0),
        dcc.Store(id="store-run-log", data="Ready. Click a phase button or 'Run All' to start.\n"),

        # Layout
        _sidebar(),
        html.Div(id="page-content", style={
            "marginLeft": "240px", "padding": "28px 36px",
            "minHeight": "100vh", "background": COLORS["bg"],
        }),

        # Mermaid script
        html.Script(src=MERMAID_JS),
        html.Script("document.addEventListener('DOMContentLoaded', function() { if(typeof mermaid !== 'undefined') mermaid.initialize({startOnLoad:true, theme:'default'}); });"),

        # Interval for re-rendering mermaid after page switch
        dcc.Interval(id="mermaid-re-render", interval=1500, n_intervals=0, max_intervals=0),
    ], style={
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "margin": 0, "padding": 0, "background": COLORS["bg"], "color": COLORS["text"],
    })

    _register_callbacks(app, project_dir)
    return app


# ── Callbacks ────────────────────────────────────────────────────────────────

def _register_callbacks(app: Dash, initial_project_dir: Path):
    from gui.pages import (
        build_dashboard_page,
        build_project_page,
        build_config_page,
        build_run_page,
        build_requirements_page,
        build_roles_page,
        build_architecture_page,
        build_development_page,
        build_deployment_page,
        build_schedule_page,
        build_diagrams_page,
        build_export_page,
    )

    # ── helpers ──

    def _load_project(proj_dir: str) -> dict | None:
        p = Path(proj_dir) / ".rai" / "project.yaml"
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        return None

    def _load_config_yaml(proj_dir: str) -> dict:
        p = Path(proj_dir) / ".rai" / "config.yaml"
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return {}

    # ── Navigation ──

    @app.callback(
        Output("store-page", "data"),
        [Input({"type": "nav-link", "index": item["value"]}, "n_clicks") for item in NAV_ITEMS],
        prevent_initial_call=True,
    )
    def navigate(*_args):
        ctx = callback_context
        if not ctx.triggered_id:
            return no_update
        return ctx.triggered_id["index"]

    # ── Page routing ──

    @app.callback(
        Output("page-content", "children"),
        Input("store-page", "data"),
        Input("store-refresh", "data"),
        State("store-project-dir", "data"),
    )
    def render_page(page, _refresh, proj_dir):
        project = _load_project(proj_dir)
        cfg = _load_config_yaml(proj_dir)
        builders = {
            "dashboard": lambda: build_dashboard_page(project, proj_dir),
            "project": lambda: build_project_page(project, proj_dir),
            "config": lambda: build_config_page(cfg, proj_dir),
            "run": lambda: build_run_page(project, proj_dir),
            "requirements": lambda: build_requirements_page(project),
            "roles": lambda: build_roles_page(project),
            "architecture": lambda: build_architecture_page(project),
            "development": lambda: build_development_page(project),
            "deployment": lambda: build_deployment_page(project),
            "schedule": lambda: build_schedule_page(project),
            "diagrams": lambda: build_diagrams_page(project),
            "export": lambda: build_export_page(project, proj_dir),
        }
        fn = builders.get(page, builders["dashboard"])
        return fn()

    # ── Sidebar project name ──

    @app.callback(
        Output("sidebar-project-name", "children"),
        Input("store-refresh", "data"),
        State("store-project-dir", "data"),
    )
    def update_sidebar_project(_r, proj_dir):
        project = _load_project(proj_dir)
        if project:
            return [
                html.P("PROJECT", style={"color": COLORS["sidebar_text"], "fontSize": "9px", "letterSpacing": "1.5px", "margin": "0 0 2px"}),
                html.P(project.get("name", "Untitled"), style={"color": "#FFF", "fontSize": "13px", "fontWeight": "600", "margin": 0, "wordBreak": "break-word"}),
            ]
        return html.P("No project loaded", style={"color": COLORS["sidebar_text"], "fontSize": "12px", "fontStyle": "italic", "margin": 0})

    # ── Create project ──

    @app.callback(
        Output("store-refresh", "data", allow_duplicate=True),
        Output("create-result", "children"),
        Input("btn-create-project", "n_clicks"),
        State("input-project-name", "value"),
        State("input-project-desc", "value"),
        State("store-project-dir", "data"),
        prevent_initial_call=True,
    )
    def create_project(n_clicks, name, desc, proj_dir):
        if not n_clicks or not name:
            return no_update, html.Span("Please enter a project name.", style={"color": COLORS["danger"]})
        try:
            os.chdir(proj_dir)
            from rational_ai.config import load_config, save_config
            from rational_ai.project import ProjectOrchestrator
            cfg = load_config(Path(proj_dir))
            orch = ProjectOrchestrator(cfg)
            orch.init_project(name, desc or "")
            return n_clicks, html.Span(f"✓ Project '{name}' created!", style={"color": COLORS["success"], "fontWeight": "600"})
        except Exception as e:
            return no_update, html.Span(f"Error: {e}", style={"color": COLORS["danger"]})

    # ── Save config ──

    @app.callback(
        Output("config-result", "children"),
        Output("store-refresh", "data", allow_duplicate=True),
        Input("btn-save-config", "n_clicks"),
        State("cfg-provider", "value"),
        State("cfg-model", "value"),
        State("cfg-api-key", "value"),
        State("cfg-base-url", "value"),
        State("cfg-temperature", "value"),
        State("cfg-max-tokens", "value"),
        State("store-project-dir", "data"),
        prevent_initial_call=True,
    )
    def save_config_cb(n, provider, model, api_key, base_url, temp, max_tok, proj_dir):
        if not n:
            return no_update, no_update
        try:
            os.chdir(proj_dir)
            from rational_ai.config import load_config, save_config
            cfg = load_config(Path(proj_dir))
            cfg.ai.provider = provider or "openai"
            cfg.ai.model = model or "gpt-4o"
            if api_key:
                cfg.ai.api_key = api_key
                os.environ["RAI_API_KEY"] = api_key
            cfg.ai.base_url = base_url or ""
            cfg.ai.temperature = float(temp) if temp else 0.7
            cfg.ai.max_tokens = int(max_tok) if max_tok else 4096
            save_config(cfg)
            return html.Span("✓ Configuration saved!", style={"color": COLORS["success"], "fontWeight": "600"}), (n or 0)
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": COLORS["danger"]}), no_update

    # ── Run phases ──

    @app.callback(
        Output("run-log", "children", allow_duplicate=True),
        Output("store-run-log", "data"),
        Output("store-refresh", "data", allow_duplicate=True),
        Input("btn-run-requirements", "n_clicks"),
        Input("btn-run-roles", "n_clicks"),
        Input("btn-run-architecture", "n_clicks"),
        Input("btn-run-development", "n_clicks"),
        Input("btn-run-deployment", "n_clicks"),
        Input("btn-run-schedule", "n_clicks"),
        Input("btn-run-all", "n_clicks"),
        State("run-extra-desc", "value"),
        State("run-stakeholder-notes", "value"),
        State("store-project-dir", "data"),
        State("store-refresh", "data"),
        prevent_initial_call=True,
    )
    def run_phase(n_req, n_roles, n_arch, n_dev, n_dep, n_sched, n_all,
                  extra_desc, notes, proj_dir, prev_refresh):
        ctx = callback_context
        if not ctx.triggered_id:
            return no_update, no_update, no_update
        btn_id = ctx.triggered_id

        os.chdir(proj_dir)

        from rational_ai.config import load_config
        from rational_ai.project import ProjectOrchestrator
        from rational_ai.phases import (
            requirements as req_mod,
            roles as roles_mod,
            architecture as arch_mod,
            development as dev_mod,
            deployment as dep_mod,
            scheduling as sched_mod,
        )
        from rational_ai import project as project_mod

        # Capture Rich output: Rich Console objects cache their file handle
        # at creation time, so redirect_stdout won't catch them.
        # Monkey-patch every module's console.file to our buffer instead.
        buf = io.StringIO()
        all_consoles = []
        for mod in [project_mod, req_mod, roles_mod, arch_mod, dev_mod, dep_mod, sched_mod]:
            c = getattr(mod, "console", None)
            if c is not None:
                all_consoles.append((c, c.file))
                c.file = buf    # redirect Rich output into buffer

        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = buf
        sys.stderr = buf

        try:
            cfg = load_config(Path(proj_dir))
            orch = ProjectOrchestrator(cfg)
            orch.load()

            desc = extra_desc or ""
            sn = notes or ""

            if btn_id == "btn-run-requirements":
                orch.run_requirements(desc, sn)
            elif btn_id == "btn-run-roles":
                orch.run_roles()
            elif btn_id == "btn-run-architecture":
                orch.run_architecture()
            elif btn_id == "btn-run-development":
                orch.run_development()
            elif btn_id == "btn-run-deployment":
                orch.run_deployment()
            elif btn_id == "btn-run-schedule":
                orch.run_schedule()
            elif btn_id == "btn-run-all":
                orch.run_all(desc, sn)

            phase_name = btn_id.replace("btn-run-", "").replace("-", " ").title()
            output = buf.getvalue()
            log = f"═══ Running: {phase_name} ═══\n\n"
            if output.strip():
                log += output + "\n"
            log += f"\n✓ {phase_name} completed successfully!\n"
            return log, log, (prev_refresh or 0) + 1
        except Exception as e:
            output = buf.getvalue()
            tb = traceback.format_exc()
            log = f"═══ ERROR ═══\n\n"
            if output.strip():
                log += output + "\n\n"
            log += f"{tb}\n"
            return log, log, no_update
        finally:
            # Restore all consoles and stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            for c, original_file in all_consoles:
                c.file = original_file

    # ── Sync log store → Pre element ──

    @app.callback(
        Output("run-log", "children", allow_duplicate=True),
        Input("store-run-log", "data"),
        prevent_initial_call=True,
    )
    def sync_log(log_text):
        return log_text or "Ready.\n"

    # ── Export ──

    @app.callback(
        Output("export-result", "children"),
        Input("btn-export-md", "n_clicks"),
        Input("btn-export-html", "n_clicks"),
        Input("btn-export-diagrams", "n_clicks"),
        Input("btn-export-all", "n_clicks"),
        State("export-output-dir", "value"),
        State("store-project-dir", "data"),
        prevent_initial_call=True,
    )
    def export_project(n_md, n_html, n_diag, n_all, output_dir, proj_dir):
        ctx = callback_context
        if not ctx.triggered_id:
            return no_update
        btn = ctx.triggered_id

        os.chdir(proj_dir)

        from rational_ai.config import load_config
        from rational_ai.project import ProjectOrchestrator

        try:
            cfg = load_config(Path(proj_dir))
            orch = ProjectOrchestrator(cfg)
            orch.load()

            out = Path(output_dir) if output_dir else None
            results = []

            if btn in ("btn-export-md", "btn-export-all"):
                p = orch.export_markdown(out)
                results.append(f"Markdown: {p}")
            if btn in ("btn-export-html", "btn-export-all"):
                p = orch.export_html(out)
                results.append(f"HTML: {p}")
            if btn in ("btn-export-diagrams", "btn-export-all"):
                paths = orch.export_diagrams(out)
                results.append(f"Diagrams: {len(paths)} files")

            return html.Div([
                html.Span("✓ Export complete!", style={"color": COLORS["success"], "fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                *[html.P(r, style={"fontSize": "13px", "margin": "2px 0", "color": COLORS["text_secondary"]}) for r in results],
            ])
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": COLORS["danger"]})


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rational AI Platform GUI")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--project", type=str, default=".")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    app = create_app(project_dir)

    print(f"\n🧠 Rational AI — Platform GUI")
    print(f"   Project dir: {project_dir}")
    print(f"   URL: http://localhost:{args.port}")
    print(f"   Press Ctrl+C to stop\n")

    app.run(debug=args.debug, port=args.port, host="0.0.0.0")


if __name__ == "__main__":
    main()
