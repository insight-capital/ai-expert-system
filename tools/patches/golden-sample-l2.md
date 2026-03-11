### Sample 2: L2 — Simple Prompt Sequence

```
TASK: "Research the top 5 competitors to our SaaS analytics product, create
a comparison table of features and pricing, then write a one-page recommendation
on positioning."

RESOLUTION LEVEL: Level 2 — Simple Prompt Sequence

RATIONALE: Three stages (research, tabulate, recommend), all linear (A->B->C),
no conditional branching, no specialized domain expertise required beyond general
business analysis. Each step has a single predictable output that feeds the next.
No persona needed — a general-purpose model with good prompting handles all three
stages competently.

ALTERNATIVES CONSIDERED:
- L1 (Single Prompt): Rejected. Asking a single prompt to research, tabulate,
  AND recommend would produce shallow research and a rushed recommendation.
  Separating the stages allows each to receive full attention.
- L4 (AI Strategy & GTM Lead, persona-013): Rejected. While persona-013 covers
  competitive positioning, this task is a lightweight comparison exercise, not a
  full GTM strategy engagement. The judgment complexity does not warrant a
  specialized persona.

ACTION: Define three-step prompt sequence.

SEQUENCE:
Step 1 — Competitive Research
  Prompt: "You are a market research analyst. Identify the top 5 competitors
  to a SaaS analytics platform that provides real-time business metrics
  dashboards, automated reporting, and predictive analytics for mid-market
  companies. For each competitor, document: company name, product URL, key
  features, pricing model, target market, and notable strengths/weaknesses.
  Present as a structured list."
  Input: Product description (above).
  Output: Structured competitor profiles (5 entries).

Step 2 — Comparison Table
  Prompt: "Using the competitor research below, create a feature and pricing
  comparison table. Columns: Company, Key Features, Pricing, Target Market,
  Strengths, Weaknesses. Include our product as the first row for direct
  comparison. Format as a Markdown table."
  Input: Step 1 output + our product description.
  Output: Markdown comparison table.

Step 3 — Positioning Recommendation
  Prompt: "Based on the competitive comparison table below, write a one-page
  recommendation on how to position our analytics platform in this market.
  Address: (1) our strongest differentiators, (2) the most vulnerable
  competitor and why, (3) the positioning statement you recommend, and
  (4) two specific feature investments that would strengthen our position.
  Write in a direct, executive-briefing style."
  Input: Step 2 output.
  Output: One-page positioning recommendation.

EXPECTED FINAL OUTPUT: One-page positioning recommendation with supporting
comparison table.
```
