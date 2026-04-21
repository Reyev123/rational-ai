# Rational AI — Architecture Document

> **AI-Powered Software Engineering Lifecycle Platform**
> Inspired by IBM Rational Rose, rebuilt for the AI era.

---

## 1. System Overview

Rational AI is a CLI-driven platform that orchestrates the entire software development lifecycle through specialized AI agents. Each lifecycle phase — from requirements gathering to deployment planning — is handled by a dedicated agent that produces structured, traceable artifacts.

### 1.1 High-Level Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'secondaryColor': '#FFF8E7', 'tertiaryColor': '#F0FFF0', 'background': '#FFFFFF', 'mainBkg': '#E8F4FD', 'nodeBorder': '#7FB3D3', 'clusterBkg': '#F5FAFF', 'clusterBorder': '#B8D8E8', 'titleColor': '#1B3A4B', 'edgeLabelBackground': '#FFFFFF' }}}%%
graph TB
    subgraph USER["👤 User Interface Layer"]
        CLI["CLI<br/><i>Typer</i>"]
        VSCODE["VS Code Tasks<br/><i>.vscode/tasks.json</i>"]
    end

    subgraph ORCH["🎯 Orchestration Layer"]
        PO["ProjectOrchestrator<br/><i>project.py</i>"]
        CFG["Config Manager<br/><i>config.py</i>"]
    end

    subgraph AGENTS["🤖 AI Agent Layer"]
        RA["Requirements<br/>Agent"]
        ROA["Roles<br/>Agent"]
        AA["Architecture<br/>Agent"]
        DA["Development<br/>Agent"]
        DPA["Deployment<br/>Agent"]
        SA["Schedule<br/>Agent"]
    end

    subgraph AI["🧠 AI Provider Layer"]
        AIP["AIProvider<br/><i>providers.py</i>"]
        PR["Prompt Templates<br/><i>prompts.py</i>"]
    end

    subgraph LLM["☁️ LLM Backends"]
        OAI["OpenAI<br/><i>GPT-4o</i>"]
        ANT["Anthropic<br/><i>Claude</i>"]
        OLL["Ollama<br/><i>Local LLMs</i>"]
    end

    subgraph DATA["💾 Data & Persistence Layer"]
        SCHEMA["Pydantic Models<br/><i>schema.py</i>"]
        YAML["YAML Store<br/><i>.rai/ directory</i>"]
    end

    subgraph EXPORT["📄 Export Layer"]
        MD["Markdown<br/>Exporter"]
        HTML["HTML<br/>Exporter"]
        MMD["Mermaid<br/>Exporter"]
    end

    CLI --> PO
    VSCODE --> PO
    PO --> CFG
    PO --> RA & ROA & AA & DA & DPA & SA
    RA & ROA & AA & DA & DPA & SA --> AIP
    AIP --> PR
    AIP --> OAI & ANT & OLL
    RA & ROA & AA & DA & DPA & SA --> SCHEMA
    PO --> YAML
    PO --> MD & HTML & MMD
    SCHEMA --> YAML

    style USER fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style ORCH fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style AGENTS fill:#F0FFF0,stroke:#90C695,stroke-width:2px
    style AI fill:#FFF0F5,stroke:#D4A0B0,stroke-width:2px
    style LLM fill:#F5F0FF,stroke:#B0A0D4,stroke-width:2px
    style DATA fill:#FFFAF0,stroke:#D4B896,stroke-width:2px
    style EXPORT fill:#F0FFFF,stroke:#96C8D4,stroke-width:2px
