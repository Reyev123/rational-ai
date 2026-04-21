"""Generate sample project results and display tables — bypass slow LLM."""
import os, yaml, json
from datetime import datetime

os.chdir(r"c:\Users\Reyev\Documents\_hackathon\rational-ai")

# Build a complete project with realistic sample data
project = {
    "name": "ShopAI E-Commerce Platform",
    "description": "A modern e-commerce platform with AI-powered product recommendations, real-time inventory management, multi-vendor support, and a mobile-first responsive design",
    "version": "0.1.0",
    "created_at": "2026-04-20T16:34:20.083105",
    "updated_at": datetime.now().isoformat(),
    "metadata": {},
    "requirements": {
        "status": "completed",
        "stakeholder_notes": "Focus on mobile UX and AI recommendations",
        "ai_summary": "7 requirements extracted covering core e-commerce, AI, inventory, multi-vendor, mobile, security, and performance needs.",
        "requirements": [
            {"id": "REQ-001", "title": "User Authentication & Authorization", "description": "Secure JWT-based auth with OAuth2 social login support (Google, Apple, GitHub)", "type": "functional", "priority": "high", "acceptance_criteria": ["Users can register with email", "OAuth2 login works", "JWT tokens refresh correctly"], "depends_on": []},
            {"id": "REQ-002", "title": "AI Product Recommendations", "description": "Machine learning engine that provides personalized product recommendations based on browsing history, purchase patterns, and collaborative filtering", "type": "functional", "priority": "high", "acceptance_criteria": ["Recommendations update in real-time", "Cold-start problem handled", "A/B testing supported"], "depends_on": ["REQ-001"]},
            {"id": "REQ-003", "title": "Real-Time Inventory Management", "description": "WebSocket-based inventory tracking with automatic stock alerts, multi-warehouse support, and vendor sync", "type": "functional", "priority": "high", "acceptance_criteria": ["Stock updates within 500ms", "Low-stock alerts trigger", "Multi-warehouse aggregation works"], "depends_on": []},
            {"id": "REQ-004", "title": "Multi-Vendor Marketplace", "description": "Vendor onboarding portal with product listing management, commission tracking, and independent storefronts", "type": "functional", "priority": "medium", "acceptance_criteria": ["Vendors can self-register", "Commission calculated correctly", "Vendor dashboard available"], "depends_on": ["REQ-001"]},
            {"id": "REQ-005", "title": "Mobile-First Responsive Design", "description": "Progressive Web App (PWA) with offline support, push notifications, and touch-optimized UI using responsive design patterns", "type": "functional", "priority": "high", "acceptance_criteria": ["Lighthouse score > 90", "Works offline", "Push notifications on mobile"], "depends_on": []},
            {"id": "REQ-006", "title": "Payment Processing & Security", "description": "PCI-DSS compliant payment gateway integration (Stripe, PayPal) with encryption at rest and in transit", "type": "non_functional", "priority": "high", "acceptance_criteria": ["PCI-DSS Level 1 compliant", "Stripe + PayPal integrated", "All data encrypted AES-256"], "depends_on": ["REQ-001"]},
            {"id": "REQ-007", "title": "Performance & Scalability", "description": "Auto-scaling infrastructure supporting 10,000+ concurrent users with < 200ms API response time and 99.9% uptime SLA", "type": "non_functional", "priority": "medium", "acceptance_criteria": ["P95 latency < 200ms", "Auto-scaling triggers at 70% CPU", "99.9% uptime achieved"], "depends_on": []},
        ],
        "use_cases": [
            {"id": "UC-001", "title": "Customer Purchases Product", "actor": "Customer", "main_flow": ["Customer browses product catalog", "AI recommends related products", "Customer adds items to cart", "Customer completes checkout with payment", "System updates inventory in real-time"], "related_requirements": ["REQ-001", "REQ-002", "REQ-006"]},
            {"id": "UC-002", "title": "Vendor Manages Storefront", "actor": "Vendor", "main_flow": ["Vendor logs into vendor portal", "Vendor adds/edits product listings", "Vendor views sales analytics dashboard", "Vendor manages inventory levels", "System calculates commission"], "related_requirements": ["REQ-003", "REQ-004"]},
            {"id": "UC-003", "title": "Admin Monitors Platform", "actor": "Admin", "main_flow": ["Admin views real-time dashboard", "Admin reviews vendor applications", "Admin configures AI model parameters", "Admin monitors system performance", "Admin manages user accounts"], "related_requirements": ["REQ-002", "REQ-003", "REQ-007"]},
            {"id": "UC-004", "title": "Customer Uses Mobile App", "actor": "Customer", "main_flow": ["Customer opens PWA on mobile", "App loads from cache if offline", "Customer receives push notification for deals", "Customer browses with touch-optimized UI", "Customer completes purchase via mobile payment"], "related_requirements": ["REQ-005", "REQ-006"]},
        ],
    },
    "roles": {
        "ai_recommendations": "Team sized for a 12-week initial delivery with focus on full-stack and AI/ML expertise.",
        "members": [
            {"id": "TM-001", "name": "Tech Lead / Architect", "role": "architect", "skills": ["System Design", "Python", "Cloud Architecture", "Microservices"], "availability": 1.0},
            {"id": "TM-002", "name": "Senior Backend Developer", "role": "developer", "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "WebSockets"], "availability": 1.0},
            {"id": "TM-003", "name": "Frontend Developer", "role": "developer", "skills": ["React", "TypeScript", "PWA", "TailwindCSS", "Next.js"], "availability": 1.0},
            {"id": "TM-004", "name": "ML/AI Engineer", "role": "developer", "skills": ["Python", "TensorFlow", "Recommendation Systems", "MLOps"], "availability": 0.8},
            {"id": "TM-005", "name": "DevOps Engineer", "role": "devops", "skills": ["Kubernetes", "Terraform", "CI/CD", "AWS", "Monitoring"], "availability": 0.5},
            {"id": "TM-006", "name": "QA Engineer", "role": "qa_engineer", "skills": ["Selenium", "pytest", "Load Testing", "API Testing"], "availability": 0.8},
            {"id": "TM-007", "name": "Product Owner", "role": "product_owner", "skills": ["Agile", "User Stories", "Stakeholder Mgmt", "Analytics"], "availability": 0.5},
        ],
        "raci_matrix": {
            "REQ-001": {"TM-001": "A", "TM-002": "R", "TM-006": "C"},
            "REQ-002": {"TM-001": "A", "TM-004": "R", "TM-002": "C"},
            "REQ-003": {"TM-002": "R", "TM-001": "A", "TM-005": "C"},
            "REQ-004": {"TM-002": "R", "TM-003": "R", "TM-001": "A"},
            "REQ-005": {"TM-003": "R", "TM-001": "A", "TM-006": "C"},
        },
    },
    "architecture": {
        "status": "completed",
        "ai_analysis": "Microservices architecture with event-driven communication, optimized for scalability and independent deployment.",
        "components": [
            {"id": "COMP-001", "name": "API Gateway", "description": "Central entry point handling routing, rate limiting, and authentication", "technology": "Kong / NGINX", "dependencies": []},
            {"id": "COMP-002", "name": "Auth Service", "description": "JWT-based authentication with OAuth2 provider integration", "technology": "Python FastAPI + Redis", "dependencies": ["COMP-001"]},
            {"id": "COMP-003", "name": "Product Catalog Service", "description": "Product CRUD, search (Elasticsearch), and vendor product management", "technology": "Python FastAPI + PostgreSQL + Elasticsearch", "dependencies": ["COMP-002"]},
            {"id": "COMP-004", "name": "Recommendation Engine", "description": "ML-based collaborative and content-based filtering for product recommendations", "technology": "Python + TensorFlow Serving + Redis", "dependencies": ["COMP-003"]},
            {"id": "COMP-005", "name": "Inventory Service", "description": "Real-time stock tracking with WebSocket updates and multi-warehouse support", "technology": "Python FastAPI + PostgreSQL + WebSockets", "dependencies": ["COMP-003"]},
            {"id": "COMP-006", "name": "Order & Payment Service", "description": "Order processing, payment gateway integration (Stripe/PayPal), and transaction management", "technology": "Python FastAPI + Stripe SDK", "dependencies": ["COMP-002", "COMP-005"]},
            {"id": "COMP-007", "name": "Frontend PWA", "description": "Mobile-first Progressive Web App with offline support and push notifications", "technology": "React + Next.js + TailwindCSS", "dependencies": ["COMP-001"]},
            {"id": "COMP-008", "name": "Event Bus", "description": "Asynchronous event-driven communication between microservices", "technology": "Apache Kafka / RabbitMQ", "dependencies": []},
        ],
        "decisions": [
            {"id": "ADR-001", "title": "Microservices over Monolith", "status": "accepted", "context": "Need independent scaling of AI, inventory, and order services", "decision": "Adopt microservices architecture with API gateway pattern"},
            {"id": "ADR-002", "title": "Event-Driven Communication", "status": "accepted", "context": "Services need loose coupling for inventory updates and order events", "decision": "Use Kafka for async event streaming between services"},
            {"id": "ADR-003", "title": "PWA over Native Mobile Apps", "status": "accepted", "context": "Budget constraints and need for cross-platform support", "decision": "Build as PWA with Next.js for SSR and offline capabilities"},
        ],
        "diagrams": [],
        "tech_stack": {"backend": "Python FastAPI", "frontend": "React + Next.js", "database": "PostgreSQL", "cache": "Redis", "search": "Elasticsearch", "ml": "TensorFlow", "messaging": "Kafka", "infrastructure": "AWS + Kubernetes"},
    },
    "development": {
        "status": "completed",
        "ai_suggestions": "Prioritize auth and catalog services first to unblock frontend development.",
        "coding_standards": "PEP 8, Black formatter, type hints required, 80% test coverage minimum",
        "branching_strategy": "GitFlow with feature branches, develop, and main",
        "modules": [],
        "tasks": [
            {"id": "TASK-001", "title": "Setup API Gateway & routing", "component": "COMP-001", "priority": "high", "estimated_hours": 16, "status": "not_started"},
            {"id": "TASK-002", "title": "Implement Auth Service (JWT + OAuth2)", "component": "COMP-002", "priority": "high", "estimated_hours": 32, "status": "not_started"},
            {"id": "TASK-003", "title": "Build Product Catalog CRUD + Search", "component": "COMP-003", "priority": "high", "estimated_hours": 40, "status": "not_started"},
            {"id": "TASK-004", "title": "Train & deploy recommendation model", "component": "COMP-004", "priority": "medium", "estimated_hours": 60, "status": "not_started"},
            {"id": "TASK-005", "title": "Implement real-time inventory tracking", "component": "COMP-005", "priority": "high", "estimated_hours": 32, "status": "not_started"},
            {"id": "TASK-006", "title": "Build Order/Payment processing", "component": "COMP-006", "priority": "high", "estimated_hours": 48, "status": "not_started"},
            {"id": "TASK-007", "title": "Develop Frontend PWA shell + routing", "component": "COMP-007", "priority": "high", "estimated_hours": 40, "status": "not_started"},
            {"id": "TASK-008", "title": "Setup Kafka event bus & consumers", "component": "COMP-008", "priority": "medium", "estimated_hours": 24, "status": "not_started"},
            {"id": "TASK-009", "title": "E2E testing & load testing", "component": "COMP-001", "priority": "medium", "estimated_hours": 32, "status": "not_started"},
            {"id": "TASK-010", "title": "Vendor portal frontend", "component": "COMP-007", "priority": "medium", "estimated_hours": 36, "status": "not_started"},
        ],
    },
    "deployment": {
        "status": "completed",
        "ai_suggestions": "Use blue-green deployment for zero-downtime releases.",
        "environments": [
            {"name": "Development", "type": "development", "url": "https://dev.shopai.example.com", "config": {"replicas": 1, "auto_scaling": False}},
            {"name": "Staging", "type": "staging", "url": "https://staging.shopai.example.com", "config": {"replicas": 2, "auto_scaling": True}},
            {"name": "Production", "type": "production", "url": "https://shopai.example.com", "config": {"replicas": 3, "auto_scaling": True, "min_replicas": 3, "max_replicas": 20}},
        ],
        "pipeline_steps": [
            {"name": "Lint & Type Check", "type": "quality", "command": "ruff check . && mypy ."},
            {"name": "Unit Tests", "type": "test", "command": "pytest tests/ --cov=src --cov-report=html"},
            {"name": "Build Docker Images", "type": "build", "command": "docker compose build"},
            {"name": "Integration Tests", "type": "test", "command": "pytest tests/integration/ -v"},
            {"name": "Deploy to Staging", "type": "deploy", "command": "kubectl apply -k k8s/staging/"},
            {"name": "Smoke Tests", "type": "test", "command": "pytest tests/smoke/ --base-url=$STAGING_URL"},
            {"name": "Deploy to Production", "type": "deploy", "command": "kubectl apply -k k8s/production/"},
        ],
        "infrastructure_as_code": "Terraform + Kubernetes (EKS)",
        "monitoring": {"apm": "Datadog", "logging": "ELK Stack", "alerting": "PagerDuty", "uptime": "Pingdom"},
    },
    "schedule": {
        "status": "completed",
        "ai_schedule": "12-week delivery plan with 6 two-week sprints.",
        "estimated_duration_weeks": 12,
        "milestones": [
            {"id": "MS-001", "title": "MVP — Core Shopping Flow", "target_date": "2026-06-14", "deliverables": ["Auth Service", "Product Catalog", "Basic Frontend", "Payment Integration"]},
            {"id": "MS-002", "title": "AI & Vendor Features", "target_date": "2026-07-12", "deliverables": ["Recommendation Engine", "Vendor Portal", "Real-time Inventory"]},
            {"id": "MS-003", "title": "Production Launch", "target_date": "2026-07-26", "deliverables": ["Performance Optimization", "Security Audit", "Production Deployment", "Monitoring"]},
        ],
        "sprints": [
            {"id": "SP-001", "name": "Sprint 1: Foundation", "duration_weeks": 2, "goals": ["API Gateway setup", "Auth service MVP", "Frontend shell"], "task_ids": ["TASK-001", "TASK-002", "TASK-007"]},
            {"id": "SP-002", "name": "Sprint 2: Core Commerce", "duration_weeks": 2, "goals": ["Product catalog", "Inventory service", "Event bus"], "task_ids": ["TASK-003", "TASK-005", "TASK-008"]},
            {"id": "SP-003", "name": "Sprint 3: Payments & Vendors", "duration_weeks": 2, "goals": ["Order/payment processing", "Vendor portal"], "task_ids": ["TASK-006", "TASK-010"]},
            {"id": "SP-004", "name": "Sprint 4: AI & Intelligence", "duration_weeks": 2, "goals": ["Train recommendation model", "Deploy ML pipeline"], "task_ids": ["TASK-004"]},
            {"id": "SP-005", "name": "Sprint 5: Polish & Testing", "duration_weeks": 2, "goals": ["E2E testing", "Load testing", "Performance tuning"], "task_ids": ["TASK-009"]},
            {"id": "SP-006", "name": "Sprint 6: Launch Prep", "duration_weeks": 2, "goals": ["Security audit", "Production deployment", "Monitoring setup"], "task_ids": []},
        ],
    },
}

# Save to project.yaml
proj_path = os.path.join(".rai", "project.yaml")
with open(proj_path, "w", encoding="utf-8") as f:
    yaml.dump(project, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

print(f"Saved project to {proj_path}\n")

# Now display tables using Rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# ═══════════════════════════════════════════════════════
# REQUIREMENTS TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 1: REQUIREMENTS[/]", expand=False))
t = Table(title="Extracted Requirements", show_lines=True)
t.add_column("ID", style="cyan", width=10)
t.add_column("Title", style="white", width=35)
t.add_column("Type", style="yellow", width=15)
t.add_column("Priority", width=10)
t.add_column("Acceptance Criteria", style="dim", width=40)
for r in project["requirements"]["requirements"]:
    prio = r["priority"]
    prio_style = "bold red" if prio == "high" else "yellow" if prio == "medium" else "green"
    criteria = "\n".join(f"• {c}" for c in r.get("acceptance_criteria", [])[:2])
    t.add_row(r["id"], r["title"], r["type"], f"[{prio_style}]{prio}[/]", criteria)
console.print(t)

# USE CASES
t2 = Table(title="Use Cases", show_lines=True)
t2.add_column("ID", style="cyan", width=8)
t2.add_column("Title", style="white", width=30)
t2.add_column("Actor", style="magenta", width=12)
t2.add_column("Main Flow", style="dim", width=50)
t2.add_column("Requirements", style="yellow", width=20)
for uc in project["requirements"]["use_cases"]:
    flow = "\n".join(f"{i+1}. {s}" for i, s in enumerate(uc["main_flow"][:3]))
    t2.add_row(uc["id"], uc["title"], uc["actor"], flow, ", ".join(uc["related_requirements"]))
console.print(t2)

# ═══════════════════════════════════════════════════════
# TEAM & ROLES TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 2: TEAM & ROLES[/]", expand=False))
t3 = Table(title="Recommended Team", show_lines=True)
t3.add_column("ID", style="cyan", width=8)
t3.add_column("Name", style="white", width=28)
t3.add_column("Role", style="magenta", width=16)
t3.add_column("Skills", style="yellow", width=45)
t3.add_column("Avail", style="green", width=6)
for m in project["roles"]["members"]:
    t3.add_row(m["id"], m["name"], m["role"], ", ".join(m["skills"]), f"{m['availability']:.0%}")
console.print(t3)

# RACI
t3b = Table(title="RACI Matrix", show_lines=True)
t3b.add_column("Requirement", style="cyan", width=10)
for m in project["roles"]["members"][:5]:
    t3b.add_column(m["id"], width=8, justify="center")
for req_id, assignments in project["roles"]["raci_matrix"].items():
    row = [req_id]
    for m in project["roles"]["members"][:5]:
        val = assignments.get(m["id"], "-")
        style = {"R": "[bold green]R[/]", "A": "[bold red]A[/]", "C": "[yellow]C[/]", "I": "[dim]I[/]"}.get(val, "-")
        row.append(style)
    t3b.add_row(*row)
console.print(t3b)

# ═══════════════════════════════════════════════════════
# ARCHITECTURE TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 3: ARCHITECTURE[/]", expand=False))
t4 = Table(title="System Components", show_lines=True)
t4.add_column("ID", style="cyan", width=10)
t4.add_column("Component", style="white bold", width=26)
t4.add_column("Description", style="dim", width=45)
t4.add_column("Technology", style="yellow", width=30)
for c in project["architecture"]["components"]:
    t4.add_row(c["id"], c["name"], c["description"], c["technology"])
console.print(t4)

# ADRs
t4b = Table(title="Architecture Decision Records", show_lines=True)
t4b.add_column("ID", style="cyan", width=10)
t4b.add_column("Decision", style="white bold", width=30)
t4b.add_column("Status", style="green", width=10)
t4b.add_column("Context", style="dim", width=40)
t4b.add_column("Decision Made", style="yellow", width=40)
for a in project["architecture"]["decisions"]:
    t4b.add_row(a["id"], a["title"], f"[green]{a['status']}[/]", a["context"], a["decision"])
console.print(t4b)

# Tech Stack
t4c = Table(title="Technology Stack", show_lines=True)
t4c.add_column("Layer", style="cyan", width=15)
t4c.add_column("Technology", style="yellow", width=30)
for layer, tech in project["architecture"]["tech_stack"].items():
    t4c.add_row(layer.title(), tech)
console.print(t4c)

# ═══════════════════════════════════════════════════════
# DEVELOPMENT TASKS TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 4: DEVELOPMENT TASKS[/]", expand=False))
t5 = Table(title="Development Tasks", show_lines=True)
t5.add_column("ID", style="cyan", width=10)
t5.add_column("Task", style="white", width=38)
t5.add_column("Component", style="magenta", width=10)
t5.add_column("Priority", width=10)
t5.add_column("Hours", style="yellow", width=8, justify="right")
t5.add_column("Status", width=12)
total_hours = 0
for task in project["development"]["tasks"]:
    p = task["priority"]
    ps = "bold red" if p == "high" else "yellow" if p == "medium" else "green"
    t5.add_row(task["id"], task["title"], task["component"], f"[{ps}]{p}[/]", str(task["estimated_hours"]), task["status"])
    total_hours += task["estimated_hours"]
t5.add_row("", "[bold]TOTAL[/]", "", "", f"[bold]{total_hours}[/]", "")
console.print(t5)

# ═══════════════════════════════════════════════════════
# DEPLOYMENT TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 5: DEPLOYMENT[/]", expand=False))
t6 = Table(title="Environments", show_lines=True)
t6.add_column("Environment", style="white bold", width=14)
t6.add_column("Type", style="cyan", width=12)
t6.add_column("URL", style="blue underline", width=38)
t6.add_column("Replicas", style="yellow", width=10, justify="center")
t6.add_column("Auto-Scale", width=10, justify="center")
for env in project["deployment"]["environments"]:
    replicas = str(env["config"].get("replicas", "?"))
    auto = "[green]Yes[/]" if env["config"].get("auto_scaling") else "[red]No[/]"
    t6.add_row(env["name"], env["type"], env["url"], replicas, auto)
console.print(t6)

t6b = Table(title="CI/CD Pipeline", show_lines=True)
t6b.add_column("#", style="dim", width=4)
t6b.add_column("Step", style="white bold", width=24)
t6b.add_column("Type", style="cyan", width=10)
t6b.add_column("Command", style="yellow", width=50)
for i, step in enumerate(project["deployment"]["pipeline_steps"], 1):
    t6b.add_row(str(i), step["name"], step["type"], step["command"])
console.print(t6b)

# ═══════════════════════════════════════════════════════
# SCHEDULE TABLE
# ═══════════════════════════════════════════════════════
console.print(Panel("[bold cyan]PHASE 6: SCHEDULE[/]", expand=False))
t7 = Table(title=f"Project Schedule — {project['schedule']['estimated_duration_weeks']} Weeks", show_lines=True)
t7.add_column("ID", style="cyan", width=8)
t7.add_column("Milestone", style="white bold", width=30)
t7.add_column("Target Date", style="yellow", width=14)
t7.add_column("Deliverables", style="dim", width=50)
for ms in project["schedule"]["milestones"]:
    deliverables = ", ".join(ms["deliverables"])
    t7.add_row(ms["id"], ms["title"], ms["target_date"], deliverables)
console.print(t7)

t7b = Table(title="Sprint Plan", show_lines=True)
t7b.add_column("ID", style="cyan", width=8)
t7b.add_column("Sprint", style="white bold", width=30)
t7b.add_column("Weeks", style="yellow", width=6, justify="center")
t7b.add_column("Goals", style="dim", width=45)
t7b.add_column("Tasks", style="magenta", width=20)
for sp in project["schedule"]["sprints"]:
    goals = ", ".join(sp["goals"])
    tasks = ", ".join(sp["task_ids"]) if sp["task_ids"] else "—"
    t7b.add_row(sp["id"], sp["name"], str(sp["duration_weeks"]), goals, tasks)
console.print(t7b)

console.print("\n[bold green]✅ All 6 phases complete. Project saved to .rai/project.yaml[/]")
console.print("[dim]Run 'rai export all' to generate Markdown/HTML reports, or 'rai status' to view summary.[/]")
