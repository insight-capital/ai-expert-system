#!/usr/bin/env python3
"""
batch_add_personas_2.py -- Batch registration of 10 unregistered personas.

Usage (from repo root):
    python tools/batch_add_personas_2.py

Registers all 10 personas into:
  - registry/registry.yaml (entries + families + count)
  - master-expert/meta-orchestrator.md (routing table rows)
  - adapters/claude-code-adapter.md (reference table)
  - adapters/chatgpt-adapter.md (reference table)
  - adapters/gemini-adapter.md (reference table)
"""

import sys
from pathlib import Path

# Ensure add_persona is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from add_persona import (
    PERSONAS_DIR,
    REGISTRY_PATH,
    read_file,
    strip_code_fences,
    extract_role_summary,
    extract_cognitive_posture,
    extract_domain_scope,
    extract_out_of_scope,
    extract_input_spec,
    extract_output_spec,
    extract_persona_references,
    extract_tags_auto,
    to_kebab_case,
    load_registry_data,
    load_registry_text,
    get_next_persona_id,
    build_registry_entry_yaml,
    insert_registry_entry,
    update_total_personas,
    update_persona_families,
    add_new_family,
    append_routing_table_row,
    update_adapter_tables,
)


# -----------------------------------------------------------------------
# Batch configuration -- pre-baked answers (no interactive prompts)
# -----------------------------------------------------------------------

PERSONAS = [
    # --- M&A / Deal Execution family (new) ---
    {
        "file": "Buy_Side_MA_Advisor.md",
        "name": "Buy-Side M&A Advisor",
        "family": "M&A / Deal Execution",
        "short_name": "Buy-Side M&A",
    },
    {
        "file": "Post_Merger_Integration_Lead.md",
        "name": "Post-Merger Integration Lead",
        "family": "M&A / Deal Execution",
        "short_name": "PMI Lead",
    },
    {
        "file": "Insurance_Risk_Advisor.md",
        "name": "Insurance Risk Advisor",
        "family": "M&A / Deal Execution",
        "short_name": "Insurance Risk",
    },
    {
        "file": "MA_Data_Integration_Engineer.md",
        "name": "M&A Data Integration Engineer",
        "family": "M&A / Deal Execution",
        "short_name": "M&A Data Integration",
    },
    # --- Valuation & Finance family (existing) ---
    {
        "file": "Debt-capital-markets-advisor.md",
        "name": "Debt & Capital Markets Advisor",
        "family": "Valuation & Finance",
        "short_name": "Debt Capital Markets",
    },
    {
        "file": "QofE_Expert_Persona.md",
        "name": "Senior Transaction Services Advisor (Quality of Earnings)",
        "family": "Valuation & Finance",
        "short_name": "Quality of Earnings",
    },
    {
        "file": "Capital_Markets_Strategic_Transactions_Advisor.md",
        "name": "Capital Markets & Strategic Transactions Advisor",
        "family": "Valuation & Finance",
        "short_name": "Capital Markets Advisor",
    },
    # --- Legal family (existing) ---
    {
        "file": "MA_Legal_Counsel_Persona.md",
        "name": "M&A Legal Counsel",
        "family": "Legal",
        "short_name": "M&A Legal Counsel",
    },
    {
        "file": "Regulatory_Licensing_Specialist_Persona.md",
        "name": "Regulatory & Licensing Specialist",
        "family": "Legal",
        "short_name": "Regulatory Licensing",
    },
    # --- General AI Biz family (existing) ---
    {
        "file": "Applied_AI_Engineering_Lead.md",
        "name": "Applied AI Engineering Lead",
        "family": "General AI Biz",
        "short_name": "AI Engineering Lead",
    },
]

# New families to create (in order of first appearance)
NEW_FAMILIES = ["M&A / Deal Execution"]


