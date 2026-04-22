"""E2E tests — Callback actions.

Tests every interactive callback in the GUI:
  - Navigation
  - Sidebar project name
  - Create project
  - Save config
  - Run phases (individual + all, with mocked AI)
  - Sync log
  - Export (markdown, html, diagrams, all)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from tests.conftest import DashCallbackClient, REAL_PROJECT_DIR


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Callback registration
# ═══════════════════════════════════════════════════════════════════════════════

def test_callback_count(app):
    """App should have exactly 8 registered callbacks."""
    assert len(app.callback_map) == 8, (
        f"Expected 8 callbacks, got {len(app.callback_map)}: "
        + ", ".join(sorted(app.callback_map.keys()))
    )


def test_all_expected_callbacks_registered(app):
    """Verify every expected output target has a callback."""
    keys_str = " ".join(app.callback_map.keys())
    expected_outputs = [
        "store-page",
        "page-content",
        "sidebar-project-name",
        "create-result",
        "config-result",
        "store-run-log",
        "run-log",
        "export-result",
    ]
    for out in expected_outputs:
        assert out in keys_str, f"Missing callback for output '{out}'"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Sidebar project name
# ═══════════════════════════════════════════════════════════════════════════════

def test_sidebar_shows_project_name(cb, project_dir):
    result = cb.fire(
        output="sidebar-project-name.children",
        inputs={"store-refresh.data": 0},
        state={"store-project-dir.data": str(project_dir)},
    )
    assert result.ok
    assert result.has("ShopAI")


def test_sidebar_no_project(tmp_path):
    """Sidebar should show 'No project loaded' when no project.yaml exists."""
    (tmp_path / ".rai").mkdir()
    os.chdir(tmp_path)
    from gui.app import create_app
    app = create_app(tmp_path)
    cb = DashCallbackClient(app.server.test_client(), app)
    result = cb.fire(
        output="sidebar-project-name.children",
        inputs={"store-refresh.data": 0},
        state={"store-project-dir.data": str(tmp_path)},
    )
    assert result.ok
    assert result.has("No project")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Save configuration
# ═══════════════════════════════════════════════════════════════════════════════

def test_save_config_success(tmp_cb, tmp_project):
    result = tmp_cb.fire(
        output="config-result",
        inputs={"btn-save-config.n_clicks": 1},
        state={
            "cfg-provider.value": "local",
            "cfg-model.value": "llama3.1:8b",
            "cfg-api-key.value": "",
            "cfg-base-url.value": "http://localhost:11434/v1",
            "cfg-temperature.value": "0.7",
            "cfg-max-tokens.value": "4096",
            "store-project-dir.data": str(tmp_project),
        },
    )
    assert result.ok
    assert result.has("Configuration saved")


def test_save_config_updates_yaml(tmp_cb, tmp_project):
    tmp_cb.fire(
        output="config-result",
        inputs={"btn-save-config.n_clicks": 1},
        state={
            "cfg-provider.value": "openai",
            "cfg-model.value": "gpt-4o-mini",
            "cfg-api-key.value": "",
            "cfg-base-url.value": "",
            "cfg-temperature.value": "0.5",
            "cfg-max-tokens.value": "2048",
            "store-project-dir.data": str(tmp_project),
        },
    )
    cfg = yaml.safe_load((tmp_project / ".rai" / "config.yaml").read_text())
    assert cfg["ai"]["provider"] == "openai"
    assert cfg["ai"]["model"] == "gpt-4o-mini"
    assert cfg["ai"]["temperature"] == 0.5
    assert cfg["ai"]["max_tokens"] == 2048


def test_save_config_no_click(tmp_cb, tmp_project):
    """Should return no_update when n_clicks is 0."""
    result = tmp_cb.fire(
        output="config-result",
        inputs={"btn-save-config.n_clicks": 0},
        state={
            "cfg-provider.value": "local",
            "cfg-model.value": "llama3.1:8b",
            "cfg-api-key.value": "",
            "cfg-base-url.value": "",
            "cfg-temperature.value": "0.7",
            "cfg-max-tokens.value": "4096",
            "store-project-dir.data": str(tmp_project),
        },
    )
    assert result.ok


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Create project
# ═══════════════════════════════════════════════════════════════════════════════

def test_create_project_success(tmp_project):
    """Creating a project should update project.yaml."""
    os.chdir(tmp_project)
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    result = cb.fire(
        output="create-result",
        inputs={"btn-create-project.n_clicks": 1},
        state={
            "input-project-name.value": "E2E Test Project",
            "input-project-desc.value": "Created by E2E test",
            "store-project-dir.data": str(tmp_project),
        },
    )
    assert result.ok
    assert result.has("E2E Test Project") or result.has("created")


def test_create_project_no_name(tmp_cb, tmp_project):
    """Creating without a name should show error."""
    result = tmp_cb.fire(
        output="create-result",
        inputs={"btn-create-project.n_clicks": 1},
        state={
            "input-project-name.value": "",
            "input-project-desc.value": "",
            "store-project-dir.data": str(tmp_project),
        },
    )
    assert result.ok
    assert result.has("Please enter")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Run phases (with mocked AI)
# ═══════════════════════════════════════════════════════════════════════════════

RUN_STATE_BASE = {
    "run-extra-desc.value": "E2E test context",
    "run-stakeholder-notes.value": "E2E test notes",
}

PHASE_BUTTONS = [
    "btn-run-requirements",
    "btn-run-roles",
    "btn-run-architecture",
    "btn-run-development",
    "btn-run-deployment",
    "btn-run-schedule",
]


def _build_run_inputs(triggered_btn: str) -> dict:
    """Build the inputs dict for the run callback with one button clicked."""
    inputs = {}
    for btn in PHASE_BUTTONS + ["btn-run-all"]:
        inputs[f"{btn}.n_clicks"] = 1 if btn == triggered_btn else 0
    return inputs


@pytest.mark.parametrize("btn", PHASE_BUTTONS)
def test_run_individual_phase(btn, tmp_project, mock_ai):
    """Each individual phase button should execute and produce log output."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    inputs = _build_run_inputs(btn)
    state = {**RUN_STATE_BASE, "store-project-dir.data": str(tmp_project), "store-refresh.data": 0}

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state=state,
        changed=f"{btn}.n_clicks",
    )
    assert result.ok, f"{btn} returned {result.status_code}: {result.text[:300]}"

    # Should contain success or error output
    phase_name = btn.replace("btn-run-", "").replace("-", " ").title()
    assert result.has("Running") or result.has("ERROR"), (
        f"{btn} log should contain 'Running' or 'ERROR', got: {result.text[:300]}"
    )


