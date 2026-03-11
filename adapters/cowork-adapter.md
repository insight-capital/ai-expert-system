# Claude Cowork Adapter

Deploy AI Persona System personas inside Claude Cowork (multi-agent) — as a project coordinator, as specialist agents, or as a full pipeline with monitored handoffs.

---

## Quick Start

1. Create a new Cowork project
2. Set the meta-orchestrator as the project-level coordinator agent
3. Add specialist agents by creating agent profiles with persona `.md` files as system prompts
4. Assign the coordinator to route tasks; let specialists handle domain execution

---

## What is Claude Cowork?

Claude Cowork is Anthropic's multi-agent workspace where multiple Claude instances run as distinct agents within a shared project. Each agent has:
- Its own system prompt (persona definition)
- Its own message thread
- The ability to receive tasks from a coordinator or human
- Visibility into a shared project context

This maps directly to the AI Persona System's composability model: each persona is already designed as a discrete agent with defined inputs, outputs, and interface contracts.

---

## Pattern 1: Meta-Orchestrator as Project Coordinator

**Use when:** You have a complex task requiring multiple expert perspectives and want a single coordinator to route work intelligently across specialists.

**How it works:**
- The meta-orchestrator agent reads the incoming task
- It identifies which specialist personas are relevant based on the registry
- It assigns subtasks to specialist agents in sequence or in parallel
- It synthesizes outputs into a unified deliverable

**Setup steps:**

1. Create a new Cowork project

2. Add a **Coordinator agent:**
   - Name: "Project Coordinator" or "Orchestrator"
   - System prompt: full contents of `master-expert/meta-orchestrator.md`
   - Role: receives all incoming tasks, routes to specialists

3. Upload `registry/registry.yaml` as shared project context so the coordinator can reference persona IDs and capabilities

4. Add specialist agents (see Pattern 2)

5. Provide tasks to the coordinator:
```
Task: Produce a board-ready assessment of our AI vendor integration options.
We need: security posture analysis, ROI model for top 3 vendors, architectural fit review.
Deadline: EOD Friday.
```

The coordinator will:
- Parse the task against registry capabilities
- Assign security analysis to the Security & Risk Lead agent
- Assign ROI modeling to the Value/ROI Lead agent
- Assign architecture review to the Agentic Systems Architect agent
- Consolidate outputs via the Report Author agent

**Best for:**
- Multi-domain deliverables with a single output artifact
- Tasks where scope is unclear upfront and routing decisions are non-trivial
- Projects where the human does not want to manage agent assignment manually

---

## Pattern 2: Individual Personas as Task Specialists

**Use when:** You know which experts you need and want to configure each as a named specialist agent for direct interaction or coordinator routing.

**Setup steps:**

1. For each persona you want to deploy, create an agent in Cowork:
   - **Agent name:** Use the persona's display name (e.g., "Security & Risk Lead")
   - **System prompt:** Paste the full contents of the corresponding persona `.md` file
   - **Tag or label:** Include the persona ID (e.g., `persona-007`) for coordinator reference

2. Configure agent capabilities to match the persona's `domain_scope` in the registry

3. Assign agents to the project — they are now available for direct messaging or coordinator routing

**Example agent configuration — Security & Risk Lead:**
```
Agent name: Security & Risk Lead (persona-007)
System prompt: [full contents of personas/security-risk-lead.md]
Input: architecture docs, threat models, vendor assessments
Output: risk matrices, go/no-go recommendations, remediation roadmaps
```

**Direct agent interaction:**
```
Human → Security & Risk Lead:
Review this API authentication design for SOC 2 compliance gaps.
[attach architecture doc]

Security & Risk Lead → Human:
Risk matrix with severity ratings and remediation steps.
```

**Coordinator-routed interaction:**
```
Coordinator → Security & Risk Lead:
Subtask 1 of 3: Assess authentication architecture (see attached doc).
Output required: risk matrix + top 3 remediation priorities.
Return output to coordinator when complete.
```

**Recommended specialist agent set for common pipelines:**

| Pipeline | Agents to Configure |
|---|---|
| AI vendor assessment | persona-006, persona-007, persona-008, persona-009, persona-012 |
| Content production | persona-019, persona-020, persona-021, persona-022 |
| Example Assessment | persona-004, persona-005, persona-006, persona-007, persona-008, persona-009 |
| Technical architecture review | persona-006, persona-010, persona-012, persona-015 |

---

## Pattern 3: Pipeline Handoff Monitoring

