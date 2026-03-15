# Google Gemini Gems Adapter

Deploy AI Persona System personas as Google Gemini Gems — persistent expert configurations available through Gemini Advanced with a custom instruction set and uploaded context files.

---

## Quick Start

1. Go to [gemini.google.com](https://gemini.google.com) and select **Gems** in the left sidebar
2. Click **Create a Gem**
3. In the **Instructions** field, paste your persona's core content (Role & Goal, Cognitive Posture, Constraints, Interface Contract)
4. Upload the full persona `.md` file as a context file
5. Name the Gem after the persona and save
6. Start a conversation — the persona is active

---

## What is a Gemini Gem?

A Gemini Gem is a persistent, custom Gemini configuration with:
- **Instructions:** A free-form text field defining the Gem's behavior (Gemini's equivalent of a system prompt)
- **Context files:** Uploadable files that the Gem references during conversations
- **Name and description:** Shown on the Gem's landing card
- **Persistent access:** Available across all Gemini conversations via the Gems panel

Gems are available on Gemini Advanced (Google One AI Premium or Workspace plans). The context window for Gemini 1.5 Pro and Gemini 2.0 Flash is up to 1 million tokens — significantly larger than ChatGPT Custom GPTs (8K instruction limit) and comparable to Claude.ai Projects (~200K).

---

## Gemini vs. Claude Format Differences

AI Persona System personas are written in Markdown with Claude in mind. Gemini Gems use the same Markdown-structured Instructions format, but there are a few behavioral and format differences to be aware of:

**1. Instruction format:**
- Gemini Gems accept plain text or Markdown in the Instructions field
- Markdown headers (`##`), bullet lists, and bold text all render correctly
- The full persona `.md` structure (Role & Goal, Cognitive Posture, etc.) works as-is — no reformatting required

**2. Context window:**
- Gemini 1.5 Pro / 2.0: up to 1 million tokens
- Gemini 2.0 Flash: 1 million tokens input context
- This means you can upload significantly more supporting files than in ChatGPT Custom GPTs
- For pipeline Gems, load all participating persona files without concern for truncation

**3. Persona adherence:**
- Gemini tends to follow persona instructions well for structured, domain-specific tasks
- For highly constrained output formats (JSON arrays, structured risk matrices), include explicit format examples in the Instructions — Gemini responds well to few-shot formatting guidance
- Gemini may be slightly more likely than Claude to offer unsolicited alternatives or caveats when the persona calls for direct, opinionated output. Counter this by including a constraint like: "Do not offer alternatives unless explicitly asked. Provide direct recommendations."

**4. File retrieval:**
- Gemini retrieves context file content more holistically than GPT's vector retrieval
- Large context windows mean full file content is often loaded, not just retrieved chunks
- This makes Gemini Gems particularly good for persona configurations that reference detailed domain knowledge (e.g., persona-007 with a full compliance framework uploaded)

**5. Multimodal support:**
- Gemini natively processes images, PDFs, audio, and video in context
- Personas that work with visual inputs (architecture diagrams, screenshots) benefit from Gemini's multimodal capabilities without needing special handling

---

## Step-by-Step: Deploying a Single Persona Gem

**Example: Deploying the Data Strategy & Data Engineering Lead (persona-018)**

**Step 1 — Open Gems:**
- Go to gemini.google.com
- In the left sidebar, click **Gems**
- Click **Create a Gem** (or the **+** icon)

**Step 2 — Set the Gem name:**
```
Data Strategy & Data Engineering Lead
```

**Step 3 — Add Instructions:**
Paste the persona content. The opening should orient Gemini clearly:

```
You are the Data Strategy & Data Engineering Lead, a senior expert in data architecture,
pipeline design, and data platform strategy. Apply the following persona definition to
all interactions in this Gem.

## Role & Goal
[paste from personas/data-strategy-lead.md]

## Cognitive Posture
[paste from personas/data-strategy-lead.md]

## Constraints
[paste from personas/data-strategy-lead.md]

## Interface Contract
[paste from personas/data-strategy-lead.md]

## Output Format Rules
- Always structure recommendations as: Assessment → Options → Recommendation → Trade-offs
- Use Markdown tables for schema comparisons and performance benchmarks
- Lead with the recommendation; justify afterward
- Do not use hedging language ("might", "could potentially") — state positions directly
```

The full persona `.md` file content can be pasted into Instructions without truncation concerns — Gemini's instruction field accepts long content.

**Step 4 — Upload context files:**
Click **Add files** and upload:
- `personas/data-strategy-lead.md` (full file)
- Any project-specific schema docs, ERDs, or pipeline specs

**Step 5 — Save and test:**
- Click **Save**
- Test with an input matching the persona's `input_spec.required_fields`
- Example test prompt: "Review this PostgreSQL schema for a multi-tenant SaaS application. Flag normalization issues and recommend indexing strategy."
- Verify the output matches the persona's expected format

---

## Pattern 1: Single Domain Expert Gem

One Gem per persona. Direct expert access, always available from the Gems sidebar.

**Best for:**
- High-frequency expert consultations
- Domain-specific projects where one persona covers 80% of the work
- Sharing expert access with Google Workspace colleagues (Gemini for Workspace plans support Gem sharing)

**Recommended Gems by use case:**

