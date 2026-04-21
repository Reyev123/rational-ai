# Rational AI - Copilot Instructions

This is an AI-powered software engineering lifecycle platform inspired by IBM Rational Rose.

## Architecture

- **Phases**: Requirements → Roles → Architecture → Development → Deployment → Scheduling
- **AI Providers**: Abstracted via `rational_ai.ai.providers` — supports OpenAI, Anthropic, local models
- **Data Models**: All artifacts use Pydantic models in `rational_ai.models.schema`
- **CLI**: Typer-based CLI exposed as `rai` command
- **Project State**: YAML-based project files in `.rai/` directory

## Conventions

- Use Pydantic v2 models for all data structures
- AI interactions go through the `AIProvider` abstraction
- All phase operations are in `rational_ai.phases/`
- Export/rendering logic is in `rational_ai.exporters/`
- Use `rich` for terminal output formatting
