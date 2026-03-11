# The Architecture of Expertise

## A Comprehensive Framework for Engineering High-Fidelity LLM Personas

**Version 2.0 — Updated with Composability, Voice Calibration, and Scope Boundary Frameworks**

*February 2026*

---

## 1. The Paradigm Shift from Role-Based Prompting to Persona Engineering

This finding suggests that for a persona to be effective, it must be robust enough to maintain its specific linguistic and cognitive trajectory through the initial layers of processing to fully activate these deeper representations. Consequently, a high-fidelity expert persona must integrate multifaceted attributes, including professional history, specific technical knowledge, and a clearly defined value system, which collectively act as a "Persona Shell" or identity layer.

Critically, modern personas must also be composable — designed to operate alongside other personas in orchestrated multi-agent workflows, not merely as isolated conversational partners. This composability requirement introduces design considerations around interface contracts, role boundary clarity, and constraint compatibility that earlier persona engineering methodologies did not address. By developing a systematic framework for persona construction that accounts for both standalone quality and team-level composability, practitioners can maximize the reliability, accuracy, and professional utility of LLM outputs.

---

## 2. Neuro-Linguistic Encoding and the Mechanics of Persona Representation

This indicates that the LLM's latent space contains highly granular clusters of persona traits that can be strategically triggered.

| Persona Dimension | Model Representation Location | Behavioral Outcome |
|---|---|---|
| Personality Traits | Final 1/3 of Decoder Layers | Shifts in agreeableness, extraversion, and conscientiousness. |
| Professional Logic | Latent Role Vectors | Activation of domain-specific problem-solving strategies. |
| Linguistic Register | Syntax and Lexical Weights | Adjustment of tone, formality, and technical vocabulary. |
| Ethical Frameworks | Value-Driven Activation | Priority-based decision-making in ambiguous contexts. |

This suggests that overly hyperbolic or "imaginative" persona constructs can sometimes introduce noise into the model's reasoning process, whereas direct, specific role assignments ("You are a senior data scientist") are more effective. To maximize results, personas must be grounded in realistic professional standards rather than idealized or theatrical archetypes.

---

## 3. The Five-Part Structural Framework for Expert Personas

### 3.1 Role and Goal Definition

#### 3.1.1 Team Context and Role Boundary Design

When a persona is designed to operate within a multi-agent workflow — alongside other personas in a coordinated pipeline, supervisor-worker topology, or ensemble architecture — the Role and Goal definition must address team-level concerns that are absent in standalone persona design.

**Role Boundary Specification.** The persona's role definition should explicitly state what the persona does and does not own. In a team context, the most common source of dysfunction is blurred boundaries between adjacent roles: two personas that both "analyze data" with slightly different names will produce conflicting outputs and confuse the orchestrator. The Role section should include a brief "Out of Scope" declaration listing the competencies that belong to adjacent personas. For example, a Research Strategist in a content pipeline might declare: "This persona does not draft prose, edit copy, or make SEO recommendations. These functions are owned by adjacent personas."

**Cognitive Posture Differentiation.** When multiple personas share a team, the designer must ensure that role names reflect genuinely different reasoning styles, not merely different functional labels. Five personas with different titles but identical reasoning patterns (all analytical, all risk-averse, all structured-output-oriented) will produce homogeneous results regardless of their nominal specializations. The Role section should specify the persona's cognitive posture: is it an advocate, a skeptic, a synthesizer, a forensic investigator, or a creative generator? This specification drives meaningful diversity in team output.

**Constraint Compatibility.** When a persona will operate alongside others, the designer should review the constraint sets of adjacent personas for potential conflicts. If Persona A is mandated to "always provide comprehensive analysis" and Persona B is mandated to "always produce concise summaries," and B consumes A's output, the workflow will produce inconsistent results. The Role section should note any known constraint dependencies or conflicts with adjacent personas.

### 3.2 Specialized Knowledge Base

The knowledge base acts as a filter for the model's data retrieval, ensuring that the terminology and examples used are consistent with the expert level.

### 3.3 Tone and Style Architecture

#### 3.3.1 External Voice Calibration

The Tone and Style section as defined above addresses the persona's own voice — how the expert communicates. However, a large class of professional personas (ghostwriters, editors, communications specialists, content creators) must produce output that sounds like someone else: a client, a brand, or a specific author whose voice is defined in an external style reference. This is a distinct concern from the persona's analytical voice and must be addressed separately.