```

_See also: [system-overview.svg](svg/system-overview.svg)_

---

## 2. Lifecycle Pipeline

The platform follows a sequential 6-phase pipeline, where each phase enriches the unified `Project` model. Phases can run individually or in sequence via `rai full`.

### 2.1 Phase Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'secondaryColor': '#FFF8E7', 'tertiaryColor': '#F0FFF0', 'background': '#FFFFFF' }}}%%
flowchart LR
    INPUT["📝 Project<br/>Description"] --> REQ

    subgraph PIPELINE["Software Lifecycle Pipeline"]
        direction LR
        REQ["1️⃣ Requirements<br/><b>Extract & Analyze</b><br/><i>REQ-001..N</i><br/><i>UC-001..N</i>"]
        ROLES["2️⃣ Roles<br/><b>Team Composition</b><br/><i>RACI Matrix</i><br/><i>Skill Mapping</i>"]
        ARCH["3️⃣ Architecture<br/><b>Design & Review</b><br/><i>Components</i><br/><i>ADRs, Diagrams</i>"]
        DEV["4️⃣ Development<br/><b>Task Breakdown</b><br/><i>TASK-001..N</i><br/><i>Code Scaffold</i>"]
        DEPLOY["5️⃣ Deployment<br/><b>CI/CD & IaC</b><br/><i>Environments</i><br/><i>Pipeline</i>"]
        SCHED["6️⃣ Schedule<br/><b>Plan & Estimate</b><br/><i>Milestones</i><br/><i>Sprints</i>"]

        REQ --> ROLES --> ARCH --> DEV --> DEPLOY --> SCHED
    end

    SCHED --> OUTPUT["📊 Reports<br/>& Exports"]

    style INPUT fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style OUTPUT fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style PIPELINE fill:#FAFFFE,stroke:#90C695,stroke-width:2px
    style REQ fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style ROLES fill:#FFF8E7,stroke:#E6C97A,stroke-width:1px
    style ARCH fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style DEV fill:#FFF0F5,stroke:#D4A0B0,stroke-width:1px
    style DEPLOY fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style SCHED fill:#FFFAF0,stroke:#D4B896,stroke-width:1px
```

_See also: [lifecycle-pipeline.svg](svg/lifecycle-pipeline.svg)_

---

## 3. Component Architecture

### 3.1 Package Structure

```
rational_ai/
├── __init__.py              # Package root, version
├── cli.py                   # Typer CLI — user-facing commands
├── config.py                # Configuration management (YAML + env vars)
├── project.py               # ProjectOrchestrator — lifecycle coordinator
│
├── ai/                      # AI abstraction layer
│   ├── providers.py         # AIProvider — unified LLM interface
│   ├── prompts.py           # Curated prompt templates per phase
│   └── agents.py            # 6 specialized AI agents
│
├── models/
│   └── schema.py            # Pydantic v2 data models (30+ types)
│
├── phases/                  # Phase execution modules
│   ├── requirements.py      # Gather, analyze, display, save/load
│   ├── roles.py             # Recommend, assign, RACI
│   ├── architecture.py      # Design, review, diagrams, ADRs
│   ├── development.py       # Tasks, scaffolding, standards
│   ├── deployment.py        # Environments, pipelines, IaC
│   └── scheduling.py        # Milestones, sprints, critical path
│
├── exporters/               # Output renderers
│   ├── markdown.py          # Full project → Markdown report
│   ├── html.py              # Full project → interactive HTML
│   └── mermaid.py           # Diagrams → .mmd files + HTML viewer
│
└── utils/
    └── files.py             # YAML read/write helpers
```

### 3.2 Component Dependency Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
graph TD
    CLI["cli.py<br/><i>Typer App</i>"] --> PO["project.py<br/><i>ProjectOrchestrator</i>"]
    CLI --> CFG["config.py<br/><i>Config / load / save</i>"]

    PO --> CFG
    PO --> PHASES
    PO --> EXPORTERS
    PO --> AIP["ai/providers.py<br/><i>AIProvider</i>"]

    subgraph PHASES["phases/"]
        REQ["requirements.py"]
        ROL["roles.py"]
        ARC["architecture.py"]
        DEV["development.py"]
        DEP["deployment.py"]
        SCH["scheduling.py"]
    end

    subgraph EXPORTERS["exporters/"]
        EXP_MD["markdown.py"]
        EXP_HTML["html.py"]
        EXP_MMD["mermaid.py"]
    end

    PHASES --> AGENTS["ai/agents.py<br/><i>6 Agent Classes</i>"]
    PHASES --> SCHEMA["models/schema.py<br/><i>Pydantic Models</i>"]

    AGENTS --> AIP
    AGENTS --> PROMPTS["ai/prompts.py<br/><i>Prompt Templates</i>"]
    AGENTS --> SCHEMA

    AIP --> OPENAI["openai SDK"]
    EXPORTERS --> SCHEMA
    EXP_HTML --> JINJA["jinja2"]

    CFG --> PYYAML["pyyaml"]
    PO --> PYYAML

    style CLI fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style PO fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style CFG fill:#FFFAF0,stroke:#D4B896,stroke-width:1px
    style PHASES fill:#F0FFF0,stroke:#90C695,stroke-width:2px
    style EXPORTERS fill:#F0FFFF,stroke:#96C8D4,stroke-width:2px
    style AGENTS fill:#FFF0F5,stroke:#D4A0B0,stroke-width:1px
    style SCHEMA fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style AIP fill:#FFF0F5,stroke:#D4A0B0,stroke-width:1px
    style PROMPTS fill:#FFF0F5,stroke:#D4A0B0,stroke-width:1px
