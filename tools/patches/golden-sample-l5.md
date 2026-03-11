### Sample 5: L5 — Orchestrated Persona Workflow

```
TASK: "Produce a publish-ready thought leadership blog post on AI agents
replacing business analysts, with cross-platform adaptation for LinkedIn,
X, and Substack."

RESOLUTION LEVEL: Level 5 — Orchestrated Persona Workflow

RATIONALE: This task spans topic research, long-form drafting, claim
verification, editorial quality judgment, discoverability optimization, and
cross-platform adaptation — six distinct competencies with structured artifact
handoffs. A known validated workflow exists: content-pipeline.

ALTERNATIVES CONSIDERED:
- L1/L2 (Prompt): Rejected. The task requires specialized research methodology
  (persona-019's specialization), voice-calibrated long-form drafting
  (persona-020's specialization), fact verification (persona-021's
  specialization), editorial judgment (persona-022's specialization), SAEO
  optimization (persona-023's specialization), and platform adaptation
  (persona-024's specialization). A generic prompt would produce a generic
  article without the depth, accuracy, or platform optimization that a
  production pipeline delivers.
- L4 (Single Persona): Rejected. No single persona covers research AND
  drafting AND fact-checking AND editing AND optimization AND adaptation.
  The task inherently requires six distinct competencies in sequence.

ACTION: Deploy validated workflow content-pipeline.

PIPELINE:
Stage 1: Content Research Strategist (persona-019)
  Task: Identify angles, sources, key claims, and competitive content gaps
  for the topic. Produce Research Strategy Document (RSD).
  Input: Content brief (topic, audience, format, length).
  Output: Research Strategy Document with recommended angle, source plan,
  and confidence assessment.

Stage 2: Business Blog Ghostwriter (persona-020)
  Task: Draft the full blog post using the RSD as the foundation. Match
  the voice profile defined in the style guide.
  Input: RSD from Stage 1 + style guide.
  Output: Blog Post Draft + Draft Brief (thesis, structure, flagged
  placeholders).

Stage 3: Business Fact-Checker (persona-021)
  Task: Verify all factual claims in the draft. Flag unverifiable claims
  and statistical accuracy issues.
  Input: Draft from Stage 2.
  Output: Verification Report with per-claim ratings and risk summary.

Stage 4: Business Content Editor (persona-022)
  Task: Structural and line editing. Consume the verification report.
  Ensure voice consistency and publication readiness.
  Input: Draft from Stage 2 + Verification Report from Stage 3.
  Output: Editorial Memo + Revised Draft.

Stage 5: SAEO Strategist (persona-023)
  Task: Optimize the approved draft for search and AI engine discoverability.
  Structural recommendations only — does not rewrite prose.
  Input: Approved draft from human gate.
  Output: Post-Level SAEO Brief.

Stage 6: Content Adaptation Specialist (persona-024)
  Task: Adapt the final post for LinkedIn, X/Twitter, and Substack.
  Input: Final post (SAEO-optimized).
  Output: Content Adaptation Package (X thread, LinkedIn post, Substack
  framing, distribution sequence).

COMPOSABILITY CHECK: Confirmed.
- persona-019 output (RSD) matches persona-020 input spec.
- persona-020 output (Draft) matches persona-021 input spec.
- persona-021 output (Verification Report) + persona-020 output (Draft)
  match persona-022 compound input spec.
- persona-023 operates on the approved draft (post-human-gate).
- persona-024 receives the SAEO-optimized final post.
- Pipeline terminal stage (persona-024) produces the final deliverable.

EXPECTED FINAL OUTPUT: Publish-ready blog post + cross-platform content
adaptation package.
```
