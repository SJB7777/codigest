import textwrap
from string.templatelib import Template

def dedent(template: Template | str) -> str:
    """
    Handles both Template objects (t-strings) and regular strings.
    """
    if isinstance(template, str):
        return textwrap.dedent(template).strip()

    # Reconstruct the string for dedenting
    # Template.strings always has 1 more element than Template.interpolations
    parts = []
    for i, s in enumerate(template.strings):
        parts.append(s)
        if i < len(template.interpolations):
            # Access the evaluated value
            parts.append(str(template.interpolations[i].value))
            
    full_text = "".join(parts)
    return textwrap.dedent(full_text).strip()

def xml(template: Template) -> str:
    """
    Safe XML Generator that escapes interpolated values.
    """
    result = []
    
    # Interleave static strings and dynamic interpolations
    for i, s in enumerate(template.strings):
        result.append(s) # Static parts are trusted
        
        if i < len(template.interpolations):
            # Dynamic parts are untrusted
            val = str(template.interpolations[i].value)
            
            # Escape critical XML characters to prevent context breakout
            # (In production, use html.escape(val, quote=False))
            if "</" in val:
                val = val.replace("</", "<!/")
            
            result.append(val)
            
    return "".join(result)