```

_See also: [component-dependencies.svg](svg/component-dependencies.svg)_

---

## 4. Data Model Architecture

### 4.1 Unified Project Model

The `Project` model is the central data structure that accumulates artifacts from every phase. It is serialized to YAML in `.rai/project.yaml`.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF', 'classText': '#1B3A4B' }}}%%
classDiagram
    class Project {
        +str name
        +str description
        +str version
        +datetime created_at
        +datetime updated_at
        +RequirementsPackage requirements
        +RolesPackage roles
        +ArchitecturePackage architecture
        +DevelopmentPackage development
        +DeploymentPackage deployment
        +SchedulePackage schedule
    }

    class RequirementsPackage {
        +List~Requirement~ requirements
        +List~UseCase~ use_cases
        +str stakeholder_notes
        +str ai_summary
        +PhaseStatus status
    }

    class Requirement {
        +str id
        +str title
        +str description
        +RequirementType type
        +Priority priority
        +List~str~ acceptance_criteria
        +List~str~ depends_on
    }

    class UseCase {
        +str id
        +str title
        +str actor
        +List~str~ main_flow
        +List~str~ related_requirements
    }

    class RolesPackage {
        +List~TeamMember~ members
        +Dict raci_matrix
        +str ai_recommendations
    }

    class TeamMember {
        +str id
        +str name
        +RoleType role
        +List~str~ skills
        +float availability
    }

    class ArchitecturePackage {
        +List~ArchComponent~ components
        +List~ArchDiagram~ diagrams
        +List~ArchDecision~ decisions
        +Dict tech_stack
        +PhaseStatus status
    }

    class DevelopmentPackage {
        +List~DevTask~ tasks
        +List~CodeModule~ modules
        +str coding_standards
        +str branching_strategy
    }

    class DeploymentPackage {
        +List~Environment~ environments
        +List~DeploymentStep~ pipeline_steps
        +str infrastructure_as_code
        +Dict monitoring
    }

    class SchedulePackage {
        +List~Milestone~ milestones
        +List~Sprint~ sprints
        +int estimated_duration_weeks
    }

    Project *-- RequirementsPackage
    Project *-- RolesPackage
    Project *-- ArchitecturePackage
    Project *-- DevelopmentPackage
    Project *-- DeploymentPackage
    Project *-- SchedulePackage

    RequirementsPackage *-- Requirement
    RequirementsPackage *-- UseCase
    RolesPackage *-- TeamMember
    DevelopmentPackage *-- DevTask
    DeploymentPackage *-- Environment
    SchedulePackage *-- Milestone
    SchedulePackage *-- Sprint

    class DevTask {
        +str id
        +str title
        +str component
        +Priority priority
        +float estimated_hours
        +TaskStatus status
    }
```

_See also: [data-model.svg](svg/data-model.svg)_

---

## 5. AI Integration Architecture

### 5.1 Provider Abstraction

The `AIProvider` class wraps the OpenAI SDK and provides a unified interface to any OpenAI-compatible API (OpenAI, Anthropic via proxy, Ollama, LM Studio, vLLM).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
sequenceDiagram
    participant CLI as CLI / User
    participant PO as ProjectOrchestrator
    participant Agent as AI Agent<br/>(e.g. RequirementsAgent)
    participant AIP as AIProvider
    participant PR as Prompts
    participant LLM as LLM Backend<br/>(OpenAI / Ollama)

    CLI->>PO: rai requirements
    PO->>PO: _ensure_project()
    PO->>Agent: extract_requirements(description)

    Agent->>PR: REQUIREMENTS_EXTRACT
    PR-->>Agent: system prompt template

    Agent->>AIP: chat_json(system, user)
    AIP->>AIP: append "Respond with valid JSON"
    AIP->>LLM: POST /chat/completions<br/>{ model, messages, response_format }
    LLM-->>AIP: { choices: [{ message: { content: "..." } }] }
    AIP-->>Agent: parsed JSON dict

    Agent->>Agent: Requirement(**r) for each item
    Agent-->>PO: RequirementsPackage

    PO->>PO: save to .rai/requirements/
    PO-->>CLI: display rich table