def main() -> int:
    print()
    print("AI Persona System -- Batch Registration (10 personas)")
    print("=" * 55)

    # ------------------------------------------------------------------
    # Pre-flight checks
    # ------------------------------------------------------------------
    missing = []
    for p in PERSONAS:
        path = PERSONAS_DIR / p["file"]
        if not path.is_file():
            missing.append(p["file"])
    if missing:
        print(f"\nERROR: Missing persona files:")
        for f in missing:
            print(f"  - personas/{f}")
        return 1

    # ------------------------------------------------------------------
    # Load registry
    # ------------------------------------------------------------------
    registry_data = load_registry_data()
    registry_text = load_registry_text()
    next_id_num = int(get_next_persona_id(registry_data).split("-")[1])

    old_count = registry_data.get("total_personas", 0)
    new_count = old_count + len(PERSONAS)

    print(f"\nCurrent registry: {old_count} personas")
    print(f"Adding: {len(PERSONAS)} personas (persona-{next_id_num:03d} through persona-{next_id_num + len(PERSONAS) - 1:03d})")
    print(f"New total: {new_count}")

    # ------------------------------------------------------------------
    # Extract metadata and build entries
    # ------------------------------------------------------------------
    entries = []
    warnings = []
    families_created = set()

    for i, p in enumerate(PERSONAS):
        persona_id = f"persona-{next_id_num + i:03d}"
        source_path = PERSONAS_DIR / p["file"]
        content = read_file(source_path)
        content = strip_code_fences(content)

        name = p["name"]
        family = p["family"]
        source_file = f"personas/{p['file']}"

        # Extract metadata
        role_summary = extract_role_summary(content) or ""
        cognitive_posture = extract_cognitive_posture(content) or ""
        domain_scope = extract_domain_scope(content) or []
        out_of_scope = extract_out_of_scope(content) or []
        input_spec = extract_input_spec(content)
        output_spec = extract_output_spec(content)
        persona_refs = extract_persona_references(content)
        tags = extract_tags_auto(name, domain_scope, family)

        # Track extraction gaps
        gaps = []
        if not role_summary:
            gaps.append("role_summary")
        if not cognitive_posture:
            gaps.append("cognitive_posture")
        if not domain_scope:
            gaps.append("domain_scope")
        if gaps:
            warnings.append(f"  {persona_id} ({name}): missing {', '.join(gaps)}")

        metadata = {
            "id": persona_id,
            "name": name,
            "source_file": source_file,
            "role_summary": role_summary,
            "cognitive_posture": cognitive_posture,
            "domain_scope": domain_scope,
            "out_of_scope": out_of_scope,
            "input_spec": input_spec,
            "output_spec": output_spec,
            "composability": {
                "works_with": persona_refs,
                "position_in_pipeline": "standalone",
                "known_workflows": [],
            },
            "voice_calibration": "uses_own_voice",
            "tags": tags,
        }

        entries.append({
            "persona_id": persona_id,
            "name": name,
            "family": family,
            "short_name": p.get("short_name", name),
            "metadata": metadata,
            "domain_scope": domain_scope,
        })

        print(f"  [{i+1:2d}/10] {persona_id} -- {name}")

    # ------------------------------------------------------------------
    # Apply registry changes
    # ------------------------------------------------------------------
    print(f"\nWriting registry entries...")

    # 1. Insert all persona entries
    for entry in entries:
        entry_yaml = build_registry_entry_yaml(entry["metadata"])
        registry_text = insert_registry_entry(registry_text, entry_yaml)

    # 2. Update total_personas
    registry_text = update_total_personas(registry_text, old_count, new_count)

    # 3. Add new families and assign persona IDs
    for entry in entries:
        family = entry["family"]
        pid = entry["persona_id"]

        if family in NEW_FAMILIES and family not in families_created:
            # First persona in a new family -- create the family
            registry_text = add_new_family(registry_text, family, pid)
            families_created.add(family)
        elif family in families_created:
            # Subsequent persona in a newly created family
            registry_text = update_persona_families(registry_text, family, pid)
        else:
            # Existing family
            registry_text = update_persona_families(registry_text, family, pid)

    # Write registry
    REGISTRY_PATH.write_text(registry_text, encoding="utf-8")
    print(f"  + Wrote registry.yaml ({old_count} -> {new_count} personas, +{len(NEW_FAMILIES)} new families)")

    # ------------------------------------------------------------------
    # Append routing table rows
    # ------------------------------------------------------------------
    print(f"\nAppending routing table rows...")
    for entry in entries:
        domain_brief = "; ".join(entry["domain_scope"][:3]) if entry["domain_scope"] else entry["name"]
        pipeline_membership = f"{entry['family']} / Standalone"
        append_routing_table_row(
            entry["persona_id"],
            entry["name"],
            domain_brief,
            pipeline_membership,
        )
    print(f"  + Added {len(entries)} rows to meta-orchestrator.md")

    # ------------------------------------------------------------------
    # Update adapter reference tables
    # ------------------------------------------------------------------
    print(f"\nUpdating adapter reference tables...")
    for entry in entries:
        update_adapter_tables(
            entry["persona_id"],
            entry["name"],
            entry["family"],
            entry["domain_scope"],
            short_name=entry["short_name"],
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 55}")
    print(f"DONE -- Registered {len(entries)} personas")
    print(f"  Registry: persona-{next_id_num:03d} through persona-{next_id_num + len(entries) - 1:03d}")
    print(f"  New families: {', '.join(NEW_FAMILIES)}")
    print(f"  Total personas: {new_count}")

    if warnings:
        print(f"\nExtraction warnings (may need manual review):")
        for w in warnings:
            print(w)

    print(f"\nNext steps:")
    print(f"  python tools/validate_registry.py")
    print(f"  python tools/export_claude_project.py")
    print(f"  python tools/export_public_release.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
