### Sample 4: L4 — Single Expert Persona

```
TASK: "We need to assess the data architecture for our analytics platform —
specifically whether our current PostgreSQL schema with vector search and
geospatial extensions will scale to 50 cities and 100K entities, and what
migration path we should plan for."

RESOLUTION LEVEL: Level 4 — Single Expert Persona

RATIONALE: This task requires specialized domain expertise in data architecture,
database scaling patterns, and migration planning. A general-purpose prompt would
produce generic advice that misses the specific nuances of vector index behavior
at scale, geospatial query optimization, and platform-specific constraints.
The task benefits from a persistent identity with data architecture expertise and
the cognitive posture of a strategic advisor (not just a technical implementer).

ALTERNATIVES CONSIDERED:
- L1/L2 (Prompt): Rejected. Data architecture scaling assessment requires
  domain expertise that materially affects output quality. Generic model
  knowledge of PostgreSQL scaling is insufficient for vector search and
  geospatial-specific guidance.
- L4 — AI CTO (persona-012): Considered. Persona-012 covers architecture
  decisions, but its scope is broader (full technical strategy). For a focused
  data architecture question, persona-018 is the closer fit.
- L5 (Pipeline): Rejected. Single domain — no need for multiple personas.

ACTION: Deploy Data Strategy Lead (persona-018).

TASK BRIEF FOR PERSONA-018:
---
Task: Assess scaling readiness of current data architecture.

Context:
- Current stack: PostgreSQL with vector search and geospatial extensions
- Current scale: ~5K entities, 1 city, ~50K records
- Target scale: 50 cities, ~100K entities, ~1M records
- Known issues: Vector index variance across connections,
  statement timeouts on large result sets with exclusion filters,
  connection pooling challenges with HTTP/2

Desired Output:
1. Assessment of current schema's scaling ceiling with specific bottlenecks
2. Recommended migration path (index type changes, connection pooling, etc.)
3. Platform constraints at target scale (row limits, connection limits)
4. Phased migration plan with effort estimates

Format: Structured technical assessment with executive summary.
---

EXPECTED OUTPUT: Technical assessment document with scaling analysis,
recommended migration path, and phased plan.
```
