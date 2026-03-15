# Getting Started with the AI Persona System

## Step 1: Save the System Files

Where you save them depends on how you plan to use the system:

| Setup | Where to Save | Best For |
|---|---|---|
| Local drive | Any folder (e.g., `~/ai-persona-system/`) | Single LLM platform, solo use |
| Google Drive | A shared Drive folder | Accessing personas from multiple LLM platforms or devices |
| Local git repo | `git init` in the folder | Version control as you add/modify personas |
| GitHub repo | Push to a private or public repo | Collaboration, backup |

You can combine these -- e.g., a local git repo synced to Google Drive.

## Step 2: Understand the Framework

Read `methodology/v2-framework.md` -- the Five-Part Structural Framework every persona is built on:

1. **Role & Goal Definition** -- Identity, objectives, cognitive posture
2. **Knowledge Base** -- Domain scope, out-of-scope boundaries
3. **Tone & Style** -- Voice calibration, output formatting
4. **Behavioral Constraints** -- Hard rules, anti-patterns, mandates
5. **Interface Contract** -- Input/output specs, composability rules

## Step 3: Deploy a Single Expert Persona

Pick any persona from `personas/`. Each `.md` file is a self-contained system prompt.

**On Claude.ai:** Create a Project → paste Part 1 (Role & Goal) and Part 3 (Tone & Style) into Project Instructions → upload the full persona `.md` as a Knowledge file → start chatting.

For other platforms, see the adapter guide in `adapters/` for your platform.

## Step 4: Create Your Own Experts

Upload `methodology/v2-framework.md` as a Knowledge file and ask the LLM to create a new persona. Takes 1-2 minutes. Save the persona `.md` file in `personas/`. You can use it immediately -- just deploy it to your LLM platform following the adapter guide.

If you want to use the Meta-Orchestrator for automatic routing, register the persona in the registry:

**Registry sync (requires terminal):**
```bash
python tools/sync_registry.py
```
Scans for unregistered personas, extracts metadata, and adds them to the registry. Run `python tools/validate_registry.py` afterward to verify.

In Claude Code, you can also use `/create-persona` -- see the [Claude Code adapter](adapters/claude-code-adapter.md).

## Step 5: Build Expert Teams

Two included personas specialize in vetting team composition:
- **Multi-Agent Orchestration Architect** -- organization design and persona engineering
- **Agentic Systems Architect** -- governance, autonomy classification, interface contracts

Or use the Meta-Orchestrator at L5 to design pipelines automatically.

## Step 6: Deploy the Meta-Orchestrator (Intelligent Routing)

Once you have multiple personas, deploy the Meta-Orchestrator as your system entry point.

Upload to your LLM platform:
- `master-expert/meta-orchestrator.md` -- as Project Instructions / system prompt (includes the full routing table)
- `methodology/v2-framework.md` -- as a Knowledge file (enables L6 persona creation)

The Meta-Orchestrator classifies tasks into resolution levels (L1-L6) from a single direct prompt to multi-persona pipelines to gap identification and new expert creation. At L6, the orchestrator identifies capability gaps and can auto-create the missing persona if you're running in Claude Code.

Note: `registry/registry.yaml` does NOT need to be uploaded -- the routing table is embedded in the orchestrator file. The registry is for the Python tooling only.

## File Reference

| File / Directory | Role | Upload to LLM? |
|---|---|---|
| `personas/*.md` | Self-contained expert system prompts | Yes |
| `master-expert/meta-orchestrator.md` | Routing layer with embedded routing table | Yes |
| `methodology/v2-framework.md` | Persona creation framework + validation rubrics | Yes |
| `registry/registry.yaml` | Machine-readable index for Python tooling | No |
| `adapters/*.md` | Platform deployment guides | No |
| `voice-cards/*.md` | Voice calibration profiles | Optional |
| `tools/*.py` | Registration, validation, export utilities | No |