**Use when:** You want to run a defined multi-stage pipeline in Cowork with explicit stage gates and human review checkpoints between stages.

**How it works:**
- Each pipeline stage is a separate agent with a single-stage persona
- The Cowork coordinator manages handoffs
- Human review is injected at defined checkpoints before the next stage receives input
- The coordinator tracks pipeline state and logs stage outputs

**Setup:**

1. Configure a coordinator agent with the pipeline sequence document as its system prompt (e.g., `prompts/sequences/content-production-pipeline.md`)

2. Configure one agent per pipeline stage:
   - Stage 1: Content Research Strategist (persona-019)
   - Stage 2: Business Blog Ghostwriter (persona-020)
   - Stage 3: Business Content Fact-Checker (persona-021)
   - Stage 4: Business Content Editor (persona-022)
   - Stage 5: Content Adaptation Specialist (persona-024, optional)

3. Define handoff protocol in the coordinator's instructions:
```
Pipeline execution protocol:
1. Receive topic brief from human
2. Route to Stage 1 agent (Content Research Strategist)
3. Receive Stage 1 output — present to human for approval
4. On human approval: route Stage 1 output to Stage 2 agent
5. Continue through all stages with approval gates
6. Deliver final output to human after Stage 4 (or 5)
```

**Pipeline execution in Cowork:**
```
Human → Coordinator:
Run content pipeline.
Topic: "AI agents replacing business analysts"
Audience: Mid-market ops leaders
Length: 1,200 words

Coordinator → Stage 1 (Content Research Strategist):
[Forwards brief]

Stage 1 → Coordinator:
[Research brief with angles, sources, key claims]

Coordinator → Human:
Stage 1 complete. Research brief attached. Approve to proceed to drafting?

Human → Coordinator: Approved

Coordinator → Stage 2 (Ghostwriter):
[Forwards research brief]
...
```

**Best for:**
- Content pipelines where quality gates matter
- Assessment pipelines with defined deliverables at each stage
- Workflows where the human wants visibility into intermediate outputs before handoff

---

## Interface Contract Alignment

Each persona's `interface_contract` section defines its expected inputs and outputs. When configuring Cowork agents, use these contracts to set agent expectations:

```yaml
# From registry.yaml — persona-007 Security & Risk Lead
input_spec:
  accepts: ["architecture_docs", "threat_models", "vendor_assessments"]
  required_fields: ["system_description", "threat_context"]
output_spec:
  produces: "risk_assessment_report"
  format: "structured_markdown"
  fields: ["risk_matrix", "severity_ratings", "remediation_roadmap"]
```

In Cowork, configure the agent's input/output expectations to match these specs. This ensures the coordinator can hand off cleanly between agents without format translation.

---

## Tips

**Start with fewer agents:** Configure 2-3 specialists before scaling to a full pipeline. Validate that each agent produces the expected output format before adding the next stage.

**Name agents by persona ID:** Include the ID (e.g., `persona-007`) in the agent name. This makes coordinator routing instructions unambiguous and easier to debug.

**Keep coordinator instructions minimal:** The meta-orchestrator already has detailed routing logic in its persona file. Avoid duplicating routing rules in Cowork coordinator settings — let the persona govern.

**Test handoffs with synthetic input:** Before running a real task, test each handoff with a short synthetic input. Confirm the receiving agent produces the expected output format before wiring up the full pipeline.

---

## Limitations

- **No shared memory across agent threads:** Each agent in Cowork has its own context window. Shared knowledge (registry, domain docs) must be uploaded to the project level and available to all agents.
- **Coordinator routing is prompt-driven, not programmatic:** The coordinator routes by reading its instructions and making judgment calls — it does not use a deterministic routing algorithm. Ambiguous tasks may route to the wrong specialist.
- **Pipeline state is ephemeral:** Cowork does not natively persist pipeline state between sessions. If a pipeline run is interrupted, restart from the last completed stage manually.
- **Parallel execution constraints:** Fully parallel agent execution (e.g., 4 specialists working simultaneously on stage 2 of the Example pipeline) depends on Cowork's concurrency model. Verify concurrent agent limits for your plan before designing parallel stages.
- **Persona file size:** Very large persona files (>8K tokens) as agent system prompts may compress or lose lower-priority sections. Prioritize Role & Goal, Cognitive Posture, Constraints, and Interface Contract. Trim Golden Samples if needed.
- **No cross-agent memory by default:** Agent A does not know what Agent B said in a previous conversation. For continuity, route all context through the coordinator, which aggregates and forwards relevant outputs.
