"""Page builders for the Rational AI platform GUI.

Each function returns a Dash layout for its respective page.
Pages that are interactive rely on callbacks registered in app.py.
"""

from __future__ import annotations

from pathlib import Path

from dash import dcc, html

from gui.theme import (
    BTN_DANGER, BTN_PHASE, BTN_PRIMARY, BTN_SECONDARY, BTN_SUCCESS,
    CARD_STYLE, COLORS, FORM_GROUP, INPUT_STYLE, LABEL_STYLE,
    PHASE_COLORS, PRIORITY_COLORS, SELECT_STYLE, STATUS_COLORS,
    TEXTAREA_STYLE,
)
from gui.components import (
    badge, card, data_table, empty_state, form_label, log_panel,
    mermaid_div, page_header, priority_badge, progress_bar, stat_card, status_badge,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _g(d, *keys, default=""):
    if d is None:
        return default
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def _phase_list(project):
    phases = [
        ("Requirements", "requirements", "📋"),
        ("Team & Roles", "roles", "👥"),
        ("Architecture", "architecture", "🏗️"),
        ("Development", "development", "⚙️"),
        ("Deployment", "deployment", "🚀"),
        ("Schedule", "schedule", "📅"),
    ]
    result = []
    for label, key, icon in phases:
        section = (project or {}).get(key, {})
        st = section.get("status", "not_started") if isinstance(section, dict) else "not_started"
        pct = {"completed": 100, "review": 75, "in_progress": 40, "not_started": 0}.get(st, 0)
        color = PHASE_COLORS.get(key, COLORS["primary"])
        result.append({"label": label, "key": key, "icon": icon, "status": st, "pct": pct, "color": color})
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def build_dashboard_page(project: dict | None, proj_dir: str) -> html.Div:
    if not project:
        return html.Div([
            page_header("Dashboard", "Welcome to Rational AI", "📊"),
            card("No Project Loaded", [
                html.P("No project found in this directory. Use the Create / Open page to initialize one.", style={"color": COLORS["text_secondary"], "fontSize": "14px"}),
                html.P(f"Directory: {proj_dir}", style={"color": COLORS["text_muted"], "fontSize": "12px", "fontFamily": "monospace"}),
            ], "📁"),
        ])

    reqs = _g(project, "requirements", "requirements", default=[]) or []
    members = _g(project, "roles", "members", default=[]) or []
    components = _g(project, "architecture", "components", default=[]) or []
    tasks = _g(project, "development", "tasks", default=[]) or []
    envs = _g(project, "deployment", "environments", default=[]) or []
    sprints = _g(project, "schedule", "sprints", default=[]) or []
    diagrams = _g(project, "architecture", "diagrams", default=[]) or []
    total_hours = sum(t.get("estimated_hours", 0) for t in tasks)

    # KPIs
    kpi_row = html.Div([
        stat_card("Requirements", len(reqs), COLORS["accent_blue"], "📋"),
        stat_card("Team", len(members), COLORS["accent_purple"], "👥"),
        stat_card("Components", len(components), COLORS["accent_green"], "🏗️"),
        stat_card("Tasks", len(tasks), COLORS["accent_yellow"], "⚙️"),
        stat_card("Sprints", len(sprints), COLORS["accent_blue"], "🔄"),
        stat_card("Dev Hours", f"{total_hours:,}", COLORS["accent_pink"], "⏱️"),
    ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "24px"})

    # Phase cards
    phases = _phase_list(project)
    phase_cards = []
    for p in phases:
        phase_cards.append(html.Div([
            html.Div([
                html.Span(p["icon"], style={"fontSize": "18px"}),
                html.Span(p["label"], style={"fontWeight": "600", "fontSize": "14px", "marginLeft": "8px"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
            progress_bar(p["pct"], p["color"]),
            html.Span(p["status"].replace("_", " ").title(), style={"fontSize": "11px", "color": COLORS["text_secondary"], "marginTop": "4px", "display": "block"}),
        ], style={
            "background": COLORS["card_bg"], "borderRadius": "10px", "padding": "14px",
            "border": f"1px solid {COLORS['border']}", "flex": "1", "minWidth": "180px",
        }))
    phase_row = html.Div(phase_cards, style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "24px"})

    # Project info
    info_card = card("Project Info", [
        html.Div([
            _info_line("Name", project.get("name", "")),
            _info_line("Description", project.get("description", "")),
            _info_line("Version", project.get("version", "")),
            _info_line("Duration", f"{_g(project, 'schedule', 'estimated_duration_weeks', default='—')} weeks"),
            _info_line("Created", str(project.get("created_at", ""))[:19]),
        ], style={"fontSize": "14px", "lineHeight": "1.8"}),
    ], "📑")

    return html.Div([
        page_header("Dashboard", f"{project.get('name', 'Untitled')} — Project Overview", "📊"),
        kpi_row, phase_row, info_card,
    ])


def _info_line(label, value):
    return html.Div([
        html.Strong(f"{label}: ", style={"color": COLORS["text_secondary"], "minWidth": "120px", "display": "inline-block"}),
        html.Span(value),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CREATE / OPEN PROJECT
# ═══════════════════════════════════════════════════════════════════════════════

def build_project_page(project: dict | None, proj_dir: str) -> html.Div:
    has_project = project is not None

    current_info = None
    if has_project:
        current_info = card("Current Project", [
            html.Div([
                badge("LOADED", COLORS["success"], COLORS["success_light"]),
                html.Strong(f"  {project.get('name', '')}", style={"marginLeft": "8px", "fontSize": "16px"}),
            ], style={"marginBottom": "12px"}),
            _info_line("Description", project.get("description", "—")),
            _info_line("Version", project.get("version", "0.1.0")),
            _info_line("Directory", proj_dir),
        ], "📁")

    create_card = card("Create New Project" if not has_project else "Re-initialize Project", [
        html.Div([
            form_label("Project Name *"),
            dcc.Input(id="input-project-name", type="text", placeholder="My AI Project", style=INPUT_STYLE, value=""),
        ], style=FORM_GROUP),
        html.Div([
            form_label("Description"),
            dcc.Textarea(id="input-project-desc", placeholder="Describe your project...", style=TEXTAREA_STYLE, value=""),
        ], style=FORM_GROUP),
        html.Div([
            html.Button("🚀 Create Project", id="btn-create-project", n_clicks=0, style=BTN_SUCCESS),
        ], style={"marginTop": "8px"}),
        html.Div(id="create-result", style={"marginTop": "12px"}),
    ], "➕" if not has_project else "🔄")

    dir_card = card("Project Directory", [
        html.P(proj_dir, style={"fontFamily": "monospace", "fontSize": "13px", "color": COLORS["text_secondary"], "background": COLORS["bg"], "padding": "10px 14px", "borderRadius": "6px"}),
        html.P("Launch the GUI with --project /path to switch directories.", style={"fontSize": "12px", "color": COLORS["text_muted"], "marginTop": "8px", "marginBottom": 0}),
    ], "📂")

    children = [page_header("Create / Open Project", "Initialize a new project or view the current one", "📁")]
    if current_info:
        children.append(current_info)
    children.extend([create_card, dir_card])
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def build_config_page(cfg: dict, proj_dir: str) -> html.Div:
    ai = cfg.get("ai", {})

    provider_card = card("AI Provider Settings", [
        html.Div([
            html.Div([
                form_label("Provider"),
                dcc.Dropdown(
                    id="cfg-provider",
                    options=[
                        {"label": "OpenAI", "value": "openai"},
                        {"label": "Anthropic", "value": "anthropic"},
                        {"label": "Local / Ollama", "value": "local"},
                    ],
                    value=ai.get("provider", "openai"),
                    clearable=False,
                    style={"fontSize": "14px"},
                ),
            ], style={**FORM_GROUP, "flex": "1"}),
            html.Div([
                form_label("Model"),
                dcc.Input(id="cfg-model", type="text", value=ai.get("model", "gpt-4o"), style=INPUT_STYLE),
            ], style={**FORM_GROUP, "flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),

        html.Div([
            html.Div([
                form_label("API Key"),
                dcc.Input(id="cfg-api-key", type="password", placeholder="sk-... (or set RAI_API_KEY env var)", style=INPUT_STYLE, value=""),
            ], style={**FORM_GROUP, "flex": "2"}),
            html.Div([
                form_label("Base URL (optional)"),
                dcc.Input(id="cfg-base-url", type="text", value=ai.get("base_url", ""), placeholder="http://localhost:11434/v1", style=INPUT_STYLE),
            ], style={**FORM_GROUP, "flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),

        html.Div([
            html.Div([
                form_label("Temperature"),
                dcc.Input(id="cfg-temperature", type="number", value=ai.get("temperature", 0.7), min=0, max=2, step=0.1, style=INPUT_STYLE),
            ], style={**FORM_GROUP, "flex": "1"}),
            html.Div([
                form_label("Max Tokens"),
                dcc.Input(id="cfg-max-tokens", type="number", value=ai.get("max_tokens", 4096), min=256, step=256, style=INPUT_STYLE),
            ], style={**FORM_GROUP, "flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),

        html.Div([
            html.Button("💾 Save Configuration", id="btn-save-config", n_clicks=0, style=BTN_PRIMARY),
        ], style={"marginTop": "8px"}),
        html.Div(id="config-result", style={"marginTop": "12px"}),
    ], "🔧")

    presets = card("Quick Presets", [
        html.P("Common provider configurations:", style={"fontSize": "13px", "color": COLORS["text_secondary"], "marginBottom": "12px"}),
        html.Div([
            _preset_box("OpenAI GPT-4o", "openai", "gpt-4o", ""),
            _preset_box("OpenAI GPT-4o-mini", "openai", "gpt-4o-mini", ""),
            _preset_box("Anthropic Claude", "anthropic", "claude-sonnet-4-20250514", ""),
            _preset_box("Ollama (local)", "local", "llama3.1:8b", "http://localhost:11434/v1"),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"}),
    ], "⚡")

    return html.Div([
        page_header("Configuration", "Configure AI provider and model settings", "⚙️"),
        provider_card, presets,
    ])


def _preset_box(title, provider, model, base_url):
    return html.Div([
        html.Strong(title, style={"fontSize": "13px", "display": "block", "marginBottom": "4px"}),
        html.Span(f"{provider} / {model}", style={"fontSize": "11px", "color": COLORS["text_secondary"]}),
        html.Br(),
        html.Span(base_url or "default endpoint", style={"fontSize": "10px", "color": COLORS["text_muted"], "fontFamily": "monospace"}),
    ], style={"padding": "12px", "background": COLORS["bg"], "borderRadius": "8px", "border": f"1px solid {COLORS['border']}"})


# ═══════════════════════════════════════════════════════════════════════════════
# 4. RUN PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def build_run_page(project: dict | None, proj_dir: str) -> html.Div:
    if not project:
        return html.Div([
            page_header("Run Phases", "Execute AI-powered lifecycle phases", "▶️"),
            card("No Project", [html.P("Create a project first via the Create / Open page.", style={"color": COLORS["text_secondary"]})], "⚠️"),
        ])

    # Phase status
    phases = _phase_list(project)
    status_row = html.Div([
        html.Div([
            html.Span(p["icon"], style={"fontSize": "16px"}),
            html.Span(p["label"], style={"fontSize": "12px", "marginLeft": "6px", "fontWeight": "500"}),
            status_badge(p["status"]),
        ], style={"display": "flex", "alignItems": "center", "gap": "6px", "padding": "8px 12px", "background": COLORS["card_bg"], "borderRadius": "8px", "border": f"1px solid {COLORS['border']}"})
        for p in phases
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "24px"})

    # Phase buttons
    phase_btns_data = [
        ("btn-run-requirements", "📋 Requirements", PHASE_COLORS["requirements"]),
        ("btn-run-roles", "👥 Team & Roles", PHASE_COLORS["roles"]),
        ("btn-run-architecture", "🏗️ Architecture", PHASE_COLORS["architecture"]),
        ("btn-run-development", "💻 Development", PHASE_COLORS["development"]),
        ("btn-run-deployment", "🚀 Deployment", PHASE_COLORS["deployment"]),
        ("btn-run-schedule", "📅 Schedule", PHASE_COLORS["schedule"]),
    ]
    phase_buttons = []
    for btn_id, label, color in phase_btns_data:
        phase_buttons.append(
            html.Button(label, id=btn_id, n_clicks=0, style={**BTN_PHASE, "background": color})
        )

    buttons_card = card("Run Individual Phase", [
        html.P("Click a phase to execute it. Phases use AI to generate artifacts.", style={"fontSize": "13px", "color": COLORS["text_secondary"], "marginBottom": "12px"}),
        html.Div(phase_buttons, style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "10px"}),
    ], "🎯")

    run_all_card = card("Run Full Lifecycle", [
        html.P("Execute all 6 phases sequentially (Requirements → Roles → Architecture → Development → Deployment → Schedule).",
               style={"fontSize": "13px", "color": COLORS["text_secondary"], "marginBottom": "12px"}),
        html.Div([
            html.Div([
                form_label("Additional Context (optional)"),
                dcc.Textarea(id="run-extra-desc", placeholder="Extra project context for AI...", style={**TEXTAREA_STYLE, "minHeight": "60px"}, value=""),
            ], style=FORM_GROUP),
            html.Div([
                form_label("Stakeholder Notes (optional)"),
                dcc.Textarea(id="run-stakeholder-notes", placeholder="Notes from stakeholders...", style={**TEXTAREA_STYLE, "minHeight": "60px"}, value=""),
            ], style=FORM_GROUP),
        ]),
        html.Button("🚀 Run All Phases", id="btn-run-all", n_clicks=0, style={**BTN_SUCCESS, "fontSize": "16px", "padding": "14px 32px"}),
    ], "⚡")

    log_card = card("Execution Log", [log_panel()], "📟")

    return html.Div([
        page_header("Run Phases", "Execute AI-powered lifecycle phases", "▶️"),
        status_row, buttons_card, run_all_card, log_card,
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# 5. REQUIREMENTS (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_requirements_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Requirements", "📋")

    req_section = (project or {}).get("requirements", {})
    reqs = req_section.get("requirements", []) or []
    use_cases = req_section.get("use_cases", []) or []

    ai_note = req_section.get("ai_summary", "")
    ai_card = card("AI Analysis", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    # Req table
    rows = []
    for r in reqs:
        dep_badges = html.Div([badge(d, COLORS["info"]) for d in r.get("depends_on", [])], style={"display": "flex", "gap": "4px", "flexWrap": "wrap"})
        rows.append([
            badge(r.get("id", ""), COLORS["primary"], COLORS["primary_light"]),
            r.get("title", ""),
            r.get("description", "")[:100],
            badge(r.get("type", ""), COLORS["secondary"], COLORS["accent_purple"]),
            priority_badge(r.get("priority", "")),
            dep_badges,
        ])
    req_card = card(f"Requirements ({len(reqs)})",
        data_table(["ID", "Title", "Description", "Type", "Priority", "Deps"], rows, ["70px", "160px", "auto", "90px", "80px", "100px"]) if rows else empty_state("Run the Requirements phase to generate requirements."),
        "📋")

    # Acceptance criteria
    ac_items = []
    for r in reqs:
        ac = r.get("acceptance_criteria", [])
        if ac:
            ac_items.append(html.Div([
                html.Div([badge(r["id"], COLORS["primary"], COLORS["primary_light"]), html.Strong(f" {r.get('title', '')}", style={"marginLeft": "8px"})], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
                html.Ul([html.Li(c, style={"fontSize": "13px", "color": COLORS["text_secondary"]}) for c in ac], style={"margin": "4px 0 0 20px", "padding": 0}),
            ], style={"padding": "10px 0", "borderBottom": f"1px solid {COLORS['border_light']}"}))
    ac_card = card("Acceptance Criteria", ac_items or [empty_state("No criteria")], "✅")

    # Use cases
    uc_items = []
    for uc in use_cases:
        steps = html.Ol([html.Li(s, style={"fontSize": "13px", "color": COLORS["text_secondary"]}) for s in uc.get("main_flow", [])], style={"margin": "4px 0 0 16px", "padding": 0})
        related = html.Div([badge(r, COLORS["primary"], COLORS["primary_light"]) for r in uc.get("related_requirements", [])], style={"display": "flex", "gap": "4px", "marginTop": "6px"})
        uc_items.append(html.Div([
            html.Div([badge(uc["id"], COLORS["secondary"], COLORS["accent_purple"]), html.Strong(f" {uc.get('title', '')}", style={"marginLeft": "8px"}), badge(f"Actor: {uc.get('actor', '')}", COLORS["text_secondary"])], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
            steps, related,
        ], style={"padding": "14px 0", "borderBottom": f"1px solid {COLORS['border_light']}"}))
    uc_card = card(f"Use Cases ({len(use_cases)})", uc_items or [empty_state("No use cases")], "🎭")

    children = [page_header("Requirements", _g(project, "requirements", "stakeholder_notes", default=""), "📋")]
    if ai_card:
        children.append(ai_card)
    children.extend([req_card, html.Div([ac_card, uc_card], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"})])
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. TEAM & ROLES (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_roles_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Team & Roles", "👥")

    roles_section = project.get("roles", {})
    members = roles_section.get("members", []) or []
    raci = roles_section.get("raci_matrix", {}) or {}

    ai_note = roles_section.get("ai_recommendations", "")
    ai_card = card("AI Recommendations", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    role_colors = {"architect": COLORS["secondary"], "developer": COLORS["primary"], "devops": COLORS["success"], "qa_engineer": COLORS["warning"], "project_manager": COLORS["danger"], "designer": COLORS["info"]}
    rows = []
    for m in members:
        rc = role_colors.get(m.get("role", ""), COLORS["text_secondary"])
        skills = html.Div([badge(s, COLORS["primary"], COLORS["accent_blue"]) for s in m.get("skills", [])], style={"display": "flex", "gap": "4px", "flexWrap": "wrap"})
        avail = m.get("availability", 1.0)
        rows.append([
            badge(m.get("id", ""), rc, f"{rc}18"),
            m.get("name", ""),
            badge(m.get("role", "").replace("_", " ").title(), rc, f"{rc}18"),
            skills,
            progress_bar(avail * 100, COLORS["success"] if avail >= 0.8 else COLORS["warning"], f"{int(avail * 100)}%"),
        ])
    team_card = card(f"Team Members ({len(members)})",
        data_table(["ID", "Name", "Role", "Skills", "Avail."], rows, ["70px", "180px", "130px", "auto", "100px"]) if rows else empty_state("Run the Roles phase to generate team."),
        "👥")

    # RACI
    if raci and members:
        member_ids = [m["id"] for m in members]
        raci_headers = ["Req"] + [m.get("name", m["id"]).split(" ")[0] for m in members]
        raci_colors_map = {"R": COLORS["primary"], "A": COLORS["danger"], "C": COLORS["success"], "I": COLORS["text_secondary"]}
        raci_rows = []
        for req_id, assignments in raci.items():
            row = [badge(req_id, COLORS["primary"], COLORS["primary_light"])]
            for mid in member_ids:
                v = assignments.get(mid, "—")
                row.append(badge(v, raci_colors_map.get(v, COLORS["text_muted"]), f"{raci_colors_map.get(v, COLORS['text_muted'])}18") if v in raci_colors_map else html.Span("—", style={"color": COLORS["text_muted"]}))
            raci_rows.append(row)
        raci_card = card("RACI Matrix", [
            html.Div([badge("R=Responsible", COLORS["primary"], COLORS["primary_light"]), badge("A=Accountable", COLORS["danger"], COLORS["danger_light"]), badge("C=Consulted", COLORS["success"], COLORS["success_light"]), badge("I=Informed", COLORS["text_secondary"])], style={"display": "flex", "gap": "8px", "marginBottom": "12px", "flexWrap": "wrap"}),
            data_table(raci_headers, raci_rows),
        ], "📊")
    else:
        raci_card = card("RACI Matrix", empty_state("No RACI matrix"), "📊")

    children = [page_header("Team & Roles", "Team composition and responsibilities", "👥")]
    if ai_card:
        children.append(ai_card)
    children.extend([team_card, raci_card])
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ARCHITECTURE (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_architecture_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Architecture", "🏗️")

    arch = project.get("architecture", {})
    components = arch.get("components", []) or []
    decisions = arch.get("decisions", []) or []
    tech_stack = arch.get("tech_stack", {}) or {}

    ai_note = arch.get("ai_analysis", "")
    ai_card = card("AI Analysis", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    # Tech stack
    tech_card = None
    if tech_stack:
        icons = {"backend": "⚙️", "frontend": "🖥️", "database": "🗄️", "cache": "⚡", "messaging": "📨", "search": "🔍", "infrastructure": "☁️", "ml": "🧠"}
        items = [html.Div([
            html.Span(icons.get(k, "🔧"), style={"fontSize": "18px"}),
            html.Div([
                html.P(k.replace("_", " ").title(), style={"fontSize": "10px", "color": COLORS["text_secondary"], "margin": 0, "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                html.P(v, style={"fontSize": "14px", "fontWeight": "600", "margin": "2px 0 0"}),
            ]),
        ], style={"display": "flex", "gap": "8px", "alignItems": "center", "padding": "10px", "background": COLORS["bg"], "borderRadius": "8px"}) for k, v in tech_stack.items()]
        tech_card = card("Technology Stack", html.Div(items, style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr 1fr", "gap": "8px"}), "🛠️")

    # Components
    type_colors = {"gateway": COLORS["warning"], "service": COLORS["primary"], "frontend": COLORS["success"], "queue": COLORS["secondary"], "database": COLORS["danger"]}
    comp_rows = []
    for c in components:
        tc = type_colors.get(c.get("type", ""), COLORS["text_secondary"])
        deps = html.Div([badge(d, COLORS["info"]) for d in c.get("dependencies", [])], style={"display": "flex", "gap": "4px", "flexWrap": "wrap"}) if c.get("dependencies") else html.Span("—", style={"color": COLORS["text_muted"]})
        comp_rows.append([
            badge(c.get("id", ""), tc, f"{tc}18"),
            html.Div([html.Strong(c.get("name", "")), html.Br(), html.Span(c.get("description", "")[:80], style={"color": COLORS["text_secondary"], "fontSize": "12px"})]),
            badge(c.get("type", ""), tc, f"{tc}18"),
            badge(c.get("technology", ""), COLORS["text_secondary"], COLORS["bg"]),
            deps,
        ])
    comp_card = card(f"Components ({len(components)})",
        data_table(["ID", "Name", "Type", "Technology", "Deps"], comp_rows, ["70px", "auto", "80px", "160px", "100px"]) if comp_rows else empty_state("Run Architecture phase."),
        "🏗️")

    # ADRs
    adr_items = []
    sc_map = {"accepted": COLORS["success"], "proposed": COLORS["warning"], "rejected": COLORS["danger"]}
    for d in decisions:
        sc = sc_map.get(d.get("status", ""), COLORS["text_secondary"])
        adr_items.append(html.Div([
            html.Div([badge(d.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]), html.Strong(f" {d.get('title', '')}", style={"marginLeft": "8px"}), badge(d.get("status", "").title(), sc, f"{sc}18")], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
            html.P([html.Strong("Context: "), d.get("context", "")], style={"fontSize": "13px", "color": COLORS["text_secondary"], "margin": "4px 0 0"}),
            html.P([html.Strong("Decision: "), d.get("decision", "")], style={"fontSize": "13px", "margin": "2px 0 0"}),
        ], style={"padding": "12px 0", "borderBottom": f"1px solid {COLORS['border_light']}"}))
    adr_card = card(f"ADRs ({len(decisions)})", adr_items or [empty_state("No ADRs")], "📜")

    children = [page_header("Architecture", "System design, components, and decisions", "🏗️")]
    if ai_card:
        children.append(ai_card)
    if tech_card:
        children.append(tech_card)
    children.extend([comp_card, adr_card])
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. DEVELOPMENT (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_development_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Development", "💻")

    dev = project.get("development", {})
    tasks = dev.get("tasks", []) or []
    standards = dev.get("coding_standards", "")
    branching = dev.get("branching_strategy", "")

    ai_note = dev.get("ai_suggestions", "")
    ai_card = card("AI Suggestions", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
    by_priority = {}
    for t in tasks:
        p = t.get("priority", "medium")
        by_priority[p] = by_priority.get(p, 0) + 1

    metrics = html.Div([
        stat_card("Tasks", len(tasks), COLORS["accent_blue"], "📝"),
        stat_card("Hours", f"{total_hours:,}", COLORS["accent_green"], "⏱️"),
        stat_card("High Priority", by_priority.get("high", 0), COLORS["accent_pink"], "🔴"),
    ], style={"display": "flex", "gap": "14px", "marginBottom": "20px"})

    # Standards
    std_items = []
    if standards:
        std_items.append(html.Div([html.Strong("Standards: "), standards], style={"fontSize": "13px", "marginBottom": "4px"}))
    if branching:
        std_items.append(html.Div([html.Strong("Branching: "), branching], style={"fontSize": "13px"}))
    std_card = card("Standards", std_items, "📏") if std_items else None

    # Tasks table
    task_rows = []
    for t in tasks:
        task_rows.append([
            badge(t.get("id", ""), COLORS["primary"], COLORS["primary_light"]),
            t.get("title", ""),
            priority_badge(t.get("priority", "")),
            status_badge(t.get("status", "")),
            badge(t.get("component", ""), COLORS["text_secondary"], COLORS["bg"]),
            f"{t.get('estimated_hours', 0)}h",
        ])
    task_card = card(f"Tasks ({len(tasks)})",
        data_table(["ID", "Title", "Priority", "Status", "Component", "Hours"], task_rows, ["80px", "auto", "80px", "100px", "90px", "60px"]) if task_rows else empty_state("Run Development phase."),
        "⚙️")

    children = [page_header("Development", "Tasks, standards, and progress", "💻")]
    if ai_card:
        children.append(ai_card)
    children.append(metrics)
    if std_card:
        children.append(std_card)
    children.append(task_card)
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. DEPLOYMENT (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_deployment_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Deployment", "🚀")

    dep = project.get("deployment", {})
    envs = dep.get("environments", []) or []
    pipeline = dep.get("pipeline_steps", []) or []
    monitoring = dep.get("monitoring", {}) or {}
    iac = dep.get("infrastructure_as_code", "")

    ai_note = dep.get("ai_suggestions", "")
    ai_card = card("AI Suggestions", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    # Environments
    env_type_colors = {"development": COLORS["info"], "staging": COLORS["warning"], "production": COLORS["success"]}
    env_cards = []
    for e in envs:
        ec = env_type_colors.get(e.get("type", ""), COLORS["text_secondary"])
        config = e.get("config", {})
        config_lines = [html.Div([html.Strong(f"{k}: "), str(v)], style={"fontSize": "12px"}) for k, v in config.items()]
        env_cards.append(html.Div([
            html.Div([html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%", "background": ec}), html.Strong(e.get("name", "")), badge(e.get("type", "").title(), ec, f"{ec}18")], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}),
            html.A(e.get("url", ""), href="#", style={"color": COLORS["primary"], "fontSize": "12px", "textDecoration": "none"}),
            html.Div(config_lines, style={"background": COLORS["bg"], "borderRadius": "6px", "padding": "8px", "marginTop": "8px"}) if config_lines else None,
        ], style={**CARD_STYLE, "flex": "1", "minWidth": "220px"}))
    envs_row = html.Div(env_cards, style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "20px"}) if env_cards else None

    # Pipeline
    sorted_pipeline = sorted(pipeline, key=lambda x: x.get("order", 0))
    step_icons = {"quality": "🔍", "test": "🧪", "build": "🔨", "deploy": "🚀"}
    steps_vis = []
    for i, st in enumerate(sorted_pipeline):
        si = step_icons.get(st.get("description", ""), "▶️")
        steps_vis.append(html.Div([
            html.Div([
                html.Div(f"{st.get('order', i+1)}", style={"width": "26px", "height": "26px", "borderRadius": "50%", "background": COLORS["primary"], "color": "white", "display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "12px", "fontWeight": "700"}),
                html.Span(si),
            ], style={"display": "flex", "alignItems": "center", "gap": "6px", "marginBottom": "4px"}),
            html.Strong(st.get("name", ""), style={"fontSize": "12px", "display": "block"}),
            html.Code(st.get("command", ""), style={"fontSize": "10px", "color": COLORS["text_secondary"], "background": COLORS["bg"], "padding": "3px 6px", "borderRadius": "4px", "display": "block", "marginTop": "4px", "wordBreak": "break-all"}),
        ], style={"background": COLORS["card_bg"], "border": f"1px solid {COLORS['border']}", "borderRadius": "8px", "padding": "12px", "flex": "1", "minWidth": "150px"}))
        if i < len(sorted_pipeline) - 1:
            steps_vis.append(html.Div("→", style={"fontSize": "20px", "color": COLORS["text_muted"], "display": "flex", "alignItems": "center"}))
    pipeline_card = card(f"CI/CD Pipeline ({len(pipeline)} steps)",
        html.Div(steps_vis, style={"display": "flex", "gap": "6px", "flexWrap": "wrap", "alignItems": "stretch"}) if steps_vis else empty_state("No CI/CD pipeline"),
        "🔄")

    # Monitoring
    mon_card = None
    if monitoring:
        mon_icons = {"logging": "📝", "apm": "📈", "alerting": "🔔", "uptime": "🟢"}
        mon_items = [html.Div([html.Span(mon_icons.get(k, "🔧")), html.Div([html.P(k.upper(), style={"fontSize": "10px", "color": COLORS["text_secondary"], "margin": 0}), html.P(v, style={"fontSize": "13px", "fontWeight": "600", "margin": "2px 0 0"})])], style={"display": "flex", "gap": "8px", "alignItems": "center", "padding": "8px 12px", "background": COLORS["bg"], "borderRadius": "8px"}) for k, v in monitoring.items()]
        mon_card = card("Monitoring", html.Div(mon_items, style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"}), "📡")

    children = [page_header("Deployment", "Environments, CI/CD, and monitoring", "🚀")]
    if ai_card:
        children.append(ai_card)
    if envs_row:
        children.append(envs_row)
    children.append(pipeline_card)
    if mon_card:
        children.append(mon_card)
    if iac:
        children.append(card("Infrastructure as Code", html.Code(iac, style={"fontSize": "14px"}), "🏗️"))
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. SCHEDULE (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_schedule_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Schedule", "📅")

    sched = project.get("schedule", {})
    milestones = sched.get("milestones", []) or []
    sprints = sched.get("sprints", []) or []
    duration = sched.get("estimated_duration_weeks", "?")

    tasks_map = {}
    for t in (project.get("development", {}).get("tasks", []) or []):
        tasks_map[t["id"]] = t

    ai_note = sched.get("ai_schedule", "")
    ai_card = card("AI Schedule Analysis", html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}), "🤖") if ai_note else None

    kpi = html.Div([
        stat_card("Duration", f"{duration} wk", COLORS["accent_blue"], "📅"),
        stat_card("Milestones", len(milestones), COLORS["accent_green"], "🎯"),
        stat_card("Sprints", len(sprints), COLORS["accent_purple"], "🔄"),
    ], style={"display": "flex", "gap": "14px", "marginBottom": "20px"})

    # Milestones
    ms_items = []
    ms_colors = [COLORS["primary"], COLORS["success"], COLORS["secondary"]]
    for i, ms in enumerate(milestones):
        mc = ms_colors[i % len(ms_colors)]
        ms_items.append(html.Div([
            html.Div([
                html.Div(style={"width": "12px", "height": "12px", "borderRadius": "50%", "background": mc, "flexShrink": 0}),
                html.Div([
                    html.Div([badge(ms.get("id", ""), mc, f"{mc}18"), html.Strong(f" {ms.get('name', '')}", style={"marginLeft": "6px"}), badge(ms.get("target_date", ""), COLORS["text_secondary"])], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
                    html.Div([badge(d, COLORS["text_secondary"], COLORS["bg"]) for d in ms.get("deliverables", [])], style={"display": "flex", "flexWrap": "wrap", "gap": "4px", "marginTop": "6px"}),
                ]),
            ], style={"display": "flex", "gap": "12px", "alignItems": "flex-start"}),
        ], style={"padding": "12px 0", "borderBottom": f"1px solid {COLORS['border_light']}"}))
    ms_card = card("Milestones", ms_items or [empty_state("No milestones")], "🎯")

    # Sprints
    sprint_items = []
    for sp in sprints:
        sp_tasks = [tasks_map.get(tid, {"id": tid, "title": tid, "status": "backlog", "estimated_hours": 0}) for tid in sp.get("tasks", [])]
        sp_hours = sum(t.get("estimated_hours", 0) for t in sp_tasks)
        task_list = [html.Div([
            badge(t.get("id", ""), COLORS["primary"], COLORS["primary_light"]),
            html.Span(t.get("title", ""), style={"fontSize": "13px", "marginLeft": "6px"}),
            status_badge(t.get("status", "backlog")),
            html.Span(f"{t.get('estimated_hours', 0)}h", style={"fontSize": "12px", "color": COLORS["text_secondary"], "marginLeft": "auto"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "4px", "padding": "4px 0", "borderBottom": f"1px solid {COLORS['border_light']}"}) for t in sp_tasks]

        goals = html.Ul([html.Li(g, style={"fontSize": "12px", "color": COLORS["text_secondary"]}) for g in sp.get("goals", [])], style={"margin": "4px 0 8px 16px", "padding": 0})

        sprint_items.append(html.Div([
            html.Div([badge(sp.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]), html.Strong(f" {sp.get('name', '')}", style={"marginLeft": "8px"}), html.Span(f"{sp_hours}h", style={"marginLeft": "auto", "fontSize": "13px", "color": COLORS["text_secondary"]})], style={"display": "flex", "alignItems": "center"}),
            goals,
            html.Div(task_list) if task_list else html.Span("No tasks assigned", style={"color": COLORS["text_muted"], "fontSize": "13px", "fontStyle": "italic"}),
        ], style={**CARD_STYLE}))

    sprints_card = card(f"Sprints ({len(sprints)})", sprint_items or [empty_state("No sprints")], "🔄")

    children = [page_header("Schedule", "Timeline, milestones, and sprints", "📅"), kpi]
    if ai_card:
        children.append(ai_card)
    children.extend([html.Div([ms_card, sprints_card], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"})])
    return html.Div(children)


# ═══════════════════════════════════════════════════════════════════════════════
# 11. DIAGRAMS (view)
# ═══════════════════════════════════════════════════════════════════════════════

def build_diagrams_page(project: dict | None) -> html.Div:
    if not project:
        return _no_project_page("Diagrams", "📐")

    diagrams = _g(project, "architecture", "diagrams", default=[]) or []
    if not diagrams:
        return html.Div([
            page_header("Diagrams", "Architecture diagrams", "📐"),
            empty_state("No diagrams yet. Run the Architecture phase to generate diagrams.", "📐"),
        ])

    type_icons = {"component": "🏗️", "sequence": "🔄", "deployment": "☁️", "flowchart": "📊", "er": "🗄️", "class": "📦"}
    diagram_cards = []
    for d in diagrams:
        code = d.get("mermaid_code", "")
        dtype = d.get("type", "")
        diagram_cards.append(html.Div([
            html.Div([
                badge(d.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]),
                html.Span(type_icons.get(dtype, "📐"), style={"fontSize": "16px", "marginLeft": "6px"}),
                html.Strong(f" {d.get('title', '')}", style={"marginLeft": "6px"}),
                badge(dtype.title(), COLORS["text_secondary"]),
            ], style={"display": "flex", "alignItems": "center", "gap": "4px", "marginBottom": "6px"}),
            html.P(d.get("description", ""), style={"color": COLORS["text_secondary"], "fontSize": "13px", "margin": "0 0 10px"}),
            mermaid_div(code),
        ], style=CARD_STYLE))

    return html.Div([
        page_header("Diagrams", f"{len(diagrams)} architecture diagram(s)", "📐"),
        html.P("Diagrams are rendered with Mermaid.js. Refresh if they don't appear.", style={"color": COLORS["text_muted"], "fontSize": "12px", "fontStyle": "italic", "marginBottom": "16px"}),
        *diagram_cards,
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# 12. EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def build_export_page(project: dict | None, proj_dir: str) -> html.Div:
    if not project:
        return _no_project_page("Export", "📤")

    default_out = str((Path(proj_dir) / ".rai" / "exports"))

    return html.Div([
        page_header("Export", "Export project reports and diagrams", "📤"),

        card("Export Settings", [
            html.Div([
                form_label("Output Directory"),
                dcc.Input(id="export-output-dir", type="text", value=default_out, style=INPUT_STYLE),
            ], style=FORM_GROUP),
            html.P("Leave blank for default (.rai/exports/).", style={"fontSize": "12px", "color": COLORS["text_muted"], "marginBottom": "16px"}),
        ], "📂"),

        card("Export Actions", [
            html.Div([
                html.Button("📄 Markdown Report", id="btn-export-md", n_clicks=0, style={**BTN_PRIMARY, "flex": "1"}),
                html.Button("🌐 HTML Report", id="btn-export-html", n_clicks=0, style={**BTN_SUCCESS, "flex": "1"}),
                html.Button("📐 Diagrams", id="btn-export-diagrams", n_clicks=0, style={**BTN_SECONDARY, "flex": "1"}),
                html.Button("📦 Export All", id="btn-export-all", n_clicks=0, style={**BTN_DANGER, "flex": "1", "background": COLORS["secondary"]}),
            ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),
            html.Div(id="export-result", style={"marginTop": "16px"}),
        ], "🚀"),

        card("What Gets Exported", [
            html.Ul([
                html.Li([html.Strong("Markdown: "), "Full project report in .md format"], style={"marginBottom": "4px", "fontSize": "13px"}),
                html.Li([html.Strong("HTML: "), "Styled responsive HTML report with live Mermaid diagrams"], style={"marginBottom": "4px", "fontSize": "13px"}),
                html.Li([html.Strong("Diagrams: "), "Individual .mmd files + combined HTML viewer"], style={"marginBottom": "4px", "fontSize": "13px"}),
                html.Li([html.Strong("All: "), "All formats above in one go"], style={"fontSize": "13px"}),
            ], style={"margin": 0, "paddingLeft": "20px"}),
        ], "📋"),
    ])


# ── Shared ──

def _no_project_page(title: str, icon: str) -> html.Div:
    return html.Div([
        page_header(title, "", icon),
        card("No Project", [
            html.P("No project loaded. Create one via the Create / Open page, then run the relevant phase.", style={"color": COLORS["text_secondary"], "fontSize": "14px"}),
        ], "⚠️"),
    ])
