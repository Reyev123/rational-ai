"""Theme constants for the Rational AI GUI."""

COLORS = {
    "primary": "#4A90D9",
    "primary_light": "#E8F4FD",
    "secondary": "#6C5CE7",
    "success": "#00B894",
    "success_light": "#E8FFF8",
    "warning": "#FDCB6E",
    "warning_light": "#FFF8E7",
    "danger": "#E17055",
    "danger_light": "#FFF0F0",
    "info": "#74B9FF",
    "bg": "#F8FAFB",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#FFFFFF",
    "text": "#2D3436",
    "text_secondary": "#636E72",
    "text_muted": "#B2BEC3",
    "border": "#E8ECEF",
    "border_light": "#F1F3F5",
    "accent_blue": "#DCEEFB",
    "accent_green": "#E8FFE8",
    "accent_yellow": "#FFF8E7",
    "accent_purple": "#F5F0FF",
    "accent_pink": "#FFF0F5",
    "accent_teal": "#F0FFFF",
}

PRIORITY_COLORS = {
    "critical": "#E74C3C",
    "high": "#E17055",
    "medium": "#FDCB6E",
    "low": "#00B894",
}

STATUS_COLORS = {
    "not_started": "#B2BEC3",
    "in_progress": "#74B9FF",
    "review": "#FDCB6E",
    "completed": "#00B894",
    "backlog": "#B2BEC3",
    "todo": "#74B9FF",
    "blocked": "#E17055",
    "done": "#00B894",
}

PHASE_COLORS = [
    "#4A90D9",  # Requirements
    "#6C5CE7",  # Roles
    "#00B894",  # Architecture
    "#E17055",  # Development
    "#FDCB6E",  # Deployment
    "#00CEC9",  # Schedule
]

EXTERNAL_CSS = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
]

MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs"

# ── Reusable style helpers ────────────────────────────────────────────────────

CARD_STYLE = {
    "background": COLORS["card_bg"],
    "borderRadius": "12px",
    "padding": "24px",
    "marginBottom": "20px",
    "border": f"1px solid {COLORS['border']}",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.04)",
}

BADGE_BASE = {
    "display": "inline-block",
    "padding": "3px 10px",
    "borderRadius": "12px",
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
}

TABLE_HEADER_STYLE = {
    "background": COLORS["bg"],
    "color": COLORS["text_secondary"],
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
    "padding": "10px 14px",
    "borderBottom": f"2px solid {COLORS['border']}",
    "textAlign": "left",
}

TABLE_CELL_STYLE = {
    "padding": "12px 14px",
    "borderBottom": f"1px solid {COLORS['border_light']}",
    "fontSize": "13px",
    "verticalAlign": "top",
}

SECTION_TITLE_STYLE = {
    "fontSize": "18px",
    "fontWeight": "600",
    "color": COLORS["text"],
    "margin": "0 0 16px 0",
}

PAGE_TITLE_STYLE = {
    "fontSize": "28px",
    "fontWeight": "700",
    "color": COLORS["text"],
    "margin": "0 0 8px 0",
}
