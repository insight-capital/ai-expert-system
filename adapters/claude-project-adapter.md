# Claude.ai Project Adapter

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

## Pattern 2: Export-Based Deployment — Meta-Orchestrator as Task Router

**Use when:** You want a persistent Task Router project powered by the full meta-orchestrator, with easy updates when personas change.

**Why not Pattern 1?** The meta-orchestrator is ~55KB. Pasting it into Project Instructions works, but you must re-paste the entire file every time a persona is added or removed. Pattern 2 splits this into a stable loader prompt (pasted once) and a knowledge file (drag-and-drop to update).

**Setup (one time):**

1. Generate export files:
   ```bash
   python tools/export_claude_project.py
   ```

2. Create a Claude.ai Project named "Task Router"

3. Paste the contents of `exports/claude-project/project-instructions.md` into **Project Instructions** (~500 tokens, stable — you won't need to change this again)

4. Upload `exports/claude-project/meta-orchestrator-knowledge.md` as a **Project Knowledge** file

**Updating after persona changes:**

```bash
# 1. Add persona (existing workflow)
python tools/add_persona.py path/to/new-persona.md
#    → prints: "Claude.ai project knowledge file is now stale"

# 2. Re-export
python tools/export_claude_project.py

# 3. In Claude.ai Task Router project:
#    → Delete old meta-orchestrator-knowledge.md from Knowledge
#    → Upload the new one (drag-and-drop, ~10 seconds)
```

**Checking for drift:**
```bash
python tools/export_claude_project.py --check
# OK: Up to date (39 personas, 9 families).
# — or —
# STALE: Content has changed since last export (39 personas, was 27 at last export).
```

**How it works:**
- The loader prompt tells Claude to treat the knowledge file as its system prompt
- The knowledge file is the full meta-orchestrator with stale hardcoded counts patched to current values
- A manifest (`export-manifest.json`) tracks content hashes for drift detection
- `add_persona.py` automatically reminds you to re-export after registration

**Best for:**
- The "Task Router" project that uses the full meta-orchestrator
- Any deployment where the persona file is large and changes frequently
- Minimizing manual copy-paste overhead

---


## Context Window Management

The ~200K token limit is generous but not unlimited. Budget tokens carefully:

| Component | Approximate Token Cost | Priority |
|---|---|---|
| Identity block (Part 1 + Part 3) in Instructions | 1,500–3,000 tokens | High — core behavior, always in context |
| Full persona `.md` in Knowledge | 3,000–8,000 tokens | High — retrieved as needed |
| Supporting domain files | Varies | Medium — load only what's needed |
| Conversation history | Grows with each message | Monitor in long sessions |

**For single-persona projects:** No concern. The identity block in Instructions + the full persona in Knowledge + a few data files leaves 180K+ tokens free for conversation.

**For knowledge-heavy projects:** Upload large reference documents as Project Knowledge files (they are indexed and retrieved selectively) rather than pasting them into Instructions.

---

## Sharing Projects

Claude.ai Projects can be shared with collaborators (on Team/Enterprise plans):
- Share a Project to give a team a consistent expert interface
- All members see the same instructions and knowledge
- Each member's conversations are private within the shared Project

This is useful for deploying a `security-risk-lead` or `ai-cto` persona to an entire team without each member managing their own persona files.

---

## Limitations

- **System prompt size:** Claude.ai has an ~8K character limit on Project Instructions. The split approach (identity block in Instructions, full file in Knowledge) solves this for all but the most extreme personas. If the identity block alone exceeds the limit, trim Part 3 formatting examples first.
- **No dynamic persona switching:** A Project has one instruction set. To switch personas, create a separate Project or manually edit instructions. There is no `/switch-persona` mechanism inside a Project conversation.
- **Knowledge is not real-time:** Uploaded files are indexed at upload time. If you update a persona `.md`, re-upload the file to the Project.
- **No code execution:** Unlike Claude Code, Claude.ai Projects cannot run scripts, read local files, or execute shell commands. Outputs are text only — no automated file writes.
- **Conversation isolation:** Conversations within a Project share instructions and knowledge but not each other's history. Claude in Conversation B does not remember what was said in Conversation A.
- **Pipeline state is manual:** For multi-stage pipelines, Claude tracks state within a single conversation. If you close the conversation mid-pipeline, you must provide context to resume in a new conversation.
- **No automatic routing:** Claude.ai Projects do not automatically route tasks to different personas. Routing decisions must be prompted explicitly.
