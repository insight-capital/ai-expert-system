#!/usr/bin/env python3
"""
batch_add_personas_3.py -- Register 1 new persona: GTM Strategy Lead.
"""

import sys
from pathlib import Path

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
    load_registry_data,
    load_registry_text,
    get_next_persona_id,
    build_registry_entry_yaml,
    insert_registry_entry,
    update_total_personas,
    update_persona_families,
    append_routing_table_row,
    update_adapter_tables,
)

PERSONAS = [
    {
        "file": "gtm-strategy-lead.md",
        "name": "Go-to-Market Strategy Lead",
        "family": "General AI Biz",
        "short_name": "GTM Strategy Lead",
    },
]


def main() -> int:
    print()
    print("AI Persona System -- Register GTM Strategy Lead")
    print("=" * 55)

    missing = [p["file"] for p in PERSONAS if not (PERSONAS_DIR / p["file"]).is_file()]
    if missing:
        print(f"\nERROR: Missing: {missing}")
        return 1

    registry_data = load_registry_data()
    registry_text = load_registry_text()
    next_id_num = int(get_next_persona_id(registry_data).split("-")[1])

    old_count = registry_data.get("total_personas", 0)
    new_count = old_count + len(PERSONAS)

    print(f"\nCurrent: {old_count} personas")
    print(f"Adding: persona-{next_id_num:03d}")

    entries = []
    warnings = []

    for i, p in enumerate(PERSONAS):
        persona_id = f"persona-{next_id_num + i:03d}"
        source_path = PERSONAS_DIR / p["file"]
        content = read_file(source_path)
        content = strip_code_fences(content)

        name = p["name"]
        family = p["family"]
        source_file = f"personas/{p['file']}"

        role_summary = extract_role_summary(content) or ""
        cognitive_posture = extract_cognitive_posture(content) or ""
        domain_scope = extract_domain_scope(content) or []
        out_of_scope = extract_out_of_scope(content) or []
        input_spec = extract_input_spec(content)
        output_spec = extract_output_spec(content)
        persona_refs = extract_persona_references(content)
        tags = extract_tags_auto(name, domain_scope, family)

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

        print(f"  {persona_id} -- {name}")

    print(f"\nWriting registry...")

    for entry in entries:
        entry_yaml = build_registry_entry_yaml(entry["metadata"])
        registry_text = insert_registry_entry(registry_text, entry_yaml)

    registry_text = update_total_personas(registry_text, old_count, new_count)

    for entry in entries:
        registry_text = update_persona_families(registry_text, entry["family"], entry["persona_id"])

    REGISTRY_PATH.write_text(registry_text, encoding="utf-8")
    print(f"  + Registry: {old_count} -> {new_count}")

    print(f"\nRouting table...")
    for entry in entries:
        domain_brief = "; ".join(entry["domain_scope"][:3]) if entry["domain_scope"] else entry["name"]
        append_routing_table_row(entry["persona_id"], entry["name"], domain_brief, f"{entry['family']} / Standalone")
    print(f"  + Added row to meta-orchestrator.md")

    print(f"\nAdapters...")
    for entry in entries:
        update_adapter_tables(entry["persona_id"], entry["name"], entry["family"], entry["domain_scope"], short_name=entry["short_name"])

    print(f"\n{'=' * 55}")
    print(f"DONE -- {new_count} total personas")

    if warnings:
        print(f"\nWarnings:")
        for w in warnings:
            print(w)

    return 0


if __name__ == "__main__":
    sys.exit(main())
