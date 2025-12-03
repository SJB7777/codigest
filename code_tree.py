from pathlib import Path
from typing import Set, Optional, List

# Check for pathspec
try:
    import pathspec
except ImportError:
    # Fallback if pathspec is missing (optional, but safer for LLM agents)
    pathspec = None

# Default Ignore Lists (Optimized for React/Python)
DEFAULT_IGNORE_DIRS = {
    # Node.js / React
    "node_modules", ".next", "build", "dist", "coverage", ".git", ".yarn",
    # Python
    "__pycache__", ".venv", "venv", "env", ".pytest_cache", ".mypy_cache", 
    # IDE / Misc
    ".idea", ".vscode", ".DS_Store"
}

DEFAULT_IGNORE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    ".DS_Store", "Thumbs.db", "*.pyc"
}

class LLMContextTreeGenerator:
    def __init__(
        self, 
        root_dir: Path | str, 
        use_gitignore: bool = True,
        extra_ignore_dirs: Optional[Set[str]] = None,
        extra_ignore_files: Optional[Set[str]] = None,
        max_depth: Optional[int] = None
    ):
        self.root_path = Path(root_dir).resolve()
        self.use_gitignore = use_gitignore
        self.max_depth = max_depth
        
        self.ignore_dirs = DEFAULT_IGNORE_DIRS.copy()
        if extra_ignore_dirs:
            self.ignore_dirs.update(extra_ignore_dirs)
            
        self.ignore_files = DEFAULT_IGNORE_FILES.copy()
        if extra_ignore_files:
            self.ignore_files.update(extra_ignore_files)

        self.gitignore_spec = self._load_gitignore() if use_gitignore and pathspec else None

    def _load_gitignore(self) -> Optional['pathspec.PathSpec']:
        gitignore_path = self.root_path / ".gitignore"
        if not gitignore_path.exists():
            return None
        try:
            with gitignore_path.open('r', encoding='utf-8') as f:
                patterns = f.read().splitlines()
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        except Exception:
            return None

    def _should_ignore(self, path: Path) -> bool:
        # Fast name check first
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
        if path.is_file() and path.name in self.ignore_files:
            return True

        # Gitignore check
        if self.gitignore_spec:
            try:
                # Get relative path for gitignore matching
                rel_path = path.relative_to(self.root_path).as_posix()
                if path.is_dir():
                    rel_path += "/"
                if self.gitignore_spec.match_file(rel_path):
                    return True
            except ValueError:
                pass
        return False

    def generate_text_structure(self, current_path: Optional[Path] = None, depth: int = 0) -> List[str]:
        """
        Generates a plain text list of paths suitable for LLM system prompts.
        Format:
        root/
          subdir/
            file.txt
        """
        if current_path is None:
            current_path = self.root_path
            # Start with root name
            lines = [f"{current_path.name}/"]
        else:
            lines = []

        if self.max_depth is not None and depth >= self.max_depth:
            return lines

        try:
            # Sort: Directories first, then files
            items = sorted(list(current_path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return lines

        filtered_items = [p for p in items if not self._should_ignore(p)]

        for item in filtered_items:
            indent = "  " * (depth + 1)
            if item.is_dir():
                lines.append(f"{indent}{item.name}/")
                lines.extend(self.generate_text_structure(item, depth + 1))
            else:
                lines.append(f"{indent}{item.name}")
        
        return lines

def get_project_structure(path: Path | str, max_depth: int = 10, ignore_dirs: Set[str] = None) -> str:
    """
    Returns a string representation of the project structure.
    """
    generator = LLMContextTreeGenerator(
        root_dir=path,
        max_depth=max_depth,
        extra_ignore_dirs=ignore_dirs
    )
    # Join lines with newlines
    structure_lines = generator.generate_text_structure()
    return "\n".join(structure_lines)

if __name__ == "__main__":
    # Example usage
    project_path = Path(r"D:\02_Projects\Dev\Web\reflX-monorepo\apps")
    
    # Generate the strict text structure
    structure = get_project_structure(project_path, max_depth=5, ignore_dirs={"tests", "docs", "public"})
    
    # Print to stdout (can be piped to a file or clipboard)
    print(structure)
