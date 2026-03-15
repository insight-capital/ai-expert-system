# ChatGPT Custom GPT Adapter

Deploy AI Persona System personas as ChatGPT Custom GPTs — persistent expert interfaces available via ChatGPT's GPT Builder with a shareable URL.

---

## Quick Start

1. Go to [chatgpt.com](https://chatgpt.com) and click **Explore GPTs > Create a GPT**
2. In the **Configure** tab, paste your persona's Role & Goal + Cognitive Posture + Constraints into the **Instructions** field
3. Upload the full persona `.md` file under **Knowledge**
4. Set the GPT name and description to match the persona
5. Save and test

---

## What is a Custom GPT?

A Custom GPT is a persistent, shareable ChatGPT configuration with:
- **Instructions:** A system prompt governing behavior (up to ~8,000 tokens / ~32,000 characters)
- **Knowledge:** Uploaded files that the GPT can reference via retrieval
- **Capabilities:** Toggleable tools (web browsing, DALL-E image generation, code interpreter)
- **Actions:** Optional API integrations (custom OpenAPI endpoints)
- **Shareable URL:** A public or workspace-visible link to the configured GPT

The Instructions field maps directly to an AI Persona System persona definition. The Knowledge upload provides the full persona context and any supporting domain files.

---

## System Prompt Size Limit — 8K Token Budget

ChatGPT Custom GPT instructions are limited to approximately 8,000 tokens (~32,000 characters). Most AI Persona System persona files fall within this range, but dense personas with extensive Golden Samples may exceed it.

**Prioritization when truncation is needed:**

| Section | Priority | Action if over limit |
|---|---|---|
| Role & Goal | Critical | Always include — do not trim |
| Cognitive Posture | Critical | Always include — do not trim |
| Constraints (Hard Rules) | Critical | Always include — do not trim |
| Interface Contract | High | Include abbreviated version |
| Domain Scope | High | Include abbreviated list |
| Knowledge Base | Medium | Move to Knowledge file upload |
| Anti-Patterns | Medium | Include top 3 only |
| Golden Samples | Low | Move to Knowledge file upload |
| Formatting Rules | Low | Include 3-5 key rules only |

**Truncation strategy:**
1. Copy the full persona `.md` into the Instructions field
2. If the character count exceeds 32,000, remove the Golden Samples section first
3. If still over, move the Knowledge Base section to a Knowledge file upload
4. If still over, reduce Domain Scope to a bulleted list of 5-7 items
5. Upload the full untruncated persona as a Knowledge file so the GPT can reference it

---

## Step-by-Step: Deploying a Single Persona

**Example: Deploying the Security & Risk Lead (persona-007)**

**Step 1 — Open GPT Builder:**
- Go to chatgpt.com > Explore GPTs > Create a GPT
- Select the **Configure** tab (not the chat builder)

**Step 2 — Set name and description:**
```
Name: Security & Risk Lead
Description: Enterprise AI security and risk assessment specialist.
Reviews architectures, vendor integrations, and compliance posture.
Delivers structured risk matrices and go/no-go recommendations.
```

**Step 3 — Paste Instructions:**
Copy and paste from `personas/security-risk-lead.md`, starting from the Role & Goal section. If the file is within the 32K character limit, paste the entire file. If over, follow the truncation strategy above.

The opening line of your Instructions should orient the GPT immediately:
```
You are the Security & Risk Lead, a senior AI security specialist operating under
the AI Persona System framework. Apply the following persona definition to all
interactions in this GPT.

[paste persona content]
```

**Step 4 — Upload Knowledge files:**
Click **Upload files** under Knowledge and upload:
- `personas/security-risk-lead.md` (full file, for retrieval)
- Any domain-specific reference materials (compliance frameworks, threat taxonomies)

**Step 5 — Configure capabilities:**
- **Web browsing:** Enable if the persona needs current threat intelligence or CVE lookups
- **Code interpreter:** Enable if the persona may need to analyze configuration files or run compliance checks
- **DALL-E:** Disable (not relevant for text-based expert personas)

**Step 6 — Set conversation starters:**
Add 3-4 example prompts to guide users:
```
Review this API authentication design for SOC 2 compliance gaps
Assess our AI vendor integration risk posture
Provide a go/no-go recommendation for this third-party data pipeline
Create a risk matrix for our proposed cloud migration
```

**Step 7 — Save and test:**
- Click **Save** (Private or Anyone with a link)
- Test with a real input from the persona's expected use cases
- Verify the GPT responds in-character with the expected output format

---

## Pattern 1: Single Persona GPT

One Custom GPT per persona. Each GPT is a standalone expert.

**Best for:**
- Frequently used personas where direct access is valuable
- Sharing a specific expert with a team via a GPT link
- Personas with complex knowledge bases that benefit from file retrieval

**Recommended personas to deploy as standalone Custom GPTs:**

| Persona | GPT Name | Primary Use Case |
|---|---|---|
| persona-007 | Security & Risk Lead | Architecture reviews, vendor assessments |
| persona-012 | AI Chief Technology Officer | Strategic technology decisions |
| persona-020 | Business Blog Ghostwriter | Draft production |
| persona-022 | Business Content Editor | Editing and polish |
| persona-018 | Data Strategy Lead | Database and pipeline design |
| persona-011 | Prompt Architecture Strategist | Prompt engineering and optimization |

---

## Pattern 2: Pipeline GPT (Multi-Stage in One GPT)

Configure a single Custom GPT to run a multi-stage pipeline, with the Instructions defining the pipeline orchestration and Knowledge files containing all participating personas.

**Instructions template:**
```
You are a multi-stage content production pipeline. You manage the handoff between
four specialist personas to produce a final publishable piece.

Pipeline stages:
1. Content Research Strategist — topic research, angle development, source identification
2. Business Blog Ghostwriter — first draft production
3. Business Content Fact-Checker — accuracy and claim verification
4. Business Content Editor — final polish and structure

Execution rules:
- Run stages sequentially unless the user specifies otherwise
- Show each stage's output and ask for approval before advancing
- If the user says "run pipeline" without specifying stages, run all four
- Final output: formatted Substack post (or LinkedIn/X if specified)

All persona definitions are in the uploaded Knowledge files. Reference them by name.
```

**Knowledge files to upload:**
- `personas/content-research-strategist.md`
- `personas/business-blog-ghostwriter.md`
- `personas/business-fact-checker.md`
- `personas/business-content-editor.md`

**Best for:**
- Content production workflows where you want a single GPT URL for the full pipeline
- Teams that want one tool, not four separate GPTs

---

## Persona to Custom GPT Name Reference

The GPT name matches the persona display name. A few examples:

| ID | Persona Name | Suggested GPT Name | Knowledge Priority |
|---|---|---|---|
| persona-007 | Security & Risk Lead | Security & Risk Lead | compliance-frameworks |
| persona-012 | AI Chief Technology Officer | AI CTO | tech-strategy-context |
| persona-018 | Data Strategy Lead | Data Strategy Lead | schema-docs, pipeline-specs |
| persona-020 | Business Blog Ghostwriter | Ghostwriter | style-samples, voice-template |

For a complete list, see `registry/registry.yaml`.

---

## Tips

**Test with the persona's interface contract:** After configuring, send inputs that match the persona's `input_spec.required_fields`. Verify the response matches the `output_spec.format` and `fields`. If it does not, check that the Instructions section contains the Interface Contract block.

**Use conversation starters strategically:** The 4 conversation starters shown on the GPT landing page are prime real estate. Use them to demonstrate the persona's highest-value use cases. Pull examples directly from the persona's Golden Samples section.

**GPT vs. Claude for persona fidelity:** Custom GPT Instructions are a system prompt, not a fine-tuned model. Persona fidelity depends on how precisely the Instructions are written and how closely the user's prompts match the persona's expected input format. ChatGPT will generally follow the persona but may drift on ambiguous inputs. Claude models tend to maintain stronger persona consistency from the same persona `.md` content.

---

## Limitations

- **8K token instruction limit:** Large persona files with extensive Golden Samples may need trimming. Follow the prioritization table above.
- **Knowledge retrieval is non-deterministic:** Uploaded Knowledge files are retrieved by relevance, not loaded in full. Critical constraints and behavioral rules must be in the Instructions field (not just Knowledge files) to guarantee they are always applied.
- **No persistent cross-conversation memory by default:** Custom GPTs do not remember previous conversations unless the Memory capability is enabled and the user has memory turned on. Each conversation starts fresh.
- **No native pipeline orchestration:** A pipeline GPT (Pattern 2) requires the user to follow the pipeline protocol. ChatGPT has no built-in mechanism to enforce stage gates or prevent the user from skipping stages.
- **Sharing limitations:** Custom GPTs shared publicly are visible to all ChatGPT users. For internal-only use, use "Only me" or "Anyone with a link" (Team/Enterprise plans allow workspace sharing).
- **GPT model version:** Custom GPTs run on GPT-4o by default (as of 2026). Persona fidelity may vary if OpenAI updates the underlying model. Re-test after major model updates.
