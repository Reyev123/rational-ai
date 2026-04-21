"""Theme constants for the Rational AI platform GUI."""

COLORS = {
    "primary": "#4A90D9",
    "primary_dark": "#3A7BC8",
    "primary_light": "#E8F4FD",
    "secondary": "#6C5CE7",
    "secondary_light": "#F5F0FF",
    "success": "#00B894",
    "success_light": "#E8FFF8",
    "warning": "#FDCB6E",
    "warning_light": "#FFF8E7",
    "danger": "#E17055",
    "danger_light": "#FFF0F0",
    "info": "#74B9FF",
    "bg": "#F8FAFB",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#1A1D23",
    "sidebar_text": "#A0A4AE",
    "sidebar_active": "#4A90D9",
    "sidebar_hover": "#2A2D35",
    "text": "#2D3436",
    "text_secondary": "#636E72",
    "text_muted": "#B2BEC3",
    "border": "#E8ECEF",
    "border_light": "#F1F3F5",
    "input_bg": "#FFFFFF",
    "input_border": "#D1D5DB",
    "accent_blue": "#DCEEFB",
    "accent_green": "#E8FFE8",
    "accent_yellow": "#FFF8E7",
    "accent_purple": "#F5F0FF",
    "accent_pink": "#FFF0F5",
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
    "configured": "#00B894",
}

PHASE_COLORS = {
    "requirements": "#4A90D9",
    "roles": "#6C5CE7",
    "architecture": "#00B894",
    "development": "#E17055",
    "deployment": "#FDCB6E",
    "schedule": "#00CEC9",
}

EXTERNAL_CSS = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
]

MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

# ── Reusable Styles ──────────────────────────────────────────────────────────

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
    "margin": "0",
}

INPUT_STYLE = {
    "width": "100%",
    "padding": "10px 14px",
    "borderRadius": "8px",
    "border": f"1px solid {COLORS['input_border']}",
    "fontSize": "14px",
    "fontFamily": "inherit",
    "background": COLORS["input_bg"],
    "color": COLORS["text"],
    "boxSizing": "border-box",
}

TEXTAREA_STYLE = {
    **INPUT_STYLE,
    "minHeight": "80px",
    "resize": "vertical",
}

SELECT_STYLE = {
    **INPUT_STYLE,
    "cursor": "pointer",
}

BTN_PRIMARY = {
    "padding": "10px 24px",
    "borderRadius": "8px",
    "border": "none",
    "background": COLORS["primary"],
    "color": "white",
    "fontSize": "14px",
    "fontWeight": "600",
    "cursor": "pointer",
    "fontFamily": "inherit",
    "transition": "all 0.2s",
}

BTN_SUCCESS = {**BTN_PRIMARY, "background": COLORS["success"]}
BTN_DANGER = {**BTN_PRIMARY, "background": COLORS["danger"]}
BTN_SECONDARY = {
    **BTN_PRIMARY,
    "background": "transparent",
    "color": COLORS["text"],
    "border": f"1px solid {COLORS['border']}",
}

BTN_PHASE = {
    "padding": "12px 20px",
    "borderRadius": "10px",
    "border": "none",
    "fontSize": "14px",
    "fontWeight": "600",
    "cursor": "pointer",
    "fontFamily": "inherit",
    "color": "white",
    "display": "flex",
    "alignItems": "center",
    "gap": "8px",
    "transition": "all 0.2s",
    "width": "100%",
    "justifyContent": "center",
}

LABEL_STYLE = {
    "display": "block",
    "fontSize": "13px",
    "fontWeight": "600",
    "color": COLORS["text_secondary"],
    "marginBottom": "6px",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
}

FORM_GROUP = {"marginBottom": "16px"}
