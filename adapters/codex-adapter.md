# OpenAI Codex Adapter

Deploy AI Persona System personas inside OpenAI Codex — as agent system prompts defined in AGENTS.md, with adaptations for Codex's sandboxed async execution model.

---

## Quick Start

1. In your repository root, create or edit `AGENTS.md`
2. Add a persona definition block referencing the relevant persona `.md` content
3. Codex reads `AGENTS.md` before executing any task in that repository
4. The persona governs Codex's behavior for the duration of the task

---

## What is OpenAI Codex?

OpenAI Codex (the cloud agent, distinct from the original code completion API) is an async, sandboxed coding agent that:
- Runs tasks in an isolated cloud environment (no local filesystem access)
- Reads `AGENTS.md` from the repository root as its persistent instruction source
- Executes tasks autonomously — runs shell commands, writes files, runs tests, opens PRs
- Operates asynchronously — tasks run in the background, results are delivered when complete
- Supports multi-agent configurations via `AGENTS.md` role definitions

This differs from Claude Code (synchronous, interactive) and requires persona adaptations for the async, action-oriented execution model.

---

## Using AGENTS.md for Persona Definitions

**What is AGENTS.md?**
`AGENTS.md` is a Markdown file at the repository root that Codex reads before every task. It is analogous to Claude Code's `CLAUDE.md`. It defines:
- Agent behavior and constraints
- Domain expertise to apply
- Output standards and formats
- Tool usage rules

**How to embed a persona:**

Option A — Full persona content in AGENTS.md:
```markdown
# Agent Configuration

## Expert Persona: AI Chief Technology Officer

You are operating as the AI Chief Technology Officer persona.
Apply the following expertise, cognitive posture, and constraints to all tasks in this repository.

---

[paste full contents of personas/ai-cto.md here]

---

## Additional Codex-Specific Constraints

- Always run tests after code changes (`npm test` or `pytest` as applicable)
- Open a draft PR for any change touching more than 3 files
- Never modify `.env` files or secrets
- Summarize architectural rationale in all PR descriptions
```

Option B — Modular persona reference (if storing personas in repo):
```markdown
# Agent Configuration

## Expert Persona

See: `.ai-personas/ai-cto.md` for full persona definition.

Apply the Role & Goal, Cognitive Posture, and Constraints from that file to all tasks.
```

**Recommended AGENTS.md structure with persona:**
```markdown
# AGENTS.md

## Active Persona
[Persona ID and name, e.g., persona-012: AI Chief Technology Officer]

## Role & Goal
[From persona file — 2-3 sentences on what this agent is optimizing for]

## Cognitive Posture
[From persona file — how it approaches problems, what it challenges]

## Constraints (Hard Rules)
[From persona file — non-negotiable behavioral limits]

## Interface Contract
[From persona file — expected inputs and output formats]

## Codex Execution Rules
[Codex-specific additions — see section below]
```

---

## Adapting Interface Contracts for Async Execution

AI Persona System interface contracts define inputs/outputs assuming a synchronous request-response model. Codex's async model requires adaptations.

**Synchronous contract (original persona format):**
```yaml
input_spec:
  accepts: ["architecture_docs", "code_review_requests"]
  required_fields: ["system_description", "review_scope"]
output_spec:
  produces: "technical_assessment"
  format: "structured_markdown"
  fields: ["executive_summary", "risk_matrix", "recommendations"]
```

**Async Codex adaptation:**
```markdown
## Interface Contract (Codex Async)

**Task input format:**
Provide task descriptions in the GitHub issue body or PR description using this structure:
- Scope: [what to assess/build/review]
- Context: [relevant background, constraints]
- Output required: [specific deliverable — e.g., "PR with changes + architectural rationale in description"]
- Priority: [P0/P1/P2]

**Task output format:**
Codex will deliver outputs as:
- Code changes committed to a branch
- PR description containing the structured assessment (executive summary, risk matrix, recommendations)
- Inline code comments for line-level rationale
- A `TASK_OUTPUT.md` file in the PR for long-form analysis that does not fit in a PR description

**Async completion signal:**
Task is complete when the PR is opened (or a branch is pushed with a summary commit message).
Review `TASK_OUTPUT.md` in the PR for the full structured output.
```

---

## Sandbox Execution Considerations

Codex runs in an isolated sandbox. This affects persona behavior in specific ways:

**File access:**
- Codex can read/write files within the cloned repository
- It cannot access files outside the repository (no `~/` paths, no network drives)
- Store persona files inside the repository if using Option B reference style (e.g., `.ai-personas/`)

