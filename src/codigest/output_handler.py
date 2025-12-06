"""
Handles file I/O, directory management, and system integration (clipboard, gitignore).
"""
import pyperclip
import json
from pathlib import Path
from typing import Optional, Dict

from .config import ARTIFACT_DIR_NAME, CONFIG_FILENAME

class ArtifactManager:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.artifact_dir = self.root_path / ARTIFACT_DIR_NAME
        self.config_file = self.artifact_dir / CONFIG_FILENAME

    def _ensure_gitignore(self):
        """
        Safely appends .codigest/ to .gitignore if it exists and is missing the entry.
        """
        gitignore_path = self.root_path / ".gitignore"
        ignore_entry = f"{ARTIFACT_DIR_NAME}/"
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                if ignore_entry not in content:
                    with gitignore_path.open("a", encoding="utf-8") as f:
                        prefix = "\n" if content and not content.endswith("\n") else ""
                        f.write(f"{prefix}# Added by codigest\n{ignore_entry}\n")
            else:
                gitignore_path.write_text(f"# Added by codigest\n{ignore_entry}\n", encoding="utf-8")
        except Exception:
            # Non-blocking: fail silently if permissions are an issue
            pass

    def _ensure_artifact_dir(self):
        """Creates the artifact directory and updates .gitignore."""
        if not self.artifact_dir.exists():
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_gitignore()

    def save_file(self, filename: str, content: str) -> Path:
        """Saves content to a file in the artifact directory."""
        self._ensure_artifact_dir()
        file_path = self.artifact_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def load_config(self) -> Optional[Dict]:
        """Loads user configuration if it exists."""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def save_config(self, data: Dict) -> Path:
        """Saves configuration to config.json."""
        self._ensure_artifact_dir()
        self.config_file.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        return self.config_file

    def copy_to_clipboard(self, content: str) -> bool:
        """Copies content to the system clipboard."""
        try:
            pyperclip.copy(content)
            return True
        except Exception:
            return False