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
    5. Updates total_personas count and persona_families in the registry
    6. Appends a row to the routing table in master-expert/meta-orchestrator.md

Dependencies: PyYAML
"""

import re
import sys
import shutil
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
PERSONAS_DIR = REPO_ROOT / "personas"
REGISTRY_PATH = REPO_ROOT / "registry" / "registry.yaml"
ORCHESTRATOR_PATH = REPO_ROOT / "master-expert" / "meta-orchestrator.md"
ADAPTERS_DIR = REPO_ROOT / "adapters"
ADAPTER_FILES = {
    "claude-code": ADAPTERS_DIR / "claude-code-adapter.md",
    "chatgpt": ADAPTERS_DIR / "chatgpt-adapter.md",
    "gemini": ADAPTERS_DIR / "gemini-adapter.md",
}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def to_kebab_case(name: str) -> str:
    """Convert a display name to a kebab-case filename stem.

    Examples:
        'AI Chief Technology Officer' -> 'ai-chief-technology-officer'
        'AI/ML Forward-Deployed Engineer' -> 'ai-ml-forward-deployed-engineer'
        'Persona 1: Audience Relevance Analyst' -> 'audience-relevance-analyst'
    """
    # Strip leading "Persona N:", "Expert Persona:", "Expert Research Persona: The", etc.
    name = re.sub(r'^Expert\s+(?:\w+\s+)?Persona\s*\d*\s*:\s*(?:The\s+)?', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'^Persona\s*\d+\s*:\s*', '', name, flags=re.IGNORECASE).strip()
    # Replace slashes, ampersands, dots with hyphens
    name = re.sub(r'[/&.]+', '-', name)
    # Replace non-alphanumeric (except hyphens) with hyphens
    name = re.sub(r'[^a-zA-Z0-9-]+', '-', name)
    # Collapse multiple hyphens
    name = re.sub(r'-{2,}', '-', name)
    # Strip leading/trailing hyphens, lowercase
    return name.strip('-').lower()


def to_snake_case(text: str) -> str:
    """Convert a phrase like 'Strategic Architect' to 'strategic_architect'."""
    text = text.strip().rstrip('.')
    text = re.sub(r'[^a-zA-Z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_').lower()


def first_sentence(text: str, max_sentences: int = 2) -> str:
    """Extract the first 1-2 sentences from a paragraph."""
    text = text.strip()
    # Split on sentence-ending punctuation followed by space or end-of-string
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = ' '.join(sentences[:max_sentences]).strip()
    # Cap at ~300 chars for registry brevity
    if len(result) > 300:
        result = result[:297].rsplit(' ', 1)[0] + '...'
    return result


# ---------------------------------------------------------------------------
# Metadata extraction — tries multiple regex patterns per field
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    """Read a file with UTF-8 encoding."""
    return path.read_text(encoding='utf-8')


def strip_code_fences(content: str) -> str:
    """Strip wrapping code fences from v1-era personas.

    v1 personas wrap the body inside a fenced code block after the top-level
    heading and a '## Master System Prompt' section header. This function
    detects that pattern and removes the opening/closing ``` lines so that
    downstream regex extraction works on the actual markdown content.
    """
    # Look for an opening ``` on its own line (possibly with a language tag)
    # that appears early in the document (within the first ~10 lines)
    lines = content.split('\n')
    fence_open_idx = None
    fence_close_idx = None

    # Find the first opening code fence in the first 10 lines
    for i, line in enumerate(lines[:10]):
        if re.match(r'^```\s*\w*\s*$', line):
            fence_open_idx = i
            break

    if fence_open_idx is None:
        return content  # No code fence found — nothing to strip

    # Find the matching closing fence (last ``` in the file)
    for i in range(len(lines) - 1, fence_open_idx, -1):
        if re.match(r'^```\s*$', lines[i]):
            fence_close_idx = i
            break

    if fence_close_idx is None or fence_close_idx <= fence_open_idx:
        return content  # No closing fence — leave as-is

    # Remove the fence lines, keep everything else
    result_lines = lines[:fence_open_idx] + lines[fence_open_idx + 1:fence_close_idx] + lines[fence_close_idx + 1:]
    return '\n'.join(result_lines)


