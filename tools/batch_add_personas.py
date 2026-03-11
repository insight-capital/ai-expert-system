#!/usr/bin/env python3
"""
batch_add_personas.py -- One-time batch registration of 12 unregistered personas.

Usage (from repo root):
    python tools/batch_add_personas.py

Registers all 12 personas into:
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
    # --- Legal family ---
    {
        "file": "AI Emerging Tech Lawyer.md",
        "name": "AI / Emerging Technology Lawyer",
        "family": "Legal",
        "short_name": "AI Tech Lawyer",
    },
    {
        "file": "Commercial Contracts Lawyer.md",
        "name": "Commercial Contracts Lawyer",
        "family": "Legal",
        "short_name": "Contracts Lawyer",
    },
    {
        "file": "Corporate Counsel.md",
        "name": "Corporate Counsel",
        "family": "Legal",
        "short_name": "Corporate Counsel",
    },
    {
        "file": "Corporate_Dissolution_Wind_Down_Counsel.md",
        "name": "Corporate Dissolution & Wind-Down Counsel",
        "family": "Legal",
        "short_name": "Wind-Down Counsel",
    },
    {
        "file": "Tax Attorney.md",
        "name": "Tax Attorney",
        "family": "Legal",
        "short_name": "Tax Attorney",
    },
    # --- Valuation & Finance family ---
    {
        "file": "Meridian_Web3_Valuation_Expert.md",
        "name": "Meridian -- Web3 Valuation & Digital Assets Advisor",
        "family": "Valuation & Finance",
        "short_name": "Web3 Valuation Advisor",
    },
    {
        "file": "Senior_Valuation_Advisor.md",
        "name": "Senior Valuation & Corporate Finance Advisor",
        "family": "Valuation & Finance",
        "short_name": "Valuation Advisor",
    },
    {
        "file": "Strategic Valuation Positioning Advisor.md",
        "name": "Strategic Valuation Positioning Advisor",
        "family": "Valuation & Finance",
        "short_name": "Valuation Positioning Advisor",
    },
    {
        "file": "Strategic_Finance_Diligence_Lead.md",
        "name": "Strategic Finance & Unit Economics Diligence Lead",
        "family": "Valuation & Finance",
        "short_name": "Finance Diligence Lead",
    },
    # --- Security & Engineering family ---
    {
        "file": "Principal Engineer_Code Auditor.md",
        "name": "Principal Engineer -- Code Auditor",
        "family": "Security & Engineering",
        "short_name": "Code Auditor",
    },
    {
        "file": "Principal Security Consultant (penetration tester).md",
        "name": "Principal Security Consultant",
        "family": "Security & Engineering",
        "short_name": "Security Consultant",
    },
    {
        "file": "cybersecurity-vulnerability-advisor.md",
        "name": "Cybersecurity Vulnerability Advisor",
        "family": "Security & Engineering",
        "short_name": "Cybersecurity Advisor",
    },
]

# New families to create (in order of first appearance)
NEW_FAMILIES = ["Legal", "Valuation & Finance", "Security & Engineering"]


def main() -> int:
    print()
    print("AI Persona System -- Batch Registration (12 personas)")
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

        print(f"  [{i+1:2d}/12] {persona_id} -- {name}")

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
            # Existing family (shouldn't happen for this batch, but safe)
            registry_text = update_persona_families(registry_text, family, pid)

    # Write registry
    REGISTRY_PATH.write_text(registry_text, encoding="utf-8")
    print(f"  + Wrote registry.yaml ({old_count} -> {new_count} personas, +{len(NEW_FAMILIES)} families)")

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
    print(f"  git diff")
    return 0


if __name__ == "__main__":
    sys.exit(main())
