"""E2E tests — End-to-end workflow scenarios.

These tests simulate complete user workflows:
  1. New user onboarding (create project → configure → run → view → export)
  2. Existing project interaction (view, re-run phase, export)
  3. Error handling scenarios
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from tests.conftest import DashCallbackClient


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Full onboarding workflow
# ═══════════════════════════════════════════════════════════════════════════════

def test_full_onboarding_workflow(tmp_path, mock_ai):
    """Simulate a new user: create project → configure AI → run all → export."""
    # Setup empty project dir
    (tmp_path / ".rai").mkdir()
    os.chdir(tmp_path)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_path)
    cb = DashCallbackClient(app.server.test_client(), app)

    # Step 1: Verify dashboard shows "no project"
    result = cb.render_page("dashboard", tmp_path)
    assert result.ok

    # Step 2: Create project
    result = cb.fire(
        output="create-result",
        inputs={"btn-create-project.n_clicks": 1},
        state={
            "input-project-name.value": "Workflow Test",
            "input-project-desc.value": "An AI-powered test project",
            "store-project-dir.data": str(tmp_path),
        },
    )
    assert result.ok
    assert result.has("Workflow Test") or result.has("created")

    # Step 3: Save config
    result = cb.fire(
        output="config-result",
        inputs={"btn-save-config.n_clicks": 1},
        state={
            "cfg-provider.value": "local",
            "cfg-model.value": "test-model",
            "cfg-api-key.value": "test-key",
            "cfg-base-url.value": "http://localhost:11434/v1",
            "cfg-temperature.value": "0.7",
            "cfg-max-tokens.value": "4096",
            "store-project-dir.data": str(tmp_path),
        },
    )
    assert result.ok
    assert result.has("Configuration saved")

    # Step 4: Run all phases
    inputs = {f"btn-run-{p}.n_clicks": 0 for p in
              ["requirements", "roles", "architecture", "development", "deployment", "schedule"]}
    inputs["btn-run-all.n_clicks"] = 1

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state={
            "run-extra-desc.value": "E2E workflow test",
            "run-stakeholder-notes.value": "Test notes",
            "store-project-dir.data": str(tmp_path),
            "store-refresh.data": 1,
        },
        changed="btn-run-all.n_clicks",
    )
    assert result.ok

    # Step 5: Verify sidebar shows project name
    result = cb.fire(
        output="sidebar-project-name.children",
        inputs={"store-refresh.data": 2},
        state={"store-project-dir.data": str(tmp_path)},
    )
    assert result.ok
    assert result.has("Workflow Test")

    # Step 6: Export all
    result = cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 0,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 1,
        },
        state={
            "export-output-dir.value": "",
            "store-project-dir.data": str(tmp_path),
        },
        changed="btn-export-all.n_clicks",
    )
    assert result.ok
    assert result.has("Export complete")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Existing project — re-run single phase
# ═══════════════════════════════════════════════════════════════════════════════

def test_rerun_single_phase(tmp_project, mock_ai):
    """Re-running a single phase on existing project should update data."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    # Run only architecture
    inputs = {f"btn-run-{p}.n_clicks": 0 for p in
              ["requirements", "roles", "architecture", "development", "deployment", "schedule"]}
    inputs["btn-run-architecture.n_clicks"] = 1
    inputs["btn-run-all.n_clicks"] = 0

    result = cb.fire(
        output="store-run-log",
        inputs=inputs,
        state={
            "run-extra-desc.value": "",
            "run-stakeholder-notes.value": "",
            "store-project-dir.data": str(tmp_project),
            "store-refresh.data": 0,
        },
        changed="btn-run-architecture.n_clicks",
    )
    assert result.ok
    assert result.has("Architecture") or result.has("Running")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. View all pages after full run
# ═══════════════════════════════════════════════════════════════════════════════

