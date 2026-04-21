"""Page builders for the Rational AI GUI dashboard."""

from __future__ import annotations

from dash import html, dcc

from gui.theme import COLORS, PHASE_COLORS, PRIORITY_COLORS, STATUS_COLORS, CARD_STYLE
from gui.components import (
    badge,
    card,
    data_table,
    empty_state,
    mermaid_div,
    page_header,
    priority_badge,
    progress_bar,
    stat_card,
    status_badge,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get(d: dict, *keys, default=""):
    """Safe nested dict access."""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


def _phase_progress(project: dict) -> list[dict]:
    """Compute phase completion info."""
    phases = [
        {"name": "Requirements", "key": "requirements", "icon": "📋", "color": PHASE_COLORS[0]},
        {"name": "Team & Roles", "key": "roles", "icon": "👥", "color": PHASE_COLORS[1]},
        {"name": "Architecture", "key": "architecture", "icon": "🏗️", "color": PHASE_COLORS[2]},
        {"name": "Development", "key": "development", "icon": "⚙️", "color": PHASE_COLORS[3]},
        {"name": "Deployment", "key": "deployment", "icon": "🚀", "color": PHASE_COLORS[4]},
        {"name": "Schedule", "key": "schedule", "icon": "📅", "color": PHASE_COLORS[5]},
    ]
    result = []
    for p in phases:
        section = project.get(p["key"], {})
        status = section.get("status", "not_started") if isinstance(section, dict) else "not_started"
        pct = {"completed": 100, "review": 75, "in_progress": 40, "not_started": 0}.get(status, 0)
        result.append({**p, "status": status, "pct": pct})
    return result


# ─── Overview ─────────────────────────────────────────────────────────────────

def build_overview_page(project: dict) -> html.Div:
    """Dashboard overview with KPIs and phase progress."""
    reqs = _get(project, "requirements", "requirements", default=[]) or []
    members = _get(project, "roles", "members", default=[]) or []
    components = _get(project, "architecture", "components", default=[]) or []
    tasks = _get(project, "development", "tasks", default=[]) or []
    envs = _get(project, "deployment", "environments", default=[]) or []
    sprints = _get(project, "schedule", "sprints", default=[]) or []
    milestones = _get(project, "schedule", "milestones", default=[]) or []

    total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
    done_tasks = sum(1 for t in tasks if t.get("status") == "done")
    phases = _phase_progress(project)
    completed_phases = sum(1 for p in phases if p["status"] == "completed")

    # KPI row
    kpi_row = html.Div(
        [
            stat_card("Requirements", len(reqs), COLORS["accent_blue"], "📋"),
            stat_card("Team Members", len(members), COLORS["accent_purple"], "👥"),
            stat_card("Components", len(components), COLORS["accent_green"], "🏗️"),
            stat_card("Dev Tasks", len(tasks), COLORS["accent_yellow"], "⚙️"),
            stat_card("Sprints", len(sprints), COLORS["accent_teal"], "🔄"),
            stat_card("Environments", len(envs), COLORS["accent_pink"], "🌍"),
        ],
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"},
    )

    # Phase progress
    phase_cards = []
    for p in phases:
        phase_cards.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(p["icon"], style={"fontSize": "20px"}),
                            html.Span(p["name"], style={"fontWeight": "600", "fontSize": "14px", "marginLeft": "8px"}),
                        ],
                        style={"display": "flex", "alignItems": "center", "marginBottom": "8px"},
                    ),
                    progress_bar(p["pct"], p["color"]),
                    html.Span(
                        p["status"].replace("_", " ").title(),
                        style={"fontSize": "11px", "color": COLORS["text_secondary"], "marginTop": "4px", "display": "block"},
                    ),
                ],
                style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "10px",
                    "padding": "16px",
                    "border": f"1px solid {COLORS['border']}",
                    "flex": "1",
                    "minWidth": "200px",
                },
            )
        )
    phase_row = html.Div(phase_cards, style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "24px"})

    # Project summary
    summary_card = card(
        "Project Summary",
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Project: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(project.get("name", "Untitled")),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Description: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(project.get("description", "—")),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Version: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(project.get("version", "0.1.0")),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Estimated Duration: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(f"{_get(project, 'schedule', 'estimated_duration_weeks', default='?')} weeks"),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Total Dev Hours: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(f"{total_hours:,} hours ({len(tasks)} tasks)"),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Phases Complete: ", style={"color": COLORS["text_secondary"]}),
                            html.Span(f"{completed_phases} / {len(phases)}"),
                        ],
                    ),
                ],
                style={"fontSize": "14px", "lineHeight": "1.6"},
            ),
        ],
        "📑",
    )

    # Quick milestones
    milestone_items = []
    for ms in milestones:
        milestone_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong(ms.get("name", ""), style={"fontSize": "14px"}),
                            badge(ms.get("target_date", ""), COLORS["primary"], COLORS["primary_light"]),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                    ),
                    html.Div(
                        [badge(d, COLORS["text_secondary"]) for d in ms.get("deliverables", [])],
                        style={"marginTop": "6px", "display": "flex", "flexWrap": "wrap", "gap": "4px"},
                    ),
                ],
                style={"padding": "12px 0", "borderBottom": f"1px solid {COLORS['border_light']}"},
            )
        )
    milestones_card = card("Milestones", milestone_items or [empty_state("No milestones")], "🎯")

    return html.Div([
        page_header("Dashboard", f"Overview of {project.get('name', 'project')}", "📊"),
        kpi_row,
        phase_row,
        html.Div([summary_card, milestones_card], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}),
    ])


