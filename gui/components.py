"""Reusable UI components for Rational AI GUI."""

from __future__ import annotations

from dash import html

from gui.theme import (
    BADGE_BASE,
    CARD_STYLE,
    COLORS,
    PAGE_TITLE_STYLE,
    PRIORITY_COLORS,
    SECTION_TITLE_STYLE,
    STATUS_COLORS,
    TABLE_CELL_STYLE,
    TABLE_HEADER_STYLE,
)


def page_header(title: str, subtitle: str = "", icon: str = "") -> html.Div:
    """Page title with optional subtitle."""
    children = []
    if icon:
        children.append(html.Span(icon, style={"fontSize": "32px", "marginRight": "12px"}))
    children.append(html.H1(title, style=PAGE_TITLE_STYLE))
    elements = [html.Div(children, style={"display": "flex", "alignItems": "center"})]
    if subtitle:
        elements.append(
            html.P(subtitle, style={"color": COLORS["text_secondary"], "margin": "0 0 24px 0", "fontSize": "14px"})
        )
    return html.Div(elements, style={"marginBottom": "24px"})


def card(title: str, children, icon: str = "", extra_style: dict | None = None) -> html.Div:
    """Styled card wrapper."""
    style = {**CARD_STYLE, **(extra_style or {})}
    header_children = []
    if icon:
        header_children.append(html.Span(icon, style={"marginRight": "8px"}))
    header_children.append(html.Span(title))
    return html.Div(
        [
            html.H3(header_children, style=SECTION_TITLE_STYLE),
            html.Div(children),
        ],
        style=style,
    )


def stat_card(label: str, value: str | int, color: str = "", icon: str = "") -> html.Div:
    """Small stat card for KPI display."""
    bg = color or COLORS["primary_light"]
    return html.Div(
        [
            html.Div(
                [
                    html.Span(icon, style={"fontSize": "24px"}) if icon else None,
                    html.P(
                        str(value),
                        style={"fontSize": "32px", "fontWeight": "700", "margin": "8px 0 4px 0", "color": COLORS["text"]},
                    ),
                    html.P(
                        label,
                        style={"fontSize": "12px", "color": COLORS["text_secondary"], "margin": "0", "textTransform": "uppercase", "letterSpacing": "0.5px"},
                    ),
                ],
            ),
        ],
        style={
            "background": bg,
            "borderRadius": "12px",
            "padding": "20px",
            "textAlign": "center",
            "minWidth": "140px",
            "flex": "1",
        },
    )


def badge(text: str, color: str = "", bg: str = "") -> html.Span:
    """Colored badge/tag."""
    c = color or COLORS["text_secondary"]
    b = bg or COLORS["bg"]
    return html.Span(text, style={**BADGE_BASE, "color": c, "background": b})


def priority_badge(priority: str) -> html.Span:
    """Priority-colored badge."""
    c = PRIORITY_COLORS.get(priority, COLORS["text_secondary"])
    return html.Span(
        priority.upper(),
        style={**BADGE_BASE, "color": c, "background": f"{c}18", "border": f"1px solid {c}40"},
    )


def status_badge(status: str) -> html.Span:
    """Status-colored badge."""
    c = STATUS_COLORS.get(status, COLORS["text_secondary"])
    label = status.replace("_", " ").title()
    return html.Span(
        label,
        style={**BADGE_BASE, "color": c, "background": f"{c}18", "border": f"1px solid {c}40"},
    )


def data_table(headers: list[str], rows: list[list], col_widths: list[str] | None = None) -> html.Table:
    """Styled HTML table."""
    thead = html.Thead(
        html.Tr([html.Th(h, style={**TABLE_HEADER_STYLE, "width": w if col_widths and i < len(col_widths) else "auto"}) for i, (h, w) in enumerate(zip(headers, col_widths or ["auto"] * len(headers)))])
    )
    tbody_rows = []
    for row in rows:
        cells = []
        for cell in row:
            if isinstance(cell, (html.Span, html.Div, html.A)):
                cells.append(html.Td(cell, style=TABLE_CELL_STYLE))
            else:
                cells.append(html.Td(str(cell) if cell is not None else "", style=TABLE_CELL_STYLE))
        tbody_rows.append(html.Tr(cells, style={"transition": "background 0.15s"}))
    tbody = html.Tbody(tbody_rows)
    return html.Table(
        [thead, tbody],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "background": COLORS["card_bg"],
            "borderRadius": "8px",
            "overflow": "hidden",
        },
    )


def progress_bar(value: float, color: str = "", label: str = "") -> html.Div:
    """Horizontal progress bar."""
    c = color or COLORS["primary"]
    return html.Div(
        [
            html.Div(
                style={
                    "width": f"{min(value, 100)}%",
                    "height": "8px",
                    "background": c,
                    "borderRadius": "4px",
                    "transition": "width 0.5s ease",
                },
            ),
            html.Span(
                label or f"{value:.0f}%",
                style={"fontSize": "11px", "color": COLORS["text_secondary"], "marginLeft": "8px"},
            ) if label or value else None,
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "background": COLORS["bg"],
            "borderRadius": "4px",
            "overflow": "hidden",
            "flex": "1",
        },
    )


def mermaid_div(code: str, diagram_id: str = "mermaid-1") -> html.Div:
    """Wrapper for Mermaid diagram rendering."""
    return html.Div(
        [
            html.Pre(
                code,
                className="mermaid",
                style={"background": "transparent", "border": "none", "textAlign": "center"},
            ),
        ],
        style={
            "background": COLORS["card_bg"],
            "borderRadius": "12px",
            "padding": "24px",
            "border": f"1px solid {COLORS['border']}",
            "marginBottom": "20px",
            "overflow": "auto",
        },
    )


def empty_state(message: str = "No data available", icon: str = "📭") -> html.Div:
    """Empty state placeholder."""
    return html.Div(
        [
            html.Span(icon, style={"fontSize": "48px"}),
            html.P(message, style={"color": COLORS["text_secondary"], "marginTop": "12px"}),
        ],
        style={"textAlign": "center", "padding": "60px 20px"},
    )
