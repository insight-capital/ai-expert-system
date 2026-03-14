#!/usr/bin/env python3
"""
validate_registry.py — Registry integrity checker for the AI Persona System.

Usage (from repo root):
    python tools/validate_registry.py

Exit codes:
    0  All checks passed
    1  One or more checks failed
"""

import sys
import os
from collections import Counter
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"


class CheckResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.messages: list[str] = []

    def fail(self, msg: str):
        self.passed = False
        self.messages.append(f"  {FAIL} {msg}")

    def warn(self, msg: str):
        self.messages.append(f"  {WARN} {msg}")

    def info(self, msg: str):
        self.messages.append(f"       {msg}")

    def status_line(self) -> str:
        icon = PASS if self.passed else FAIL
        return f"{icon} {self.name}"


def load_registry() -> dict:
    """Load and parse registry.yaml, exit on parse failure."""
    if not REGISTRY_PATH.exists():
        print(f"{FAIL} Registry file not found: {REGISTRY_PATH}")
        sys.exit(1)
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        print(f"{FAIL} registry.yaml did not parse to a mapping.")
        sys.exit(1)
    return data


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_persona_source_files(data: dict) -> CheckResult:
    """Check 1: All persona source_file paths resolve to actual files."""
    result = CheckResult("Persona source_file paths resolve to real files")
    personas = data.get("personas", [])
    for p in personas:
        pid = p.get("id", "<no-id>")
        sf = p.get("source_file")
        if not sf:
            result.fail(f"{pid}: missing source_file field")
            continue
        full_path = REPO_ROOT / sf
        if not full_path.is_file():
            result.fail(f"{pid}: file not found — {sf}")
        else:
            result.info(f"{pid}: OK ({sf})")
    return result


def check_prompt_template_source_files(data: dict) -> CheckResult:
    """Check 2a: All prompt template source_file paths resolve to actual files."""
    result = CheckResult("Prompt template source_file paths resolve to real files")
    templates = data.get("prompt_templates", [])
    for t in templates:
        tid = t.get("id", "<no-id>")
        sf = t.get("source_file")
        if not sf:
            result.fail(f"{tid}: missing source_file field")
            continue
        full_path = REPO_ROOT / sf
        if not full_path.is_file():
            result.fail(f"{tid}: file not found — {sf}")
        else:
            result.info(f"{tid}: OK ({sf})")
    return result


def check_prompt_sequence_source_files(data: dict) -> CheckResult:
    """Check 2b: All prompt sequence source_file paths resolve to actual files."""
    result = CheckResult("Prompt sequence source_file paths resolve to real files")
    sequences = data.get("prompt_sequences", [])
    for s in sequences:
        sid = s.get("id", "<no-id>")
        sf = s.get("source_file")
        if not sf:
            result.fail(f"{sid}: missing source_file field")
            continue
        full_path = REPO_ROOT / sf
        if not full_path.is_file():
            result.fail(f"{sid}: file not found — {sf}")
        else:
            result.info(f"{sid}: OK ({sf})")
    return result


def check_persona_id_uniqueness(data: dict) -> CheckResult:
    """Check 3: All persona IDs are unique."""
    result = CheckResult("Persona IDs are unique")
    personas = data.get("personas", [])
    ids = [p.get("id") for p in personas if p.get("id")]
    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    if duplicates:
        for pid, count in sorted(duplicates.items()):
            result.fail(f"Duplicate persona ID '{pid}' appears {count} times")
    else:
        result.info(f"{len(ids)} persona IDs all unique")
    return result


def check_prompt_template_id_uniqueness(data: dict) -> CheckResult:
    """Check 4: All prompt template IDs are unique."""
    result = CheckResult("Prompt template IDs are unique")
    templates = data.get("prompt_templates", [])
    ids = [t.get("id") for t in templates if t.get("id")]
    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    if duplicates:
        for tid, count in sorted(duplicates.items()):
            result.fail(f"Duplicate prompt template ID '{tid}' appears {count} times")
    else:
        result.info(f"{len(ids)} prompt template IDs all unique")
    return result


def check_prompt_sequence_id_uniqueness(data: dict) -> CheckResult:
    """Check 5: All prompt sequence IDs are unique."""
    result = CheckResult("Prompt sequence IDs are unique")
    sequences = data.get("prompt_sequences", [])
    ids = [s.get("id") for s in sequences if s.get("id")]
    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    if duplicates:
        for sid, count in sorted(duplicates.items()):
            result.fail(f"Duplicate prompt sequence ID '{sid}' appears {count} times")
    else:
        result.info(f"{len(ids)} prompt sequence IDs all unique")
    return result