# ─── Requirements ─────────────────────────────────────────────────────────────

def build_requirements_page(project: dict) -> html.Div:
    """Requirements listing with use cases."""
    req_section = project.get("requirements", {})
    reqs = req_section.get("requirements", []) or []
    use_cases = req_section.get("use_cases", []) or []

    # AI summary
    ai_note = req_section.get("ai_summary", "")
    ai_card = card(
        "AI Analysis",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Requirements table
    rows = []
    for r in reqs:
        dep_badges = html.Div([badge(d, COLORS["info"]) for d in r.get("depends_on", [])], style={"display": "flex", "gap": "4px", "flexWrap": "wrap"})
        rows.append([
            badge(r.get("id", ""), COLORS["primary"], COLORS["primary_light"]),
            r.get("title", ""),
            r.get("description", "")[:120] + ("..." if len(r.get("description", "")) > 120 else ""),
            badge(r.get("type", ""), COLORS["secondary"], COLORS["accent_purple"]),
            priority_badge(r.get("priority", "")),
            dep_badges,
        ])
    req_table = card(
        f"Requirements ({len(reqs)})",
        data_table(["ID", "Title", "Description", "Type", "Priority", "Dependencies"], rows, ["80px", "180px", "auto", "100px", "90px", "120px"]) if rows else empty_state("No requirements"),
        "📋",
    )

    # Acceptance criteria details
    criteria_items = []
    for r in reqs:
        ac = r.get("acceptance_criteria", [])
        if ac:
            criteria_items.append(
                html.Div(
                    [
                        html.Div(
                            [badge(r["id"], COLORS["primary"], COLORS["primary_light"]), html.Strong(f" {r.get('title', '')}", style={"fontSize": "14px", "marginLeft": "8px"})],
                            style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
                        ),
                        html.Ul([html.Li(c, style={"fontSize": "13px", "color": COLORS["text_secondary"]}) for c in ac], style={"margin": "4px 0 0 20px", "padding": 0}),
                    ],
                    style={"padding": "12px 0", "borderBottom": f"1px solid {COLORS['border_light']}"},
                )
            )
    criteria_card = card("Acceptance Criteria", criteria_items or [empty_state("No criteria defined")], "✅")

    # Use cases
    uc_items = []
    for uc in use_cases:
        steps = html.Ol(
            [html.Li(s, style={"fontSize": "13px", "color": COLORS["text_secondary"], "marginBottom": "2px"}) for s in uc.get("main_flow", [])],
            style={"margin": "6px 0 0 20px", "padding": 0},
        )
        related = html.Div(
            [badge(r, COLORS["primary"], COLORS["primary_light"]) for r in uc.get("related_requirements", [])],
            style={"display": "flex", "gap": "4px", "marginTop": "6px"},
        )
        uc_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            badge(uc["id"], COLORS["secondary"], COLORS["accent_purple"]),
                            html.Strong(f" {uc.get('title', '')}", style={"marginLeft": "8px"}),
                            badge(f"Actor: {uc.get('actor', '')}", COLORS["text_secondary"], COLORS["bg"]),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                    ),
                    steps,
                    related,
                ],
                style={"padding": "16px 0", "borderBottom": f"1px solid {COLORS['border_light']}"},
            )
        )
    uc_card = card(f"Use Cases ({len(use_cases)})", uc_items or [empty_state("No use cases")], "🎭")

    children = [page_header("Requirements", _get(project, "requirements", "stakeholder_notes", default=""), "📋")]
    if ai_card:
        children.append(ai_card)
    children.extend([req_table, html.Div([criteria_card, uc_card], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"})])
    return html.Div(children)


# ─── Team & Roles ────────────────────────────────────────────────────────────

def build_roles_page(project: dict) -> html.Div:
    """Team members, skills, and RACI matrix."""
    roles_section = project.get("roles", {})
    members = roles_section.get("members", []) or []
    raci = roles_section.get("raci_matrix", {}) or {}

    ai_note = roles_section.get("ai_recommendations", "")
    ai_card = card(
        "AI Recommendations",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Team table
    rows = []
    role_colors = {
        "architect": COLORS["secondary"],
        "developer": COLORS["primary"],
        "devops": COLORS["success"],
        "qa_engineer": COLORS["warning"],
        "project_manager": COLORS["danger"],
        "designer": COLORS["info"],
    }
    for m in members:
        role_c = role_colors.get(m.get("role", ""), COLORS["text_secondary"])
        skill_badges = html.Div(
            [badge(s, COLORS["primary"], COLORS["accent_blue"]) for s in m.get("skills", [])],
            style={"display": "flex", "gap": "4px", "flexWrap": "wrap"},
        )
        avail = m.get("availability", 1.0)
        avail_bar = html.Div(
            [
                progress_bar(avail * 100, COLORS["success"] if avail >= 0.8 else COLORS["warning"], f"{int(avail * 100)}%"),
            ],
            style={"minWidth": "80px"},
        )
        rows.append([
            badge(m.get("id", ""), role_c, f"{role_c}18"),
            m.get("name", ""),
            badge(m.get("role", "").replace("_", " ").title(), role_c, f"{role_c}18"),
            skill_badges,
            avail_bar,
        ])
    team_card = card(
        f"Team Members ({len(members)})",
        data_table(["ID", "Name", "Role", "Skills", "Availability"], rows, ["80px", "200px", "140px", "auto", "120px"]) if rows else empty_state("No team members"),
        "👥",
    )

    # RACI Matrix
    if raci and members:
        member_ids = [m["id"] for m in members]
        raci_headers = ["Requirement"] + [m.get("name", m["id"]).split(" ")[0] for m in members]
        raci_rows = []
        raci_colors_map = {"R": COLORS["primary"], "A": COLORS["danger"], "C": COLORS["success"], "I": COLORS["text_secondary"]}
        for req_id, assignments in raci.items():
            row = [badge(req_id, COLORS["primary"], COLORS["primary_light"])]
            for mid in member_ids:
                val = assignments.get(mid, "—")
                if val in raci_colors_map:
                    row.append(badge(val, raci_colors_map[val], f"{raci_colors_map[val]}18"))
                else:
                    row.append(html.Span("—", style={"color": COLORS["text_muted"]}))
            raci_rows.append(row)
        raci_card = card(
            "RACI Matrix",
            [
                html.Div(
                    [
                        badge("R = Responsible", COLORS["primary"], COLORS["primary_light"]),
                        badge("A = Accountable", COLORS["danger"], COLORS["danger_light"]),
                        badge("C = Consulted", COLORS["success"], COLORS["success_light"]),
                        badge("I = Informed", COLORS["text_secondary"], COLORS["bg"]),
                    ],
                    style={"display": "flex", "gap": "8px", "marginBottom": "12px", "flexWrap": "wrap"},
                ),
                data_table(raci_headers, raci_rows),
            ],
            "📊",
        )
    else:
        raci_card = card("RACI Matrix", empty_state("No RACI matrix defined"), "📊")

    children = [page_header("Team & Roles", "Team composition and responsibility assignments", "👥")]
    if ai_card:
        children.append(ai_card)
    children.extend([team_card, raci_card])
    return html.Div(children)


# ─── Architecture ─────────────────────────────────────────────────────────────

def build_architecture_page(project: dict) -> html.Div:
    """Architecture components, tech stack, ADRs."""
    arch = project.get("architecture", {})
    components = arch.get("components", []) or []
    decisions = arch.get("decisions", []) or []
    tech_stack = arch.get("tech_stack", {}) or {}

    ai_note = arch.get("ai_analysis", "")
    ai_card = card(
        "AI Analysis",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Tech stack
    if tech_stack:
        tech_items = []
        tech_icons = {"backend": "⚙️", "frontend": "🖥️", "database": "🗄️", "cache": "⚡", "messaging": "📨", "search": "🔍", "infrastructure": "☁️", "ml": "🧠"}
        for key, val in tech_stack.items():
            tech_items.append(
                html.Div(
                    [
                        html.Span(tech_icons.get(key, "🔧"), style={"fontSize": "20px"}),
                        html.Div(
                            [
                                html.P(key.replace("_", " ").title(), style={"fontSize": "11px", "color": COLORS["text_secondary"], "margin": 0, "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                                html.P(val, style={"fontSize": "14px", "fontWeight": "600", "margin": "2px 0 0 0"}),
                            ],
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "alignItems": "center", "padding": "10px 14px", "background": COLORS["bg"], "borderRadius": "8px"},
                )
            )
        tech_card = card("Technology Stack", html.Div(tech_items, style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr 1fr", "gap": "10px"}), "🛠️")
    else:
        tech_card = None

    # Components table
    type_colors = {"gateway": COLORS["warning"], "service": COLORS["primary"], "frontend": COLORS["success"], "queue": COLORS["secondary"], "database": COLORS["danger"]}
    comp_rows = []
    for c in components:
        deps = html.Div(
            [badge(d, COLORS["info"]) for d in c.get("dependencies", [])],
            style={"display": "flex", "gap": "4px", "flexWrap": "wrap"},
        ) if c.get("dependencies") else html.Span("—", style={"color": COLORS["text_muted"]})
        tc = type_colors.get(c.get("type", ""), COLORS["text_secondary"])
        comp_rows.append([
            badge(c.get("id", ""), tc, f"{tc}18"),
            html.Div([html.Strong(c.get("name", "")), html.Br(), html.Span(c.get("description", "")[:100], style={"color": COLORS["text_secondary"], "fontSize": "12px"})]),
            badge(c.get("type", ""), tc, f"{tc}18"),
            badge(c.get("technology", ""), COLORS["text_secondary"], COLORS["bg"]),
            deps,
        ])
    comp_card = card(
        f"Components ({len(components)})",
        data_table(["ID", "Name / Description", "Type", "Technology", "Dependencies"], comp_rows, ["80px", "auto", "90px", "180px", "120px"]) if comp_rows else empty_state("No components"),
        "🏗️",
    )

    # ADRs
    adr_items = []
    adr_status_colors = {"accepted": COLORS["success"], "proposed": COLORS["warning"], "rejected": COLORS["danger"]}
    for d in decisions:
        sc = adr_status_colors.get(d.get("status", ""), COLORS["text_secondary"])
        adr_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            badge(d.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]),
                            html.Strong(f" {d.get('title', '')}", style={"marginLeft": "8px"}),
                            badge(d.get("status", "").title(), sc, f"{sc}18"),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                    ),
                    html.P(
                        [html.Strong("Context: "), d.get("context", "")],
                        style={"fontSize": "13px", "color": COLORS["text_secondary"], "margin": "6px 0 0 0"},
                    ),
                    html.P(
                        [html.Strong("Decision: "), d.get("decision", "")],
                        style={"fontSize": "13px", "color": COLORS["text"], "margin": "4px 0 0 0"},
                    ),
                ],
                style={"padding": "14px 0", "borderBottom": f"1px solid {COLORS['border_light']}"},
            )
        )
    adr_card = card(f"Architecture Decision Records ({len(decisions)})", adr_items or [empty_state("No ADRs")], "📜")

    children = [page_header("Architecture", "System design, components, and decisions", "🏗️")]
    if ai_card:
        children.append(ai_card)
    if tech_card:
        children.append(tech_card)
    children.extend([comp_card, adr_card])
    return html.Div(children)


# ─── Development ──────────────────────────────────────────────────────────────

def build_development_page(project: dict) -> html.Div:
    """Development tasks, coding standards, metrics."""
    dev = project.get("development", {})
    tasks = dev.get("tasks", []) or []
    standards = dev.get("coding_standards", "")
    branching = dev.get("branching_strategy", "")

    ai_note = dev.get("ai_suggestions", "")
    ai_card = card(
        "AI Suggestions",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Dev metrics
    total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
    by_priority = {}
    by_status = {}
    for t in tasks:
        p = t.get("priority", "medium")
        s = t.get("status", "backlog")
        by_priority[p] = by_priority.get(p, 0) + 1
        by_status[s] = by_status.get(s, 0) + 1

    metrics_row = html.Div(
        [
            stat_card("Total Tasks", len(tasks), COLORS["accent_blue"], "📝"),
            stat_card("Total Hours", f"{total_hours:,}", COLORS["accent_green"], "⏱️"),
            stat_card("High Priority", by_priority.get("high", 0), COLORS["accent_pink"], "🔴"),
            stat_card("Done", by_status.get("done", 0), COLORS["accent_green"], "✅"),
        ],
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"},
    )

    # Standards card
    standards_items = []
    if standards:
        standards_items.append(html.Div([html.Strong("Coding Standards: "), html.Span(standards)], style={"fontSize": "13px", "marginBottom": "6px"}))
    if branching:
        standards_items.append(html.Div([html.Strong("Branching Strategy: "), html.Span(branching)], style={"fontSize": "13px"}))
    standards_card = card("Development Standards", standards_items or [empty_state("No standards defined")], "📏") if standards_items else None

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
    task_card = card(
        f"Development Tasks ({len(tasks)})",
        data_table(["ID", "Title", "Priority", "Status", "Component", "Hours"], task_rows, ["90px", "auto", "90px", "110px", "100px", "70px"]) if task_rows else empty_state("No tasks"),
        "⚙️",
    )

    # Task distribution by priority (visual)
    priority_dist = []
    for p_name, p_count in sorted(by_priority.items(), key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x[0], 4)):
        pct = (p_count / len(tasks) * 100) if tasks else 0
        pc = PRIORITY_COLORS.get(p_name, COLORS["text_secondary"])
        priority_dist.append(
            html.Div(
                [
                    html.Div(
                        [html.Span(p_name.title(), style={"fontSize": "13px", "fontWeight": "500"}), html.Span(f"{p_count}", style={"fontSize": "13px", "color": COLORS["text_secondary"]})],
                        style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"},
                    ),
                    progress_bar(pct, pc),
                ],
                style={"marginBottom": "10px"},
            )
        )
    dist_card = card("Priority Distribution", priority_dist or [empty_state("No data")], "📊")

    children = [page_header("Development", "Tasks, standards, and progress tracking", "⚙️")]
    if ai_card:
        children.append(ai_card)
    children.append(metrics_row)
    if standards_card:
        children.append(standards_card)
    children.extend([
        task_card,
        dist_card,
    ])
    return html.Div(children)


# ─── Deployment ───────────────────────────────────────────────────────────────

def build_deployment_page(project: dict) -> html.Div:
    """Deployment environments, CI/CD pipeline, monitoring."""
    dep = project.get("deployment", {})
    envs = dep.get("environments", []) or []
    pipeline = dep.get("pipeline_steps", []) or []
    monitoring = dep.get("monitoring", {}) or {}
    iac = dep.get("infrastructure_as_code", "")

    ai_note = dep.get("ai_suggestions", "")
    ai_card = card(
        "AI Suggestions",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Environments
    env_cards = []
    env_type_colors = {"development": COLORS["info"], "staging": COLORS["warning"], "production": COLORS["success"]}
    for e in envs:
        ec = env_type_colors.get(e.get("type", ""), COLORS["text_secondary"])
        config = e.get("config", {})
        config_items = []
        for k, v in config.items():
            config_items.append(html.Div([html.Strong(f"{k}: ", style={"fontSize": "12px"}), html.Span(str(v), style={"fontSize": "12px"})]))

        env_cards.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(style={"width": "10px", "height": "10px", "borderRadius": "50%", "background": ec, "marginRight": "8px"}),
                            html.Strong(e.get("name", ""), style={"fontSize": "16px"}),
                            badge(e.get("type", "").title(), ec, f"{ec}18"),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "10px"},
                    ),
                    html.Div(
                        [html.A(e.get("url", ""), href=e.get("url", "#"), style={"color": COLORS["primary"], "fontSize": "13px", "textDecoration": "none"})],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(config_items, style={"background": COLORS["bg"], "borderRadius": "6px", "padding": "8px 12px"}),
                ],
                style={**CARD_STYLE, "flex": "1", "minWidth": "250px"},
            )
        )
    envs_row = html.Div(env_cards, style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"}) if env_cards else None

    # CI/CD Pipeline (visual steps)
    steps_visual = []
    sorted_pipeline = sorted(pipeline, key=lambda x: x.get("order", 0))
    step_icons = {"quality": "🔍", "test": "🧪", "build": "🔨", "deploy": "🚀"}
    for i, step in enumerate(sorted_pipeline):
        si = step_icons.get(step.get("description", ""), "▶️")
        steps_visual.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(f"{step.get('order', i + 1)}", style={"width": "28px", "height": "28px", "borderRadius": "50%", "background": COLORS["primary"], "color": "white", "display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "13px", "fontWeight": "700"}),
                            html.Span(si, style={"fontSize": "18px"}),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "6px"},
                    ),
                    html.Strong(step.get("name", ""), style={"fontSize": "13px", "display": "block"}),
                    html.Code(step.get("command", ""), style={"fontSize": "11px", "color": COLORS["text_secondary"], "background": COLORS["bg"], "padding": "4px 8px", "borderRadius": "4px", "display": "block", "marginTop": "6px", "wordBreak": "break-all"}),
                ],
                style={
                    "background": COLORS["card_bg"],
                    "border": f"1px solid {COLORS['border']}",
                    "borderRadius": "10px",
                    "padding": "14px",
                    "flex": "1",
                    "minWidth": "180px",
                    "position": "relative",
                },
            )
        )
        if i < len(sorted_pipeline) - 1:
            steps_visual.append(
                html.Div("→", style={"fontSize": "24px", "color": COLORS["text_muted"], "display": "flex", "alignItems": "center", "padding": "0 4px"})
            )
    pipeline_card = card(
        f"CI/CD Pipeline ({len(pipeline)} steps)",
        html.Div(steps_visual, style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "alignItems": "stretch"}) if steps_visual else empty_state("No pipeline steps"),
        "🔄",
    )

    # Monitoring
    if monitoring:
        mon_items = []
        mon_icons = {"logging": "📝", "apm": "📈", "alerting": "🔔", "uptime": "🟢"}
        for k, v in monitoring.items():
            mon_items.append(
                html.Div(
                    [
                        html.Span(mon_icons.get(k, "🔧"), style={"fontSize": "18px"}),
                        html.Div(
                            [
                                html.P(k.upper(), style={"fontSize": "10px", "color": COLORS["text_secondary"], "margin": 0, "letterSpacing": "0.5px"}),
                                html.P(v, style={"fontSize": "14px", "fontWeight": "600", "margin": "2px 0 0 0"}),
                            ],
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "alignItems": "center", "padding": "10px 14px", "background": COLORS["bg"], "borderRadius": "8px"},
                )
            )
        monitoring_card = card("Monitoring & Observability", html.Div(mon_items, style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"}), "📡")
    else:
        monitoring_card = None

    # IaC
    iac_card = card(
        "Infrastructure as Code",
        html.Div([html.Code(iac, style={"fontSize": "14px", "background": COLORS["bg"], "padding": "8px 12px", "borderRadius": "6px"})]),
        "🏗️",
    ) if iac else None

    children = [page_header("Deployment", "Environments, CI/CD pipeline, and monitoring", "🚀")]
    if ai_card:
        children.append(ai_card)
    if envs_row:
        children.append(envs_row)
    children.append(pipeline_card)
    bottom_row = [c for c in [monitoring_card, iac_card] if c]
    if bottom_row:
        children.append(html.Div(bottom_row, style={"display": "grid", "gridTemplateColumns": "1fr " * len(bottom_row), "gap": "20px"}))
    return html.Div(children)


# ─── Schedule ─────────────────────────────────────────────────────────────────

def build_schedule_page(project: dict) -> html.Div:
    """Schedule with milestones, sprints, and Gantt-like view."""
    sched = project.get("schedule", {})
    milestones = sched.get("milestones", []) or []
    sprints = sched.get("sprints", []) or []
    duration = sched.get("estimated_duration_weeks", "?")

    ai_note = sched.get("ai_schedule", "")

    tasks_map = {}
    for t in project.get("development", {}).get("tasks", []) or []:
        tasks_map[t["id"]] = t

    # Duration KPI
    kpi = html.Div(
        [
            stat_card("Duration", f"{duration} weeks", COLORS["accent_blue"], "📅"),
            stat_card("Milestones", len(milestones), COLORS["accent_green"], "🎯"),
            stat_card("Sprints", len(sprints), COLORS["accent_purple"], "🔄"),
        ],
        style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
    )

    # AI note
    ai_card = card(
        "AI Schedule Analysis",
        html.P(ai_note, style={"color": COLORS["text_secondary"], "fontSize": "14px", "margin": 0}),
        "🤖",
    ) if ai_note else None

    # Milestones timeline
    ms_items = []
    ms_colors = [COLORS["primary"], COLORS["success"], COLORS["secondary"]]
    for i, ms in enumerate(milestones):
        mc = ms_colors[i % len(ms_colors)]
        ms_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                style={"width": "14px", "height": "14px", "borderRadius": "50%", "background": mc, "border": f"3px solid {mc}40", "flexShrink": 0},
                            ),
                            html.Div(
                                style={"width": "2px", "background": COLORS["border"], "flex": "1"} if i < len(milestones) - 1 else {"display": "none"},
                            ),
                        ],
                        style={"display": "flex", "flexDirection": "column", "alignItems": "center", "marginRight": "16px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    badge(ms.get("id", ""), mc, f"{mc}18"),
                                    html.Strong(f" {ms.get('name', '')}", style={"fontSize": "15px", "marginLeft": "8px"}),
                                    badge(ms.get("target_date", ""), COLORS["text_secondary"], COLORS["bg"]),
                                ],
                                style={"display": "flex", "alignItems": "center", "gap": "8px"},
                            ),
                            html.Div(
                                [badge(d, COLORS["text_secondary"], COLORS["bg"]) for d in ms.get("deliverables", [])],
                                style={"display": "flex", "flexWrap": "wrap", "gap": "4px", "marginTop": "8px"},
                            ),
                        ],
                        style={"paddingBottom": "24px"},
                    ),
                ],
                style={"display": "flex"},
            )
        )
    ms_card = card("Milestones Timeline", ms_items or [empty_state("No milestones")], "🎯")

    # Sprint cards
    sprint_items = []
    for sp in sprints:
        sp_tasks = [tasks_map.get(tid, {"id": tid, "title": tid, "status": "backlog", "estimated_hours": 0}) for tid in sp.get("tasks", [])]
        sp_hours = sum(t.get("estimated_hours", 0) for t in sp_tasks)
        task_list = []
        for t in sp_tasks:
            task_list.append(
                html.Div(
                    [
                        badge(t.get("id", ""), COLORS["primary"], COLORS["primary_light"]),
                        html.Span(t.get("title", ""), style={"fontSize": "13px", "marginLeft": "6px"}),
                        status_badge(t.get("status", "backlog")),
                        html.Span(f"{t.get('estimated_hours', 0)}h", style={"fontSize": "12px", "color": COLORS["text_secondary"], "marginLeft": "auto"}),
                    ],
                    style={"display": "flex", "alignItems": "center", "gap": "6px", "padding": "6px 0", "borderBottom": f"1px solid {COLORS['border_light']}"},
                )
            )
        goals_list = html.Ul(
            [html.Li(g, style={"fontSize": "12px", "color": COLORS["text_secondary"]}) for g in sp.get("goals", [])],
            style={"margin": "6px 0 10px 16px", "padding": 0},
        )

        sprint_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            badge(sp.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]),
                            html.Strong(f" {sp.get('name', '')}", style={"marginLeft": "8px", "fontSize": "15px"}),
                            html.Span(f"{sp_hours}h", style={"marginLeft": "auto", "fontSize": "13px", "color": COLORS["text_secondary"], "fontWeight": "600"}),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    goals_list,
                    html.Div(task_list) if task_list else html.Div(
                        html.Span("No tasks assigned", style={"color": COLORS["text_muted"], "fontSize": "13px", "fontStyle": "italic"}),
                        style={"padding": "6px 0"},
                    ),
                ],
                style={**CARD_STYLE, "marginBottom": "12px"},
            )
        )

    sprints_section = card(f"Sprint Plan ({len(sprints)} sprints)", sprint_items or [empty_state("No sprints planned")], "🔄")

    # Gantt-like visualization
    gantt_bars = []
    total_sprints = len(sprints) if sprints else 1
    sprint_colors = [PHASE_COLORS[i % len(PHASE_COLORS)] for i in range(total_sprints)]
    for i, sp in enumerate(sprints):
        sp_tasks = [tasks_map.get(tid) for tid in sp.get("tasks", [])]
        sp_hours = sum(t.get("estimated_hours", 0) for t in sp_tasks if t)
        gantt_bars.append(
            html.Div(
                [
                    html.Div(
                        sp.get("name", f"Sprint {i + 1}").split(": ")[-1] if ": " in sp.get("name", "") else sp.get("name", ""),
                        style={
                            "background": sprint_colors[i],
                            "color": "white",
                            "borderRadius": "6px",
                            "padding": "8px 14px",
                            "fontSize": "12px",
                            "fontWeight": "600",
                            "width": f"{max(100 / total_sprints, 14)}%",
                            "marginLeft": f"{(100 / total_sprints) * i}%",
                            "whiteSpace": "nowrap",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                        },
                    ),
                ],
                style={"marginBottom": "6px"},
            )
        )

    # Week markers
    week_markers = html.Div(
        [html.Span(f"W{w + 1}", style={"fontSize": "10px", "color": COLORS["text_muted"], "flex": "1", "textAlign": "center"}) for w in range(int(duration) if str(duration).isdigit() else 12)],
        style={"display": "flex", "marginTop": "8px", "borderTop": f"1px solid {COLORS['border_light']}", "paddingTop": "6px"},
    )

    gantt_card = card(
        "Timeline Overview",
        [html.Div(gantt_bars), week_markers] if gantt_bars else [empty_state("No schedule data")],
        "📊",
    )

    children = [page_header("Schedule", "Project timeline, milestones, and sprint plan", "📅"), kpi]
    if ai_card:
        children.append(ai_card)
    children.extend([
        gantt_card,
        html.Div([ms_card, sprints_section], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}),
    ])
    return html.Div(children)


