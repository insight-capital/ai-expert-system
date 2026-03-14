#!/usr/bin/env python3
"""
registry_utils.py — Shared extraction and registry manipulation functions
for the AI Persona System tooling.

Used by: add_persona.py, sync_registry.py
"""

import re
from pathlib import Path

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is not installed. Run: pip install pyyaml")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PERSONAS_DIR = REPO_ROOT / "personas"
REGISTRY_PATH = REPO_ROOT / "registry" / "registry.yaml"
ORCHESTRATOR_PATH = REPO_ROOT / "master-expert" / "meta-orchestrator.md"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def to_kebab_case(name: str) -> str:
    """Convert a display name to a kebab-case filename stem."""
    name = re.sub(r'^Expert\s+(?:\w+\s+)?Persona\s*\d*\s*:\s*(?:The\s+)?', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'^Persona\s*\d+\s*:\s*', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'[/&.]+', '-', name)
    name = re.sub(r'[^a-zA-Z0-9-]+', '-', name)
    name = re.sub(r'-{2,}', '-', name)
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
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = ' '.join(sentences[:max_sentences]).strip()
    if len(result) > 300:
        result = result[:297].rsplit(' ', 1)[0] + '...'
    return result


# ---------------------------------------------------------------------------
# File reading helpers
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    """Read a file with UTF-8 encoding."""
    return path.read_text(encoding='utf-8')


def strip_code_fences(content: str) -> str:
    """Strip wrapping code fences from v1-era personas."""
    lines = content.split('\n')
    fence_open_idx = None
    fence_close_idx = None

    for i, line in enumerate(lines[:10]):
        if re.match(r'^```\s*\w*\s*$', line):
            fence_open_idx = i
            break

    if fence_open_idx is None:
        return content

    for i in range(len(lines) - 1, fence_open_idx, -1):
        if re.match(r'^```\s*$', lines[i]):
            fence_close_idx = i
            break

    if fence_close_idx is None or fence_close_idx <= fence_open_idx:
        return content

    result_lines = lines[:fence_open_idx] + lines[fence_open_idx + 1:fence_close_idx] + lines[fence_close_idx + 1:]
    return '\n'.join(result_lines)


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_name(content: str) -> str | None:
    """Extract persona display name from the first heading."""
    m = re.search(r'^#\s+Expert\s+\w+\s+Persona:\s*(?:The\s+)?(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+Expert\s+Persona:\s*(?:The\s+)?(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+Persona\s+\d+:\s*(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        raw = m.group(1).strip()
        raw = re.sub(r'^Expert\s+(?:\w+\s+)?Persona:\s*(?:The\s+)?', '', raw, flags=re.IGNORECASE).strip()
        return raw if raw else m.group(1).strip()
    return None


def extract_role_summary(content: str) -> str | None:
    """Extract role summary from Primary Objective / Primary Goal / Role."""
    patterns = [
        r'###\s*Primary\s+Objective\s*\n+(.+?)(?:\n\n|\n###|\n##)',
        r'###\s*Primary\s+Objective\s*\n+\*\*[^*]+\*\*\s*(.+?)(?:\n\n|\n###|\n##)',
        r'\*\*Primary\s+Goal:\*\*\s*(.+?)(?:\n\n|\n###|\n##|\n\*\*)',
        r'\*\*Role:\*\*\s*(.+?)(?:\n\n|\n###|\n##|\n\*\*)',
        r'Your primary mission is to\s+(.+?)(?:\n\n|\n---)',
    ]
    for pat in patterns:
        m = re.search(pat, content, re.DOTALL)
        if m:
            text = m.group(1).strip()
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\s+', ' ', text)
            return first_sentence(text)
    return None


def extract_cognitive_posture(content: str) -> str | None:
    """Extract cognitive posture name and convert to snake_case."""
    m = re.search(
        r'###?\s*Cognitive\s+Posture\s*\n+\*\*([^.*]+)[.*]',
        content, re.MULTILINE
    )
    if m:
        return to_snake_case(m.group(1).strip())

    m = re.search(
        r'\*\*Cognitive\s+Posture:\*\*\s*([^.]+)\.',
        content
    )
    if m:
        return to_snake_case(m.group(1).strip())

    m = re.search(
        r'###?\s*Cognitive\s+Posture\s*\n+([^#*\n][^\n.]+)\.',
        content, re.MULTILINE
    )
    if m:
        posture_text = m.group(1).strip()
        short = re.split(r'\s+and\s+|\s*[,;]\s*|\.\s+|\s+You\s+', posture_text)[0]
        words = short.split()
        if len(words) > 4:
            short = ' '.join(words[:4])
        return to_snake_case(short)

    return None


def extract_domain_scope(content: str) -> list[str]:
    """Extract domain scope items from Core Domains / Core Competencies section."""
    m = re.search(
        r'###?\s*Core\s+(?:Domains|Competencies|Technical\s+Competencies)\s*\n',
        content, re.MULTILINE
    )
    if not m:
        m = re.search(
            r'\*\*Core\s+(?:Domains|Competencies|Technical\s+Competencies)[^*]*\*\*:?\s*\n',
            content, re.MULTILINE
        )
    if not m:
        return []

    after = content[m.end():]
    section = re.split(r'\n###?\s|\n##\s', after, maxsplit=1)[0]

    items = []
    for line in section.split('\n'):
        line = line.strip()
        if not line.startswith('-'):
            continue
        line = line.lstrip('- ').strip()
        bm = re.match(r'\*\*([^*]+)\*\*', line)
        if bm:
            domain = bm.group(1).strip().rstrip(':').rstrip('.')
            items.append(domain)
        else:
            text = line.split('.')[0].strip() if '. ' in line else line.rstrip('.').strip()
            if text:
                items.append(text)
    return items


def extract_out_of_scope(content: str) -> list[str]:
    """Extract out of scope items."""
    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Out\s+of\s+Scope[^*\n]*(?:\*\*)?\s*\n',
        content, re.MULTILINE | re.IGNORECASE
    )

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
        if line.startswith('-'):
            line = line.lstrip('- ').strip()
        elif is_numbered and re.match(r'^\d+\.\s+', line):
            line = re.sub(r'^\d+\.\s+', '', line).strip()
        else:
            continue
        line = re.sub(r'\s*\(owned\s+by[^)]*\)', '', line, flags=re.IGNORECASE)
        line = re.sub(r'\s*—\s*owned\s+by.*$', '', line, flags=re.IGNORECASE)
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        line = re.sub(r'^(?:You\s+)?(?:do\s+)?NOT?\s+', '', line, flags=re.IGNORECASE)
        line = re.sub(r'^Never\s+', '', line, flags=re.IGNORECASE)
        line = line.split('.')[0].strip() if '. ' in line else line.rstrip('.')
        if line:
            line = line[0].upper() + line[1:] if len(line) > 1 else line.upper()
            items.append(line)
    return items


