# Claude Adapter

Deploy AI Persona System personas inside Claude.ai Projects as persistent expert workspaces.

---

## Quick Start

1. Go to [claude.ai](https://claude.ai) and click **Create project**
2. In **Project Instructions**, paste **Part 1 (Role & Goal Definition)** and **Part 3 (Tone & Style Architecture)** from your chosen persona `.md` file
3. Upload the **full persona `.md` file** to Project Knowledge
4. Upload any additional relevant data files to Knowledge
5. Start chatting — the persona is active for every conversation in that Project

---

## What is a Claude.ai Project?

A Claude.ai Project is a persistent workspace with:
- **Instructions:** A system prompt (equivalent to a system-level persona definition) that applies to every conversation in the Project
- **Knowledge:** Uploaded files that Claude references across all conversations
- **Shared context:** All conversations within a Project share the same instructions and knowledge base
- **~200K token context window** for Claude 3 models

This maps cleanly to the AI Persona System because each persona `.md` file is already structured as a self-contained system prompt.

---

## Pattern 1: Split Persona — Identity in Instructions, Full File in Knowledge

**Use when:** You want a dedicated expert workspace — one domain, one persona, sustained over multiple conversations.

**Example use cases:**
- An AI CTO workspace for all architecture reviews and vendor assessments
- A Data Strategy Lead workspace for all database and pipeline design decisions
- A Content Research Strategist workspace for all editorial research tasks

**Steps:**

1. Go to **claude.ai > Projects > Create project**

2. Name the project to match the persona (e.g., "AI CTO", "Data Strategy Lead")

3. Click **Edit project instructions** and paste the **identity block** from the persona file:
   - **Part 1: Role & Goal Definition** — identity, objectives, cognitive posture, role boundaries
   - **Part 3: Tone & Style Architecture** — voice, tone, output format defaults
   - This keeps the core identity always in the system prompt (~25–40% of the full file, typically fits within the ~8K character instruction limit)

4. Upload to **Project Knowledge:**
   - The **full persona `.md` file** (Parts 1–5 — Claude retrieves detailed knowledge, constraints, and golden samples as needed)
   - Relevant domain data (architecture diagrams as text, RFCs, prior assessments)
   - Any companion tools or frameworks referenced in the persona

5. Start a conversation — the persona activates immediately on the first message

> **Note:** If the persona is small enough to fit entirely within the instruction limit (<8K characters), you can paste the entire file into Instructions instead of splitting.

**Interaction pattern — single-persona workspace:**
```
You: Evaluate our current microservices authentication pattern.
     We're using JWT with 24-hour expiry across 12 services.

[Persona responds in-character as AI CTO with architectural judgment]

You: What's your recommended migration path to short-lived tokens?

[Persona continues — no re-activation needed]
```

**Best for:**
- Sustained domain work across many sessions
- Sharing a consistent expert with a team (share the Project)
- Building up a knowledge base over time (upload new files as the domain evolves)

---

## Pattern 2: Meta-Orchestrator as Task Router

**Use when:** You want a persistent Task Router project powered by the full meta-orchestrator, have multiple personas in your registry, and want easy updates when personas change.

**Steps:**

1. Create a Claude.ai Project named "Task Router"

2. Paste the following into **Project Instructions:**

   > You are the **Task Resolution Strategist (Meta-Orchestrator)** for the AI Persona System.
   >
   > Your full persona definition — including your identity, decision hierarchy, routing table, golden samples, interface contract, and constraints — is provided in the uploaded knowledge file named `meta-orchestrator.md`.
   >
   > **On every conversation start:**
   > 1. Internalize the knowledge file as your system prompt.
   > 2. Operate exactly as specified: diagnose tasks, classify resolution levels (L1–L6), route to the optimal persona or prompt, and produce actionable output per the interface contract.
   > 3. Never fabricate persona capabilities — only route to personas listed in the routing table.
   >
   > **If the user asks "how many personas are in the system?" or similar:**
   > - Answer from the routing table in the knowledge file (count the rows).
   > - Do not guess or use a memorized number.
   >
   > For L6 (Gap Identification) tasks requiring new persona development, reference the uploaded `v2-framework.md` knowledge file — it contains the complete Five-Part Structural Framework (Sections 3.1–3.6), validation rubrics (PDSQI-9, Section 8), and the Master Instantiation Directive.
   >
   > You are the front door. Every task flows through you first.

3. Upload to **Project Knowledge:**
   - `master-expert/meta-orchestrator.md` — the full persona with routing table
   - `methodology/v2-framework.md` — enables L6 persona creation
   - Each persona `.md` file you want the Meta-Orchestrator to reference when routing

**Updating after persona changes:** When you add or modify personas, the routing table in `meta-orchestrator.md` updates automatically (via `sync_registry.py`). Re-upload the updated file to your Task Router project to pick up the changes.

**Best for:**
- Routing all tasks through a single intelligent entry point
- Teams with many personas who want consistent task classification
- Projects where the persona set changes over time

---

## Sharing Projects

Claude.ai Projects can be shared with collaborators (on Team/Enterprise plans):
- Share a Project to give a team a consistent expert interface
- All members see the same instructions and knowledge
- Each member's conversations are private within the shared Project

---

## Limitations & Notes

**Context window:** The ~200K token limit is generous. A single persona identity block (1,500–3,000 tokens) + the full persona in Knowledge (3,000–8,000 tokens) + supporting files leaves 180K+ tokens free. For knowledge-heavy projects, upload large reference documents as Knowledge files (indexed and retrieved selectively) rather than pasting into Instructions.

- **System prompt size:** Claude.ai has an ~8K character limit on Project Instructions. The split approach (identity block in Instructions, full file in Knowledge) solves this for all but the most extreme personas. If the identity block alone exceeds the limit, trim Part 3 formatting examples first.
- **Persona switching:** Single-persona Projects (Pattern 1) have one instruction set — to switch personas, create a separate Project or edit instructions. The Task Router (Pattern 2) effectively switches between personas within a conversation by routing tasks to different persona definitions in Knowledge.
- **Knowledge is not real-time:** Uploaded files are indexed at upload time. If you update a persona `.md`, re-upload the file to the Project.
- **No code execution:** Claude.ai Projects cannot run scripts, read local files, or execute shell commands. Outputs are text only — no automated file writes.
- **Conversation isolation:** Conversations within a Project share instructions and knowledge but not each other's history. Claude in Conversation B does not remember what was said in Conversation A.
- **Pipeline state is manual:** For multi-stage pipelines, Claude tracks state within a single conversation. If you close the conversation mid-pipeline, you must provide context to resume in a new conversation.

**Need more?** Several of these limitations are addressed by Claude Code. See the [Claude Code adapter](claude-code-adapter.md) for:
- Code execution and file system access
- Persistent memory across conversations (via CLAUDE.md and the memory system)
- Automated pipeline state management
- Automatic routing via the `/orchestrate` command
