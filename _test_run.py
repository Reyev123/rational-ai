"""Quick test: run each phase individually and show results."""
import os, json, time, yaml

os.chdir(r"c:\Users\Reyev\Documents\_hackathon\rational-ai")

from rational_ai.config import load_config
from rational_ai.ai.providers import AIProvider

cfg = load_config()
ai = AIProvider(cfg.ai)

DESC = cfg.project_dir / ".rai" / "project.yaml"
proj = yaml.safe_load(DESC.read_text(encoding="utf-8"))
description = proj["description"]

print(f"Project: {proj['name']}")
print(f"Description: {description}\n")

# Phase 1: Requirements (simplified prompt for speed)
print("=" * 60)
print("PHASE 1: REQUIREMENTS")
print("=" * 60)
t0 = time.time()
r = ai.chat_json(
    "You are a senior requirements analyst. Extract software requirements.",
    f"""Analyze this project and return JSON with this exact structure:
{{
  "requirements": [
    {{"id": "REQ-001", "title": "short title", "description": "one sentence", "type": "functional", "priority": "high"}}
  ]
}}

Project: {description}

Return 5-7 requirements covering functional and non-functional needs. JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
reqs = r.get("requirements", [])
print(f"  Extracted {len(reqs)} requirements:\n")
for req in reqs:
    print(f"  {req.get('id', '?'):>8} | {req.get('priority', '?'):>6} | {req.get('type', '?'):>15} | {req.get('title', '?')}")

# Phase 2: Use Cases
print(f"\n{'=' * 60}")
print("PHASE 2: USE CASES")
print("=" * 60)
t0 = time.time()
r2 = ai.chat_json(
    "You are a UML use case expert.",
    f"""Based on these requirements, generate 3-4 use cases. Return JSON:
{{
  "use_cases": [
    {{"id": "UC-001", "title": "short title", "actor": "User/Admin", "main_flow": ["step1", "step2"], "related_requirements": ["REQ-001"]}}
  ]
}}

Requirements: {json.dumps(reqs)}
JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
ucs = r2.get("use_cases", [])
print(f"  Generated {len(ucs)} use cases:\n")
for uc in ucs:
    print(f"  {uc.get('id', '?'):>7} | {uc.get('actor', '?'):>10} | {uc.get('title', '?')}")
    for step in uc.get("main_flow", [])[:3]:
        print(f"          |            | - {step}")

# Phase 3: Team Roles
print(f"\n{'=' * 60}")
print("PHASE 3: TEAM & ROLES")
print("=" * 60)
t0 = time.time()
r3 = ai.chat_json(
    "You are a project staffing expert.",
    f"""Recommend a development team for this project. Return JSON:
{{
  "members": [
    {{"id": "TM-001", "name": "Role Name", "role": "developer", "skills": ["skill1"], "availability": 1.0}}
  ]
}}

Project: {description}
Use roles: developer, designer, architect, qa_engineer, devops, project_manager, product_owner.
Recommend 4-6 team members. JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
members = r3.get("members", [])
print(f"  Recommended {len(members)} team members:\n")
for m in members:
    skills = ", ".join(m.get("skills", [])[:3])
    print(f"  {m.get('id', '?'):>7} | {m.get('role', '?'):>18} | {m.get('name', '?'):>20} | {skills}")

# Phase 4: Architecture
print(f"\n{'=' * 60}")
print("PHASE 4: ARCHITECTURE")
print("=" * 60)
t0 = time.time()
r4 = ai.chat_json(
    "You are a software architect.",
    f"""Design the architecture for this project. Return JSON:
{{
  "components": [
    {{"id": "COMP-001", "name": "Component Name", "description": "one sentence", "technology": "tech stack", "dependencies": []}}
  ],
  "decisions": [
    {{"id": "ADR-001", "title": "Decision Title", "status": "accepted", "context": "why", "decision": "what"}}
  ]
}}

Project: {description}
Requirements: {json.dumps([r.get('title','') for r in reqs])}
Return 4-6 components and 2-3 ADRs. JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
comps = r4.get("components", [])
adrs = r4.get("decisions", [])
print(f"  Designed {len(comps)} components, {len(adrs)} ADRs:\n")
for c in comps:
    print(f"  {c.get('id', '?'):>10} | {c.get('name', '?'):>25} | {c.get('technology', '?')}")
for a in adrs:
    print(f"  {a.get('id', '?'):>10} | {a.get('title', '?')}")

# Phase 5: Development Tasks
print(f"\n{'=' * 60}")
print("PHASE 5: DEVELOPMENT TASKS")
print("=" * 60)
t0 = time.time()
r5 = ai.chat_json(
    "You are a development lead.",
    f"""Break down the work into development tasks. Return JSON:
{{
  "tasks": [
    {{"id": "TASK-001", "title": "short title", "component": "COMP-001", "priority": "high", "estimated_hours": 16, "status": "not_started"}}
  ]
}}

Components: {json.dumps([c.get('name','') for c in comps])}
Return 5-8 tasks. JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
tasks = r5.get("tasks", [])
print(f"  Generated {len(tasks)} tasks:\n")
for t in tasks:
    print(f"  {t.get('id', '?'):>10} | {t.get('priority', '?'):>6} | {str(t.get('estimated_hours', '?')):>4}h | {t.get('title', '?')}")

# Phase 6: Schedule
print(f"\n{'=' * 60}")
print("PHASE 6: SCHEDULE")
print("=" * 60)
t0 = time.time()
r6 = ai.chat_json(
    "You are a project scheduler.",
    f"""Create a project schedule. Return JSON:
{{
  "milestones": [
    {{"id": "MS-001", "title": "Milestone", "target_date": "2026-06-01", "deliverables": ["item1"]}}
  ],
  "sprints": [
    {{"id": "SP-001", "name": "Sprint 1", "duration_weeks": 2, "goals": ["goal1"], "task_ids": ["TASK-001"]}}
  ],
  "estimated_duration_weeks": 12
}}

Tasks: {json.dumps([t.get('title','') for t in tasks])}
Plan 3-4 sprints and 2-3 milestones. JSON only.""",
)
elapsed = time.time() - t0
print(f"  Completed in {elapsed:.1f}s")
milestones = r6.get("milestones", [])
sprints = r6.get("sprints", [])
weeks = r6.get("estimated_duration_weeks", "?")
print(f"  Planned {len(milestones)} milestones, {len(sprints)} sprints, ~{weeks} weeks:\n")
for ms in milestones:
    print(f"  {ms.get('id', '?'):>7} | {ms.get('target_date', '?'):>12} | {ms.get('title', '?')}")
for sp in sprints:
    print(f"  {sp.get('id', '?'):>7} | {sp.get('duration_weeks', '?'):>2}w | {sp.get('name', '?')}: {', '.join(sp.get('goals', [])[:2])}")

print(f"\n{'=' * 60}")
print("ALL PHASES COMPLETE")
print("=" * 60)
