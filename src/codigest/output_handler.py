import pyperclip
from pathlib import Path
from typing import Tuple
from .config import ARTIFACT_DIR_NAME, SNAPSHOT_FILENAME, DIFF_FILENAME

class ArtifactManager:
    """Manages the storage of generated context and diff files."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.artifact_dir = self.root_path / ARTIFACT_DIR_NAME

    def _ensure_gitignore(self):
        """
        Automatically appends the artifact directory to .gitignore
        to prevent generated files from being committed.
        """
        gitignore_path = self.root_path / ".gitignore"
        ignore_entry = f"{ARTIFACT_DIR_NAME}/"
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                
                # Check if our folder is already ignored
                if ignore_entry not in content:
                    with gitignore_path.open("a", encoding="utf-8") as f:
                        # Ensure we start on a new line if the file doesn't end with one
                        prefix = "\n" if content and not content.endswith("\n") else ""
                        f.write(f"{prefix}# Added by codigest\n{ignore_entry}\n")
            else:
                # Create a new .gitignore if it doesn't exist
                gitignore_path.write_text(f"# Added by codigest\n{ignore_entry}\n", encoding="utf-8")
                
        except Exception as e:
            # Non-blocking warning: don't crash if we can't write to .gitignore
            print(f"⚠️ Warning: Could not update .gitignore automatically: {e}")

    def _ensure_artifact_dir(self) -> Path:
        """Ensures the .codigest directory exists and is ignored."""
        if not self.artifact_dir.exists():
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Check gitignore every time we write, just to be safe
        self._ensure_gitignore()
        
        return self.artifact_dir

    def save_snapshot(self, content: str) -> Path:
        """Saves the full codebase context."""
        self._ensure_artifact_dir()
        file_path = self.artifact_dir / SNAPSHOT_FILENAME
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def save_diff(self, content: str) -> Path:
        """Saves the git diff content."""
        self._ensure_artifact_dir()
        file_path = self.artifact_dir / DIFF_FILENAME
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def copy_to_clipboard(self, content: str) -> bool:
        """Copies content to system clipboard safely."""
        try:
            pyperclip.copy(content)
            return True
        except Exception:
            return False

    def get_artifact_paths(self) -> Tuple[Path, Path]:
        """Returns the paths for snapshot and diff files."""
        return (
            self.artifact_dir / SNAPSHOT_FILENAME,
            self.artifact_dir / DIFF_FILENAME
        )