def extract_input_spec(content: str) -> dict:
    """Extract input specification: accepts list and required_fields."""
    result = {"accepts": [], "required_fields": []}

    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Input\s+Spec(?:ification)?(?:\*\*)?[:\s]*\n',
        content, re.MULTILINE | re.IGNORECASE
    )
    if not m:
        return result

    after = content[m.end():]
    section = re.split(r'\n###?\s|\n##\s|\n\*\*Output', after, maxsplit=1)[0]

    am = re.search(r'\*\*Accepts:\*\*\s*\n?(.*?)(?:\n\*\*|\n\n\*\*|$)', section, re.DOTALL)
    if am:
        accepts_text = am.group(1)
        lines = [l.strip() for l in accepts_text.split('\n') if l.strip()]
        has_bullets = any(l.startswith('- ') for l in lines)
        if has_bullets:
            for line in lines:
                if not line.startswith('- '):
                    continue
                line = line.lstrip('- ').strip()
                backtick_items = re.findall(r'`([^`]+)`', line)
                if backtick_items:
                    result["accepts"].extend(backtick_items)
                else:
                    phrase = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
                    phrase = phrase.split(',')[0].split('(')[0].strip()
                    if phrase and len(phrase) < 80:
                        result["accepts"].append(to_snake_case(phrase))
        else:
            for line in lines:
                for mp in re.finditer(r'(?:a |A )(?:batch of )?([a-z][\w\s]+?)(?:[,.]|\s+(?:each|in |containing))', line):
                    artifact = mp.group(1).strip()
                    if len(artifact) < 60:
                        result["accepts"].append(to_snake_case(artifact))

    if not result["accepts"]:
        rm = re.search(r'\*\*Required:\*\*\s*(.*?)(?:\n\*\*|\n\n|$)', section, re.DOTALL)
        if rm:
            req_text = rm.group(1).strip()
            for part in re.split(r'[,\n]', req_text):
                part = part.strip().lstrip('- ').strip()
                if part:
                    part = re.sub(r'\*\*([^*]+)\*\*', r'\1', part)
                    short = part.split('(')[0].strip().rstrip('.')
                    if short and len(short) < 80:
                        result["accepts"].append(to_snake_case(short))

    if not result["accepts"]:
        for tm in re.finditer(r'\|\s*\*\*([^|*]+)\*\*\s*\|', section):
            artifact = tm.group(1).strip()
            if artifact and artifact.lower() not in ('input artifact', 'field', 'parameter'):
                result["accepts"].append(to_snake_case(artifact))

    if not result["accepts"]:
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                text = line.lstrip('- ').strip()
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
                short = text.split(':')[0].split('(')[0].strip()
                if short and len(short) < 60:
                    result["accepts"].append(to_snake_case(short))

    rm = re.search(
        r'\*\*[Rr]equired[\s_]?fields?:\*\*\s*(.*?)(?:\n\*\*|\n\n|$)',
        section, re.DOTALL
    )
    if rm:
        fields_text = rm.group(1).strip()
        backtick_items = re.findall(r'`([^`]+)`', fields_text)
        if backtick_items:
            result["required_fields"] = backtick_items
        else:
            lines = [l.strip() for l in fields_text.split('\n') if l.strip()]
            if any(l.startswith('- ') for l in lines):
                for line in lines:
                    if line.startswith('- '):
                        part = line.lstrip('- ').strip()
                        if part and len(part) < 60:
                            result["required_fields"].append(to_snake_case(part))
            else:
                both_m = re.search(r'[Bb]oth\s+(?:the\s+)?(.+?)\s+and\s+(.+?)\s+must', fields_text)
                if both_m:
                    result["required_fields"].append(to_snake_case(both_m.group(1).strip()))
                    result["required_fields"].append(to_snake_case(both_m.group(2).strip()))
                else:
                    for part in re.split(r'[,\n]', fields_text):
                        part = part.strip().lstrip('- ').strip()
                        if part and len(part) < 60:
                            result["required_fields"].append(to_snake_case(part))

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

    m = re.search(
        r'(?:###?\s*)?(?:\*\*)?Output\s+Spec(?:ification)?(?:\*\*)?[:\s]*\n',
        content, re.MULTILINE | re.IGNORECASE
    )
    if not m:
        return result

    after = content[m.end():]
    section = re.split(r'\n###?\s|\n##\s|\n---', after, maxsplit=1)[0]

    pm = re.search(r'\*\*Produces:\*\*\s*(.+)', section)
    if pm:
        result["produces"] = to_snake_case(pm.group(1).strip().rstrip('.'))
    else:
        pm = re.search(r'primary\s+output\s+artifact\s+is\s+a?\s*\*\*([^*]+)\*\*', section, re.IGNORECASE)
        if pm:
            result["produces"] = to_snake_case(pm.group(1).strip())

    fm = re.search(r'\*\*(?:Output\s+)?Format:\*\*\s*(.+)', section)
    if fm:
        fmt = fm.group(1).strip().rstrip('.')
        result["format"] = to_snake_case(fmt.split('.')[0])

    fields_m = re.search(r'\*\*Required\s+output\s+fields[^:]*:\*\*\s*\n(.*?)(?:\n\*\*|\n\n\*\*|$)', section, re.DOTALL)
    if fields_m:
        for fm in re.finditer(r'`([^`]+)`', fields_m.group(1)):
            result["fields"].append(fm.group(1))

    if not result["fields"]:
        for tm in re.finditer(r'\|\s*\*\*([^|*]+)\*\*\s*\|', section):
            artifact = tm.group(1).strip()
            if artifact.lower() not in ('output artifact', 'format', 'required fields'):
                result["fields"].append(to_snake_case(artifact))

    if not result["fields"]:
        for nm in re.finditer(r'^\d+\.\s+\*\*([^*]+)\*\*', section, re.MULTILINE):
            result["fields"].append(to_snake_case(nm.group(1).strip()))

    return result


