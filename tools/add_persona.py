#!/usr/bin/env python3
"""
add_persona.py — Automates adding a new persona to the AI Persona System.

Usage (from repo root):
    python tools/add_persona.py path/to/new-persona.md

What it does:
    1. Copies the .md file to personas/ with a kebab-case filename
    2. Extracts metadata from the .md file using regex
    3. Assigns the next available persona ID
    4. Appends a registry entry to registry/registry.yaml
    5. Updates total_personas count in the registry
    6. Appends a row to the routing table in master-expert/meta-orchestrator.md

Dependencies: PyYAML
"""

import sys
import shutil
from pathlib import Path

# Ensure tools/ is on the path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from registry_utils import (
    PERSONAS_DIR,
    REGISTRY_PATH,
    to_kebab_case,
    read_file,
    strip_code_fences,
    extract_name,
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
    append_routing_table_row,
)


# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------

def prompt_field(field_name: str, hint: str = '') -> str:
    """Prompt user for a field that could not be auto-extracted."""
    hint_text = f" ({hint})" if hint else ""
    print(f"\n  Could not extract '{field_name}' from the file.")
    return input(f"  Enter {field_name}{hint_text}: ").strip()


def prompt_list(field_name: str, hint: str = '') -> list[str]:
    """Prompt user for a list field (comma-separated)."""
    hint_text = f" ({hint})" if hint else ""
    print(f"\n  Could not extract '{field_name}' from the file.")
    raw = input(f"  Enter {field_name}{hint_text} [comma-separated]: ").strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(',') if item.strip()]


def prompt_tags(auto_tags: list[str]) -> list[str]:
    """Show auto-detected tags and let user confirm or modify."""
    print(f"\nTags (auto-detected): {auto_tags}")
    edit = input("Confirm or edit tags [Enter to accept, or type new comma-separated list]: ").strip()
    if not edit:
        return auto_tags
    return [t.strip() for t in edit.split(',') if t.strip()]


