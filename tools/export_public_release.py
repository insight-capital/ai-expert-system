#!/usr/bin/env python3
"""
Export a sanitized public release of the AI Persona System.

Reads tools/public_release_config.yaml, copies/transforms all files into
exports/public-release/, then validates that no forbidden terms leaked.

Usage:
    python tools/export_public_release.py           # generate export
    python tools/export_public_release.py --check   # validate existing export only
"""

import os
import re
import sys
import json
import shutil
import hashlib
import fnmatch
from pathlib import Path
from datetime import datetime, timezone

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "public_release_config.yaml"
PATCHES_DIR = Path(__file__).resolve().parent / "patches"
OUTPUT_DIR = REPO_ROOT / "exports" / "public-release"


# ---------------------------------------------------------------------------
# Config & Registry Loading
# ---------------------------------------------------------------------------

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_registry():
    registry_path = REPO_ROOT / "registry" / "registry.yaml"
    with open(registry_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_excluded_ids(config, registry):
    """Return set of persona IDs to exclude based on excluded_families."""
    excluded_families = set(config.get("excluded_families", []))
    excluded = set()
    for family in registry.get("persona_families", []):
        if family["name"] in excluded_families:
            excluded.update(family["ids"])
    return excluded


def resolve_excluded_source_files(excluded_ids, registry):
    """Return set of relative source_file paths for excluded personas."""
    paths = set()
    for persona in registry.get("personas", []):
        if persona["id"] in excluded_ids:
            paths.add(persona["source_file"])
    return paths


# ---------------------------------------------------------------------------
# File Manifest
# ---------------------------------------------------------------------------

def build_manifest(config, excluded_source_files):
    """Walk repo, classify each file as skip / copy / transform."""
    excluded_patterns = config.get("excluded_files", [])
    manifest = []

    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden dirs and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for fname in files:
            abs_path = Path(root) / fname
            rel_path = abs_path.relative_to(REPO_ROOT).as_posix()

            # Check exclusion patterns
            skip = False
            for pattern in excluded_patterns:
                if fnmatch.fnmatch(rel_path, pattern):
                    skip = True
                    break

            if skip:
                continue

            # Check excluded persona source files
            if rel_path in excluded_source_files:
                continue

            # Classify
            ext = abs_path.suffix.lower()
            if ext in (".md", ".yaml", ".yml", ".json", ".txt", ".py"):
                manifest.append((abs_path, rel_path, "transform"))
            else:
                manifest.append((abs_path, rel_path, "copy"))

    return manifest


# ---------------------------------------------------------------------------
# Global Replacements
# ---------------------------------------------------------------------------

def apply_global_replacements(content, config):
    """Apply literal then regex replacements."""
    # Literal replacements — longest first to prevent partial matches
    replacements = config.get("global_replacements", {})
    for find in sorted(replacements.keys(), key=len, reverse=True):
        content = content.replace(find, replacements[find])

    # Regex replacements
    for pattern, replace in config.get("regex_replacements", {}).items():
        content = re.sub(pattern, replace, content)

    return content


# ---------------------------------------------------------------------------
# Table Row Removal
# ---------------------------------------------------------------------------

def remove_excluded_rows(content, excluded_ids):
    """Remove Markdown table rows that reference any excluded persona ID."""
    lines = content.split("\n")
    filtered = []
    for line in lines:
        if "|" in line and any(pid in line for pid in excluded_ids):
            continue
        filtered.append(line)
    return "\n".join(filtered)


# ---------------------------------------------------------------------------
# Registry Sanitization
# ---------------------------------------------------------------------------

def sanitize_registry(registry_data, config, excluded_ids):
    """Produce sanitized registry YAML string."""
    data = _deep_copy_dict(registry_data)

    # Update metadata
    data["owner"] = "[Your Name]"
    data["storage_location"] = "your-storage-location"

    # Remove excluded families
    excluded_families = set(config.get("excluded_families", []))
    data["persona_families"] = [
        f for f in data.get("persona_families", [])
        if f["name"] not in excluded_families
    ]

    # Remove excluded persona entries
    data["personas"] = [
        p for p in data.get("personas", [])
        if p["id"] not in excluded_ids
    ]

    # Update counts
    data["total_personas"] = len(data["personas"])

    # Remove prompt templates and sequences (files excluded from export)
    data["prompt_templates"] = []
    data["total_prompt_templates"] = 0
    data["prompt_sequences"] = []
    data["total_prompt_sequences"] = 0

    # Serialize back to YAML
    header = (
        "# ============================================================\n"
        "# AI PERSONA SYSTEM — MASTER REGISTRY\n"
        "# ============================================================\n"
        "#\n"
        "# This file is the single source of truth for all registered\n"
        "# personas, prompt templates, and prompt sequences in the\n"
        "# AI Persona System.\n"
        "#\n"
        "# Schema Version: 1.0\n"
        "# Methodology: LLM Expert Persona Development Framework v2.0\n"
        f"# Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        "# ============================================================\n\n"
    )

    yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    # Apply global replacements to the YAML output
    yaml_str = apply_global_replacements(yaml_str, config)

    return header + yaml_str


def _deep_copy_dict(d):
    """Simple deep copy using JSON round-trip (works for YAML-safe data)."""
    return json.loads(json.dumps(d))


# ---------------------------------------------------------------------------
# Meta-Orchestrator Patching
# ---------------------------------------------------------------------------

def patch_orchestrator(content, excluded_ids, remaining_count):
    """Apply all meta-orchestrator-specific patches."""

    # 1. Replace golden samples L2, L4, L5 with patch files
    for patch_name, start_marker, end_marker in [
        ("golden-sample-l2.md",
         "### Sample 2: L2 — Simple Prompt Sequence",
         "### Sample 3:"),
        ("golden-sample-l4.md",
         "### Sample 4: L4 — Single Expert Persona",
         "### Sample 5:"),
        ("golden-sample-l5.md",
         "### Sample 5: L5 — Orchestrated Persona Workflow",
         "### Sample 6:"),
    ]:
        patch_path = PATCHES_DIR / patch_name
        if patch_path.exists():
            patch_content = patch_path.read_text(encoding="utf-8").rstrip() + "\n\n"
            content = _replace_section(content, start_marker, end_marker, patch_content)

    # 2. Patch L6 sample: replace persona-008 reference with persona-036
    content = content.replace(
        "Value/ROI Lead (persona-008): Closest match, but scope is \"automation value\n"
        "  quantification and business case construction for AI services.\" Its expertise\n"
        "  is in modeling the ROI of AI automation projects, not in startup financial\n"
        "  modeling, fundraising projections, or cap table analysis.",
        "Strategic Finance & Unit Economics Diligence Lead (persona-036): Closest\n"
        "  match, but scope is \"SaaS metrics, marketplace economics, and unit\n"
        "  economics diligence.\" Its expertise is in analyzing existing business\n"
        "  models, not in constructing startup financial projections, fundraising\n"
        "  models, or cap table analysis."
    )

    # 3. Remove excluded workflow rows from Known Validated Workflows table
    content = _remove_workflow_rows(content, ["briefing-pipeline", "assessment-pipeline"])

    # 4. Remove excluded persona rows from routing table
    content = remove_excluded_rows(content, excluded_ids)

    # 5. Patch stale persona counts
    content = re.sub(
        r"covering all \d+ personas",
        f"covering all {remaining_count} personas",
        content
    )
    content = re.sub(
        r'\(\d+ domain personas',
        f'({remaining_count} domain personas',
        content
    )

    # 6. Patch the JSON persona shell section
    # Remove briefing and example workflows from JSON
    content = _remove_json_workflow_blocks(content)

    return content


def _replace_section(content, start_marker, end_marker, replacement):
    """Replace content from start_marker (inclusive) to end_marker (exclusive)."""
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"  WARNING: Could not find section marker: {start_marker}")
        return content

    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        print(f"  WARNING: Could not find end marker: {end_marker}")
        return content

    return content[:start_idx] + replacement + content[end_idx:]