| Use Case | Persona | Gem Name |
|---|---|---|
| Database & pipeline design | persona-018 | Data Strategy Lead |
| Security reviews | persona-007 | Security & Risk Lead |
| Prompt engineering | persona-011 | Prompt Architect |
| Content drafting | persona-020 | Business Ghostwriter |
| AI product strategy | persona-014 | AI Product PM |
| Architecture design | persona-006 | Agentic Architect |
| AI/ML deployment | persona-015 | AI/ML Engineer |

---

## Pattern 2: Pipeline Gem (Multi-Stage Orchestration)

Configure a single Gem to orchestrate a multi-stage pipeline, with all stage persona files uploaded as context.

**Instructions template for a content pipeline Gem:**

```
You are a multi-stage content production pipeline running four specialist personas
in sequence. The persona definitions for each specialist are in the uploaded context files.

## Pipeline Stages

Stage 1 — Content Research Strategist (persona-019)
Input: Topic brief, audience description, content goals
Output: Research brief with angles, sources, key claims, recommended structure

Stage 2 — Business Blog Ghostwriter (persona-020)
Input: Research brief from Stage 1
Output: Full draft in Substack Markdown format

Stage 3 — Business Content Fact-Checker (persona-021)
Input: Draft from Stage 2
Output: Annotated draft with fact-check flags, confidence ratings per claim

Stage 4 — Business Content Editor (persona-022)
Input: Fact-checked draft from Stage 3
Output: Final polished version, publication-ready

## Execution Protocol
1. When the user provides a topic brief, activate Stage 1 immediately
2. Show the full Stage 1 output
3. Ask: "Proceed to Stage 2 (drafting)?" — wait for confirmation
4. Continue through all stages with confirmation gates
5. Deliver the final output after Stage 4

## Persona reference files
content-research-strategist.md, business-blog-ghostwriter.md,
business-fact-checker.md, business-content-editor.md
```

**Context files to upload:**
- `personas/content-research-strategist.md`
- `personas/business-blog-ghostwriter.md`
- `personas/business-fact-checker.md`
- `personas/business-content-editor.md`
- Any author config or style guide relevant to your publication

Given Gemini's 1M token context window, loading all four persona files simultaneously is not a concern.

---

## Formatting Guidance for Gemini

Gemini responds well to structured Instructions. Use these formatting practices for best persona fidelity:

**Use explicit section headers:**
```markdown
## Role & Goal
## Cognitive Posture
## Hard Constraints
## Output Format
## Examples
```

**Include at least one output format example:**
Gemini tends to follow format examples more reliably than abstract format descriptions. From the persona's Golden Samples section:
```markdown
## Example Output Format

When assessing a risk, always structure your response as:

**Risk:** [name]
**Severity:** [Critical / High / Medium / Low]
**Likelihood:** [High / Medium / Low]
**Business Impact:** [1-2 sentences]
**Remediation:** [specific action items]
```

**Counteract hedging with explicit constraints:**
If the persona requires direct, opinionated recommendations (most do), add:
```markdown
## Tone Constraints
- State positions directly. Do not use "might", "could potentially", "it depends" as answers.
- When you disagree with an approach, say so directly and explain why.
- Offer one primary recommendation, not a menu of equal alternatives.
```

---

## Gem Sharing in Google Workspace

For teams using Google Workspace with Gemini for Workspace:
- Gems can be shared with specific users or workspace-wide
- Shared Gems are visible in colleagues' Gems sidebar
- This enables deploying a single `ai-cto` or `security-risk-lead` Gem across an entire team

To share: Open the Gem > click the share icon > add Google Workspace users or set workspace-wide visibility.

---

## Persona to Gem Name Reference

A few examples of Gem configurations:

| ID | Persona Name | Gem Name | Suggested Context Files |
|---|---|---|---|
| persona-007 | Security & Risk Lead | Security & Risk Lead | compliance frameworks, threat taxonomies |
| persona-012 | AI Chief Technology Officer | AI CTO | tech strategy context, roadmap docs |
| persona-018 | Data Strategy Lead | Data Strategy Lead | schema docs, pipeline specs, ERDs |
| persona-020 | Business Blog Ghostwriter | Ghostwriter | voice template, style samples |

For a complete list, see `registry/registry.yaml`.

---

## Limitations

- **No programmatic execution:** Unlike Claude Code, Gemini Gems cannot run shell commands, write files, or execute code against a local filesystem. Personas with operational components are advisory only in Gem context.
- **Instructions field is not versioned:** If you update a persona file, manually re-paste updated content into the Gem Instructions. There is no auto-sync from a file path.
- **Gem availability:** Gems require Gemini Advanced (Google One AI Premium or Google Workspace with Gemini add-on). Check current pricing on Google's plans page. Not available on free Gemini tier.
- **No native pipeline state tracking:** Pipeline Gems track state within a single conversation only. If the conversation is closed mid-pipeline, provide context to resume in a new conversation.
- **Context file formats:** Gemini accepts PDF, text, Markdown, code files, and images. For personas referencing `.docx` or `.xlsx` source materials, convert to PDF or Markdown before uploading.
- **Persona drift on long conversations:** On very long conversations (50+ turns), Gemini may drift from persona constraints. If drift occurs, start a new conversation in the same Gem — the Instructions reset cleanly.