def extract_persona_references(content: str) -> list[str]:
    """Find persona-XXX references in the file content."""
    return sorted(set(re.findall(r'persona-\d{3}', content)))


def extract_tags_auto(name: str, domain_scope: list[str]) -> list[str]:
    """Auto-generate suggested tags from name and domain scope."""
    tags = set()

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
    if any(term in name_lower for term in ['legal', 'compliance', 'regulatory']):
        tags.add('legal')
    if any(term in name_lower for term in ['finance', 'valuation', 'investment']):
        tags.add('finance')
    if any(term in name_lower for term in ['m&a', 'merger', 'acquisition', 'deal']):
        tags.add('m&a')

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


def get_registered_source_files(data: dict) -> set[str]:
    """Get set of all registered source_file paths."""
    return {p.get('source_file', '') for p in data.get('personas', []) if p.get('source_file')}


def build_registry_entry_yaml(metadata: dict) -> str:
    """Build the YAML text for a new persona registry entry."""
    def yaml_quoted_list(items: list) -> str:
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

    def yaml_safe_item(item: str) -> str:
        """Quote a YAML list item if it contains special characters."""
        if any(c in item for c in ':"\'{}[]|>&*!%@`'):
            escaped = item.replace('"', '\\"')
            return f'"{escaped}"'
        return item

    ds_lines = '\n'.join(f'    - {yaml_safe_item(item)}' for item in domain_scope) if domain_scope else '    []'
    oos_lines = '\n'.join(f'    - {yaml_safe_item(item)}' for item in out_of_scope) if out_of_scope else '    []'

    accepts = yaml_quoted_list(input_spec.get('accepts', []))
    required_fields = yaml_quoted_list(input_spec.get('required_fields', []))

    produces = output_spec.get('produces', '')
    fmt = output_spec.get('format', 'structured_markdown')
    fields = yaml_quoted_list(output_spec.get('fields', []))

    works_with = yaml_quoted_list(composability.get('works_with', []))
    position = composability.get('position_in_pipeline', 'standalone')
    known_wf = yaml_quoted_list(composability.get('known_workflows', []))

    tags_str = yaml_quoted_list(tags)

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
    """Insert the new entry before the prompt_templates section."""
    # Try comment-style separator first
    marker = '# ============================================================\n# PROMPT TEMPLATES'
    idx = registry_text.find(marker)
    if idx != -1:
        return registry_text[:idx] + entry_yaml + registry_text[idx:]

    # Try comment without separator line
    marker = '# PROMPT TEMPLATES'
    idx = registry_text.find(marker)
    if idx != -1:
        line_start = registry_text.rfind('\n', 0, idx)
        if line_start != -1:
            prev_line_start = registry_text.rfind('\n', 0, line_start)
            if prev_line_start != -1 and '=====' in registry_text[prev_line_start:line_start]:
                idx = prev_line_start + 1
            else:
                idx = line_start + 1
        return registry_text[:idx] + entry_yaml + registry_text[idx:]

    # Try bare prompt_templates: key (no comment header)
    idx = registry_text.find('\nprompt_templates:')
    if idx != -1:
        # Insert before the newline that precedes prompt_templates:
        return registry_text[:idx] + entry_yaml + registry_text[idx:]

    raise ValueError("Could not find prompt_templates section in registry.yaml")