```

_See also: [ai-sequence.svg](svg/ai-sequence.svg)_

### 5.2 Agent Specialization

Each agent encapsulates domain expertise through curated prompts:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
graph LR
    subgraph AGENTS["AI Agents"]
        direction TB
        RA["🔍 RequirementsAgent<br/><i>extract, use_cases, analyze</i>"]
        ROA["👥 RolesAgent<br/><i>recommend_roles</i>"]
        AA["🏗️ ArchitectureAgent<br/><i>design, review</i>"]
        DA["⚙️ DevelopmentAgent<br/><i>tasks, scaffold</i>"]
        DPA["🚀 DeploymentAgent<br/><i>plan_deployment</i>"]
        SA["📅 ScheduleAgent<br/><i>generate_schedule</i>"]
    end

    subgraph PROMPTS["Prompt Templates"]
        direction TB
        P1["REQUIREMENTS_EXTRACT<br/>REQUIREMENTS_ANALYZE<br/>USE_CASE_GENERATE"]
        P2["ROLES_RECOMMEND"]
        P3["ARCHITECTURE_DESIGN<br/>ARCHITECTURE_REVIEW"]
        P4["DEV_TASKS_GENERATE<br/>CODE_SCAFFOLD"]
        P5["DEPLOYMENT_PLAN"]
        P6["SCHEDULE_GENERATE"]
    end

    RA --> P1
    ROA --> P2
    AA --> P3
    DA --> P4
    DPA --> P5
    SA --> P6

    style AGENTS fill:#F0FFF0,stroke:#90C695,stroke-width:2px
    style PROMPTS fill:#FFF0F5,stroke:#D4A0B0,stroke-width:2px
    style RA fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style ROA fill:#FFF8E7,stroke:#E6C97A,stroke-width:1px
    style AA fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style DA fill:#FFF0F5,stroke:#D4A0B0,stroke-width:1px
    style DPA fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style SA fill:#FFFAF0,stroke:#D4B896,stroke-width:1px
```

_See also: [agent-specialization.svg](svg/agent-specialization.svg)_

---

## 6. Persistence & State Architecture

### 6.1 Project Directory Layout

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
graph TD
    ROOT[".rai/"] --> PROJ["project.yaml<br/><i>Unified project state</i>"]
    ROOT --> CONF["config.yaml<br/><i>AI provider settings</i>"]
    ROOT --> REQ_DIR["requirements/"]
    ROOT --> ROLES_DIR["roles/"]
    ROOT --> ARCH_DIR["architecture/"]
    ROOT --> DEV_DIR["development/"]
    ROOT --> DEP_DIR["deployment/"]
    ROOT --> SCHED_DIR["schedule/"]
    ROOT --> EXP_DIR["exports/"]

    REQ_DIR --> REQ_F["requirements.yaml"]
    ROLES_DIR --> ROL_F["roles.yaml"]
    ARCH_DIR --> ARCH_F["architecture.yaml"]
    ARCH_DIR --> DIA1["DIA-001.mmd"]
    ARCH_DIR --> DIA2["DIA-002.mmd"]
    DEV_DIR --> DEV_F["development.yaml"]
    DEP_DIR --> DEP_F["deployment.yaml"]
    SCHED_DIR --> SCHED_F["schedule.yaml"]
    EXP_DIR --> MD_F["report.md"]
    EXP_DIR --> HTML_F["report.html"]
    EXP_DIR --> DIA_DIR["diagrams/"]

    style ROOT fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style PROJ fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style CONF fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style REQ_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style ROLES_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style ARCH_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style DEV_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style DEP_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style SCHED_DIR fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style EXP_DIR fill:#F0FFFF,stroke:#96C8D4,stroke-width:1px