def _remove_workflow_rows(content, workflow_ids):
    """Remove table rows containing specific workflow IDs."""
    lines = content.split("\n")
    filtered = []
    for line in lines:
        if "|" in line and any(wid in line for wid in workflow_ids):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def _remove_json_workflow_blocks(content):
    """Remove briefing and example workflow entries from JSON known_workflows array."""
    # Remove the briefing-pipeline JSON block
    content = re.sub(
        r',?\s*\{\s*"id":\s*"briefing-pipeline"[^}]*\}',
        '',
        content
    )
    # Remove the assessment-pipeline JSON block
    content = re.sub(
        r',?\s*\{\s*"id":\s*"assessment-pipeline"[^}]*\}',
        '',
        content
    )
    # Clean up leading comma if content-pipeline is now first
    content = re.sub(
        r'(\[\s*),\s*(\{)',
        r'\1\2',
        content
    )
    return content


# ---------------------------------------------------------------------------
# Adapter Patching
# ---------------------------------------------------------------------------

def patch_adapter(content, excluded_ids, is_claude_code=False):
    """Remove rows with excluded persona IDs and clean up references."""
    content = remove_excluded_rows(content, excluded_ids)

    # Remove workflow references for excluded pipelines
    lines = content.split("\n")
    filtered = []
    for line in lines:
        lower = line.lower()
        if "|" in line and ("assessment-pipeline" in lower or "assessment-pipeline" in lower or "content briefing" in lower or "briefing" in lower):
            continue
        filtered.append(line)
    content = "\n".join(filtered)

    # Update persona counts in prose (e.g., "All 36 persona IDs")
    content = re.sub(r"All \d+ persona", "All persona", content)

    return content


