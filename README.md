# AI Persona System

A framework for building, registering, and orchestrating expert AI personas — structured identities with defined roles, cognitive postures, interface contracts, and composability rules.

## What's Inside

| Directory | Contents |
|-----------|----------|
| `master-expert/` | Meta-Orchestrator — the routing persona that classifies tasks and dispatches to specialists |
| `personas/` | Individual expert persona definitions (structured Markdown) |
| `registry/` | Master registry (YAML) — single source of truth for all personas |
| `methodology/` | Five-Part Structural Framework v2.0 — the methodology behind persona design |
| `voice-cards/` | Voice calibration profiles for consistent output tone |
| `adapters/` | Platform-specific deployment guides (Claude Code, ChatGPT, Gemini, Codex, Cowork) |
| `tools/` | Python utilities for persona registration, validation, and export |

## Quick Start

See `GETTING_STARTED.md` for a step-by-step deployment guide.

1. **Browse personas** in `personas/` — each `.md` file is a self-contained expert definition
2. **Check the registry** in `registry/registry.yaml` for the full inventory with metadata
3. **Read the methodology** in `methodology/v2-framework.md` to understand the design framework
4. **Deploy a persona** using the adapter guide for your platform (see `adapters/`)

## Using the Meta-Orchestrator

The Meta-Orchestrator (`master-expert/meta-orchestrator.md`) is the system entry point. It:
- Diagnoses incoming tasks
- Classifies them to one of six resolution levels (L1-L6)
- Routes to the optimal persona or prompt

Load it as a system prompt in your preferred AI platform. See the adapter docs for platform-specific instructions.

## Validation

```bash
python tools/validate_registry.py
```

Checks that all persona files exist, IDs are unique, cross-references resolve, and counts are consistent.

## Framework

The personas in this system are built using the **Five-Part Structural Framework v2.0**:

1. **Role & Goal Definition** — Identity, objectives, cognitive posture
2. **Knowledge Base** — Domain scope, out-of-scope boundaries
3. **Tone & Style** — Voice calibration, output formatting
4. **Behavioral Constraints** — Hard rules, anti-patterns, mandates
5. **Interface Contract** — Input/output specs, composability rules

See `methodology/v2-framework.md` for the full specification.

## Customization

- **Add personas**: Use `python tools/add_persona.py path/to/new-persona.md`
- **Customize voice**: Edit voice cards in `voice-cards/` or create new ones
- **Build pipelines**: Use the Meta-Orchestrator at L5 to design multi-persona workflows
- **Adapt for platforms**: Follow the adapter guides in `adapters/`

## License

This system is provided as-is for educational and professional use. Adapt the personas to your own domain, organization, and workflow needs.