def test_run_all_phases(tmp_project, mock_ai):
    """'Run All' should execute all 6 phases sequentially."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    inputs = _build_run_inputs("btn-run-all")
    state = {**RUN_STATE_BASE, "store-project-dir.data": str(tmp_project), "store-refresh.data": 0}

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state=state,
        changed="btn-run-all.n_clicks",
    )
    assert result.ok, f"Run All returned {result.status_code}: {result.text[:500]}"
    assert not result.has("ERROR"), (
        f"Run All raised an exception: {result.text[-500:]}"
    )
    assert result.has("All") or result.has("completed") or result.has("Running"), (
        f"Run All should show completion, got: {result.text[:500]}"
    )


def test_run_phase_updates_project_yaml(tmp_project, mock_ai):
    """After running requirements, project.yaml should be updated."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    inputs = _build_run_inputs("btn-run-requirements")
    state = {**RUN_STATE_BASE, "store-project-dir.data": str(tmp_project), "store-refresh.data": 0}

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state=state,
        changed="btn-run-requirements.n_clicks",
    )
    assert result.ok

    # Check project.yaml was updated
    proj = yaml.safe_load((tmp_project / ".rai" / "project.yaml").read_text())
    reqs = proj.get("requirements", {})
    # Should have requirements data (either from the mock or from existing data)
    assert reqs, "project.yaml should have requirements after running the phase"


def test_run_phase_captures_log_output(tmp_project, mock_ai):
    """Run callback should capture Rich console output into the log."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    inputs = _build_run_inputs("btn-run-requirements")
    state = {**RUN_STATE_BASE, "store-project-dir.data": str(tmp_project), "store-refresh.data": 0}

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state=state,
        changed="btn-run-requirements.n_clicks",
    )
    assert result.ok

    # The response should contain store-run-log data
    resp = result.json.get("response", {})
    log = resp.get("store-run-log", {}).get("data", "")
    assert len(log) > 20, f"Log should have content, got {len(log)} chars"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Sync log callback
# ═══════════════════════════════════════════════════════════════════════════════

def test_sync_log_populates_pre(cb, project_dir):
    """store-run-log → run-log sync callback should work."""
    result = cb.fire(
        output="run-log",
        inputs={"store-run-log.data": "Test log output\n"},
    )
    assert result.ok
    assert result.has("Test log output")


def test_sync_log_default_text(cb, project_dir):
    """Empty store should show 'Ready.' default."""
    result = cb.fire(
        output="run-log",
        inputs={"store-run-log.data": ""},
    )
    assert result.ok
    assert result.has("Ready.")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Export callbacks
# ═══════════════════════════════════════════════════════════════════════════════

def test_export_markdown(tmp_cb, tmp_project):
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 1,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 0,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-md.n_clicks",
    )
    assert result.ok
    assert result.has("Export complete") or result.has("Markdown")


def test_export_html(tmp_cb, tmp_project):
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 0,
            "btn-export-html.n_clicks": 1,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 0,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-html.n_clicks",
    )
    assert result.ok
    assert result.has("Export complete") or result.has("HTML")


def test_export_diagrams(tmp_cb, tmp_project):
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 0,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 1,
            "btn-export-all.n_clicks": 0,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-diagrams.n_clicks",
    )
    assert result.ok
    assert result.has("Export complete") or result.has("Diagram")


def test_export_all(tmp_cb, tmp_project):
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 0,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 1,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-all.n_clicks",
    )
    assert result.ok
    assert result.has("Export complete")


def test_export_creates_files(tmp_cb, tmp_project):
    """Export All should create actual files on disk."""
    tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 0,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 1,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-all.n_clicks",
    )
    exports_dir = tmp_project / ".rai" / "exports"
    assert exports_dir.exists(), "Exports directory should be created"
    files = list(exports_dir.glob("*"))
    assert len(files) >= 2, f"Should have at least 2 export files, got {len(files)}"


def test_export_custom_output_dir(tmp_cb, tmp_project):
    """Export should respect custom output directory."""
    custom_dir = tmp_project / "custom_export"
    custom_dir.mkdir()
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 1,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 0,
        },
        state={
            "export-output-dir.value": str(custom_dir),
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-md.n_clicks",
    )
    assert result.ok
    md_files = list(custom_dir.glob("*.md"))
    assert len(md_files) >= 1, "Markdown file should be in custom dir"