```

_See also: [persistence-layout.svg](svg/persistence-layout.svg)_

### 6.2 State Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
stateDiagram-v2
    [*] --> NotStarted
    NotStarted --> InProgress : AI agent invoked
    InProgress --> Review : Artifacts generated
    Review --> Completed : User approves
    Review --> InProgress : Re-run phase
    Completed --> InProgress : Re-run phase

    state NotStarted {
        [*] --> Waiting
        Waiting : Phase has no data
    }
    state InProgress {
        [*] --> AIProcessing
        AIProcessing : LLM generating artifacts
        AIProcessing --> Saving : JSON parsed
        Saving : Writing to .rai/
    }
    state Review {
        [*] --> Display
        Display : Rich tables in terminal
        Display --> Analysis : AI analysis available
    }
```

_See also: [state-flow.svg](svg/state-flow.svg)_

---

## 7. CLI Command Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
graph TD
    RAI["<b>rai</b><br/><i>Typer CLI</i>"]

    RAI --> INIT["<b>init</b><br/><i>name, --desc, --provider, --model</i>"]
    RAI --> FULL["<b>full</b><br/><i>--desc, --notes</i><br/>Run all 6 phases"]

    RAI --> P_REQ["<b>requirements</b><br/><i>--desc, --notes</i>"]
    RAI --> P_TEAM["<b>team</b>"]
    RAI --> P_ARCH["<b>architecture</b>"]
    RAI --> P_REV["<b>review</b>"]
    RAI --> P_DEV["<b>development</b>"]
    RAI --> P_DEP["<b>deployment</b>"]
    RAI --> P_SCHED["<b>schedule</b>"]

    RAI --> SCAFFOLD["<b>scaffold</b><br/><i>component_id</i>"]
    RAI --> EXPORT["<b>export</b><br/><i>markdown|html|diagrams|all</i>"]
    RAI --> STATUS["<b>status</b>"]
    RAI --> SHOW["<b>show</b><br/><i>phase_name</i>"]

    style RAI fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style INIT fill:#FFF8E7,stroke:#E6C97A,stroke-width:1px
    style FULL fill:#E8FFE8,stroke:#90C695,stroke-width:2px
    style P_REQ fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_TEAM fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_ARCH fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_REV fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_DEV fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_DEP fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style P_SCHED fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style SCAFFOLD fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style EXPORT fill:#F0FFFF,stroke:#96C8D4,stroke-width:1px
    style STATUS fill:#FFFAF0,stroke:#D4B896,stroke-width:1px
    style SHOW fill:#FFFAF0,stroke:#D4B896,stroke-width:1px
```

_See also: [cli-commands.svg](svg/cli-commands.svg)_

---

## 8. Export Pipeline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#7FB3D3', 'background': '#FFFFFF' }}}%%
flowchart LR
    PROJECT["Project<br/>Model<br/><i>Pydantic</i>"] --> MD_EXP["Markdown<br/>Exporter"]
    PROJECT --> HTML_EXP["HTML<br/>Exporter"]
    PROJECT --> MMD_EXP["Mermaid<br/>Exporter"]

    MD_EXP --> MD_OUT["📄 report.md<br/><i>Tables, ADRs,<br/>embedded Mermaid</i>"]
    HTML_EXP --> HTML_OUT["🌐 report.html<br/><i>Interactive, styled,<br/>Mermaid rendered</i>"]
    MMD_EXP --> MMD_OUT["📐 *.mmd files<br/><i>Individual diagrams</i>"]
    MMD_EXP --> DIA_HTML["📐 diagrams.html<br/><i>Combined viewer</i>"]

    HTML_EXP -.-> JINJA["Jinja2<br/>Template"]
    HTML_EXP -.-> MERMAID_JS["Mermaid.js<br/>CDN"]

    style PROJECT fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style MD_EXP fill:#DCEEFB,stroke:#7FB3D3,stroke-width:1px
    style HTML_EXP fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style MMD_EXP fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style MD_OUT fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style HTML_OUT fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style MMD_OUT fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style DIA_HTML fill:#F0FFF0,stroke:#90C695,stroke-width:1px
```

_See also: [export-pipeline.svg](svg/export-pipeline.svg)_

---

## 9. Technology Stack

| Layer             | Technology        | Purpose                         |
| ----------------- | ----------------- | ------------------------------- |
| **Language**      | Python 3.11+      | Core platform                   |
| **CLI Framework** | Typer             | Command-line interface          |
| **Terminal UI**   | Rich              | Tables, panels, colored output  |
| **Data Models**   | Pydantic v2       | Validation, serialization       |
| **AI SDK**        | OpenAI Python SDK | LLM communication               |
| **HTTP**          | httpx             | HTTP client (OpenAI dependency) |
| **Templates**     | Jinja2            | HTML report rendering           |
| **Serialization** | PyYAML            | Project state persistence       |
| **Diagrams**      | Mermaid           | Architecture visualization      |
| **Build**         | Hatchling         | Python packaging                |