# ─── Diagrams ─────────────────────────────────────────────────────────────────

def build_diagrams_page(project: dict) -> html.Div:
    """Render architecture diagrams (Mermaid)."""
    diagrams = _get(project, "architecture", "diagrams", default=[]) or []

    if not diagrams:
        return html.Div([
            page_header("Architecture Diagrams", "Visual system design", "📐"),
            empty_state("No diagrams defined. Run 'rai architecture' to generate diagrams.", "📐"),
        ])

    diagram_cards = []
    type_icons = {"component": "🏗️", "sequence": "🔄", "deployment": "☁️", "flowchart": "📊", "er": "🗄️", "class": "📦"}
    for d in diagrams:
        code = d.get("mermaid_code", "")
        dtype = d.get("type", "")
        icon = type_icons.get(dtype, "📐")
        diagram_cards.append(
            html.Div(
                [
                    html.Div(
                        [
                            badge(d.get("id", ""), COLORS["secondary"], COLORS["accent_purple"]),
                            html.Span(icon, style={"fontSize": "18px", "marginLeft": "8px"}),
                            html.Strong(f" {d.get('title', '')}", style={"marginLeft": "6px", "fontSize": "16px"}),
                            badge(dtype.title(), COLORS["text_secondary"], COLORS["bg"]),
                        ],
                        style={"display": "flex", "alignItems": "center", "gap": "4px", "marginBottom": "6px"},
                    ),
                    html.P(d.get("description", ""), style={"color": COLORS["text_secondary"], "fontSize": "13px", "margin": "0 0 12px 0"}),
                    mermaid_div(code, d.get("id", "mmd")),
                ],
                style={**CARD_STYLE},
            )
        )

    return html.Div([
        page_header("Architecture Diagrams", f"{len(diagrams)} diagram(s) — rendered with Mermaid.js", "📐"),
        html.Div(
            html.P(
                "Note: Mermaid diagrams require JavaScript rendering. If diagrams don't appear, open in a browser with JS enabled.",
                style={"color": COLORS["text_secondary"], "fontSize": "12px", "fontStyle": "italic", "margin": "0 0 20px 0"},
            ),
        ),
        *diagram_cards,
    ])