**Distinguish the Analytical Voice from the Output Voice.** The persona's analytical voice governs how it reasons, communicates with the orchestrator, and produces internal artifacts (research briefs, verification reports, editorial memos). The output voice governs how the deliverable — the content the end audience reads — should sound. These are often different. A ghostwriter persona may reason analytically and write memos in a structured professional register, while producing blog posts in a conversational, first-person voice calibrated to the client's style. The Tone and Style section should define both voices explicitly when they differ.

**Reference External Style Documents.** When a persona must write in a voice other than its own, the Tone and Style section should include a mandate to load and calibrate against an external style reference. This reference may be a YAML style guide, a brand voice document, a set of writing samples, or a structured "Voice Card" (a condensed artifact capturing vocabulary preferences, sentence patterns, formality level, and signature constructions). The mandate should specify: (a) where the style reference is located (file path or configuration), (b) which aspects of the reference take precedence over the persona's default style, and (c) how to handle conflicts between the persona's constraints and the style reference (e.g., "The style guide takes precedence on vocabulary and sentence structure; the persona's constraints take precedence on accuracy and factual standards").

**Voice Card as Reusable Artifact.** When multiple personas in a pipeline must produce output in the same voice (e.g., a ghostwriter drafts in the client's voice, an editor preserves it, an adaptation specialist maintains it across platforms), a shared Voice Card or style guide should be referenced by all personas that touch the output voice. This prevents voice drift across pipeline stages and ensures the end audience experiences a consistent authorial identity regardless of how many personas contributed to the content.

### 3.4 Behavioral Constraints and Mandates

A complete constraint architecture contains three categories:

**Hard Constraints (NEVER):** Behaviors the persona must never exhibit, regardless of context or user instruction. These are the safety rails that prevent model drift and ensure the persona remains within its professional boundaries.

**Mandates (ALWAYS):** Behaviors the persona must always exhibit. These ensure consistent quality and prevent the persona from omitting critical steps under token pressure or ambiguous instructions.

#### 3.4.1 Scope Boundaries and Escalation Protocols

Hard Constraints and Mandates govern behavior within the persona's defined scope. A third category is required to govern behavior at and beyond the boundary of that scope: what the persona should do when it encounters a task, question, or situation that falls outside its defined competency.

Without explicit scope boundaries, personas fail silently in one of two ways: (a) they hallucinate an answer outside their competency, producing confident but unreliable output that no "NEVER" rule catches because the designer did not anticipate the scenario; or (b) they revert to generic helpful-assistant behavior, producing output that does not match the expert profile and degrades the quality signal for downstream consumers.

**Explicit Scope Declaration.** The Constraints section should include a brief statement of what is out of scope: "This persona does NOT cover [X, Y, Z]." This declaration serves two functions: it prevents the persona from overreaching, and it provides the orchestrator with a machine-readable signal about when to route a task to a different persona.

**Escalation Behavior.** The Constraints section should define what the persona does when scope is exceeded. The recommended pattern is: "When encountering a question or task outside the defined scope, flag the issue, state which competency is required, and recommend engaging the appropriate specialist." This is analogous to a consultant saying "This is a legal question — you need counsel" rather than improvising a legal opinion.

**Distinguishing Knowledge Gaps from Scope Boundaries.** The persona should be instructed to differentiate between "I don't know" (a knowledge gap within scope — the persona should research or flag the gap) and "This is not my job" (a scope boundary — the persona should escalate). Conflating these leads to either over-escalation (the persona refuses to engage with anything uncertain) or under-escalation (the persona treats every question as within scope and answers regardless of competency).

#### 3.4.2 Interface Contracts and Composability

When a persona is designed to operate within a multi-agent workflow or to be reused across different pipelines, its Constraints section must define its interface contract: what the persona accepts as input and what it produces as output. This is analogous to defining a typed interface on a software component — it makes the persona self-describing without coupling it to any specific workflow.

Without an interface contract, personas that are individually excellent fail at integration. Each produces rich, unstructured output that the downstream persona is not designed to consume, leading to context loss, format mismatches, and orchestration failures at every stage boundary.

**Input Specification.** Define the input formats the persona can consume. This should include: (a) the artifact types accepted (e.g., "accepts a content brief, a Research Strategy Document, or a raw topic"), (b) the minimum required fields for each artifact type (e.g., "a content brief must include: topic, target audience, target length, and primary angle"), and (c) the persona's behavior when required fields are missing ("If target length is not specified, default to 1,200 words and note the assumption").

**Output Specification.** Define the output artifact the persona produces, including: (a) the artifact name and format (e.g., "produces a Verification Report in structured Markdown"), (b) the required fields and their types (e.g., "claim_id: string, claim_text: string, verdict: enum[pass, warning, fail, unverified], source: string, confidence: enum[high, medium, low]"), and (c) any summary or status fields that downstream consumers or orchestrators can use for routing decisions (e.g., "overall_risk: enum[green, yellow, red]").

**Format-Agnostic Integration Constraints.** The persona should include a mandate to "always produce output in structured format with labeled sections" — a baseline requirement that ensures any output is parseable by a downstream consumer, even if the specific handoff schema has not been defined. This makes the persona composable by default: it can be wired into a pipeline with explicit handoff contracts, but it can also be used standalone without breaking.

The interface contract is persona-level: it lives in the persona's profile and describes what the persona can accept and produce in any context. The specific field mappings between one persona's output and another persona's input — the handoff contracts — are workflow-level and should be defined in a separate pipeline orchestration document. This separation preserves persona reusability while enabling precise integration.

### 3.5 Example Output and Golden Samples

These examples provide the model with a template for formatting, depth of reasoning, and the specific application of the persona's logic. When the persona defines an interface contract (Section 3.4.2), at least one golden sample should demonstrate the persona's output artifact in its structured format, including all required fields. This ensures the model produces correctly formatted output that downstream consumers can parse.

### 3.6 Framework Summary

| Component | Requirement | Example |
|---|---|---|
| Role & Goal | Professional identity + specific objective + team context (if applicable). | Senior DevSecOps Engineer evaluating a CI/CD pipeline for vulnerabilities. Out of Scope: application logic review (owned by Code Reviewer persona). |
| Knowledge Base | Domain expertise + specific tools/versions + tacit knowledge. | Expertise in Kubernetes security, AWS IAM, and 15 years in cybersecurity. |
| Tone & Style | Emotional attitude + structural format + external voice calibration (if applicable). | Analytical and direct. Use Markdown tables. Output voice: calibrate to client's style guide (style.yaml). |
| Constraints | Hard boundaries (NEVER) + mandatory behaviors (ALWAYS) + scope boundaries (ESCALATE WHEN) + interface contract (INPUT/OUTPUT). | NEVER use jargon without definition. ESCALATE WHEN the question requires legal expertise. OUTPUT: Verification Report with claim-level verdicts. |
| Examples | 2-5 golden samples demonstrating reasoning, format, and interface contract output. | A complete security audit snippet in structured format with all required output fields populated. |

---

## 4. Integration of Elite Professional Methodologies

| Expert Framework | Core Operating Logic | Persona Application |
|---|---|---|
| MECE | No overlap, complete coverage. | Structural analysis, issue trees, and market segmentation. |
| Amazon 6-Pager | Narrative depth, substance over style. | Strategic planning, internal memos, and deep-dive reports. |
| Dalio Principles | Radical transparency, bias detection. | Conflict resolution, decision analysis, and second-order thinking. |
| Pyramid Principle | Conclusion first, then supporting data. | Executive summaries and persuasive communication. |

### 4.1 The McKinsey MECE Framework

By instructing a persona to use MECE logic, the model is forced to structure its analysis systematically. For example, when analyzing a restaurant's declining profitability, a MECE-enabled persona would divide the problem into "Increase Revenue" and "Reduce Costs," ensuring no overlapping factors and no missed areas.

### 4.2 The Amazon Narrative and 6-Page Memo

A persona modeled on this standard focuses on "substance and clarity," typically beginning with a rigorous analysis of the "State of the Business" and concluding with actionable "Strategic Priorities." This persona avoids "style over substance" and uses narrative prose to encourage deeper thinking and structured analysis among decision-makers.

### 4.3 Ray Dalio's Principles and Radical Transparency

Such a persona evaluates perspectives based on "believability-weighted" track records and maps out "second and third-order consequences" of any given action. It is explicitly instructed to "reveal hidden distortions" and prioritize "truth-seeking over harmony," providing a "clean slate" reference model for complex decisions.

---

## 5. Instructional Protocols for LLM-Driven Information Compilation

To build a robust expert persona, the LLM itself can be tasked with the research and synthesis required to define the profile. This process moves the persona development from guesswork to evidence-based construction.

### 5.1 Stage 1: The Contextual Deep-Dive and Asset Discovery

The first task is to instruct the LLM to gather raw data and "Expert Assets" from its knowledge base or the web. The model should identify the core documents that define the expert's field.

**Instructional Prompt:** "Act as a Senior Research Analyst with a focus on professional persona modeling. Your task is to compile a comprehensive knowledge base for the role of [X]. 1. Identify the 'Gold Standard' work products for this role. 2. Extract the core methodologies used by elite practitioners. 3. Document the 'Tacit Knowledge' — the unwritten rules, common industry skepticism, and 'never-do' boundaries that separate a junior from a senior expert. 4. Organize this information into a structured JSON 'Expert Blueprint' including headers for 'Core Competencies,' 'Preferred Methodologies,' and 'Ethical/Operational Constraints.'"

### 5.2 Stage 2: Searching for and Synthesizing Pre-Existing Profiles

**Instructional Prompt:** "Access repository structures like GitHub's 'Awesome ChatGPT Prompts' or 'PersonaHub' and search for robust profiles related to [X]. For each profile found: 1. Conduct a 'Diagnosis' identifying the technical decisions made in the prompt. 2. Compare these profiles against the Five-Part Structural Framework. 3. Identify gaps — what is missing that would prevent 'SOTA' results? 4. Synthesize the best elements into a 'Master Expert Profile.'"

### 5.3 Stage 3: Validation and Quality Benchmarking

The final stage of compilation is the validation of the persona's quality. The LLM must act as a judge to ensure the persona is robust and accurate.

Score the persona on a 1-5 scale across: Accuracy, Specificity, Constraint Robustness, Linguistic Fidelity, Interface Contract Completeness, and Scope Boundary Clarity. If any attribute scores below 4.5, initiate a 'Recursive Self-Improvement' loop to refactor that specific section until the quality target is met.

---

## 6. Technical Deployment: From Prompt to Persona Shell

### 6.1 The Persona Shell and Growth Metrics

The "Persona Shell" acts as a persistent identity module. In advanced implementations, this shell is stored as a JSON object containing core attributes (name, traits, values), growth metrics (tracking domain knowledge development), and relationship models (storing familiarity and communication preferences for specific users).

| Schema Element | Technical Implementation | Purpose |
|---|---|---|
| Core Identity | Static JSON Fields | Maintains stable traits and professional purpose. |
| Knowledge Vector | GraphRAG / TF-IDF | Connects persona to specific document subgraphs. |
| Memory Module | Temporal Tagging / Importance Scoring | Tracks context and past interaction outcomes. |
| Interaction Style | Probabilistic Gating | Adjusts formality and verbosity based on user needs. |
| Interface Contract | Typed Input/Output Schema | Defines accepted input artifacts and produced output artifacts with required fields. Enables composability across workflows. |
| Scope Boundary | Escalation Rules | Declares out-of-scope competencies and escalation behavior when scope is exceeded. |
| Voice Calibration | External Reference Path | Links to style guide, Voice Card, or writing samples for output voice calibration. |

### 6.2 Standardizing Identity with MCP and agents.md

MCP allows an expert persona to be stored as a Markdown file on local disk and "pulled" by any compatible LLM client (like Claude Desktop or Gemini CLI). This decoupling ensures that your expert persona is not "locked" into a single model but remains a portable software artifact.

It specifies project-specific tech stacks, coding styles, and executable test commands. This allows the AI to adopt a project-specific persona grounded in the actual codebase and project constraints.

#### 6.2.1 Separating Persona from Pipeline

When deploying personas in multi-agent workflows, maintain a clean separation between persona-level configuration (the Persona Shell, which is reusable) and pipeline-level configuration (the orchestration document, which is workflow-specific). The persona defines what the agent can accept and produce (interface contract); the pipeline document defines how agents connect to each other (handoff contracts, stage sequencing, autonomy levels, and cross-persona constraint overrides).

This separation allows the same persona to be reused in different workflows without modification. A Ghostwriter persona with a well-defined interface contract can be wired into a blog content pipeline, an investor communications pipeline, or a technical documentation pipeline — each with different orchestration documents that map its interface to different upstream and downstream consumers.

---

## 7. Advanced Optimization: Meta-Prompting and Self-Refinement

### 7.1 Recursive Self-Improvement Prompting (RSIP)

For example, after generating a first draft, the model might be prompted: "Review the above response. Does it follow the constraints of the persona? Is the tone too informal? If so, fix it." Research shows that even a single round of self-feedback can noticeably improve the reasoning and clarity of the expert response.

### 7.2 Multi-Perspective Simulation (MPS)

The model identifies distinct relevant perspectives (e.g., a skeptical CFO, a creative Product Manager, and a risk-averse Legal Counsel), simulates a dialogue between them, and concludes with an integrated analysis. This approach helps identify critical considerations that a single-persona view might overlook. Note: MPS is a within-conversation simulation technique and is distinct from multi-agent orchestration, where separate persona instances operate in a coordinated pipeline with explicit handoff contracts and autonomy governance.

### 7.3 Calibrated Confidence and Hallucination Mitigation

If a persona is unsure, it is instructed to flag the output as "ambiguous" or "insufficient information." This grounding ensures that the expert persona remains a reliable tool rather than a "confident hallucinator." The scope boundary framework (Section 3.4.1) reinforces this by giving the persona an explicit mechanism to escalate rather than guess when it encounters questions outside its defined competency.

---

## 8. Performance Benchmarking and Validation Rubrics

The final step in persona development is the application of a rigorous validation rubric to ensure that the "Silicon Sample" performs as intended across various scenarios.

### 8.1 The PDSQI-9 Validation Instrument

| # | Attribute | Success Criteria |
|---|---|---|
| 1 | Cited | All claims are supported by provided or external source material. |
| 2 | Accurate | Facts, data, and logic are factually correct and internally consistent. |
| 3 | Thorough | The analysis is deep, covering all major dimensions of the problem. |
| 4 | Useful | The output addresses the core user intent and provides actionable value. |
| 5 | Organized | Information is presented logically (e.g., using the Pyramid Principle or MECE). |
| 6 | Comprehensible | Precise language is used that is appropriate for the target audience. |
| 7 | Succinct | The response is concise, removing filler and redundant qualifiers. |
| 8 | Synthesized | Ideas are woven into a fluid narrative rather than disconnected facts. |
| 9 | Non-Stigmatizing | The response avoids reinforcing stereotypes or cultural bias. |

When validating personas designed for multi-agent workflows, two additional validation dimensions should be assessed alongside the PDSQI-9:

**Interface Contract Completeness.** Does the persona define its input and output artifacts with sufficient specificity that a downstream persona or orchestrator could consume its output without ambiguity? Are required fields defined? Is the output format structured and parseable?

**Scope Boundary Clarity.** Does the persona explicitly declare what is out of scope? Does it define escalation behavior? Can a reviewer read the persona's constraints and unambiguously determine whether a given task falls within or outside its competency?

### 8.2 Sensitivity and Robustness via PERSONA Bench

To truly validate a persona, one must test if the model's accuracy remains stable when the same task is requested in different "linguistic registers." A high-quality expert persona should maintain a consistent performance band rather than showing "brittle" performance that drops when the sociolinguistic framing changes.

---

## 9. Conclusion: Mastering the Agentic Persona

The development of an expert persona for an LLM is a transition from basic prompting to technical orchestration. By using the structural framework of Role, Knowledge, Tone, Constraints, and Examples, and grounding that framework in elite professional methodologies like MECE and Amazon Narratives, users can create synthetic agents that perform at the highest level of professional competence.

The framework extensions introduced in this version — interface contracts, scope boundaries, external voice calibration, and team context design — address the critical gap between building excellent standalone personas and building personas that are composable into multi-agent workflows. A persona that scores 5.0 on PDSQI-9 individually may still fail in a team if it lacks a defined interface, produces output that downstream consumers cannot parse, or shares blurred boundaries with adjacent roles. The extended framework ensures that persona quality encompasses both individual excellence and integration readiness.

As LLM applications evolve toward multi-agent workflows and persistent memory systems, the "Persona Shell" — complete with interface contracts, scope boundaries, and voice calibration references — will become the central organizing principle of the AI-human collaborative environment.

### 9.1 The Master Instantiation Directive

Updated to incorporate composability, voice calibration, and scope boundary concerns:

"You are now the 'Expert Prompt Design Agent' (EPDA). Your mission is to collaborate with me to translate an abstract goal into a concrete, robust expert persona profile. Follow this workflow rigorously:

**1. Initial Consultation:** Ask me to describe the target role and what a 'perfect' response looks like. Clarify whether this persona will operate standalone or within a multi-agent workflow. If the latter, ask about adjacent personas and the pipeline architecture.

**2. Diagnosis & Architecture:** Analyze the request and recommend a structural architecture (e.g., MECE for analysis, Amazon 6-pager for strategy). If the persona must write in a voice other than its own, identify the voice calibration requirements.

**3. Drafting the Master Prompt:** Create a system prompt including Role/Goal (with team context and scope boundaries if applicable), Knowledge Base, Tone (with external voice calibration if applicable), Constraints (including interface contract with input/output specifications and escalation protocols), and Examples (with at least one golden sample demonstrating the output artifact format).

**4. Validation & Refinement:** Run a 'Bias Scan' and score the draft against the PDSQI-9 rubric plus Interface Contract Completeness and Scope Boundary Clarity. Refactor until all scores are above 4.5.

**5. Output:** Deliver the final, optimized prompt in a clean Markdown code block ready for deployment in an MCP or agents.md environment."

---

## Works Cited

1. Role Prompting: Guide LLMs with Persona-Based Tasks. learnprompting.org.
2. Improving Alignment Between Human and Machine Codes. arXiv:2512.03818v1.
3. LLM Generated Persona is a Promise with a Catch. arXiv:2503.16527v1.
4. Localizing Persona Representations in LLMs. arXiv:2505.24539v1.
5. Modularizing LLMs, Memory, and Persona: A Blueprint for Practical AI Agents. Medium / DevSecOps AI.
6. Designing Role Vectors to Improve LLM Inference Behaviour. arXiv:2502.12055v1.
7. PERSONA Bench Benchmark. Emergent Mind.
8. LLM Personas: How System Prompts Influence Style, Tone, and Intent. Brim Labs.
9. Stop using "Act as a...": A 5-part framework for expert personas. Reddit / r/PromptEngineering.
10. How to write a great agents.md: Lessons from over 2,500 repositories. GitHub Blog.
11. Persona-Based LLM System. Emergent Mind.
12. How to Create McKinsey-Style Presentations (2026 Guide). SlideUpLift.
13. The Amazon 6-Pager: Guide, Templates & Tips. Visme.
14. Prompt Engineering for AI Guide. Google Cloud.
15. Meta Prompt Engineering. Romeo Mwafulirwa / Medium.
16. The Complete Prompt Engineering Guide for 2025. Alo Aguilar / Medium.
17. Guide to Writing System Prompts. Sahara AI.
18. MECE Framework McKinsey. MBA Crystal Ball.
19. MECE Framework Explained with Principles and Examples. CaseBasix.
20. No, we won't have a video call for that. Hacker News.
21. Using prompts to create prompts. Reddit / r/PromptEngineering.
22. Ray Dalio's Principles into AI prompts. Reddit / r/PromptEngineering.
23. The 5 GitHub Repositories Every Prompt Engineer Should Bookmark. DEV Community.
24. AI-Persona-Prompts-Unleash-the-Power-of-Great-Minds. GitHub / Dantheman23-coder.
25. Personal Prompt Engineer prompt. Reddit / r/ChatGPTPro.
26. Master Profile Prompt generator. Reddit / r/ChatGPTPro.
27. Evaluating clinical AI summaries with large language models as judges. PMC.
28. LLM-RUBRIC: A Multidimensional, Calibrated Approach. ACL Anthology.
29. LLM Evaluation Metrics: The Ultimate Guide. Confident AI.
30. Building custom LLM evaluation metrics. Rhesis AI.
31. Meta-Prompting: LLMs Crafting & Enhancing Their Own Prompts. IntuitionLabs.
32. persona: A developer-friendly toolkit for managing LLM personas. GitHub / JasperHG90.
33. awesome-copilot: Community-contributed instructions for GitHub Copilot. GitHub.
34. LLM Evaluation Metrics, Best Practices and Frameworks. Aisera.
35. Prompt Generator and Improver. Opik Documentation / Comet.
36. Top Prompt Engineering Tools for 2025. Irfan Sharief / Medium.
37. The Self-Improving Prompt System That Gets Smarter With Every Use. Substack / Karo Zieminski.
38. System-Prompt-Generation-Configurations. GitHub / danielrosehill.