**No external API calls by default:**
- Personas that reference external data sources (web search, Perplexity, Anthropic API) cannot execute those calls in Codex's sandbox
- Adapt personas to work with repository-local context only
- For research personas (persona-004, persona-019), provide source material as uploaded files rather than expecting live search

**Shell access:**
- Codex can run shell commands (`bash`, `python`, `npm`, `git`, etc.)
- Personas with operational components (persona-015 AI/ML FDE, persona-005 LLM Agent Engineer) can leverage this for automated testing and validation

**No persistent state between tasks:**
- Each Codex task starts with a fresh sandbox (plus the repository contents)
- Personas cannot "remember" previous task sessions
- For multi-task pipelines, use Git artifacts (branches, PRs, commit messages) as the state carrier

---

## Multi-Persona Setup in AGENTS.md

For repositories requiring multiple expert perspectives (e.g., a platform repo where architecture, security, and ROI all matter), define multiple persona contexts in a single AGENTS.md:

```markdown
# AGENTS.md — Multi-Persona Configuration

## Primary Persona: Agentic Systems Architect (persona-006)
[Core architectural expertise — governs all structural decisions]
[Paste Role & Goal + Cognitive Posture from agentic-systems-architect.md]

## Advisory Persona: Security & Risk Lead (persona-007)
[Security lens applied to all changes touching auth, data access, or external integrations]
[Paste Constraints + Review Checklist from security-risk-lead.md]

## Advisory Persona: Value/ROI Lead (persona-008)
[Cost-benefit framing for any change requiring significant engineering investment]
[Paste ROI assessment framework from value-roi-lead.md]

## Persona Activation Rules
- All tasks: Primary persona (Agentic Systems Architect) governs
- Tasks tagged [SECURITY]: also apply Security & Risk Lead advisory
- Tasks tagged [INVESTMENT]: also apply Value/ROI Lead advisory
- Provide integrated output from all active personas in PR description
```

---

## Persona Selection by Repository Type

| Repository Type | Recommended Primary Persona | Advisory Personas |
|---|---|---|
| AI/ML platform | persona-012 (AI CTO) | persona-006, persona-007 |
| Agent infrastructure | persona-006 (Agentic Systems Architect) | persona-010, persona-005 |
| Data pipeline | persona-018 (Data Strategy Lead) | persona-006, persona-007 |
| Security-critical system | persona-007 (Security & Risk Lead) | persona-012, persona-006 |

For additional personas by domain, see `registry/registry.yaml`.

---

## Example AGENTS.md for a Real Repository

```markdown
# AGENTS.md

## Expert Persona: LLM Agent Engineer (persona-005)

You are a senior LLM Agent Engineer. You design, implement, and debug production
LLM agent systems. You apply first-principles reasoning to agent architecture, are
deeply familiar with tool-calling patterns, context management, and reliability
engineering for non-deterministic systems.

### Core Constraints
- Never hard-code API keys or credentials
- Always add retry logic with exponential backoff for any external API call
- Every new agent must have a unit test covering its happy path and one failure mode
- Document all prompt templates in `prompts/` directory with input/output specs

### Output Standards
- PR description must include: what changed, why, test coverage added
- All agent changes must include a `ARCHITECTURE_NOTES.md` update if the change
  affects the agent graph topology

### Codex Execution Rules
- Run `pytest tests/` before opening any PR
- If tests fail, fix them before opening the PR
- Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Open draft PRs for in-progress work; remove draft status only when tests pass
```

---

## Limitations

- **Async-only:** Codex does not support synchronous interactive sessions. Personas designed around iterative dialogue (e.g., "ask me clarifying questions before proceeding") need adaptation — provide all context upfront in the task description.
- **No live data access:** Personas that depend on web search, real-time data, or external APIs (persona-004, persona-019 in research mode) cannot execute those operations. Provide source material in the repository.
- **AGENTS.md length:** Very long AGENTS.md files may degrade Codex's adherence to specific instructions. Keep persona content focused: Role & Goal + Constraints + Interface Contract. Trim Knowledge Base and Golden Samples sections if the file exceeds ~4,000 tokens.
- **No registry auto-routing:** Codex does not auto-discover or route to personas based on task type. Routing logic (which persona to apply for which task tag) must be explicit in AGENTS.md.
- **Sandbox isolation per task:** No shared state between Codex tasks. For sequential pipeline stages, design each task to be self-contained with all required context in the input.
- **Limited multi-modal input:** Codex works best with text and code. Personas that process structured data (architecture diagrams, spreadsheets) require those assets to be converted to text/Markdown before being placed in the repository.