def check_works_with_references(data: dict) -> CheckResult:
    """Check 6: All works_with references point to valid persona IDs."""
    result = CheckResult("composability.works_with references are valid persona IDs")
    personas = data.get("personas", [])
    valid_ids = {p.get("id") for p in personas if p.get("id")}
    for p in personas:
        pid = p.get("id", "<no-id>")
        composability = p.get("composability", {}) or {}
        works_with = composability.get("works_with", []) or []
        for ref in works_with:
            if ref not in valid_ids:
                result.fail(f"{pid}: works_with references unknown persona '{ref}'")
    if result.passed:
        result.info("All works_with references resolve to known persona IDs")
    return result


def check_count_fields(data: dict) -> CheckResult:
    """Check 7: total_personas, total_prompt_templates, total_prompt_sequences match actual counts."""
    result = CheckResult("Declared counts match actual counts")

    declared_personas = data.get("total_personas")
    declared_templates = data.get("total_prompt_templates")
    declared_sequences = data.get("total_prompt_sequences")

    actual_personas = len(data.get("personas", []))
    actual_templates = len(data.get("prompt_templates", []))
    actual_sequences = len(data.get("prompt_sequences", []))

    def check_count(field_name, declared, actual):
        if declared is None:
            result.fail(f"'{field_name}' field is missing from registry")
        elif declared != actual:
            result.fail(
                f"'{field_name}' declares {declared} but {actual} entries found"
            )
        else:
            result.info(f"{field_name}: {actual} (matches declared value)")

    check_count("total_personas", declared_personas, actual_personas)
    check_count("total_prompt_templates", declared_templates, actual_templates)
    check_count("total_prompt_sequences", declared_sequences, actual_sequences)
    return result


def check_domain_scope_overlaps(data: dict) -> CheckResult:
    """
    Check 8: Warn about personas with significant domain_scope overlaps that share
    the same cognitive_posture (which may indicate insufficient differentiation).

    Algorithm:
      - For each pair of active personas, compute a naive overlap score: number
        of domain_scope terms that share any word with the other persona's
        domain_scope terms.
      - Emit a warning when overlap_ratio >= OVERLAP_THRESHOLD AND the two
        personas have identical cognitive_postures.
    """
    result = CheckResult("Domain scope overlaps between personas (overlap warnings)")
    OVERLAP_THRESHOLD = 0.5  # 50% of the smaller set's terms overlap

    personas = [p for p in data.get("personas", []) if p.get("status") == "active"]

    def term_tokens(scope_list: list) -> set[str]:
        """Flatten domain_scope items into a bag of significant words."""
        tokens: set[str] = set()
        stop = {"and", "or", "for", "of", "the", "a", "an", "in", "with",
                "to", "from", "vs.", "vs", "/", "-", "based", "per"}
        for item in (scope_list or []):
            for word in str(item).lower().replace("/", " ").replace("-", " ").split():
                cleaned = word.strip("().,:")
                if cleaned and cleaned not in stop and len(cleaned) > 2:
                    tokens.add(cleaned)
        return tokens

    warnings_emitted = 0
    for i, pa in enumerate(personas):
        for pb in personas[i + 1:]:
            pid_a = pa.get("id", "?")
            pid_b = pb.get("id", "?")

            scope_a = term_tokens(pa.get("domain_scope", []))
            scope_b = term_tokens(pb.get("domain_scope", []))
            if not scope_a or not scope_b:
                continue

            overlap = scope_a & scope_b
            smaller = min(len(scope_a), len(scope_b))
            overlap_ratio = len(overlap) / smaller if smaller > 0 else 0

            posture_a = pa.get("cognitive_posture", "")
            posture_b = pb.get("cognitive_posture", "")
            same_posture = posture_a and posture_b and posture_a == posture_b

            if overlap_ratio >= OVERLAP_THRESHOLD and same_posture:
                result.warn(
                    f"{pid_a} ({pa.get('name')}) and {pid_b} ({pb.get('name')}) "
                    f"share {overlap_ratio:.0%} domain scope overlap "
                    f"AND identical cognitive_posture ('{posture_a}'). "
                    f"Overlapping terms: {', '.join(sorted(overlap)[:8])}"
                )
                warnings_emitted += 1
            elif overlap_ratio >= OVERLAP_THRESHOLD:
                result.info(
                    f"Note: {pid_a} and {pid_b} share {overlap_ratio:.0%} domain scope "
                    f"overlap but have differentiated cognitive postures "
                    f"('{posture_a}' vs '{posture_b}') — OK"
                )

    if warnings_emitted == 0:
        result.info("No undifferentiated domain scope overlaps detected")
    return result


