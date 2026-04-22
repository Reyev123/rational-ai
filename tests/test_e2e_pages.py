"""E2E tests — Page rendering.

Validates that every page in the GUI renders correctly (HTTP 200)
and contains the expected key elements.
"""

from __future__ import annotations

import pytest
from tests.conftest import REAL_PROJECT_DIR


# ═══════════════════════════════════════════════════════════════════════════════
# 1. All pages render (HTTP 200)
# ═══════════════════════════════════════════════════════════════════════════════

ALL_PAGES = [
    "dashboard",
    "project",
    "config",
    "run",
    "requirements",
    "roles",
    "architecture",
    "development",
    "deployment",
    "schedule",
    "diagrams",
    "export",
]


@pytest.mark.parametrize("page", ALL_PAGES)
def test_page_renders(cb, project_dir, page):
    """Every page returns HTTP 200."""
    result = cb.render_page(page, project_dir)
    assert result.ok, f"Page '{page}' returned {result.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Dashboard page
# ═══════════════════════════════════════════════════════════════════════════════

def test_dashboard_shows_project_name(cb, project_dir):
    result = cb.render_page("dashboard", project_dir)
    assert result.has("ShopAI"), "Dashboard should show the project name"


def test_dashboard_has_phase_stats(cb, project_dir):
    result = cb.render_page("dashboard", project_dir)
    # Dashboard shows phase status badges
    assert result.has("Requirements", "Architecture", "Deployment")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Create / Open page
# ═══════════════════════════════════════════════════════════════════════════════

def test_project_page_has_form(cb, project_dir):
    result = cb.render_page("project", project_dir)
    assert result.has("input-project-name", "input-project-desc", "btn-create-project")


def test_project_page_shows_current_project(cb, project_dir):
    result = cb.render_page("project", project_dir)
    assert result.has("ShopAI")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Configuration page
# ═══════════════════════════════════════════════════════════════════════════════

def test_config_page_has_all_fields(cb, project_dir):
    result = cb.render_page("config", project_dir)
    assert result.has(
        "cfg-provider",
        "cfg-model",
        "cfg-api-key",
        "cfg-base-url",
        "cfg-temperature",
        "cfg-max-tokens",
        "btn-save-config",
    )


def test_config_page_shows_current_provider(cb, project_dir):
    result = cb.render_page("config", project_dir)
    assert result.has("local") or result.has("openai")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Run Phases page
# ═══════════════════════════════════════════════════════════════════════════════

def test_run_page_has_all_phase_buttons(cb, project_dir):
    result = cb.render_page("run", project_dir)
    assert result.has(
        "btn-run-requirements",
        "btn-run-roles",
        "btn-run-architecture",
        "btn-run-development",
        "btn-run-deployment",
        "btn-run-schedule",
        "btn-run-all",
    )


def test_run_page_has_log_panel(cb, project_dir):
    result = cb.render_page("run", project_dir)
    assert result.has("run-log")


def test_run_page_has_textarea_fields(cb, project_dir):
    result = cb.render_page("run", project_dir)
    assert result.has("run-extra-desc", "run-stakeholder-notes")


def test_run_page_has_loading_component(cb, project_dir):
    result = cb.render_page("run", project_dir)
    assert result.has("Loading")


def test_run_page_shows_phase_status(cb, project_dir):
    result = cb.render_page("run", project_dir)
    # Should show status badges for each phase
    assert result.has("Requirements", "Team")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Requirements page
# ═══════════════════════════════════════════════════════════════════════════════

def test_requirements_page_shows_data(cb, project_dir):
    result = cb.render_page("requirements", project_dir)
    assert result.has("REQ-")


def test_requirements_page_has_use_cases(cb, project_dir):
    result = cb.render_page("requirements", project_dir)
    assert result.has("UC-")


def test_requirements_page_has_acceptance_criteria(cb, project_dir):
    result = cb.render_page("requirements", project_dir)
    assert result.has("Acceptance Criteria")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Team & Roles page
