"""
Core Template Engine using Python 3.14 Native Tag Strings.
Advanced Logic: Structure-Aware Dedent & XML Safety.
"""
import html
import textwrap
from typing import Any

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

def escape_value(value: Any) -> str:
    """Centralized escaping logic."""
    raw_value = str(value)
    safe_value = html.escape(raw_value, quote=False)
    if "</" in safe_value:
        safe_value = safe_value.replace("</", "&lt;/")
    return safe_value

def xml(template: Any) -> str:
    """
    [Python 3.14 Native Tag] Structure-Aware XML Generator.
    """
    # If passed a plain string by mistake, just return it
    if isinstance(template, str):
        return textwrap.dedent(template).strip()

    static_parts = [p for p in template if isinstance(p, str)]
    common_indent = _get_common_indent(static_parts)
    
    result = []
    for part in template:
        if isinstance(part, str):
            lines = part.splitlines(keepends=True)
            dedented_lines = [_dedent_line(line, common_indent) for line in lines]
            result.append("".join(dedented_lines))
        else:
            result.append(escape_value(part.value))
            
    return "".join(result).strip()

def dedent(template: Any) -> str:
    """
    [Fix] Helper for plain text dedent that handles t-strings correctly.
    """
    # 1. If it's already a string, just dedent
    if isinstance(template, str):
        return textwrap.dedent(template).strip()

    # 2. If it's a Template object (iterable), join parts first
    parts = []
    for part in template:
        if isinstance(part, str):
            parts.append(part)
        else:
            # Plain dedent does NOT escape XML, just stringifies
            parts.append(str(part.value))
            
    full_text = "".join(parts)
    return textwrap.dedent(full_text).strip()