def update_total_personas(registry_text: str, old_count: int, new_count: int) -> str:
    """Update the total_personas line."""
    old_line = f'total_personas: {old_count}'
    new_line = f'total_personas: {new_count}'
    if old_line not in registry_text:
        raise ValueError(f"Could not find '{old_line}' in registry.yaml")
    return registry_text.replace(old_line, new_line, 1)


def append_routing_table_row(persona_id: str, name: str, domain_brief: str) -> None:
    """Append a row to the routing table in meta-orchestrator.md (3-column)."""
    content = ORCHESTRATOR_PATH.read_text(encoding='utf-8')

    last_row_pattern = re.compile(r'(\| \*\*persona-\d{3}\*\* \|[^\n]+\n)', re.MULTILINE)
    matches = list(last_row_pattern.finditer(content))
    if not matches:
        print("  WARNING: Could not find routing table in meta-orchestrator.md — skipping.")
        return

    last_match = matches[-1]
    insert_pos = last_match.end()

    new_row = f'| **{persona_id}** | {name} | {domain_brief} |\n'

    content = content[:insert_pos] + new_row + content[insert_pos:]
    ORCHESTRATOR_PATH.write_text(content, encoding='utf-8')


def extract_all_metadata(content: str, source_file: str, persona_id: str) -> dict:
    """Extract all metadata from persona content and build a complete metadata dict.

    This is the non-interactive version used by sync_registry.py.
    Uses sensible defaults for any field that can't be extracted.
    """
    content = strip_code_fences(content)

    name = extract_name(content) or Path(source_file).stem.replace('-', ' ').title()
    role_summary = extract_role_summary(content) or ''
    cognitive_posture = extract_cognitive_posture(content) or ''
    domain_scope = extract_domain_scope(content)
    out_of_scope = extract_out_of_scope(content)
    input_spec = extract_input_spec(content)
    output_spec = extract_output_spec(content)
    persona_refs = extract_persona_references(content)
    tags = extract_tags_auto(name, domain_scope)

    composability = {
        "works_with": persona_refs,
        "position_in_pipeline": "standalone",
        "known_workflows": [],
    }

    return {
        'id': persona_id,
        'name': name,
        'source_file': source_file,
        'role_summary': role_summary,
        'cognitive_posture': cognitive_posture,
        'domain_scope': domain_scope,
        'out_of_scope': out_of_scope,
        'input_spec': input_spec,
        'output_spec': output_spec,
        'composability': composability,
        'voice_calibration': 'uses_own_voice',
        'tags': tags,
    }