# ---------------------------------------------------------------------------
# Content Pipeline Patching
# ---------------------------------------------------------------------------

def patch_content_pipeline(content):
    """Rename pipeline ID and human gate references."""
    content = content.replace("your-org-blog-pipeline-v1", "content-blog-pipeline-v1")
    content = content.replace("KEN GATE", "HUMAN GATE")
    content = content.replace("KEN", "HUMAN REVIEWER")
    return content


# ---------------------------------------------------------------------------
# Analytical Default Voice Card Patching
# ---------------------------------------------------------------------------

def patch_analytical_default(content, excluded_ids):
    """Patch voice card references to excluded personas."""
    # Update usage line — remove Technical family reference
    content = re.sub(
        r"Technical family \(persona-004 through persona-009\),\s*",
        "",
        content
    )
    # Remove references to excluded personas in precedence rules
    # "persona-009, persona-003" or "persona-003" etc.
    for pid in excluded_ids:
        content = re.sub(rf",?\s*{re.escape(pid)}", "", content)
        content = re.sub(rf"{re.escape(pid)},?\s*", "", content)

    # Clean up empty parenthetical references
    content = re.sub(r"\(\s*\)", "", content)
    # Fix double commas
    content = re.sub(r",\s*,", ",", content)

    return content


# ---------------------------------------------------------------------------
# Corporate Counsel Patching
# ---------------------------------------------------------------------------

def patch_corporate_counsel(content):
    """Replace AcmeTech golden sample with generic fintech example."""
    patch_path = PATCHES_DIR / "corporate-counsel-example.md"
    if patch_path.exists():
        patch_content = patch_path.read_text(encoding="utf-8").rstrip() + "\n\n"
        content = _replace_section(
            content,
            "### 5.1 Golden Sample: Legal Analysis Memo",
            "### 5.2 Golden Sample:",
            patch_content
        )
    return content


# ---------------------------------------------------------------------------
# Generated Files
# ---------------------------------------------------------------------------

def generate_sample_voice_card():
    """Create anonymized voice card from sample-authorial-voice.md."""
    source = REPO_ROOT / "voice-cards" / "sample-authorial-voice.md"
    if not source.exists():
        print("  WARNING: sample-authorial-voice.md not found, skipping voice card generation")
        return

    content = source.read_text(encoding="utf-8")

    # Replace the title
    content = content.replace(
        "# Voice Card: [Your Name] — Authorial Voice",
        "# Voice Card: Sample Authorial Voice"
    )

    # Remove personal name references
    content = re.sub(r"\b[Your Name]\b", "[Your Name]", content)
    content = re.sub(r"\bKen\b", "[Author]", content)

    dest = OUTPUT_DIR / "voice-cards" / "sample-authorial-voice.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print("  GENERATED: voice-cards/sample-authorial-voice.md")