def prompt_voice_calibration() -> str:
    """Prompt for voice calibration setting."""
    print('\nVoice calibration [Enter for "uses_own_voice", or type override]: ', end='')
    val = input().strip()
    return val if val else "uses_own_voice"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/add_persona.py <path-to-persona.md>")
        return 1

    source_path = Path(sys.argv[1]).resolve()
    if not source_path.is_file():
        print(f"ERROR: File not found: {source_path}")
        return 1
    if not source_path.suffix == '.md':
        print(f"ERROR: Expected a .md file, got: {source_path.suffix}")
        return 1

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    print()
    print("AI Persona System -- Add Persona")
    print("=" * 40)

    # ------------------------------------------------------------------
    # Read source file
    # ------------------------------------------------------------------
    content = read_file(source_path)
    content = strip_code_fences(content)

    # ------------------------------------------------------------------
    # Extract name -> determine target filename
    # ------------------------------------------------------------------
    name = extract_name(content)
    if not name:
        name = prompt_field('name', 'Display name, e.g. "AI Chief Technology Officer"')
        if not name:
            print("ERROR: Persona name is required.")
            return 1

    kebab = to_kebab_case(name)
    target_filename = f"{kebab}.md"
    target_path = PERSONAS_DIR / target_filename

    # Check if file is already in personas/
    already_in_personas = source_path.parent.resolve() == PERSONAS_DIR.resolve()
    if already_in_personas:
        target_path = source_path
        target_filename = source_path.name
    elif target_path.exists():
        print(f"\nWARNING: {target_path.name} already exists in personas/.")
        overwrite = input("Overwrite? [y/N] ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return 1

    print(f"\nSource file: {source_path}")
    if not already_in_personas:
        print(f"Target: personas/{target_filename}")
    else:
        print(f"Already in personas/ directory")

    # ------------------------------------------------------------------
    # Load registry
    # ------------------------------------------------------------------
    registry_data = load_registry_data()

    # Check if this persona name is already registered
    existing_names = {p.get('name', '').lower() for p in registry_data.get('personas', [])}
    if name.lower() in existing_names:
        print(f"\nWARNING: A persona named '{name}' is already in the registry.")
        proceed = input("Continue anyway? [y/N] ").strip().lower()
        if proceed != 'y':
            print("Aborted.")
            return 1

    # ------------------------------------------------------------------
    # Extract metadata
    # ------------------------------------------------------------------
    print("\nExtracted metadata:")

    role_summary = extract_role_summary(content)
    if not role_summary:
        role_summary = prompt_field('role_summary', 'One or two sentence summary of what this persona does')
    print(f"  Name: {name}")
    print(f"  Role summary: {role_summary[:80]}{'...' if len(role_summary) > 80 else ''}")

    cognitive_posture = extract_cognitive_posture(content)
    if not cognitive_posture:
        cognitive_posture = prompt_field('cognitive_posture', "snake_case, e.g. 'strategic_architect'")
    print(f"  Cognitive posture: {cognitive_posture}")

    domain_scope = extract_domain_scope(content)
    if not domain_scope:
        domain_scope = prompt_list('domain_scope', 'comma-separated domain items')
    print(f"  Domain scope: {domain_scope[:3]}{'...' if len(domain_scope) > 3 else ''}")

    out_of_scope = extract_out_of_scope(content)
    if not out_of_scope:
        out_of_scope = prompt_list('out_of_scope', 'comma-separated items')
    print(f"  Out of scope: {out_of_scope[:3]}{'...' if len(out_of_scope) > 3 else ''}")

    input_spec = extract_input_spec(content)
    if not input_spec.get('accepts'):
        input_spec['accepts'] = prompt_list('input_spec.accepts', 'comma-separated artifact types')
    if not input_spec.get('required_fields'):
        input_spec['required_fields'] = prompt_list('input_spec.required_fields', 'comma-separated required fields')
    print(f"  Input accepts: {input_spec['accepts']}")

    output_spec = extract_output_spec(content)
    if not output_spec.get('produces'):
        output_spec['produces'] = prompt_field('output_spec.produces', 'e.g. strategic_technology_assessment')
    if not output_spec.get('fields'):
        output_spec['fields'] = prompt_list('output_spec.fields', 'comma-separated output fields')
    print(f"  Output produces: {output_spec['produces']}")

    # ------------------------------------------------------------------
    # Interactive: tags, voice
    # ------------------------------------------------------------------
    persona_id = get_next_persona_id(registry_data)

    # Check for ID collision (shouldn't happen but be safe)
    existing_ids = {p.get('id') for p in registry_data.get('personas', [])}
    while persona_id in existing_ids:
        num = int(persona_id.split('-')[1]) + 1
        persona_id = f"persona-{num:03d}"

    print(f"\nAssigned ID: {persona_id}")

    # Composability
    persona_refs = extract_persona_references(content)
    composability = {
        "works_with": persona_refs,
        "position_in_pipeline": "standalone",
        "known_workflows": [],
    }

    # Tags
    auto_tags = extract_tags_auto(name, domain_scope)
    tags = prompt_tags(auto_tags)

    # Voice calibration
    voice_calibration = prompt_voice_calibration()

    # ------------------------------------------------------------------
    # Source file path for registry (forward slashes)
    # ------------------------------------------------------------------
    source_file_registry = f"personas/{target_filename}"

    # ------------------------------------------------------------------
    # Build metadata dict
    # ------------------------------------------------------------------
    metadata = {
        'id': persona_id,
        'name': name,
        'source_file': source_file_registry,
        'role_summary': role_summary,
        'cognitive_posture': cognitive_posture,
        'domain_scope': domain_scope,
        'out_of_scope': out_of_scope,
        'input_spec': input_spec,
        'output_spec': output_spec,
        'composability': composability,
        'voice_calibration': voice_calibration,
        'tags': tags,
    }

    # ------------------------------------------------------------------
    # Confirm
    # ------------------------------------------------------------------
    print(f"\nConfirm registration? [Y/n] ", end='')
    confirm = input().strip().lower()
    if confirm and confirm != 'y':
        print("Aborted.")
        return 1

    # ------------------------------------------------------------------
    # Execute changes
    # ------------------------------------------------------------------

    # 1. Copy persona file
    if not already_in_personas:
        shutil.copy2(source_path, target_path)
        print(f"\n  + Copied persona file to personas/{target_filename}")
    else:
        print(f"\n  = Persona file already in personas/")

    # 2. Build and insert registry entry
    entry_yaml = build_registry_entry_yaml(metadata)
    registry_text = load_registry_text()

    old_count = registry_data.get('total_personas', 0)
    new_count = old_count + 1

    # Insert the entry
    registry_text = insert_registry_entry(registry_text, entry_yaml)

    # Update total_personas
    registry_text = update_total_personas(registry_text, old_count, new_count)

    # Write registry
    REGISTRY_PATH.write_text(registry_text, encoding='utf-8')
    print(f"  + Appended registry entry ({persona_id})")
    print(f"  + Updated total_personas: {old_count} -> {new_count}")

    # 3. Append routing table row
    domain_brief = '; '.join(domain_scope[:3]) if domain_scope else name
    append_routing_table_row(persona_id, name, domain_brief)
    print(f"  + Appended routing table row in meta-orchestrator.md")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print(f"\nDone. Run 'python tools/validate_registry.py' to verify.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
