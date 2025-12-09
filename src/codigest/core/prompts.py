"""
Prompt Management Module.
Philosophy: Defaults are Code (t-strings), Overrides are Data (TOML).
"""
import tomllib
from pathlib import Path
from typing import Callable
from . import tags

# [Type Definition]
# RenderFunction takes keyword arguments and returns a processed string
RenderFunc = Callable[..., str]

# 1. Defaults as Code (Native t-string)
def _default_snapshot(project_name: str, tree_structure: str, source_code: str) -> str:
    return tags.dedent(t"""
[SYSTEM: CODIGEST - INITIAL CONTEXT]
You are an expert AI developer. I am providing the full context of a project named "{project_name}".
Please digest this structure and code to build your internal mental model.

<project_root>
{project_name}
</project_root>

<project_structure>
{tree_structure}
</project_structure>

<source_code>
{source_code}
</source_code>
    """)

def _default_diff(project_name: str, context_message: str, diff_content: str) -> str:
    return tags.dedent(t"""
        [SYSTEM: CODIGEST - INCREMENTAL UPDATE]
        Here are the latest changes for the project "{project_name}".
        {context_message}.
        
        Focus on these modifications to update your context.

        <git_diff>
        {diff_content}
        </git_diff>
    """)

# Registry update
DEFAULT_RENDERERS: dict[str, RenderFunc] = {
    "snapshot": _default_snapshot,
    "diff": _default_diff,
}

class PromptEngine:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.overrides = self._load_overrides()

    def _load_overrides(self) -> dict[str, str]:
        """Loads raw template strings from .codigest/prompts.toml"""
        prompt_file = self.root_path / ".codigest" / "prompts.toml"
        if not prompt_file.exists():
            return {}
        
        try:
            with open(prompt_file, "rb") as f:
                data = tomllib.load(f)
                return data.get("prompts", {})
        except Exception:
            return {}

    def render(self, key: str, **kwargs) -> str:
        """
        Renders a prompt by key.
        Priority: TOML Override > Default t-string Function
        """
        # 1. Check for TOML Override (String-based)
        if key in self.overrides:
            raw_template = self.overrides[key]
            # [Security] We must manually apply the same safety as tags.xml
            # because we are falling back to .format() for external files.
            safe_kwargs = {
                k: tags.escape_value(v) for k, v in kwargs.items()
            }
            try:
                # TOML templates are standard python format strings
                return raw_template.format(**safe_kwargs)
            except KeyError as e:
                return f"Error rendering template '{key}': Missing argument {e}"

        # 2. Use Default (Code-based t-string)
        if key in DEFAULT_RENDERERS:
            return DEFAULT_RENDERERS[key](**kwargs)

        return f"Error: Prompt template '{key}' not found."

# Singleton-like usage helper
def get_engine(root_path: Path) -> PromptEngine:
    return PromptEngine(root_path)