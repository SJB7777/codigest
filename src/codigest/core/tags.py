"""
Core Template Engine using Python 3.14 Native Tag Strings.
Advanced Logic: Structure-Aware Dedent & XML Safety.
"""
import html
import textwrap
from typing import Any, Callable

def _get_common_indent(parts: list[str]) -> int:
    """Calculates minimum indentation from static template parts."""
    min_indent = None
    for part in parts:
        for line in part.splitlines():
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if min_indent is None or indent < min_indent:
                min_indent = indent
    return min_indent or 0

def _dedent_line(line: str, indent: int) -> str:
    """Safely removes indentation from a single line."""
    if len(line.strip()) == 0:
        return ""
    if line.startswith(" " * indent):
        return line[indent:]
    return line.lstrip()

def escape_xml_value(value: Any) -> str:
    """[XML] Escapes characters for XML safety."""
    raw_value = str(value)
    safe_value = html.escape(raw_value, quote=False)
    if "</" in safe_value:
        safe_value = safe_value.replace("</", "&lt;/")
    return safe_value

def no_escape(value: Any) -> str:
    """[Plain] Returns string as-is (for dedent)."""
    return str(value)

def _render_structure_aware(template: Any, escape_fn: Callable[[Any], str]) -> str:
    """
    Core Logic: Dedents based on static structure, then injects processed values.
    """
    # 1. Handle plain strings (f-strings or raw strings)
    if isinstance(template, str):
        return textwrap.dedent(template).strip()

    # 2. Analyze Structure (Static parts only)
    #    Python 3.14 Template object is iterable
    static_parts = [p for p in template if isinstance(p, str)]
    common_indent = _get_common_indent(static_parts)
    
    result = []
    
    # 3. Assemble
    for part in template:
        if isinstance(part, str):
            # Dedent static parts
            lines = part.splitlines(keepends=True)
            dedented_lines = [_dedent_line(line, common_indent) for line in lines]
            result.append("".join(dedented_lines))
        else:
            # Inject dynamic value (using provided escape function)
            # The value is inserted AS-IS relative to the new dedented baseline
            result.append(escape_fn(part.value))
            
    return "".join(result).strip()

def xml(template: Any) -> str:
    """
    [Python 3.14 Native Tag] Structure-Aware XML Generator.
    Escapes values for XML safety.
    """
    return _render_structure_aware(template, escape_xml_value)

def dedent(template: Any) -> str:
    """
    [Python 3.14 Native Tag] Structure-Aware Plain Text Generator.
    Does NOT escape values (good for prompts), but fixes indentation layout.
    """
    return _render_structure_aware(template, no_escape)