def generate_readme():
    """Create a README for the public release."""
    readme = """\
# AI Persona System

A framework for building, registering, and orchestrating expert AI personas — structured identities with defined roles, cognitive postures, interface contracts, and composability rules.

## What's Inside

| Directory | Contents |
|-----------|----------|
| `master-expert/` | Meta-Orchestrator — the routing persona that classifies tasks and dispatches to specialists |
| `personas/` | Individual expert persona definitions (structured Markdown) |
| `registry/` | Master registry (YAML) — single source of truth for all personas |
| `methodology/` | Five-Part Structural Framework v2.0 — the methodology behind persona design |
| `voice-cards/` | Voice calibration profiles for consistent output tone |
| `adapters/` | Platform-specific deployment guides (Claude Code, ChatGPT, Gemini, Codex, Cowork) |
| `tools/` | Python utilities for persona registration, validation, and export |

## Quick Start

See `GETTING_STARTED.md` for a step-by-step deployment guide.

1. **Browse personas** in `personas/` — each `.md` file is a self-contained expert definition
2. **Check the registry** in `registry/registry.yaml` for the full inventory with metadata
3. **Read the methodology** in `methodology/v2-framework.md` to understand the design framework
4. **Deploy a persona** using the adapter guide for your platform (see `adapters/`)

## Using the Meta-Orchestrator

The Meta-Orchestrator (`master-expert/meta-orchestrator.md`) is the system entry point. It:
- Diagnoses incoming tasks
- Classifies them to one of six resolution levels (L1-L6)
- Routes to the optimal persona or prompt

Load it as a system prompt in your preferred AI platform. See the adapter docs for platform-specific instructions.

## Validation

```bash
python tools/validate_registry.py
```

Checks that all persona files exist, IDs are unique, cross-references resolve, and counts are consistent.

## Framework

The personas in this system are built using the **Five-Part Structural Framework v2.0**:

1. **Role & Goal Definition** — Identity, objectives, cognitive posture
2. **Knowledge Base** — Domain scope, out-of-scope boundaries
3. **Tone & Style** — Voice calibration, output formatting
4. **Behavioral Constraints** — Hard rules, anti-patterns, mandates
5. **Interface Contract** — Input/output specs, composability rules

See `methodology/v2-framework.md` for the full specification.

## Customization

- **Add personas**: Use `python tools/add_persona.py path/to/new-persona.md`
- **Customize voice**: Edit voice cards in `voice-cards/` or create new ones
- **Build pipelines**: Use the Meta-Orchestrator at L5 to design multi-persona workflows
- **Adapt for platforms**: Follow the adapter guides in `adapters/`

## License

This system is provided as-is for educational and professional use. Adapt the personas to your own domain, organization, and workflow needs.
"""
    dest = OUTPUT_DIR / "README.md"
    dest.write_text(readme, encoding="utf-8")
    print("  GENERATED: README.md")