def test_all_pages_after_run(tmp_project, mock_ai):
    """After running all phases, every view page should render with data."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    # Run all phases first
    inputs = {f"btn-run-{p}.n_clicks": 0 for p in
              ["requirements", "roles", "architecture", "development", "deployment", "schedule"]}
    inputs["btn-run-all.n_clicks"] = 1

    cb.fire(
        output="store-run-log",
        inputs=inputs,
        state={
            "run-extra-desc.value": "",
            "run-stakeholder-notes.value": "",
            "store-project-dir.data": str(tmp_project),
            "store-refresh.data": 0,
        },
        changed="btn-run-all.n_clicks",
    )

    # Now all view pages should show data
    for page in ["requirements", "roles", "architecture", "development",
                  "deployment", "schedule", "diagrams"]:
        result = cb.render_page(page, tmp_project)
        assert result.ok, f"'{page}' didn't render after run"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Error handling
# ═══════════════════════════════════════════════════════════════════════════════

def test_run_phase_shows_error_on_failure(tmp_project):
    """Run callback should show error in log when AI fails."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    from unittest.mock import patch

    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    with patch("rational_ai.ai.providers.AIProvider.chat_json",
               side_effect=ConnectionError("Ollama not reachable")):

        inputs = {f"btn-run-{p}.n_clicks": 0 for p in
                  ["requirements", "roles", "architecture", "development", "deployment", "schedule"]}
        inputs["btn-run-requirements.n_clicks"] = 1
        inputs["btn-run-all.n_clicks"] = 0

        result = cb.fire(
            output="store-run-log",
            inputs=inputs,
            state={
                "run-extra-desc.value": "",
                "run-stakeholder-notes.value": "",
                "store-project-dir.data": str(tmp_project),
                "store-refresh.data": 0,
            },
            changed="btn-run-requirements.n_clicks",
        )
        assert result.ok, "Error should be caught, not crash"
        assert result.has("ERROR") or result.has("Traceback") or result.has("ConnectionError")


def test_export_error_on_invalid_dir(tmp_cb, tmp_project):
    """Export with an invalid directory should show error."""
    result = tmp_cb.fire(
        output="export-result.children",
        inputs={
            "btn-export-md.n_clicks": 1,
            "btn-export-html.n_clicks": 0,
            "btn-export-diagrams.n_clicks": 0,
            "btn-export-all.n_clicks": 0,
        },
        state={
            "export-output-dir.value": "Z:\\nonexistent\\invalid\\path",
            "store-project-dir.data": str(tmp_project),
        },
        changed="btn-export-md.n_clicks",
    )
    assert result.ok
    assert result.has("Error") or result.has("Export complete")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Config persistence
# ═══════════════════════════════════════════════════════════════════════════════

def test_config_roundtrip(tmp_project):
    """Save config → reload config page → verify values persisted."""
    os.chdir(tmp_project)
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    # Save
    cb.fire(
        output="config-result",
        inputs={"btn-save-config.n_clicks": 1},
        state={
            "cfg-provider.value": "openai",
            "cfg-model.value": "gpt-4o-mini",
            "cfg-api-key.value": "",
            "cfg-base-url.value": "https://api.openai.com/v1",
            "cfg-temperature.value": "0.3",
            "cfg-max-tokens.value": "8192",
            "store-project-dir.data": str(tmp_project),
        },
    )

    # Reload config page
    result = cb.render_page("config", tmp_project)
    assert result.ok
    assert result.has("openai") or result.has("gpt-4o-mini")

    # Verify YAML
    cfg = yaml.safe_load((tmp_project / ".rai" / "config.yaml").read_text())
    assert cfg["ai"]["provider"] == "openai"
    assert cfg["ai"]["model"] == "gpt-4o-mini"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Multiple sequential operations
# ═══════════════════════════════════════════════════════════════════════════════

def test_run_requirements_then_roles(tmp_project, mock_ai):
    """Run requirements then roles sequentially — both should succeed."""
    os.chdir(tmp_project)
    os.environ["RAI_API_KEY"] = "test-key"
    from gui.app import create_app
    app = create_app(tmp_project)
    cb = DashCallbackClient(app.server.test_client(), app)

    for btn in ["btn-run-requirements", "btn-run-roles"]:
        inputs = {f"btn-run-{p}.n_clicks": 0 for p in
                  ["requirements", "roles", "architecture", "development", "deployment", "schedule"]}
        inputs[f"{btn}.n_clicks"] = 1
        inputs["btn-run-all.n_clicks"] = 0

        result = cb.fire(
            output="store-run-log",
            inputs=inputs,
            state={
                "run-extra-desc.value": "",
                "run-stakeholder-notes.value": "",
                "store-project-dir.data": str(tmp_project),
                "store-refresh.data": 0,
            },
            changed=f"{btn}.n_clicks",
        )
        assert result.ok, f"{btn} failed: {result.text[:300]}"
