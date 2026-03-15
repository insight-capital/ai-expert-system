# Claude Code Adapter

Deploy AI Persona System personas inside Claude Code sessions — as slash commands, project-level context, or a full meta-orchestrator.

---

## Quick Start

1. Pick a persona from `registry/registry.yaml`
2. Copy the persona `.md` file to `~/.claude/commands/<persona-id>.md`
3. Open any Claude Code session and type `/<persona-id>`
4. The persona activates immediately

---

## Pattern 1: Persona as /command

**Use when:** You want a persona available across all Claude Code sessions, independent of project.

**How it works:**
- Claude Code loads every `.md` file in `~/.claude/commands/` as an available slash command
- The filename becomes the command name (no extension)
- The file content becomes the system instruction for that invocation

**Steps:**

```bash
# Copy a single persona to your global commands directory
cp "personas/ai-cto.md" ~/.claude/commands/ai-cto.md
```

> **Batch install (optional):** To copy every persona at once, run `for f in personas/*.md; do cp "$f" ~/.claude/commands/$(basename "$f"); done` — this iterates over every `.md` file in `personas/` and copies each one to `~/.claude/commands/`.

**Invoke in any Claude Code session:**
```
/ai-cto
/data-strategy-lead
/prompt-architecture-strategist
```

**Precedence note:** Claude Code runs the command file content as a task instruction, not a persistent system prompt. For a persistent persona within a session, use Pattern 2 or Pattern 3.

**Best for:**
- Quick expert consultation during coding sessions
- One-off tasks (security review, ROI analysis, architecture critique)
- Personas you reach for frequently but not on every project

**Example — security review of a codebase:**
```
/security-risk-lead

Review the authentication flow in src/auth/ for vulnerabilities.
Flag anything that would block a SOC 2 audit.
```

---

## Pattern 2: Persona via CLAUDE.md

**Use when:** A specific project always requires a specific expert lens — the persona should be active from the first message of every session.

**How it works:**
- Claude Code reads `CLAUDE.md` (project root or `~/.claude/CLAUDE.md`) at session start
- Embedding a persona reference or full persona content here makes it always-on
- No slash command needed — the persona is the default behavior for that project

**Option A — Embed the full persona content:**

In your project's `CLAUDE.md`:
```markdown
## Active Persona

You are operating as the Data Strategy & Data Engineering Lead persona.
Apply this persona to all work in this session.

---

[paste full contents of personas/data-strategy-lead.md here]
```

**Option B — Reference the persona file by path:**

```markdown
## Active Persona

Load and apply the persona defined in:
~/ai-persona-system/personas/data-strategy-lead.md

This persona governs all analysis and recommendations in this project.
```

> **Tip:** You can reference more than one persona in CLAUDE.md — for example, a primary active persona plus additional specialists by path that Claude can consult on demand.

**Best for:**
- Domain-specific projects (content pipelines, data systems, security-critical code)
- Teams where a consistent expert voice is expected across sessions
- Long-running projects where re-invoking a persona every session is friction

---

## Pattern 3: Meta-Orchestrator as Project Intelligence

**Use when:** You have a complex task requiring multiple expert perspectives and want Claude Code to route work intelligently.

**How it works:**
- The meta-orchestrator reads the registry and routes tasks to appropriate personas
- Load it as a slash command: `/orchestrate`
- Provide the task and let the orchestrator decompose + delegate

**Setup:**

```bash
# Copy meta-orchestrator to commands
cp "master-expert/meta-orchestrator.md" ~/.claude/commands/orchestrate.md
```

**Invoke:**
```
/orchestrate

Task: Evaluate our AI vendor integration strategy. We need a security assessment,
an ROI model, and architectural recommendations before the board meeting.
```

The orchestrator will:
1. Parse the task against available persona capabilities
2. Identify which personas apply (security-risk-lead, value-roi-lead, agentic-systems-architect)
3. Sequence the work or flag parallel tracks
4. Synthesize outputs into a unified deliverable

**Best for:**
- Multi-stakeholder deliverables
- Tasks that span 3+ expert domains
- Assessment pipelines and content production workflows

---

## Persona ID to Command Name Reference

The command name matches the persona filename (without the `.md` extension). A few examples:

| ID | Persona Name | Command Name | Invoke With |
|----|---|---|---|
| persona-006 | Agentic Systems Architect | `agentic-systems-architect` | `/agentic-systems-architect` |
| persona-012 | AI Chief Technology Officer | `ai-cto` | `/ai-cto` |
| persona-018 | Data Strategy & Data Engineering Lead | `data-strategy-lead` | `/data-strategy-lead` |
| persona-020 | Business Blog Ghostwriter | `ghostwriter` | `/ghostwriter` |

For a complete list, see `registry/registry.yaml`.

---

## Tips

**Combining patterns:**
You can use Pattern 2 (always-on persona via CLAUDE.md) alongside Pattern 1 (ad-hoc slash commands). The CLAUDE.md persona sets the default lens; slash commands invoke specialists on demand.

**Persona chaining in a session:**
Invoke multiple personas sequentially within one session to simulate a pipeline:
```
/ai-cto
Assess the architecture. Output: architectural risks + recommendations.

---

/security-risk-lead
Review the same architecture. Focus on the risks the CTO flagged.
```

**Keeping commands current:**
If you update a persona file, re-copy it to `~/.claude/commands/`. The directory is read at session start — no daemon to restart.

**Creating new personas:**
Use the `/create-persona` skill to generate a complete persona from a role description:
```
/create-persona Senior M&A Integration Strategist
```
Generates the persona `.md` file, saves it to `personas/`, and auto-registers via `sync_registry.py`.

---

## Limitations

- **Context window shared with code:** Only the invoked persona loads into context — not all personas. However, in code-heavy sessions, a large persona file competes with code context for the available window. The Meta-Orchestrator (~55 KB) is the largest single file; individual personas are much smaller and only load when explicitly invoked. Prefer concise personas in large codebases.
- **No native persona handoff:** Claude Code does not natively pass persona state between slash command invocations. For true pipeline handoffs, use the meta-orchestrator (Pattern 3) or manage sequencing manually.
- **Command name collisions:** If a command name matches a built-in Claude Code command, the built-in wins. Check `~/.claude/commands/` for conflicts before naming.
- **No auto-discovery of personas:** The orchestrator's routing table is embedded in its own file. You do not need to load `registry.yaml` separately — but Claude Code has no auto-discovery of persona files outside `~/.claude/commands/`.