def generate_getting_started():
    """Create a getting-started guide for new users."""
    content = """\
# Getting Started with the AI Persona System

## Step 1: Save the System Files

Where you save them depends on how you plan to use the system:

| Setup | Where to Save | Best For |
|---|---|---|
| Local drive | Any folder (e.g., `~/ai-persona-system/`) | Single LLM platform, solo use |
| Google Drive | A shared Drive folder | Accessing personas from multiple LLM platforms or devices |
| Local git repo | `git init` in the folder | Version control as you add/modify personas |
| GitHub repo | Push to a private or public repo | Collaboration, backup |

You can combine these -- e.g., a local git repo synced to Google Drive.

## Step 2: Understand the Framework

Read `methodology/v2-framework.md` -- the Five-Part Structural Framework every persona is built on:

1. **Role & Goal Definition** -- Identity, objectives, cognitive posture
2. **Knowledge Base** -- Domain scope, out-of-scope boundaries
3. **Tone & Style** -- Voice calibration, output formatting
4. **Behavioral Constraints** -- Hard rules, anti-patterns, mandates
5. **Interface Contract** -- Input/output specs, composability rules

## Step 3: Deploy a Single Expert Persona

Pick any persona from `personas/`. Each `.md` file is a self-contained system prompt.

**On Claude.ai:** Create a Project -> paste persona contents into Project Instructions -> start chatting.

For other platforms, see the adapter guide in `adapters/` for your platform.

## Step 4: Deploy the Meta-Orchestrator (Intelligent Routing)

Once you have multiple personas, deploy the Meta-Orchestrator as your system entry point.

Upload to your LLM platform:
- `master-expert/meta-orchestrator.md` -- as Project Instructions / system prompt (includes the full routing table)
- `methodology/v2-framework.md` -- as a Knowledge file (enables L6 persona creation)

The Meta-Orchestrator classifies tasks into resolution levels (L1-L6) from a single direct prompt to multi-persona pipelines to gap identification and new expert creation.

Note: `registry/registry.yaml` does NOT need to be uploaded -- the routing table is embedded in the orchestrator file. The registry is for the Python tooling only.

## Step 5: Create Your Own Experts

Upload `methodology/v2-framework.md` as a Knowledge file and ask the LLM to create a new persona. Takes 1-2 minutes. Then register it:

```bash
python tools/add_persona.py path/to/new-persona.md
```

## Step 6: Build Expert Teams

Two included personas specialize in vetting team composition:
- **Multi-Agent Orchestration Architect** -- organization design and persona engineering
- **Agentic Systems Architect** -- governance, autonomy classification, interface contracts

Or use the Meta-Orchestrator at L5 to design pipelines automatically.

## Step 7: Validate & Maintain

```bash
python tools/validate_registry.py
```

Run this after adding or modifying personas to ensure registry consistency.

## File Reference

| File / Directory | Role | Upload to LLM? |
|---|---|---|
| `personas/*.md` | Self-contained expert system prompts | Yes |
| `master-expert/meta-orchestrator.md` | Routing layer with embedded routing table | Yes |
| `methodology/v2-framework.md` | Persona creation framework + validation rubrics | Yes |
| `registry/registry.yaml` | Machine-readable index for Python tooling | No |
| `adapters/*.md` | Platform deployment guides | No |
| `voice-cards/*.md` | Voice calibration profiles | Optional |
| `tools/*.py` | Registration, validation, export utilities | No |
"""
    dest = OUTPUT_DIR / "GETTING_STARTED.md"
    dest.write_text(content, encoding="utf-8")
    print("  GENERATED: GETTING_STARTED.md")


def generate_manifest(excluded_ids, remaining_count, family_count):
    """Write export manifest with metadata."""
    manifest = {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "export_tool": "tools/export_public_release.py",
        "source_total_personas": 39,
        "excluded_personas": sorted(excluded_ids),
        "exported_personas": remaining_count,
        "exported_families": family_count,
        "content_hash": _hash_output_dir(),
    }
    dest = OUTPUT_DIR / "export-manifest.json"
    dest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  GENERATED: export-manifest.json")


def _hash_output_dir():
    """SHA-256 hash of all output file contents concatenated."""
    h = hashlib.sha256()
    for root, _, files in os.walk(OUTPUT_DIR):
        for fname in sorted(files):
            fpath = Path(root) / fname
            if fpath.suffix == ".json" and fpath.name == "export-manifest.json":
                continue
            try:
                h.update(fpath.read_bytes())
            except Exception:
                pass
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_output(config):
    """Scan all output files for forbidden terms. Return list of violations."""
    forbidden = config.get("forbidden_terms", [])
    violations = []

    for root, _, files in os.walk(OUTPUT_DIR):
        for fname in files:
            fpath = Path(root) / fname
            rel = fpath.relative_to(OUTPUT_DIR).as_posix()

            # Skip binary and manifest
            if fpath.suffix.lower() not in (".md", ".yaml", ".yml", ".json", ".txt", ".py"):
                continue
            if fpath.name == "export-manifest.json":
                continue

            # Skip directories that contain sanitization tooling itself
            skip_dirs = config.get("validation_skip_dirs", [])
            if any(rel.startswith(d + "/") or rel == d for d in skip_dirs):
                continue

            try:
                content = fpath.read_text(encoding="utf-8")
            except Exception:
                continue

            for i, line in enumerate(content.split("\n"), 1):
                for term in forbidden:
                    if term.lower() in line.lower():
                        violations.append((rel, i, term, line.strip()[:120]))

    return violations


# ---------------------------------------------------------------------------
# Main Transform Dispatcher
# ---------------------------------------------------------------------------

