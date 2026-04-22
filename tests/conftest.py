"""Shared fixtures for Rational AI E2E tests.

All tests use Flask's test client to simulate Dash callback invocations,
avoiding any browser/Selenium dependency while exercising the full
callback → orchestrator → AI provider chain.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ── Project dir fixture ──────────────────────────────────────────────────────

REAL_PROJECT_DIR = Path(__file__).resolve().parent.parent
"""The root of the rational‑ai repository (has .rai/)."""


@pytest.fixture()
def project_dir() -> Path:
    """Return the real project directory (read‑only tests)."""
    return REAL_PROJECT_DIR


@pytest.fixture()
def tmp_project(tmp_path: Path):
    """Create a disposable project directory with copies of .rai/ data.

    This allows tests that *write* (create project, run phases, export)
    without touching the real project data.
    """
    src_rai = REAL_PROJECT_DIR / ".rai"
    dst_rai = tmp_path / ".rai"
    shutil.copytree(src_rai, dst_rai)
    return tmp_path


# ── Dash app fixtures ─────────────────────────────────────────────────────────

@pytest.fixture()
def app(project_dir: Path):
    """Create a Dash app pointed at the real project (read-only)."""
    os.chdir(project_dir)
    from gui.app import create_app
    return create_app(project_dir)


@pytest.fixture()
def client(app):
    """Flask test client for the read-only Dash app."""
    return app.server.test_client()


@pytest.fixture()
def tmp_app(tmp_project: Path):
    """Dash app pointed at a temporary writable project copy."""
    os.chdir(tmp_project)
    from gui.app import create_app
    return create_app(tmp_project)


@pytest.fixture()
def tmp_client(tmp_app):
    """Flask test client for the writable Dash app."""
    return tmp_app.server.test_client()


# ── Callback helpers ──────────────────────────────────────────────────────────

class DashCallbackClient:
    """Convenience wrapper around Flask test client for invoking Dash callbacks.

    Usage::

        cb = DashCallbackClient(client, app)
        result = cb.fire(
            output="page-content.children",
            inputs={"store-page.data": "dashboard", "store-refresh.data": 0},
            state={"store-project-dir.data": "/path/to/proj"},
            changed="store-page.data",
        )
        assert result.status_code == 200
        assert "Dashboard" in result.text
    """

    def __init__(self, flask_client, dash_app):
        self.client = flask_client
        self.app = dash_app

    # ── internal helpers ──

    @staticmethod
    def _parse_id_prop(s: str) -> tuple[str, str]:
        """Parse 'component-id.property' or 'component-id.property@hash'."""
        # Strip @hash suffix first
        clean = s.split("@")[0] if "@" in s else s
        parts = clean.rsplit(".", 1)
        return parts[0], parts[1]

    def _find_callback_key(self, output: str) -> str:
        """Find the actual callback_map key that contains the given output id(s).

        ``output`` is a user-friendly key like ``"config-result"``
        or ``"store-run-log"``.  We search callback_map for a key
        containing that string.  Prefer the shortest matching key
        to avoid ambiguity (e.g. ``run-log`` matching the run-phase
        multi-output key instead of the sync_log single-output key).
        """
        # Try exact match first
        if output in self.app.callback_map:
            return output
        # Collect all matching keys and pick the shortest (most specific)
        matches = [k for k in self.app.callback_map if output in k]
        if matches:
            return min(matches, key=len)
        raise KeyError(f"No callback found for output: {output}")

    def fire(
        self,
        output: str,
        inputs: dict[str, Any],
        state: dict[str, Any] | None = None,
        changed: str | None = None,
    ) -> "CallbackResult":
        """Invoke a Dash callback via ``/_dash-update-component``.

        Parameters
        ----------
        output : str
            A substring that uniquely identifies the callback.  Can be a
            component id like ``"config-result"`` or ``"store-run-log"``,
            or a full Dash output spec like ``"page-content.children"``.
        inputs : dict
            ``{"component-id.property": value, ...}``
        state : dict | None
            ``{"component-id.property": value, ...}``
        changed : str | None
            Which input triggered the callback (``component-id.property``).
            Defaults to the first entry in *inputs*.
        """
        changed = changed or next(iter(inputs))

        input_list = []
        for k, v in inputs.items():
            cid, prop = self._parse_id_prop(k)
            input_list.append({"id": cid, "property": prop, "value": v})

        state_list = []
        for k, v in (state or {}).items():
            cid, prop = self._parse_id_prop(k)
            state_list.append({"id": cid, "property": prop, "value": v})

        changed_ids = [changed]

        # Find the real callback key and build output spec from Output objects
        real_key = self._find_callback_key(output)
        entry = self.app.callback_map[real_key]
        output_objs = entry["output"]

        # Build outputs list from the Output objects directly
        if isinstance(output_objs, (list, tuple)):
            out_specs = [
                {"id": o.component_id, "property": o.component_property}
                for o in output_objs
            ]
        else:
            out_specs = {
                "id": output_objs.component_id,
                "property": output_objs.component_property,
            }

        body = {
            "output": real_key,
            "outputs": out_specs,
            "inputs": input_list,
            "changedPropIds": changed_ids,
            "state": state_list,
        }

        resp = self.client.post(
            "/_dash-update-component",
            json=body,
            content_type="application/json",
        )
        return CallbackResult(resp)

    def render_page(self, page: str, proj_dir: str | Path) -> "CallbackResult":
        """Shortcut to render a page via the render_page callback."""
        return self.fire(
            output="page-content.children",
            inputs={
                "store-page.data": page,
                "store-refresh.data": 0,
            },
            state={"store-project-dir.data": str(proj_dir)},
            changed="store-page.data",
        )


class CallbackResult:
    """Wrapper around Flask response for easier assertions."""

    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.text = response.data.decode("utf-8")
        self._json = None

    @property
    def json(self) -> dict:
        if self._json is None:
            self._json = json.loads(self.text)
        return self._json

    @property
    def ok(self) -> bool:
        return self.status_code == 200

    def has(self, *substrings: str) -> bool:
        """Check if response text contains all given substrings."""
        return all(s in self.text for s in substrings)

    def get_output(self, component_id: str, prop: str = "children") -> Any:
        """Extract a specific output value from the Dash response."""
        resp = self.json.get("response", {})
        entry = resp.get(component_id, {})
        return entry.get(prop)

    def __repr__(self):
        return f"<CallbackResult status={self.status_code} len={len(self.text)}>"


@pytest.fixture()
def cb(client, app) -> DashCallbackClient:
    """DashCallbackClient for the read-only app."""
    return DashCallbackClient(client, app)


@pytest.fixture()
def tmp_cb(tmp_client, tmp_app) -> DashCallbackClient:
    """DashCallbackClient for the writable app."""
    return DashCallbackClient(tmp_client, tmp_app)


# ── AI mock fixture ──────────────────────────────────────────────────────────

@pytest.fixture()
def mock_ai():
    """Mock the AIProvider so no real LLM calls are made.

    Returns a context‑manager‑style mock that patches AIProvider.chat_json
    and AIProvider.chat to return deterministic results.
    """
    fake_requirements = {
        "requirements": [
            {
                "id": "REQ-001",
                "title": "Test Requirement",
                "description": "A test requirement",
                "type": "functional",
                "priority": "high",
                "acceptance_criteria": ["It works"],
                "depends_on": [],
            }
        ],
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Test Use Case",
                "actor": "User",
                "description": "A test use case",
                "main_flow": ["Step 1", "Step 2"],
                "related_requirements": ["REQ-001"],
            }
        ],
        "stakeholder_notes": "Test notes",
        "ai_summary": "Test AI summary",
    }

    fake_roles = {
        "roles": [
            {
                "role": "developer",
                "count": 1,
                "skills": ["Python"],
                "responsibilities": ["Coding"],
                "assigned_components": ["COMP-001"],
            }
        ],
        "raci_matrix": {"coding": {"developer": "R"}},
    }

    fake_architecture = {
        "components": [
            {
                "id": "COMP-001",
                "name": "Test Service",
                "type": "service",
                "description": "A test service",
                "technology": "Python",
                "dependencies": [],
            }
        ],
        "technology_stack": {"backend": "Python", "database": "PostgreSQL"},
        "diagrams": [
            {
                "id": "DIAG-001",
                "title": "Test Diagram",
                "type": "component",
                "description": "A test diagram",
                "mermaid_code": "graph TD\n  A-->B",
            }
        ],
        "decisions": [
            {
                "id": "ADR-001",
                "title": "Test Decision",
                "status": "accepted",
                "context": "Test context",
                "decision": "Use Python",
                "consequences": "Fast development",
            }
        ],
        "ai_analysis": "Test analysis",
    }

    fake_development = {
        "tasks": [
            {
                "id": "TASK-001",
                "title": "Test Task",
                "description": "A test task",
                "priority": "high",
                "status": "todo",
                "component_id": "COMP-001",
                "estimated_hours": 8,
                "assigned_to": "TM-001",
            }
        ],
        "coding_standards": "PEP 8",
        "branching_strategy": "Git Flow",
        "ai_suggestions": "Test suggestions",
    }

    fake_deployment = {
        "environments": [
            {
                "name": "production",
                "type": "production",
                "config": {"replicas": 3},
                "url": "https://prod.example.com",
            }
        ],
        "pipeline_steps": [
            {
                "name": "Build",
                "order": 1,
                "command": "docker build",
                "description": "Build Docker image",
            }
        ],
        "monitoring": {
            "logging": "ELK Stack",
            "apm": "Datadog",
            "alerting": "PagerDuty",
            "uptime": "Pingdom",
        },
        "infrastructure_as_code": "Terraform",
        "ai_suggestions": "Test deployment suggestions",
    }

    fake_schedule = {
        "milestones": [
            {
                "id": "MS-001",
                "name": "MVP Release",
                "deliverables": ["MVP"],
            }
        ],
        "sprints": [
            {
                "id": "SP-001",
                "name": "Sprint 1",
                "goals": ["Setup"],
                "tasks": ["TASK-001"],
            }
        ],
        "estimated_duration_weeks": 8,
        "critical_path": [],
        "risks": [],
    }

    # Use-case-only response (for generate_use_cases call)
    fake_use_cases = {
        "use_cases": [
            {
                "id": "UC-001",
                "title": "Test Use Case",
                "actor": "User",
                "description": "A test use case",
                "main_flow": ["Step 1", "Step 2"],
                "related_requirements": ["REQ-001"],
            }
        ],
    }

    # Map system prompt substrings → responses so multi-call phases work
    prompt_response_map = {
        "requirements engineer": fake_requirements,   # REQUIREMENTS_EXTRACT
        "use case modeling": fake_use_cases,           # USE_CASE_GENERATE
        "staffing advisor": fake_roles,                # ROLES_RECOMMEND
        "software architect": fake_architecture,       # ARCHITECTURE_DESIGN
        "technical lead": fake_development,            # DEV_TASKS_GENERATE
        "devops engineer": fake_deployment,            # DEPLOYMENT_PLAN
        "project scheduler": fake_schedule,            # SCHEDULE_GENERATE
    }

    # Fallback sequential list for any unmatched prompts
    fallback_responses = [
        fake_requirements, fake_roles, fake_architecture,
        fake_development, fake_deployment, fake_schedule,
    ]
    call_count = {"n": 0}

    def fake_chat_json(system, user, **kwargs):
        system_lower = (system or "").lower()
        for keyword, response in prompt_response_map.items():
            if keyword in system_lower:
                return response
        # Fallback to sequential
        idx = min(call_count["n"], len(fallback_responses) - 1)
        call_count["n"] += 1
        return fallback_responses[idx]

    def fake_chat(system, user, **kwargs):
        from rational_ai.ai.providers import AIResponse
        return AIResponse(content="Mock review", model="mock", usage={"prompt_tokens": 0, "completion_tokens": 0})

    with patch("rational_ai.ai.providers.AIProvider.chat_json", side_effect=fake_chat_json), \
         patch("rational_ai.ai.providers.AIProvider.chat", side_effect=fake_chat):
        yield
