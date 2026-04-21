# Rational AI

**AI-powered software engineering lifecycle platform** — inspired by IBM Rational Rose, rebuilt for the AI era.

Rational AI unifies the entire software lifecycle — from requirements gathering through deployment — under a single AI-driven project, replacing fragmented tools with intelligent agents that understand your project holistically.

## Lifecycle Phases

| #   | Phase            | What AI Does                                                          | IBM Rational Equivalent |
| --- | ---------------- | --------------------------------------------------------------------- | ----------------------- |
| 1   | **Requirements** | Extracts, structures, and analyzes requirements from natural language | RequisitePro            |
| 2   | **Team & Roles** | Recommends team composition, generates RACI matrix                    | ClearQuest roles        |
| 3   | **Architecture** | Designs components, generates Mermaid diagrams, writes ADRs           | Rose Designer / XDE     |
| 4   | **Development**  | Breaks down tasks, estimates effort, scaffolds code                   | Rose Code Gen           |
| 5   | **Deployment**   | Plans environments, CI/CD pipelines, infrastructure                   | Rational Build Forge    |
| 6   | **Scheduling**   | Creates milestones, sprint plans, finds critical path                 | Rational Plan           |

## Quick Start

```bash
# Install
pip install -e .

# Set your AI provider key
export RAI_API_KEY="sk-..."

# Initialize a project
rai init "My Platform" -d "A SaaS analytics platform with real-time dashboards"

# Run all phases at once
rai full

# Or run phases individually
rai requirements -d "Must support 10k concurrent users, GDPR compliant"
rai team
rai architecture
rai development
rai deployment
rai schedule

# Check status
rai status

# View phase artifacts
rai show requirements
rai show architecture

# Export reports
rai export all
rai export html
rai export markdown
rai export diagrams
```

## AI Integration

### Supported Providers

| Provider         | Model Examples           | Set Via                                             |
| ---------------- | ------------------------ | --------------------------------------------------- |
| **OpenAI**       | gpt-4o, gpt-4o-mini      | `RAI_API_KEY` + `--provider openai`                 |
| **Anthropic**    | claude-sonnet-4-20250514 | `RAI_API_KEY` + `--provider anthropic`              |
| **Local/Custom** | ollama, vLLM, LM Studio  | `RAI_API_KEY` + `--provider local` + `RAI_BASE_URL` |

### VS Code + GitHub Copilot Integration

Rational AI is designed to work alongside **GitHub Copilot** in VS Code:

- **Copilot instructions** (`.github/copilot-instructions.md`) give Copilot context about your project structure
- **Architecture diagrams** exported as `.mmd` files render in VS Code with Mermaid extensions
- **Generated scaffolds** are Copilot-friendly — clear structure for Copilot to fill in implementations
- **YAML artifacts** in `.rai/` are human-readable and editable

## Project Structure

```
your-project/
├── .rai/                          # Rational AI project directory
│   ├── project.yaml               # Unified project state
│   ├── config.yaml                # AI provider configuration
│   ├── requirements/
│   │   └── requirements.yaml      # Structured requirements & use cases
│   ├── roles/
│   │   └── roles.yaml             # Team composition & RACI
│   ├── architecture/
│   │   ├── architecture.yaml      # Components, ADRs, tech stack
│   │   ├── DIA-001.mmd            # Mermaid diagram files
│   │   └── DIA-002.mmd
│   ├── development/
│   │   └── development.yaml       # Tasks, coding standards
│   ├── deployment/
│   │   └── deployment.yaml        # Environments, CI/CD pipeline
│   ├── schedule/
│   │   └── schedule.yaml          # Milestones, sprints
│   └── exports/
│       ├── project-report.md      # Full Markdown report
│       ├── project-report.html    # Interactive HTML report
│       └── diagrams/              # Individual diagram files
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    PROJECT DESCRIPTION                   │
│          "Build an e-commerce platform with..."          │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │     REQUIREMENTS AGENT     │
         │  Extract → Structure →     │
         │  Analyze → Use Cases       │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │       ROLES AGENT          │
         │  Team Composition →        │
         │  RACI Matrix               │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │    ARCHITECTURE AGENT      │
         │  Components → Diagrams →   │
         │  ADRs → Tech Stack         │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │    DEVELOPMENT AGENT       │
         │  Task Breakdown →          │
         │  Estimates → Scaffolds     │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │    DEPLOYMENT AGENT        │
         │  Environments → CI/CD →    │
         │  IaC → Monitoring          │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │     SCHEDULE AGENT         │
         │  Milestones → Sprints →    │
         │  Critical Path             │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │      EXPORT & REPORTS      │
         │  Markdown │ HTML │ Mermaid │
         └────────────────────────────┘
```

## Examples

See [`examples/sample_project/`](examples/sample_project/) for a complete example.

```bash
# Quick demo with the sample project
cd examples/sample_project
export RAI_API_KEY="sk-..."
rai init "ShopAI" -d "$(cat project.yaml | grep -A20 'description')"
rai full
rai export all
```

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check rational_ai/
```

## Comparison with IBM Rational Rose

| Feature       | IBM Rational Rose            | Rational AI                       |
| ------------- | ---------------------------- | --------------------------------- |
| Requirements  | Manual entry in RequisitePro | AI extracts from natural language |
| UML Diagrams  | Manual drag-and-drop         | AI generates Mermaid diagrams     |
| Code Gen      | Template-based stubs         | AI-powered contextual scaffolding |
| Architecture  | Manual modeling              | AI designs + reviews architecture |
| Team Planning | Separate tool (ClearQuest)   | Integrated AI team recommendation |
| Scheduling    | Manual Gantt charts          | AI-generated sprints & milestones |
| Deployment    | Not included                 | Full CI/CD + IaC planning         |
| Reports       | PDF exports                  | Interactive HTML + Markdown       |
| License       | $$$$ per seat                | Open source + bring your own LLM  |

## License

MIT