def transform_file(content, rel_path, config, excluded_ids, registry, remaining_count):
    """Apply all transformations to a file based on its path."""

    # File-specific patches BEFORE global replacements
    if rel_path == "registry/registry.yaml":
        # Registry gets full YAML-aware processing
        return sanitize_registry(registry, config, excluded_ids)

    if rel_path == "master-expert/meta-orchestrator.md":
        content = patch_orchestrator(content, excluded_ids, remaining_count)

    if rel_path.startswith("adapters/"):
        content = patch_adapter(
            content, excluded_ids,
            is_claude_code=(rel_path == "adapters/claude-code-adapter.md")
        )

    if rel_path == "prompts/sequences/content-production-pipeline.md":
        content = patch_content_pipeline(content)

    if rel_path == "voice-cards/analytical-default.md":
        content = patch_analytical_default(content, excluded_ids)

    if rel_path.endswith("Corporate Counsel.md"):
        content = patch_corporate_counsel(content)

    # Remove table rows referencing excluded personas (all .md files)
    if rel_path.endswith(".md"):
        content = remove_excluded_rows(content, excluded_ids)

    # Apply global replacements (all files)
    content = apply_global_replacements(content, config)

    return content


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def _handle_rmtree_error(func, path, exc_info):
    """Handle Windows permission errors during rmtree."""
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main():
    print("=" * 60)
    print("AI PERSONA SYSTEM — PUBLIC RELEASE EXPORT")
    print("=" * 60)

    # Load config and registry
    config = load_config()
    registry = load_registry()
    excluded_ids = resolve_excluded_ids(config, registry)
    excluded_source_files = resolve_excluded_source_files(excluded_ids, registry)

    remaining_count = registry["total_personas"] - len(excluded_ids)
    remaining_families = len(registry["persona_families"]) - len(config.get("excluded_families", []))

    print(f"\nExcluding {len(excluded_ids)} personas from {len(config['excluded_families'])} families:")
    for pid in sorted(excluded_ids):
        print(f"  - {pid}")
    print(f"Remaining: {remaining_count} personas, {remaining_families} families\n")

    # Check-only mode
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        if not OUTPUT_DIR.exists():
            print("ERROR: No export found at exports/public-release/")
            sys.exit(1)
        violations = validate_output(config)
        if violations:
            print(f"FAIL: {len(violations)} forbidden term(s) found:")
            for rel, line, term, ctx in violations:
                print(f"  {rel}:{line}  [{term}]  {ctx}")
            sys.exit(1)
        else:
            print(f"PASS: No forbidden terms in {OUTPUT_DIR}")
            sys.exit(0)

    # Clean output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, onerror=_handle_rmtree_error)
    OUTPUT_DIR.mkdir(parents=True)

    # Build file manifest
    manifest = build_manifest(config, excluded_source_files)
    print(f"Processing {len(manifest)} files...\n")

    copied = 0
    transformed = 0

    for abs_path, rel_path, treatment in manifest:
        dest = OUTPUT_DIR / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        if treatment == "copy":
            shutil.copy2(abs_path, dest)
            copied += 1
        elif treatment == "transform":
            try:
                content = abs_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Binary file disguised with text extension — just copy
                shutil.copy2(abs_path, dest)
                copied += 1
                continue

            content = transform_file(content, rel_path, config, excluded_ids, registry, remaining_count)
            dest.write_text(content, encoding="utf-8")
            transformed += 1
            print(f"  TRANSFORMED: {rel_path}")

    # Generate new files
    print()
    generate_sample_voice_card()
    generate_readme()
    generate_getting_started()
    generate_manifest(excluded_ids, remaining_count, remaining_families)

    # Validate
    print("\n" + "-" * 60)
    print("VALIDATION SCAN")
    print("-" * 60)
    violations = validate_output(config)

    if violations:
        print(f"\n⚠ FAIL: {len(violations)} forbidden term(s) found:\n")
        for rel, line, term, ctx in violations:
            print(f"  {rel}:{line}  [{term}]  {ctx}")
        print(f"\nFix these manually or update the config, then re-run.")
    else:
        print(f"\n✓ PASS: No forbidden terms found in output.")

    # Summary
    print("\n" + "=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    print(f"  Output:       {OUTPUT_DIR}")
    print(f"  Copied:       {copied} files")
    print(f"  Transformed:  {transformed} files")
    print(f"  Generated:    4 files (README, Getting Started, voice card, manifest)")
    print(f"  Personas:     {remaining_count} (excluded {len(excluded_ids)})")
    print(f"  Families:     {remaining_families} (excluded {len(config['excluded_families'])})")
    print(f"  Validation:   {'PASS' if not violations else f'FAIL ({len(violations)} issues)'}")
    print("=" * 60)

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
