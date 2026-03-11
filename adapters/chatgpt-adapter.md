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
- `registry/registry.yaml` (optional, if you want the GPT to cross-reference other personas)

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

## All 47 Personas — Custom GPT Configuration Reference

| ID | Persona Name | Suggested GPT Name | Knowledge Priority |
|---|---|---|---|
| persona-004 | AI Services Operations Researcher | AI Ops Researcher | client-context, persona-registry |
| persona-005 | LLM Agent Engineer | LLM Agent Engineer | agent-architecture-refs |
| persona-006 | Agentic Systems Architect | Agentic Architect | architecture-patterns |
| persona-007 | Security & Risk Lead | Security & Risk Lead | compliance-frameworks |
| persona-008 | Value/ROI Lead | ROI Analyst | roi-templates, vendor-data |
| persona-009 | Report Author & Editorial Director | Report Author | assessment-inputs |
| persona-010 | Multi-Agent Orchestration Architect | Orchestration Architect | system-design-refs |
| persona-011 | Prompt Architecture Strategist | Prompt Architect | prompt-pattern-library |
| persona-012 | AI Chief Technology Officer | AI CTO | tech-strategy-context |
| persona-013 | AI Strategy & GTM Lead | AI Strategy Lead | market-context |
| persona-014 | Senior AI Product Manager | AI Product PM | product-context |
| persona-015 | AI/ML Forward Deployed Engineer | AI/ML FDE | client-technical-docs |
| persona-016 | Forward Deployed Engineer (Generalist) | Forward Deployed Engineer | client-system-docs |
| persona-017 | AI-Augmented Productivity Lead | Productivity Lead | workflow-maps |
| persona-018 | Data Strategy Lead | Data Strategy Lead | schema-docs, pipeline-specs |
| persona-019 | Content Research Strategist | Content Strategist | style-guide, author-config |
| persona-020 | Business Blog Ghostwriter | Ghostwriter | style-samples, voice-template |
| persona-021 | Business Content Fact-Checker | Fact-Checker | source-library |
| persona-022 | Business Content Editor | Content Editor | style-guide, editorial-standards |
| persona-023 | SAEO Strategist | SAEO Strategist | content-inventory, seo-data |
| persona-024 | Content Adaptation Specialist | Content Adapter | platform-specs, source-content |
| persona-028 | AI / Emerging Technology Lawyer | AI Tech Lawyer | ai/ml-law-and-regulation, data-use-and-privacy |
| persona-029 | Commercial Contracts Lawyer | Contracts Lawyer | saas-and-technology-licensing, venture-studio-operating-and-jv-agreements |
| persona-030 | Corporate Counsel | Corporate Counsel | delaware-c-corp-formation-for-venture-backed-startups, delaware-llc-formation-and-operating-agreements-for-holding-companies,-spvs,-and-venture-studios |
| persona-031 | Corporate Dissolution & Wind-Down Counsel | Wind-Down Counsel | state-corporate-dissolution-law, certificate-of-dissolution-mechanics |
| persona-032 | Tax Attorney | Tax Attorney | entity-structuring, cross-border-/-international |
| persona-033 | Meridian -- Web3 Valuation & Digital Assets Advisor | Web3 Valuation Advisor | construction-and-maintenance-of-crypto-exposed-public-company-comp-sets:-miners, relevant-multiples:-ev/revenue,-ev/ebitda,-ev/active-users,-p/e,-price/book |
| persona-034 | Senior Valuation & Corporate Finance Advisor | Valuation Advisor | private-market-/-venture-stage-methods, public-market-methods |
| persona-035 | Strategic Valuation Positioning Advisor | Valuation Positioning Advisor | deep-fluency-in-valuation-methodologies:-dcf,-comparable-company-analysis,-precedent-transactions,-lbo-analysis,-sum-of-the-parts,-and-venture-stage-frameworks, expertise-in-multiple-expansion-mechanics:-what-drives-a-company-from-4x-to-12x-revenue-without-a-growth-rate-change-—-shift-in-perceived-business-model,-market-category,-margin-trajectory,-or-revenue-quality |
| persona-036 | Strategic Finance & Unit Economics Diligence Lead | Finance Diligence Lead | saas-metrics:-arr/mrr-construction,-net-revenue-retention,-logo-retention,-expansion-revenue-mechanics,-contraction-and-churn-decomposition, marketplace-and-platform-economics:-take-rates,-gmv-to-revenue-conversion,-liquidity-dynamics,-supply/demand-balance-metrics |
| persona-037 | Principal Engineer -- Code Auditor | Code Auditor | security-engineering |
| persona-038 | Principal Security Consultant | Security Consultant | security-engineering |
| persona-039 | Cybersecurity Vulnerability Advisor | Cybersecurity Advisor | application-security, infrastructure-&-cloud |
| persona-040 | Buy-Side M&A Advisor | Buy-Side M&A | m&a-/-deal-execution |
| persona-041 | Post-Merger Integration Lead | PMI Lead | day-1-readiness, first-100-days |
| persona-042 | Insurance Risk Advisor | Insurance Risk | m&a-/-deal-execution |
| persona-043 | M&A Data Integration Engineer | M&A Data Integration | m&a-/-deal-execution |
| persona-044 | Debt & Capital Markets Advisor | Debt Capital Markets | full-capital-structure-design:-senior-secured, tranche-level-sizing:-revolver-sizing-based-on-working-capital-seasonality-and-peak-borrowing-needs;-term-loan-sizing-based-on-leverage-capacity,-amortization-tolerance,-and-cash-flow-sweep-mechanics |
| persona-045 | Senior Transaction Services Advisor (Quality of Earnings) | Quality of Earnings | full-bridge-construction-methodology:-reported-net-income-→-add-back-interest,-taxes,-d&a-→-reported-ebitda-→-management-adjustments-→-buyer-adjustments-→-pro-forma-adjustments-→-run-rate-ltm-ebitda, adjustment-taxonomy:-non-recurring-vs |
| persona-046 | Capital Markets & Strategic Transactions Advisor | Capital Markets Advisor | valuation-finance |
| persona-047 | M&A Legal Counsel | M&A Legal Counsel | drafting-and-negotiating-asset-purchase-agreements,-stock-purchase-agreements,-merger-agreements, purchase-price-mechanics:-fixed-price,-locked-box,-closing-date-balance-sheet-adjustments,-working-capital-true-ups,-earnouts |
| persona-048 | Regulatory & Licensing Specialist | Regulatory Licensing | hsr/antitrust-filing-requirements-and-thresholds, cfius-review-process-for-foreign-investment-in-u |
| persona-049 | Applied AI Engineering Lead | AI Engineering Lead | general-ai-biz |
| persona-050 | Go-to-Market Strategy Lead | GTM Strategy Lead | market-segmentation-&-targeting, buyer-persona-&-buying-journey-analysis |

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
- **No programmatic access to registry:** The GPT cannot query `registry.yaml` as a structured API — it reads it as a document. For routing decisions in pipeline GPTs, provide explicit routing rules in the Instructions rather than expecting the GPT to parse registry YAML autonomously.
- **GPT model version:** Custom GPTs run on GPT-4o by default (as of 2026). Persona fidelity may vary if OpenAI updates the underlying model. Re-test after major model updates.