def check_unregistered_persona_files(data: dict) -> CheckResult:
    """Check 9: All .md files in personas/ (excluding archive/) have a registry entry."""
    result = CheckResult("All persona files in personas/ are registered")
    personas_dir = REPO_ROOT / "personas"
    if not personas_dir.is_dir():
        result.fail("personas/ directory not found")
        return result

    registered_files = set()
    for p in data.get("personas", []):
        sf = p.get("source_file", "")
        if sf:
            registered_files.add(sf)

    unregistered = []
    for md_file in sorted(personas_dir.glob("*.md")):
        relative = f"personas/{md_file.name}"
        if relative not in registered_files:
            unregistered.append(md_file.name)

    if unregistered:
        for name in unregistered:
            result.fail(f"personas/{name} exists but has no registry entry")
        result.info(
            f"Run 'python tools/add_persona.py personas/{unregistered[0]}' to register"
        )
    else:
        registered_count = len(list(personas_dir.glob("*.md")))
        result.info(
            f"All {registered_count} persona files in personas/ are registered"
        )
    return result


def check_knowledge_graph_count(data: dict) -> CheckResult:
    """Check 11: total_knowledge_graphs matches actual count of personas with knowledge_graph field."""
    result = CheckResult("Knowledge graph count matches declared total")
    declared = data.get("total_knowledge_graphs")
    if declared is None:
        result.fail("'total_knowledge_graphs' field is missing from registry")
        return result

    personas = data.get("personas", [])
    actual = sum(1 for p in personas if p.get("knowledge_graph"))
    if declared != actual:
        result.fail(
            f"'total_knowledge_graphs' declares {declared} but {actual} personas "
            f"have a knowledge_graph field"
        )
    else:
        result.info(f"total_knowledge_graphs: {actual} (matches declared value)")
    return result


def check_knowledge_graph_entry_points(data: dict) -> CheckResult:
    """Check 12: All knowledge_graph.entry_point paths resolve to real files."""
    result = CheckResult("Knowledge graph entry_point paths resolve to real files")
    personas = data.get("personas", [])
    graphs_found = 0
    for p in personas:
        kg = p.get("knowledge_graph")
        if not kg:
            continue
        graphs_found += 1
        pid = p.get("id", "<no-id>")
        entry_point = kg.get("entry_point")
        if not entry_point:
            result.fail(f"{pid}: knowledge_graph missing entry_point field")
            continue
        full_path = REPO_ROOT / entry_point
        if not full_path.is_file():
            result.fail(f"{pid}: entry_point not found — {entry_point}")
        else:
            result.info(f"{pid}: OK ({entry_point})")

    if graphs_found == 0:
        result.info("No knowledge graphs defined — check is a no-op")
    return result


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_all_checks(data: dict) -> list[CheckResult]:
    return [
        check_persona_source_files(data),
        check_prompt_template_source_files(data),
        check_prompt_sequence_source_files(data),
        check_persona_id_uniqueness(data),
        check_prompt_template_id_uniqueness(data),
        check_prompt_sequence_id_uniqueness(data),
        check_works_with_references(data),
        check_count_fields(data),
        check_domain_scope_overlaps(data),
        check_unregistered_persona_files(data),
        check_knowledge_graph_count(data),
        check_knowledge_graph_entry_points(data),
    ]


def print_report(results: list[CheckResult]) -> bool:
    """Print the full summary report. Returns True if all checks passed."""
    print()
    print("=" * 66)
    print("  AI PERSONA SYSTEM — Registry Validation Report")
    print(f"  Registry: {REGISTRY_PATH}")
    print("=" * 66)
    print()

    all_passed = True
    for result in results:
        print(result.status_line())
        for msg in result.messages:
            print(msg)
        if not result.passed:
            all_passed = False
        print()

    print("-" * 66)
    total = len(results)
    failed = sum(1 for r in results if not r.passed)
    passed = total - failed
    print(f"  Results: {passed}/{total} checks passed", end="")
    if failed:
        print(f", {failed} FAILED")
    else:
        print(" — all OK")
    print("-" * 66)
    print()
    return all_passed


def main() -> int:
    print(f"Loading registry from: {REGISTRY_PATH}")
    data = load_registry()
    results = run_all_checks(data)
    all_passed = print_report(results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