# ═══════════════════════════════════════════════════════════════════════════════

def test_roles_page_shows_members(cb, project_dir):
    result = cb.render_page("roles", project_dir)
    assert result.has("TM-")


def test_roles_page_has_raci(cb, project_dir):
    result = cb.render_page("roles", project_dir)
    assert result.has("RACI")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Architecture page
# ═══════════════════════════════════════════════════════════════════════════════

def test_architecture_page_shows_components(cb, project_dir):
    result = cb.render_page("architecture", project_dir)
    assert result.has("COMP-")


def test_architecture_page_has_tech_stack(cb, project_dir):
    result = cb.render_page("architecture", project_dir)
    assert result.has("Technology Stack") or result.has("technology")


def test_architecture_page_has_decisions(cb, project_dir):
    result = cb.render_page("architecture", project_dir)
    assert result.has("ADR-") or result.has("Decision")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Development page
# ═══════════════════════════════════════════════════════════════════════════════

def test_development_page_shows_tasks(cb, project_dir):
    result = cb.render_page("development", project_dir)
    assert result.has("TASK-")


def test_development_page_has_standards(cb, project_dir):
    result = cb.render_page("development", project_dir)
    assert result.has("Standards") or result.has("Branching") or result.has("coding")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Deployment page
# ═══════════════════════════════════════════════════════════════════════════════

def test_deployment_page_has_environments(cb, project_dir):
    result = cb.render_page("deployment", project_dir)
    assert result.has("production") or result.has("staging") or result.has("Environment")


def test_deployment_page_has_pipeline(cb, project_dir):
    result = cb.render_page("deployment", project_dir)
    assert result.has("Pipeline") or result.has("pipeline")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Schedule page
# ═══════════════════════════════════════════════════════════════════════════════

def test_schedule_page_has_milestones(cb, project_dir):
    result = cb.render_page("schedule", project_dir)
    assert result.has("MS-") or result.has("Milestone")


def test_schedule_page_has_sprints(cb, project_dir):
    result = cb.render_page("schedule", project_dir)
    assert result.has("Sprint") or result.has("SP-")


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Diagrams page
# ═══════════════════════════════════════════════════════════════════════════════

def test_diagrams_page_shows_diagrams(cb, project_dir):
    result = cb.render_page("diagrams", project_dir)
    assert result.has("DIAG-") or result.has("Diagram")


def test_diagrams_page_has_mermaid_code(cb, project_dir):
    result = cb.render_page("diagrams", project_dir)
    assert result.has("mermaid") or result.has("graph")


# ═══════════════════════════════════════════════════════════════════════════════
# 13. Export page
# ═══════════════════════════════════════════════════════════════════════════════

def test_export_page_has_buttons(cb, project_dir):
    result = cb.render_page("export", project_dir)
    assert result.has(
        "btn-export-md",
        "btn-export-html",
        "btn-export-diagrams",
        "btn-export-all",
    )


def test_export_page_has_output_dir_field(cb, project_dir):
    result = cb.render_page("export", project_dir)
    assert result.has("export-output-dir")


# ═══════════════════════════════════════════════════════════════════════════════
# 14. No-project rendering (all view pages show empty state)
# ═══════════════════════════════════════════════════════════════════════════════

EMPTY_PAGES = [
    "run",
    "requirements",
    "roles",
    "architecture",
    "development",
    "deployment",
    "schedule",
    "diagrams",
    "export",
]


@pytest.mark.parametrize("page", EMPTY_PAGES)
def test_pages_render_with_no_project(page, tmp_path):
    """Pages should render gracefully even when no project.yaml exists."""
    import os
    from gui.app import create_app

    (tmp_path / ".rai").mkdir()
    os.chdir(tmp_path)
    app = create_app(tmp_path)
    from tests.conftest import DashCallbackClient
    cb = DashCallbackClient(app.server.test_client(), app)
    result = cb.render_page(page, tmp_path)
    assert result.ok, f"Empty '{page}' page returned {result.status_code}"