# ─── Full Report ──────────────────────────────────────────────────────────────

def build_report_page(project: dict) -> html.Div:
    """Comprehensive combined report of all phases."""
    sections = []

    # Header
    sections.append(
        html.Div(
            [
                html.H1(project.get("name", "Project Report"), style={"fontSize": "32px", "fontWeight": "700", "margin": "0 0 8px 0"}),
                html.P(project.get("description", ""), style={"color": COLORS["text_secondary"], "fontSize": "16px", "lineHeight": "1.5", "margin": "0 0 16px 0"}),
                html.Div(
                    [
                        badge(f"v{project.get('version', '0.1.0')}", COLORS["primary"], COLORS["primary_light"]),
                        badge(f"Created: {project.get('created_at', '—')[:10]}", COLORS["text_secondary"], COLORS["bg"]),
                        badge(f"Updated: {project.get('updated_at', '—')[:10]}", COLORS["text_secondary"], COLORS["bg"]),
                    ],
                    style={"display": "flex", "gap": "8px"},
                ),
            ],
            style={**CARD_STYLE, "background": f"linear-gradient(135deg, {COLORS['primary_light']}, {COLORS['accent_purple']})", "marginBottom": "32px"},
        )
    )

    # Executive summary
    phases = _phase_progress(project)
    completed = sum(1 for p in phases if p["status"] == "completed")
    reqs = _get(project, "requirements", "requirements", default=[]) or []
    members = _get(project, "roles", "members", default=[]) or []
    tasks = _get(project, "development", "tasks", default=[]) or []
    total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
    duration = _get(project, "schedule", "estimated_duration_weeks", default="?")

    sections.append(card(
        "Executive Summary",
        html.Div([
            html.P(f"This report covers the complete AI-powered software engineering lifecycle for ", style={"fontSize": "14px", "margin": "0 0 4px 0"}),
            html.P([html.Strong(project.get("name", "")), html.Span(f" — {project.get('description', '')}")], style={"fontSize": "14px", "margin": "0 0 12px 0"}),
            html.Div(
                [
                    html.Div([html.Strong(f"{len(reqs)}"), html.Span(" Requirements")], style={"textAlign": "center", "padding": "12px"}),
                    html.Div([html.Strong(f"{len(members)}"), html.Span(" Team Members")], style={"textAlign": "center", "padding": "12px"}),
                    html.Div([html.Strong(f"{len(tasks)}"), html.Span(" Dev Tasks")], style={"textAlign": "center", "padding": "12px"}),
                    html.Div([html.Strong(f"{total_hours:,}"), html.Span(" Hours Est.")], style={"textAlign": "center", "padding": "12px"}),
                    html.Div([html.Strong(f"{duration}"), html.Span(" Weeks")], style={"textAlign": "center", "padding": "12px"}),
                    html.Div([html.Strong(f"{completed}/{len(phases)}"), html.Span(" Phases Done")], style={"textAlign": "center", "padding": "12px"}),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(6, 1fr)", "background": COLORS["bg"], "borderRadius": "8px", "marginTop": "12px"},
            ),
        ]),
        "📊",
    ))

    # Each phase as a sub-section
    sections.append(html.H2("📋 Requirements Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[0]}", "paddingBottom": "8px"}))
    sections.append(build_requirements_page(project))

    sections.append(html.H2("👥 Team & Roles Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[1]}", "paddingBottom": "8px"}))
    sections.append(build_roles_page(project))

    sections.append(html.H2("🏗️ Architecture Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[2]}", "paddingBottom": "8px"}))
    sections.append(build_architecture_page(project))

    sections.append(html.H2("⚙️ Development Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[3]}", "paddingBottom": "8px"}))
    sections.append(build_development_page(project))

    sections.append(html.H2("🚀 Deployment Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[4]}", "paddingBottom": "8px"}))
    sections.append(build_deployment_page(project))

    sections.append(html.H2("📅 Schedule Phase", style={"fontSize": "22px", "margin": "32px 0 16px 0", "borderBottom": f"2px solid {PHASE_COLORS[5]}", "paddingBottom": "8px"}))
    sections.append(build_schedule_page(project))

    return html.Div(sections)
