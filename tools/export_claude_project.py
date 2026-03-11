#!/usr/bin/env python3
"""
export_claude_project.py — Export meta-orchestrator for Claude.ai Project deployment.

Usage (from repo root):
    python tools/export_claude_project.py          # generate export files
    python tools/export_claude_project.py --check   # check for drift only

Generates:
    exports/claude-project/project-instructions.md      — paste into Project Instructions (once)
    exports/claude-project/meta-orchestrator-knowledge.md — upload as Project Knowledge file
    exports/claude-project/v2-framework.md               — upload as Project Knowledge file (L6 persona creation)
    exports/claude-project/export-manifest.json          — content hashes for drift detection
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "registry.yaml"
ORCHESTRATOR_PATH = REPO_ROOT / "master-expert" / "meta-orchestrator.md"
FRAMEWORK_PATH = REPO_ROOT / "methodology" / "v2-framework.md"
EXPORT_DIR = REPO_ROOT / "exports" / "claude-project"
MANIFEST_PATH = EXPORT_DIR / "export-manifest.json"


# ---------------------------------------------------------------------------
# Loader prompt (paste into Claude.ai Project Instructions — one time only)
# ---------------------------------------------------------------------------
LOADER_PROMPT = """\
You are the **Task Resolution Strategist (Meta-Orchestrator)** for [Your Name]'s AI Persona System.

Your full persona definition — including your identity, decision hierarchy, routing table, \
golden samples, interface contract, and constraints — is provided in the uploaded knowledge file \
named `meta-orchestrator-knowledge.md`.

**On every conversation start:**
1. Internalize the knowledge file as your system prompt.
2. Operate exactly as specified: diagnose tasks, classify resolution levels (L1–L6), \
route to the optimal persona or prompt, and produce actionable output per the interface contract.
3. Never fabricate persona capabilities — only route to personas listed in the routing table.

**If the user asks "how many personas are in the system?" or similar:**
- Answer from the routing table in the knowledge file (count the rows).
- Do not guess or use a memorized number.

For L6 (Gap Identification) tasks requiring new persona development, reference the \
uploaded `v2-framework.md` knowledge file — it contains the complete Five-Part \
Structural Framework (Sections 3.1–3.6), validation rubrics (PDSQI-9, Section 8), \
and the Master Instantiation Directive.

You are the front door. Every task flows through you first.
"""


def generate_loader_prompt() -> str:
    """Return the static loader prompt text."""
    return LOADER_PROMPT


def load_registry() -> dict:
    """Load and parse registry.yaml."""
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def compute_content_hash(content: str) -> str:
    """SHA-256 hash of content."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def patch_dynamic_counts(content: str, registry_data: dict) -> str:
    """Replace stale hardcoded persona counts with current values from registry."""
    total = registry_data.get("total_personas", 0)
    families = len(registry_data.get("persona_families", []))

    # Line 578: "all 24 personas" -> "all N personas"
    content = re.sub(
        r"covering all \d+ personas",
        f"covering all {total} personas",
        content,
    )

    # Line 623: "24 domain personas" -> "N domain personas"
    content = re.sub(
        r"\(\d+ domain personas",
        f"({total} domain personas",
        content,
    )

    return content


def check_drift() -> bool:
    """Compare current content hashes against manifest. Returns True if stale."""
    if not MANIFEST_PATH.exists():
        print("No manifest found. Run: python tools/export_claude_project.py")
        return True

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    orchestrator_content = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
    registry_content = REGISTRY_PATH.read_text(encoding="utf-8")
    framework_content = FRAMEWORK_PATH.read_text(encoding="utf-8")

    current_orch_hash = compute_content_hash(orchestrator_content)
    current_reg_hash = compute_content_hash(registry_content)
    current_fw_hash = compute_content_hash(framework_content)

    registry_data = load_registry()
    current_total = registry_data.get("total_personas", 0)
    prev_total = manifest.get("total_personas", 0)

    if (current_orch_hash != manifest.get("meta_orchestrator_hash")
            or current_reg_hash != manifest.get("registry_hash")
            or current_fw_hash != manifest.get("framework_hash")):
        print(
            f"STALE: Content has changed since last export "
            f"({current_total} personas, was {prev_total} at last export)."
        )
        print("  Run: python tools/export_claude_project.py")
        return True

    print(f"OK: Up to date ({current_total} personas, "
          f"{len(registry_data.get('persona_families', []))} families).")
    return False


def export_files() -> None:
    """Read sources, patch counts, write exports, print instructions."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Load sources
    registry_data = load_registry()
    orchestrator_content = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
    registry_content = REGISTRY_PATH.read_text(encoding="utf-8")
    framework_content = FRAMEWORK_PATH.read_text(encoding="utf-8")

    total = registry_data.get("total_personas", 0)
    families = len(registry_data.get("persona_families", []))

    # Patch stale counts in meta-orchestrator
    patched = patch_dynamic_counts(orchestrator_content, registry_data)

    # Write loader prompt
    loader_path = EXPORT_DIR / "project-instructions.md"
    loader_path.write_text(generate_loader_prompt(), encoding="utf-8")

    # Write knowledge file
    knowledge_path = EXPORT_DIR / "meta-orchestrator-knowledge.md"
    knowledge_path.write_text(patched, encoding="utf-8")

    # Write framework file
    framework_export_path = EXPORT_DIR / "v2-framework.md"
    framework_export_path.write_text(framework_content, encoding="utf-8")

    # Write manifest
    manifest = {
        "last_export": datetime.now(timezone.utc).isoformat(),
        "meta_orchestrator_hash": compute_content_hash(orchestrator_content),
        "registry_hash": compute_content_hash(registry_content),
        "framework_hash": compute_content_hash(framework_content),
        "total_personas": total,
        "total_families": families,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    # Print summary
    print("Exported:")
    print(f"  {loader_path.relative_to(REPO_ROOT)}")
    print(f"    (paste into Project Instructions — one time only)")
    print(f"  {knowledge_path.relative_to(REPO_ROOT)}")
    print(f"    (upload as Project Knowledge file)")
    print(f"  {framework_export_path.relative_to(REPO_ROOT)}")
    print(f"    (upload as Project Knowledge file — v2 framework for L6 persona creation)")
    print(f"  {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"    ({total} personas, {families} families)")
    print()
    print("Next steps:")
    print("  1. Open your Claude.ai Task Router project")
    print("  2. If first time: paste project-instructions.md into Project Instructions")
    print("  3. Upload meta-orchestrator-knowledge.md as a Knowledge file")
    print("     (replace existing if updating)")
    print("  4. Upload v2-framework.md as a Knowledge file")
    print("     (enables L6 persona creation with full framework compliance)")


def main() -> int:
    if "--check" in sys.argv:
        return 1 if check_drift() else 0
    export_files()
    return 0


if __name__ == "__main__":
    sys.exit(main())
