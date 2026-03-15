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
# Copy a persona to your global commands directory
cp "personas/ai-cto.md" ~/.claude/commands/ai-cto.md

# Or for the full set — copy all 47 personas at once
for f in personas/*.md; do
  name=$(basename "$f")
  cp "$f" ~/.claude/commands/"$name"
done
```

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
<your-path> AI PERSONAS\AI Persona System\personas\data-strategy-lead.md

This persona governs all analysis and recommendations in this project.
```

**Real example — price-tracker-app project:**
The `data-strategy-lead` persona is the natural fit for that project's database architecture decisions. Add to `<your-path>`:

```markdown
## Expert Context

Apply the Data Strategy & Data Engineering Lead persona for all schema,
query optimization, and pipeline design decisions in this project.
See: <your-path> AI PERSONAS\AI Persona System\personas\data-strategy-lead.md
```

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

# Copy registry for context reference
cp "registry/registry.yaml" ~/.claude/commands/persona-registry.yaml
```

**Invoke:**
```
/orchestrate

Task: Evaluate our AI vendor integration strategy. We need a security assessment,
an ROI model, and architectural recommendations before the board meeting.

Registry context: ~/.claude/commands/persona-registry.yaml
```

The orchestrator will:
1. Parse the task against available persona capabilities
2. Identify which personas apply (security-risk-lead, value-roi-lead, agentic-systems-architect)
3. Sequence the work or flag parallel tracks
4. Synthesize outputs into a unified deliverable

**Best for:**
- Multi-stakeholder deliverables
- Tasks that span 3+ expert domains
- Assessment pipelines (Example Assessment pattern, content production)

---

## Persona ID to Command Name Reference

All persona IDs and their suggested Claude Code command names.
After copying to `~/.claude/commands/`, invoke with `/<command-name>`.

| ID | Persona Name | Suggested Command Name | Invoke With |
|----|---|---|---|
| persona-004 | AI Services Operations Researcher | `ai-services-researcher` | `/ai-services-researcher` |
| persona-005 | LLM Agent Engineer | `llm-agent-engineer` | `/llm-agent-engineer` |
| persona-006 | Agentic Systems Architect | `agentic-systems-architect` | `/agentic-systems-architect` |
| persona-007 | Security & Risk Lead | `security-risk-lead` | `/security-risk-lead` |
| persona-008 | Value/ROI Lead | `value-roi-lead` | `/value-roi-lead` |
| persona-009 | Report Author & Editorial Director | `report-author` | `/report-author` |
| persona-010 | Multi-Agent Orchestration Architect | `multi-agent-architect` | `/multi-agent-architect` |
| persona-011 | Prompt Architecture Strategist | `prompt-architect` | `/prompt-architect` |
| persona-012 | AI Chief Technology Officer | `ai-cto` | `/ai-cto` |
| persona-013 | AI Strategy & GTM Lead | `ai-strategy-gtm` | `/ai-strategy-gtm` |
| persona-014 | Senior AI Product Manager | `ai-product-pm` | `/ai-product-pm` |
| persona-015 | AI/ML Forward Deployed Engineer | `ai-ml-fde` | `/ai-ml-fde` |
| persona-016 | Forward Deployed Engineer (Generalist) | `forward-deployed-engineer` | `/forward-deployed-engineer` |
| persona-017 | AI-Augmented Productivity Lead | `productivity-lead` | `/productivity-lead` |
| persona-018 | Data Strategy & Data Engineering Lead | `data-strategy-lead` | `/data-strategy-lead` |
| persona-019 | Content Research Strategist | `content-strategist` | `/content-strategist` |
| persona-020 | Business Blog Ghostwriter | `ghostwriter` | `/ghostwriter` |
| persona-021 | Business Content Fact-Checker | `fact-checker` | `/fact-checker` |
| persona-022 | Business Content Editor | `content-editor` | `/content-editor` |
| persona-023 | SAEO Strategist | `saeo-strategist` | `/saeo-strategist` |
| persona-024 | Content Adaptation Specialist | `content-adapter` | `/content-adapter` |
| persona-028 | AI / Emerging Technology Lawyer | `ai-emerging-technology-lawyer` | `/ai-emerging-technology-lawyer` |
| persona-029 | Commercial Contracts Lawyer | `commercial-contracts-lawyer` | `/commercial-contracts-lawyer` |
| persona-030 | Corporate Counsel | `corporate-counsel` | `/corporate-counsel` |
| persona-031 | Corporate Dissolution & Wind-Down Counsel | `corporate-dissolution-wind-down-counsel` | `/corporate-dissolution-wind-down-counsel` |
| persona-032 | Tax Attorney | `tax-attorney` | `/tax-attorney` |
| persona-033 | Meridian -- Web3 Valuation & Digital Assets Advisor | `meridian-web3-valuation-digital-assets-advisor` | `/meridian-web3-valuation-digital-assets-advisor` |
| persona-034 | Senior Valuation & Corporate Finance Advisor | `senior-valuation-corporate-finance-advisor` | `/senior-valuation-corporate-finance-advisor` |
| persona-035 | Strategic Valuation Positioning Advisor | `strategic-valuation-positioning-advisor` | `/strategic-valuation-positioning-advisor` |
| persona-036 | Strategic Finance & Unit Economics Diligence Lead | `strategic-finance-unit-economics-diligence-lead` | `/strategic-finance-unit-economics-diligence-lead` |
| persona-037 | Principal Engineer -- Code Auditor | `principal-engineer-code-auditor` | `/principal-engineer-code-auditor` |
| persona-038 | Principal Security Consultant | `principal-security-consultant` | `/principal-security-consultant` |
| persona-039 | Cybersecurity Vulnerability Advisor | `cybersecurity-vulnerability-advisor` | `/cybersecurity-vulnerability-advisor` |
| persona-040 | Buy-Side M&A Advisor | `buy-side-m-a-advisor` | `/buy-side-m-a-advisor` |
| persona-041 | Post-Merger Integration Lead | `post-merger-integration-lead` | `/post-merger-integration-lead` |
| persona-042 | Insurance Risk Advisor | `insurance-risk-advisor` | `/insurance-risk-advisor` |
| persona-043 | M&A Data Integration Engineer | `m-a-data-integration-engineer` | `/m-a-data-integration-engineer` |
| persona-044 | Debt & Capital Markets Advisor | `debt-capital-markets-advisor` | `/debt-capital-markets-advisor` |
| persona-045 | Senior Transaction Services Advisor (Quality of Earnings) | `senior-transaction-services-advisor-quality-of-earnings` | `/senior-transaction-services-advisor-quality-of-earnings` |
| persona-046 | Capital Markets & Strategic Transactions Advisor | `capital-markets-strategic-transactions-advisor` | `/capital-markets-strategic-transactions-advisor` |
| persona-047 | M&A Legal Counsel | `m-a-legal-counsel` | `/m-a-legal-counsel` |
| persona-048 | Regulatory & Licensing Specialist | `regulatory-licensing-specialist` | `/regulatory-licensing-specialist` |
| persona-049 | Applied AI Engineering Lead | `applied-ai-engineering-lead` | `/applied-ai-engineering-lead` |
| persona-050 | Go-to-Market Strategy Lead | `go-to-market-strategy-lead` | `/go-to-market-strategy-lead` |

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

**Existing commands as a reference:**
Your 11 current commands (`~/.claude/commands/`) follow the same pattern — `workflow-viz.md`, `company-intel.md`, `reddit-research.md`, etc. Persona files drop in identically.

---

## Limitations

- **No persistent system prompt per invocation:** Slash commands run as task instructions, not sticky system prompts. The persona governs that invocation; the next message returns to default behavior unless you re-invoke or embed in CLAUDE.md.
- **Context window shared with code:** In active coding sessions, large persona files consume tokens that would otherwise go to code context. Prefer concise personas (or Pattern 2 CLAUDE.md reference) in large codebases.
- **No native persona handoff:** Claude Code does not natively pass persona state between slash command invocations. For true pipeline handoffs, use the meta-orchestrator (Pattern 3) or manage sequencing manually.
- **Command name collisions:** If a command name matches a built-in Claude Code command, the built-in wins. Check `~/.claude/commands/` for conflicts before naming.
- **Registry not auto-loaded:** The orchestrator pattern requires manually providing the registry file path. There is no auto-discovery of `registry.yaml` by Claude Code.
