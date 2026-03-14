#!/usr/bin/env python3
"""
sync_registry.py — One-shot sync script for the AI Persona System.

Scans personas/ directory, compares against registry, auto-registers any
unregistered personas. Zero interactive prompts — uses sensible defaults.

Usage (from repo root):
    python tools/sync_registry.py

Idempotent — safe to run multiple times.
"""

import sys
from pathlib import Path

# Ensure tools/ is on the path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from registry_utils import (
    REPO_ROOT,
    PERSONAS_DIR,
    REGISTRY_PATH,
    read_file,
    load_registry_data,
    load_registry_text,
    get_registered_source_files,
    get_next_persona_id,
    extract_all_metadata,
    build_registry_entry_yaml,
    insert_registry_entry,
    update_total_personas,
    append_routing_table_row,
)


def find_unregistered_personas(registered_files: set[str]) -> list[Path]:
    """Find .md files in personas/ that are not in the registry."""
    if not PERSONAS_DIR.is_dir():
        print(f"ERROR: personas/ directory not found at {PERSONAS_DIR}")
        sys.exit(1)

    unregistered = []
    for md_file in sorted(PERSONAS_DIR.glob("*.md")):
        relative = f"personas/{md_file.name}"
        if relative not in registered_files:
            unregistered.append(md_file)
    return unregistered


def main() -> int:
    print()
    print("AI Persona System — Sync Registry")
    print("=" * 40)

    # Load current registry state
    registry_data = load_registry_data()
    registered_files = get_registered_source_files(registry_data)

    # Find unregistered personas
    unregistered = find_unregistered_personas(registered_files)

    if not unregistered:
        print("\nAll persona files are already registered. Nothing to do.")
        return 0

    print(f"\nFound {len(unregistered)} unregistered persona(s):")
    for f in unregistered:
        print(f"  - {f.name}")

    # Process each unregistered persona
    registry_text = load_registry_text()
    current_count = registry_data.get('total_personas', 0)
    registered_count = 0

    # Track existing IDs for collision avoidance
    existing_ids = {p.get('id') for p in registry_data.get('personas', [])}

    for md_file in unregistered:
        source_file = f"personas/{md_file.name}"
        content = read_file(md_file)

        # Get next available ID
        persona_id = get_next_persona_id(registry_data)
        while persona_id in existing_ids:
            num = int(persona_id.split('-')[1]) + 1
            persona_id = f"persona-{num:03d}"

        # Extract metadata (non-interactive)
        metadata = extract_all_metadata(content, source_file, persona_id)

        # Build and insert registry entry
        entry_yaml = build_registry_entry_yaml(metadata)
        registry_text = insert_registry_entry(registry_text, entry_yaml)

        # Update count
        new_count = current_count + registered_count + 1
        if registered_count == 0:
            registry_text = update_total_personas(registry_text, current_count, new_count)
        else:
            registry_text = update_total_personas(
                registry_text, current_count + registered_count, new_count
            )

        # Track for next iteration
        existing_ids.add(persona_id)
        # Add a fake entry to registry_data so get_next_persona_id works
        registry_data.setdefault('personas', []).append({'id': persona_id})

        # Append routing table row
        domain_brief = '; '.join(metadata['domain_scope'][:3]) if metadata['domain_scope'] else metadata['name']
        append_routing_table_row(persona_id, metadata['name'], domain_brief)

        registered_count += 1

        # Report
        flags = []
        if not metadata['role_summary']:
            flags.append('role_summary')
        if not metadata['cognitive_posture']:
            flags.append('cognitive_posture')
        if not metadata['domain_scope']:
            flags.append('domain_scope')
        if not metadata['input_spec'].get('accepts'):
            flags.append('input_spec.accepts')
        if not metadata['output_spec'].get('produces'):
            flags.append('output_spec.produces')

        flag_str = f" (needs review: {', '.join(flags)})" if flags else ""
        print(f"\n  + Registered: {persona_id} — {metadata['name']}{flag_str}")

    # Write updated registry
    REGISTRY_PATH.write_text(registry_text, encoding='utf-8')

    print(f"\n{'=' * 40}")
    print(f"Registered {registered_count} new persona(s).")
    print(f"Total personas: {current_count} -> {current_count + registered_count}")
    print(f"\nRun 'python tools/validate_registry.py' to verify.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