---

## 10. IBM Rational Rose Mapping

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8F4FD', 'primaryTextColor': '#1B3A4B', 'primaryBorderColor': '#7FB3D3', 'lineColor': '#90C695', 'background': '#FFFFFF' }}}%%
graph LR
    subgraph RATIONAL["IBM Rational Rose Suite"]
        direction TB
        RR_REQ["RequisitePro<br/><i>Manual entry</i>"]
        RR_ROLES["ClearQuest<br/><i>Separate tool</i>"]
        RR_ARCH["Rose Designer / XDE<br/><i>Drag & drop UML</i>"]
        RR_DEV["Rose Code Gen<br/><i>Template stubs</i>"]
        RR_BUILD["Build Forge<br/><i>Build automation</i>"]
        RR_PLAN["Rational Plan<br/><i>Manual Gantt</i>"]
    end

    subgraph AI_RAI["Rational AI"]
        direction TB
        RAI_REQ["RequirementsAgent<br/><i>AI extraction</i>"]
        RAI_ROLES["RolesAgent<br/><i>AI team planning</i>"]
        RAI_ARCH["ArchitectureAgent<br/><i>AI design + Mermaid</i>"]
        RAI_DEV["DevelopmentAgent<br/><i>AI scaffolding</i>"]
        RAI_BUILD["DeploymentAgent<br/><i>AI CI/CD + IaC</i>"]
        RAI_PLAN["ScheduleAgent<br/><i>AI sprint planning</i>"]
    end

    RR_REQ -.->|"replaced by"| RAI_REQ
    RR_ROLES -.->|"replaced by"| RAI_ROLES
    RR_ARCH -.->|"replaced by"| RAI_ARCH
    RR_DEV -.->|"replaced by"| RAI_DEV
    RR_BUILD -.->|"replaced by"| RAI_BUILD
    RR_PLAN -.->|"replaced by"| RAI_PLAN

    style RATIONAL fill:#FFF0F0,stroke:#D4A0A0,stroke-width:2px
    style AI_RAI fill:#F0FFF0,stroke:#90C695,stroke-width:2px
    style RR_REQ fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RR_ROLES fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RR_ARCH fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RR_DEV fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RR_BUILD fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RR_PLAN fill:#FFE8E8,stroke:#D4A0A0,stroke-width:1px
    style RAI_REQ fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style RAI_ROLES fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style RAI_ARCH fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style RAI_DEV fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style RAI_BUILD fill:#E8FFE8,stroke:#90C695,stroke-width:1px
    style RAI_PLAN fill:#E8FFE8,stroke:#90C695,stroke-width:1px
```

_See also: [rational-rose-mapping.svg](svg/rational-rose-mapping.svg)_

---

## 11. Security Considerations

| Area                 | Approach                                                             |
| -------------------- | -------------------------------------------------------------------- |
| **API Keys**         | Never stored in config files; loaded from `RAI_API_KEY` env var only |
| **Data at Rest**     | YAML files are local, human-readable, no encryption by default       |
| **LLM Data**         | With Ollama/local models, no data leaves the machine                 |
| **Input Validation** | All AI outputs parsed through Pydantic strict validation             |
| **Code Generation**  | Scaffolds reviewed before execution; no auto-execute                 |
| **Dependencies**     | Minimal dependency tree; pinned versions via `pyproject.toml`        |

---

## 12. Extensibility

| Extension Point     | How                                                                         |
| ------------------- | --------------------------------------------------------------------------- |
| **New AI Provider** | Implement OpenAI-compatible endpoint, set `base_url` in config              |
| **New Phase**       | Add module in `phases/`, agent in `ai/agents.py`, prompt in `ai/prompts.py` |
| **New Exporter**    | Add module in `exporters/`, register in `ProjectOrchestrator`               |
| **Custom Prompts**  | Override templates in `ai/prompts.py` for domain-specific tuning            |
| **VS Code Tasks**   | Add entries to `.vscode/tasks.json` for custom workflows                    |

---

_Generated for Rational AI v0.1.0_