def extract_name(content: str) -> str | None:
    """Extract persona display name from the first heading."""
    # Variation v1: # Expert <Word> Persona: [The] <Name>
    m = re.search(r'^#\s+Expert\s+\w+\s+Persona:\s*(?:The\s+)?(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Variation B/C: # Expert Persona: <Name>
    m = re.search(r'^#\s+Expert\s+Persona:\s*(?:The\s+)?(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Variation A: # Persona N: <Name>
    m = re.search(r'^#\s+Persona\s+\d+:\s*(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Fallback: first H1 heading
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        raw = m.group(1).strip()
        # Strip common prefixes from the fallback too
        raw = re.sub(r'^Expert\s+(?:\w+\s+)?Persona:\s*(?:The\s+)?', '', raw, flags=re.IGNORECASE).strip()
        return raw if raw else m.group(1).strip()
    return None


def extract_role_summary(content: str) -> str | None:
    """Extract role summary from Primary Objective / Primary Goal / Role."""
    # Numbered prefix pattern: optional "1.2 " etc. before heading text
    NP = r'(?:\d+\.\d+\s+)?'
    patterns = [
        # Variation A: ### [1.2] Primary Objective / Core Objective / Core Mission
        rf'###\s*{NP}(?:Primary\s+Objective|Core\s+Objective|Core\s+Mission)\s*\n+(.+?)(?:\n\n|\n###|\n##)',
        # Variation A with bold prefix
        rf'###\s*{NP}(?:Primary\s+Objective|Core\s+Objective|Core\s+Mission)\s*\n+\*\*[^*]+\*\*\s*(.+?)(?:\n\n|\n###|\n##)',
        # Variation C: **Primary Goal:** text
        r'\*\*Primary\s+Goal:\*\*\s*(.+?)(?:\n\n|\n###|\n##|\n\*\*)',
        # Variation C: **Role:** text
        r'\*\*Role:\*\*\s*(.+?)(?:\n\n|\n###|\n##|\n\*\*)',
        # v1: "Your primary mission is to ..." in opening paragraph
        r'Your primary mission is to\s+(.+?)(?:\n\n|\n---)',
        # v2: "Your mission is to ..." (without "primary")
        r'Your mission is to\s+(.+?)(?:\n\n|\n---|\n\n)',
    ]
    for pat in patterns:
        m = re.search(pat, content, re.DOTALL)
        if m:
            text = m.group(1).strip()
            # Clean up markdown formatting
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\s+', ' ', text)
            return first_sentence(text)
    return None


def extract_cognitive_posture(content: str) -> str | None:
    """Extract cognitive posture name and convert to snake_case.

    Handles:
        ### Cognitive Posture
        **Investigative Reconstructionist.** ...

        **Cognitive Posture:** Strategic Architect and Constructive Skeptic. ...

        ### Cognitive Posture
        Forensic psychologist and audience strategist. ...
    """
    # Optional numbered prefix in heading: ### 1.3 Cognitive Posture
    NP = r'(?:\d+\.\d+\s+)?'

    # Pattern 1: ### [1.3] [Dual-Mode] Cognitive Posture\n\n**Posture Name.** ...
    m = re.search(
        rf'###?\s*{NP}(?:[\w-]+\s+)?Cognitive\s+Posture\s*\n+\*\*(?:Primary:\s+|Hybrid:\s+)?([^.*]+)[.*]',
        content, re.MULTILINE
    )
    if m:
        return to_snake_case(m.group(1).strip())

    # Pattern 2: **Cognitive Posture:** Posture Name. ...  (inline)
    m = re.search(
        r'\*\*Cognitive\s+Posture:\*\*\s*([^.]+)\.',
        content
    )
    if m:
        return to_snake_case(m.group(1).strip())

    # Pattern 3: ### [1.3] [Dual-Mode] Cognitive Posture\n\nPlain text posture. ...
    m = re.search(
        rf'###?\s*{NP}(?:[\w-]+\s+)?Cognitive\s+Posture\s*\n+([^#*\n][^\n.]+)\.',
        content, re.MULTILINE
    )
    if m:
        posture_text = m.group(1).strip()
        # Take up to "and" or comma or "You" as a natural break
        short = re.split(r'\s+and\s+|\s*[,;]\s*|\.\s+|\s+You\s+', posture_text)[0]
        # If it's very long, take first 3-4 words
        words = short.split()
        if len(words) > 4:
            short = ' '.join(words[:4])
        return to_snake_case(short)

    # Pattern 4: table row | **Cognitive Posture** | Value: ... |
    m = re.search(
        r'\|\s*\*\*Cognitive\s+Posture\*\*\s*\|\s*([^|]+)\|',
        content
    )
    if m:
        posture_text = m.group(1).strip()
        short = re.split(r'[:;+]', posture_text)[0].strip()
        words = short.split()
        if len(words) > 4:
            short = ' '.join(words[:4])
        return to_snake_case(short)

    return None


def extract_domain_scope(content: str) -> list[str]:
    """Extract domain scope items from Core Domains / Core Competencies section."""
    # Optional numbered prefix: ### 2.1 Core Domains
    NP = r'(?:\d+\.\d+\s+)?'

    # Find the section header (heading form) — broad pattern to catch all variants
    m = re.search(
        rf'###?\s*{NP}(?:Core|Primary)\s+(?:\w+\s+)*(?:Domains?|Competenc\w*(?:\s+Areas?)?|Expertise|Methodolog\w*)\s*\n',
        content, re.MULTILINE
    )
    # v1 fallback: **Core Competencies:** as bold text (not a heading)
    if not m:
        m = re.search(
            r'\*\*Core\s+(?:Domains|Competencies|Technical\s+Competencies)[^*]*\*\*:?\s*\n',
            content, re.MULTILINE
        )
    if not m:
        return []

    # Get text after the header until the next same-level or higher heading
    after = content[m.end():]
    section = re.split(r'\n###?\s(?!\d+\.\d+\.\d+)|\n##\s', after, maxsplit=1)[0]

    items = []

    # Strategy 1: bullet items (most common)
    for line in section.split('\n'):
        line = line.strip()
        if not line.startswith('-'):
            continue
        line = line.lstrip('- ').strip()
        # Extract bold domain name: **Domain Name:** description...
        bm = re.match(r'\*\*([^*]+)\*\*', line)
        if bm:
            domain = bm.group(1).strip().rstrip(':').rstrip('.')
            items.append(domain)
        else:
            # Plain bullet item — take first phrase, strip trailing period
            text = line.split('.')[0].strip() if '. ' in line else line.rstrip('.').strip()
            if text:
                items.append(text)

    if items:
        return items

    # Strategy 2: #### sub-headings as domain items
    for subm in re.finditer(r'^####\s+(?:\d+\.\d+\.\d+\s+)?(.+)$', section, re.MULTILINE):
        heading = subm.group(1).strip()
        if heading and len(heading) < 80:
            items.append(heading)

    if items:
        return items

    # Strategy 3: bold items from table rows
    for tm in re.finditer(r'\|\s*\*\*([^|*]+)\*\*\s*\|', section):
        item = tm.group(1).strip()
        if item and item.lower() not in ('domain', 'field', 'parameter', 'category', 'key authorities', 'applied competency'):
            items.append(item)

    return items


def extract_out_of_scope(content: str) -> list[str]:
    """Extract out of scope items."""
    # Find Out of Scope section (multiple heading conventions)
    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Out\s+of\s+Scope[^*\n]*(?:\*\*)?\s*\n',
        content, re.MULTILINE | re.IGNORECASE
    )

    # v1 fallback: **Hard Constraints (Never Do):** with numbered items
    is_numbered = False
    if not m:
        m = re.search(
            r'\*\*Hard\s+Constraints\s*\(Never\s+Do\)[^*]*\*\*:?\s*\n',
            content, re.MULTILINE | re.IGNORECASE
        )
        if m:
            is_numbered = True

    if not m:
        return []

    after = content[m.end():]
    section = re.split(r'\n###?\s|\n##\s|\n\*\*(?:Standing|Always)', after, maxsplit=1)[0]

    items = []
    for line in section.split('\n'):
        line = line.strip()
        # Handle both bullet items and numbered items
        if line.startswith('-'):
            line = line.lstrip('- ').strip()
        elif is_numbered and re.match(r'^\d+\.\s+', line):
            line = re.sub(r'^\d+\.\s+', '', line).strip()
        else:
            continue
        # Strip "owned by" parentheticals and persona references
        line = re.sub(r'\s*\(owned\s+by[^)]*\)', '', line, flags=re.IGNORECASE)
        line = re.sub(r'\s*—\s*owned\s+by.*$', '', line, flags=re.IGNORECASE)
        # Strip markdown bold and inline refs
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        # Strip "You do NOT" / "You do not" / "Do NOT" / "Never" prefixes
        line = re.sub(r'^(?:You\s+)?(?:do\s+)?NOT?\s+', '', line, flags=re.IGNORECASE)
        line = re.sub(r'^Never\s+', '', line, flags=re.IGNORECASE)
        # Take first sentence only
        line = line.split('.')[0].strip() if '. ' in line else line.rstrip('.')
        # Capitalize first letter
        if line:
            line = line[0].upper() + line[1:] if len(line) > 1 else line.upper()
            items.append(line)
    return items


def extract_input_spec(content: str) -> dict:
    """Extract input specification: accepts list and required_fields."""
    result = {"accepts": [], "required_fields": []}

    # Find Input Specification section
    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Input\s+Spec(?:ification)?(?:\*\*)?[:\s]*\n',
        content, re.MULTILINE | re.IGNORECASE
    )
    if not m:
        return result

    after = content[m.end():]
    # Limit to section before next heading or Output Spec
    section = re.split(r'\n###?\s|\n##\s|\n\*\*Output', after, maxsplit=1)[0]

    # Extract **Accepts:** list (bullet items or paragraph)
    am = re.search(r'\*\*Accepts:\*\*\s*\n?(.*?)(?:\n\*\*|\n\n\*\*|$)', section, re.DOTALL)
    if am:
        accepts_text = am.group(1)
        # Check if this is a bullet list or a paragraph
        lines = [l.strip() for l in accepts_text.split('\n') if l.strip()]
        has_bullets = any(l.startswith('- ') for l in lines)
        if has_bullets:
            for line in lines:
                if not line.startswith('- '):
                    continue
                line = line.lstrip('- ').strip()
                # Extract backtick-enclosed terms
                backtick_items = re.findall(r'`([^`]+)`', line)
                if backtick_items:
                    result["accepts"].extend(backtick_items)
                else:
                    phrase = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
                    phrase = phrase.split(',')[0].split('(')[0].strip()
                    if phrase and len(phrase) < 80:
                        result["accepts"].append(to_snake_case(phrase))
        else:
            # Paragraph form: look for "A batch of X" or "A <noun>" patterns
            # and "Y in structured format" patterns — extract as artifact types
            for line in lines:
                # Try to extract "a batch of <X>" or "a <noun phrase>"
                for mp in re.finditer(r'(?:a |A )(?:batch of )?([a-z][\w\s]+?)(?:[,.]|\s+(?:each|in |containing))', line):
                    artifact = mp.group(1).strip()
                    if len(artifact) < 60:
                        result["accepts"].append(to_snake_case(artifact))

    # Variation B: **Required:** / **Optional:** pattern
    if not result["accepts"]:
        rm = re.search(r'\*\*Required:\*\*\s*(.*?)(?:\n\*\*|\n\n|$)', section, re.DOTALL)
        if rm:
            req_text = rm.group(1).strip()
            # Split on commas, extract meaningful phrases
            for part in re.split(r'[,\n]', req_text):
                part = part.strip().lstrip('- ').strip()
                if part:
                    part = re.sub(r'\*\*([^*]+)\*\*', r'\1', part)
                    short = part.split('(')[0].strip().rstrip('.')
                    if short and len(short) < 80:
                        result["accepts"].append(to_snake_case(short))

    # Also try table-based input spec (Variation C)
    if not result["accepts"]:
        # Look for table rows with Input Artifact
        for tm in re.finditer(r'\|\s*\*\*([^|*]+)\*\*\s*\|', section):
            artifact = tm.group(1).strip()
            if artifact and artifact.lower() not in ('input artifact', 'field', 'parameter'):
                result["accepts"].append(to_snake_case(artifact))

    # Also try: accepts from bullet items directly after the section header
    if not result["accepts"]:
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                text = line.lstrip('- ').strip()
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
                short = text.split(':')[0].split('(')[0].strip()
                if short and len(short) < 60:
                    result["accepts"].append(to_snake_case(short))

    # Extract **Required fields:** or **required_fields:** or **Required:**
    rm = re.search(
        r'\*\*[Rr]equired[\s_]?fields?:\*\*\s*(.*?)(?:\n\*\*|\n\n|$)',
        section, re.DOTALL
    )
    if rm:
        fields_text = rm.group(1).strip()
        # Extract backtick-enclosed terms first (most reliable)
        backtick_items = re.findall(r'`([^`]+)`', fields_text)
        if backtick_items:
            result["required_fields"] = backtick_items
        else:
            # Check if it's a bullet list
            lines = [l.strip() for l in fields_text.split('\n') if l.strip()]
            if any(l.startswith('- ') for l in lines):
                for line in lines:
                    if line.startswith('- '):
                        part = line.lstrip('- ').strip()
                        if part and len(part) < 60:
                            result["required_fields"].append(to_snake_case(part))
            else:
                # Paragraph form — try "Both X and Y" pattern
                both_m = re.search(r'[Bb]oth\s+(?:the\s+)?(.+?)\s+and\s+(.+?)\s+must', fields_text)
                if both_m:
                    result["required_fields"].append(to_snake_case(both_m.group(1).strip()))
                    result["required_fields"].append(to_snake_case(both_m.group(2).strip()))
                else:
                    # Comma-separated
                    for part in re.split(r'[,\n]', fields_text):
                        part = part.strip().lstrip('- ').strip()
                        if part and len(part) < 60:
                            result["required_fields"].append(to_snake_case(part))

    # Extract Required from table rows
    if not result["required_fields"]:
        for tm in re.finditer(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', section):
            col2 = tm.group(2).strip()
            if 'required' in col2.lower():
                fields = re.findall(r'`([^`]+)`', col2)
                result["required_fields"].extend(fields)

    return result


def extract_output_spec(content: str) -> dict:
    """Extract output specification: produces, format, fields."""
    result = {"produces": "", "format": "structured_markdown", "fields": []}

    # Find Output Specification section
    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Output\s+Spec(?:ification)?(?:\*\*)?[:\s]*\n',
        content, re.MULTILINE | re.IGNORECASE
    )
    if not m:
        return result

    after = content[m.end():]
    section = re.split(r'\n###?\s|\n##\s|\n---', after, maxsplit=1)[0]

    # Extract **Produces:** text
    pm = re.search(r'\*\*Produces:\*\*\s*(.+)', section)
    if pm:
        result["produces"] = to_snake_case(pm.group(1).strip().rstrip('.'))
    else:
        # Look for "The primary output artifact is a **Name**"
        pm = re.search(r'primary\s+output\s+artifact\s+is\s+a?\s*\*\*([^*]+)\*\*', section, re.IGNORECASE)
        if pm:
            result["produces"] = to_snake_case(pm.group(1).strip())

    # Extract **Format:** text
    fm = re.search(r'\*\*(?:Output\s+)?Format:\*\*\s*(.+)', section)
    if fm:
        fmt = fm.group(1).strip().rstrip('.')
        result["format"] = to_snake_case(fmt.split('.')[0])

    # Extract fields from **Required output fields** list or table
    fields_m = re.search(r'\*\*Required\s+output\s+fields[^:]*:\*\*\s*\n(.*?)(?:\n\*\*|\n\n\*\*|$)', section, re.DOTALL)
    if fields_m:
        for fm in re.finditer(r'`([^`]+)`', fields_m.group(1)):
            result["fields"].append(fm.group(1))

    # Also try extracting from table
    if not result["fields"]:
        for tm in re.finditer(r'\|\s*\*\*([^|*]+)\*\*\s*\|', section):
            artifact = tm.group(1).strip()
            if artifact.lower() not in ('output artifact', 'format', 'required fields'):
                result["fields"].append(to_snake_case(artifact))

    # Also try numbered list items that describe sections
    if not result["fields"]:
        for nm in re.finditer(r'^\d+\.\s+\*\*([^*]+)\*\*', section, re.MULTILINE):
            result["fields"].append(to_snake_case(nm.group(1).strip()))

    return result


def extract_persona_references(content: str) -> list[str]:
    """Find persona-XXX references in the file content."""
    return sorted(set(re.findall(r'persona-\d{3}', content)))


def extract_tags_auto(name: str, domain_scope: list[str], family: str) -> list[str]:
    """Auto-generate suggested tags from name, domain, and family."""
    tags = set()

    # Family-based tag
    family_tag_map = {
        "Content Briefing": "briefing",
        "Example Assessment": "example",
        "Meta": "meta",
        "General AI Biz": "ai-biz",
        "Writing": "writing",
        "Career Search": "career-search",
        "Legal": "legal",
        "Valuation & Finance": "valuation-finance",
        "Security & Engineering": "security-engineering",
    }
    fam_tag = family_tag_map.get(family)
    if fam_tag:
        tags.add(fam_tag)

    # Name-based tags
    name_lower = name.lower()
    if 'strategy' in name_lower or 'strategist' in name_lower:
        tags.add('strategy')
    if 'engineer' in name_lower:
        tags.add('engineering')
    if 'architect' in name_lower:
        tags.add('architecture')
    if 'lead' in name_lower or 'director' in name_lower:
        tags.add('leadership')
    if 'research' in name_lower:
        tags.add('research')
    if 'content' in name_lower or 'writer' in name_lower or 'editor' in name_lower:
        tags.add('content')
    if 'security' in name_lower or 'risk' in name_lower:
        tags.add('security')
    if 'data' in name_lower:
        tags.add('data')
    if any(term in name_lower for term in ['ai', 'ml', 'llm']):
        tags.add('ai')

    # Domain-scope based tags
    for item in domain_scope[:3]:
        item_lower = item.lower()
        if 'prompt' in item_lower:
            tags.add('prompt-engineering')
        if 'agent' in item_lower:
            tags.add('agent-architecture')
        if 'pipeline' in item_lower:
            tags.add('pipeline')

    return sorted(tags)


# ---------------------------------------------------------------------------
# Registry manipulation
# ---------------------------------------------------------------------------

def load_registry_text() -> str:
    """Load registry.yaml as raw text (to preserve formatting and comments)."""
    return REGISTRY_PATH.read_text(encoding='utf-8')


def load_registry_data() -> dict:
    """Load and parse registry.yaml."""
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def get_next_persona_id(data: dict) -> str:
    """Determine the next available persona-XXX ID."""
    personas = data.get('personas', [])
    existing_ids = set()
    for p in personas:
        pid = p.get('id', '')
        m = re.match(r'persona-(\d{3})', pid)
        if m:
            existing_ids.add(int(m.group(1)))

    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"persona-{next_num:03d}"


def get_families(data: dict) -> list[dict]:
    """Get the persona_families list."""
    return data.get('persona_families', [])


def build_registry_entry_yaml(metadata: dict) -> str:
    """Build the YAML text for a new persona registry entry.

    We build this manually (not via yaml.dump) to match the exact formatting
    of the existing registry entries.
    """
    def yaml_scalar(text: str) -> str:
        """Quote a YAML scalar if it contains special characters."""
        if any(ch in text for ch in ':"{}[]&*?|>!%@`'):
            escaped = text.replace('"', '\\"')
            return f'"{escaped}"'
        return text

    def yaml_list(items: list, indent: int = 6) -> str:
        """Format a YAML list with the given indentation."""
        if not items:
            return f"{' ' * indent}[]"  # This won't be reached for non-empty lists
        prefix = ' ' * indent
        return '\n'.join(f'{prefix}- {yaml_scalar(item)}' for item in items)

    def yaml_quoted_list(items: list) -> str:
        """Format a YAML inline list with quoted strings."""
        if not items:
            return '[]'
        return '[' + ', '.join(f'"{item}"' for item in items) + ']'

    pid = metadata['id']
    name = metadata['name']
    source_file = metadata['source_file']
    role_summary = metadata.get('role_summary', '')
    cog_posture = metadata.get('cognitive_posture', '')
    domain_scope = metadata.get('domain_scope', [])
    out_of_scope = metadata.get('out_of_scope', [])
    input_spec = metadata.get('input_spec', {})
    output_spec = metadata.get('output_spec', {})
    composability = metadata.get('composability', {})
    voice_cal = metadata.get('voice_calibration', 'uses_own_voice')
    tags = metadata.get('tags', [])

    # Build domain_scope lines (use yaml_scalar for safe quoting)
    ds_lines = yaml_list(domain_scope) if domain_scope else '      []'
    # Build out_of_scope lines
    oos_lines = yaml_list(out_of_scope) if out_of_scope else '      []'

    accepts = yaml_quoted_list(input_spec.get('accepts', []))
    required_fields = yaml_quoted_list(input_spec.get('required_fields', []))

    produces = output_spec.get('produces', '')
    fmt = output_spec.get('format', 'structured_markdown')
    fields = yaml_quoted_list(output_spec.get('fields', []))

    works_with = yaml_quoted_list(composability.get('works_with', []))
    position = composability.get('position_in_pipeline', 'standalone')
    known_wf = yaml_quoted_list(composability.get('known_workflows', []))

    tags_str = yaml_quoted_list(tags)

    # Escape double quotes in text fields
    role_summary_escaped = role_summary.replace('"', '\\"')
    name_escaped = name.replace('"', '\\"')

    entry = f"""
  - id: {pid}
    name: "{name_escaped}"
    status: active
    source_file: "{source_file}"
    role_summary: "{role_summary_escaped}"
    cognitive_posture: "{cog_posture}"
    domain_scope:
{ds_lines}
    out_of_scope:
{oos_lines}
    input_spec:
      accepts: {accepts}
      required_fields: {required_fields}
    output_spec:
      produces: "{produces}"
      format: "{fmt}"
      fields: {fields}
    composability:
      works_with: {works_with}
      position_in_pipeline: "{position}"
      known_workflows: {known_wf}
    voice_calibration: "{voice_cal}"
    tags: {tags_str}
"""
    return entry


def insert_registry_entry(registry_text: str, entry_yaml: str) -> str:
    """Insert the new entry before the PROMPT TEMPLATES separator line."""
    # Find the separator line before PROMPT TEMPLATES
    marker = '# ============================================================\n# PROMPT TEMPLATES'
    idx = registry_text.find(marker)
    if idx == -1:
        # Fallback: find just the PROMPT TEMPLATES comment
        marker = '# PROMPT TEMPLATES'
        idx = registry_text.find(marker)
        if idx == -1:
            raise ValueError("Could not find '# PROMPT TEMPLATES' marker in registry.yaml")
        # Back up to the separator line before it
        line_start = registry_text.rfind('\n', 0, idx)
        if line_start != -1:
            prev_line_start = registry_text.rfind('\n', 0, line_start)
            if prev_line_start != -1 and '=====' in registry_text[prev_line_start:line_start]:
                idx = prev_line_start + 1
            else:
                idx = line_start + 1
        else:
            idx = idx
    else:
        pass  # idx points to the separator, which is correct

    # Insert the entry before the marker
    return registry_text[:idx] + entry_yaml + registry_text[idx:]


def update_total_personas(registry_text: str, old_count: int, new_count: int) -> str:
    """Update the total_personas line."""
    old_line = f'total_personas: {old_count}'
    new_line = f'total_personas: {new_count}'
    if old_line not in registry_text:
        raise ValueError(f"Could not find '{old_line}' in registry.yaml")
    return registry_text.replace(old_line, new_line, 1)


def update_persona_families(registry_text: str, family_name: str, new_id: str) -> str:
    """Append the new persona ID to the correct family's ids list."""
    # Find the family entry and its ids line
    # Pattern: name: "Family Name"\n    ids: ["persona-001", ...]
    pattern = re.compile(
        r'(  - name: "' + re.escape(family_name) + r'"\s*\n\s*ids: \[)([^\]]*)\]',
        re.MULTILINE
    )
    m = pattern.search(registry_text)
    if not m:
        raise ValueError(f"Could not find family '{family_name}' in persona_families section")

    prefix = m.group(1)
    existing_ids = m.group(2).strip()

    if existing_ids:
        new_ids = f'{existing_ids}, "{new_id}"'
    else:
        new_ids = f'"{new_id}"'

    old_text = m.group(0)
    new_text = f'{prefix}{new_ids}]'
    return registry_text.replace(old_text, new_text, 1)


def add_new_family(registry_text: str, family_name: str, new_id: str) -> str:
    """Add a new family entry to the persona_families section."""
    # Find the last family entry (the line before the separator)
    # We look for the last ids: [...] line in persona_families
    pattern = re.compile(r'(    ids: \[[^\]]*\]\n)(\n# ====)', re.MULTILINE)
    m = pattern.search(registry_text)
    if m:
        insert_point = m.start(2)
        new_family = f'  - name: "{family_name}"\n    ids: ["{new_id}"]\n'
        return registry_text[:insert_point] + new_family + registry_text[insert_point:]

    # Fallback: find persona_families block end
    raise ValueError("Could not locate end of persona_families section to add new family")


# ---------------------------------------------------------------------------
# Meta-orchestrator routing table
# ---------------------------------------------------------------------------

def append_routing_table_row(persona_id: str, name: str, domain_brief: str, family: str) -> None:
    """Append a row to the routing table in meta-orchestrator.md."""
    content = ORCHESTRATOR_PATH.read_text(encoding='utf-8')

    # Find the last persona row in the table
    last_row_pattern = re.compile(r'(\| \*\*persona-\d{3}\*\* \|[^\n]+\n)', re.MULTILINE)
    matches = list(last_row_pattern.finditer(content))
    if not matches:
        print("  WARNING: Could not find routing table in meta-orchestrator.md — skipping.")
        return

    last_match = matches[-1]
    insert_pos = last_match.end()

    # Build the new row
    new_row = f'| **{persona_id}** | {name} | {domain_brief} | {family} |\n'

    content = content[:insert_pos] + new_row + content[insert_pos:]
    ORCHESTRATOR_PATH.write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# Adapter reference table updates
# ---------------------------------------------------------------------------

def update_adapter_tables(
    persona_id: str,
    name: str,
    family: str,
    domain_scope: list[str],
    short_name: str | None = None,
) -> None:
    """Append a row to the reference tables in all 3 adapter .md files.

    Also increments the "All N personas" count text in each file.
    """
    kebab = to_kebab_case(name)
    if not short_name:
        short_name = name

    # Knowledge/context hint from domain scope
    if domain_scope:
        knowledge_hint = ", ".join(
            item.lower().split("(")[0].strip().replace(" ", "-")
            for item in domain_scope[:2]
        )
    else:
        knowledge_hint = family.lower().replace(" & ", "-").replace(" ", "-")

    adapter_rows = {
        "claude-code": f'| {persona_id} | {name} | `{kebab}` | `/{kebab}` |',
        "chatgpt": f'| {persona_id} | {name} | {short_name} | {knowledge_hint} |',
        "gemini": f'| {persona_id} | {name} | {short_name} | {knowledge_hint} |',
    }

    for adapter_key, adapter_path in ADAPTER_FILES.items():
        if not adapter_path.exists():
            print(f"  WARNING: Adapter file not found: {adapter_path}")
            continue

        content = adapter_path.read_text(encoding='utf-8')
        row = adapter_rows[adapter_key]

        # Find the last persona row in the table
        last_row_pattern = re.compile(r'(\| persona-\d{3} \|[^\n]+\n)', re.MULTILINE)
        matches = list(last_row_pattern.finditer(content))
        if not matches:
            print(f"  WARNING: No persona rows found in {adapter_path.name}")
            continue

        insert_pos = matches[-1].end()
        content = content[:insert_pos] + row + '\n' + content[insert_pos:]

        # Increment persona count in "All N persona" / "all N personas" text
        def _increment_count(m: re.Match) -> str:
            old_num = int(m.group(1))
            return m.group(0).replace(str(old_num), str(old_num + 1))

        content = re.sub(
            r'(?:All |all |copy all )(\d+) [Pp]ersona',
            _increment_count,
            content,
        )

        adapter_path.write_text(content, encoding='utf-8')
        print(f"  + Updated {adapter_path.name}")


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


def prompt_family(families: list[dict]) -> tuple[str, bool]:
    """Prompt user to select a persona family. Returns (family_name, is_new)."""
    print("\nWhich family?")
    for i, fam in enumerate(families, 1):
        count = len(fam.get('ids', []))
        print(f"  [{i}] {fam['name']} ({count} personas)")
    print(f"  [{len(families) + 1}] New family")

    while True:
        choice = input("> ").strip()
        if not choice.isdigit():
            print("  Please enter a number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(families):
            return families[idx - 1]['name'], False
        elif idx == len(families) + 1:
            new_name = input("  Enter new family name: ").strip()
            if new_name:
                return new_name, True
            print("  Family name cannot be empty.")
        else:
            print(f"  Please enter 1-{len(families) + 1}.")


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
    # Interactive: family, tags, voice
    # ------------------------------------------------------------------
    families = get_families(registry_data)
    family_name, is_new_family = prompt_family(families)

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
    auto_tags = extract_tags_auto(name, domain_scope, family_name)
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

    # Update persona_families
    if is_new_family:
        registry_text = add_new_family(registry_text, family_name, persona_id)
    else:
        registry_text = update_persona_families(registry_text, family_name, persona_id)

    # Write registry
    REGISTRY_PATH.write_text(registry_text, encoding='utf-8')
    print(f"  + Appended registry entry ({persona_id})")
    print(f"  + Updated total_personas: {old_count} -> {new_count}")
    print(f"  + Updated persona_families: {family_name}")

    # 3. Append routing table row
    domain_brief = '; '.join(domain_scope[:3]) if domain_scope else name
    pipeline_membership = f"{family_name} / Standalone"
    append_routing_table_row(persona_id, name, domain_brief, pipeline_membership)
    print(f"  + Appended routing table row in meta-orchestrator.md")

    # 4. Update adapter reference tables
    update_adapter_tables(persona_id, name, family_name, domain_scope)

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print(f"\nDone. Run 'python tools/validate_registry.py' to verify.")

    # Remind about Claude.ai project drift
    manifest_path = REPO_ROOT / "exports" / "claude-project" / "export-manifest.json"
    if manifest_path.exists():
        print("\n  NOTE: Claude.ai project knowledge file is now stale.")
        print("  Run: python tools/export_claude_project.py")

    return 0


if __name__ == '__main__':
    sys.exit(main())
