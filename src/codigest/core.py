"""
Core scanning logic.
"""
from pathlib import Path
from typing import List
import pathspec
from .config import DEFAULT_IGNORE_PATTERNS, TARGET_EXTENSIONS, ARTIFACT_DIR_NAME

class ScanLimitError(Exception):
    pass

class ProjectScanner:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.gitignore_spec = self._load_gitignore()

    def _load_gitignore(self) -> pathspec.PathSpec:
        patterns = list(DEFAULT_IGNORE_PATTERNS)
        
        # Explicitly ignore our artifact directory regardless of user config
        if f"{ARTIFACT_DIR_NAME}/" not in patterns:
            patterns.append(f"{ARTIFACT_DIR_NAME}/")
            
        gitignore = self.root_path / ".gitignore"
        if gitignore.exists():
            try:
                with open(gitignore, "r", encoding="utf-8") as f:
                    patterns.extend(f.read().splitlines())
            except Exception: pass
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def is_ignored(self, path: Path) -> bool:
        try:
            rel = path.relative_to(self.root_path).as_posix()
        except ValueError:
            return False
        if path.is_dir():
            rel += "/"
        return self.gitignore_spec.match_file(rel)

    def scan(self, max_files: int = 10000) -> List[Path]:
        valid_files = []
        dirs_stack = [self.root_path]
        
        while dirs_stack:
            if len(valid_files) > max_files:
                raise ScanLimitError(f"Too many files (> {max_files}). Missing .gitignore?")

            try:
                current = dirs_stack.pop()
                items = sorted(current.iterdir(), key=lambda x: x.name)
            except PermissionError: continue

            for item in items:
                if self.is_ignored(item): continue
                
                if item.is_dir():
                    dirs_stack.append(item)
                elif item.is_file():
                    if item.suffix.lower() in TARGET_EXTENSIONS or item.name in {".gitignore", "Dockerfile", "pyproject.toml"}:
                        valid_files.append(item)
        
        return sorted(valid_files)

    def generate_tree(self) -> str:
        lines = []
        def _walk(path, prefix="", depth=0):
            if depth > 10: return
            try: items = sorted(path.iterdir(), key=lambda x: x.name)
            except PermissionError: return
            
            filtered = [i for i in items if not self.is_ignored(i)]
            count = len(filtered)
            if count > 50:
                filtered = filtered[:50]
                lines.append(f"{prefix}└── ... ({count-50} more files)")
            
            for i, item in enumerate(filtered):
                is_last = (i == count - 1)
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{item.name}")
                if item.is_dir():
                    _walk(item, prefix + ("    " if is_last else "│   "), depth + 1)
        
        _walk(self.root_path)
        return "\n".join(lines)