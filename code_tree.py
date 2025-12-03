<<<<<<< HEAD
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
=======
import pathspec
from pathlib import Path
from typing import Union, Set, Optional, List

class ProjectTreePrinter:
    def __init__(
        self,
        root_dir: Union[str, Path] = ".",
        ignore_dirs: Optional[Set[str]] = None,
        ignore_files: Optional[Set[str]] = None,
        max_depth: Optional[int] = None,
        use_gitignore: bool = True
    ):
        self.root_path = Path(root_dir).resolve()
        self.ignore_dirs = ignore_dirs if ignore_dirs else set()
        self.ignore_files = ignore_files if ignore_files else set()
        self.max_depth = max_depth
        self.use_gitignore = use_gitignore
        self.gitignore_spec = self._load_gitignore() if use_gitignore else None

    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """
        .gitignore 파일을 읽어 pathspec 객체로 반환
        """
        gitignore_path = self.root_path / ".gitignore"
        if not gitignore_path.exists():
            return None

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = f.read().splitlines()
            
            # 빈 줄과 주석 제거
            patterns = [p.strip() for p in patterns if p.strip() and not p.startswith('#')]
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        except Exception as e:
            print(f"Warning: Failed to read .gitignore: {e}")
            return None

    def _should_ignore(self, path: Path) -> bool:
        """
        파일/디렉토리가 무시 목록이나 .gitignore에 포함되는지 확인
        """
        # 1. 명시적 이름 확인 (파일명/폴더명 자체)
>>>>>>> b9ebcc1b1eb501c33e93d075a662c23533521a76
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
        if path.is_file() and path.name in self.ignore_files:
            return True

<<<<<<< HEAD
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
=======
        # 2. .gitignore 규칙 확인
        if self.gitignore_spec:
            try:
                # gitignore는 프로젝트 루트 기준 상대 경로로 체크해야 함
                relative_path = path.relative_to(self.root_path)
                path_str = str(relative_path)
                if path.is_dir():
                    path_str += "/" # 디렉토리임을 명시
                
                if self.gitignore_spec.match_file(path_str):
                    return True
            except ValueError:
                # 경로 계산 오류 시 무시하지 않음
                pass
        
        return False

    def print_tree(self):
        """
        트리 출력의 진입점
        """
        if not self.root_path.exists():
            print(f"Error: Directory not found - {self.root_path}")
            return

        print(f"{self.root_path.name}/")
        self._print_recursive(self.root_path, indent="", depth=0)

    def _print_recursive(self, current_dir: Path, indent: str, depth: int):
        """
        내부 재귀 로직
        """
        if self.max_depth is not None and depth >= self.max_depth:
            return

        try:
            # 항목 가져오기 및 정렬 (디렉토리 우선 정렬을 원하면 lambda 수정 가능)
            items = sorted(list(current_dir.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            print(f"{indent}└── [Permission Denied]")
            return

        # 필터링
        filtered_items = [p for p in items if not self._should_ignore(p)]
        count = len(filtered_items)

        for i, path in enumerate(filtered_items):
            is_last = (i == count - 1)
            
            # 나뭇가지 모양 설정
            branch = "└── " if is_last else "├── "
            # 파일/폴더 이름 출력
            suffix = "/" if path.is_dir() else ""
            print(f"{indent}{branch}{path.name}{suffix}")

            # 재귀 호출 (디렉토리인 경우)
            if path.is_dir():
                # 다음 레벨의 들여쓰기 계산
                next_indent = indent + ("    " if is_last else "│   ")
                self._print_recursive(path, next_indent, depth + 1)

# ---------------------------------------------------------
# 사용 예시
# ---------------------------------------------------------
if __name__ == "__main__":
    # raw string(r"...")을 사용하여 윈도우 경로 백슬래시 문제 방지
    target_root = Path(r"D:\Dev\AI\reflecto") 

    # 2. 클래스 인스턴스 생성
    tree_printer = ProjectTreePrinter(
        root_dir=target_root,
        ignore_dirs={".git", ".idea", "__pycache__", ".ruff_cache", "venv", "env"},
        ignore_files={".DS_Store"},
        max_depth=5,
        use_gitignore=True
    )

    # 3. 출력 실행
    print(f"--- Project Tree: {target_root.name} ---")
    tree_printer.print_tree()
>>>>>>> b9ebcc1b1eb501c33e93d075a662c23533521a76
