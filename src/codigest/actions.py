import pyperclip
from pathlib import Path
from typing import List, Optional
from .core import ProjectScanner
from .git_ops import get_git_diff, is_git_repo
from .prompts import INITIAL_PROMPT_TEMPLATE, UPDATE_PROMPT_TEMPLATE

class DigestActions:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()

    def scan(self, target_paths: Optional[List[Path]] = None) -> str:
        """
        전체 프로젝트 혹은 특정 경로들을 스캔합니다.
        target_paths가 None이면 전체 스캔.
        """
        scanner = ProjectScanner(self.root_path)
        
        # 트리 구조 생성 (전체 구조를 보여줌)
        tree_str = scanner.generate_tree()
        file_contents = []

        # 스캔 대상 결정
        if target_paths:
            # 특정 파일들만 지정된 경우
            paths_to_scan = []
            for p in target_paths:
                if p.is_dir():
                    # 폴더면 내부 파일 스캔 (ProjectScanner 활용 가능하나 간단히 처리)
                    # 여기서는 간단히 scanner.scan() 결과 중 해당 폴더 아래 있는 것만 필터링
                    paths_to_scan.extend([f for f in scanner.scan() if str(f).startswith(str(p))])
                else:
                    paths_to_scan.append(p)
            # 중복 제거
            paths_to_scan = sorted(list(set(paths_to_scan)))
        else:
            # 전체 스캔
            paths_to_scan = scanner.scan()

        # 파일 읽기
        for file_path in paths_to_scan:
            try:
                rel_path = file_path.relative_to(self.root_path).as_posix()
            except ValueError:
                rel_path = file_path.name
            
            try:
                text = file_path.read_text(encoding="utf-8")
                file_contents.append(f'<file path="{rel_path}">\n{text}\n</file>')
            except Exception:
                pass # 바이너리 등 읽기 실패 무시

        return INITIAL_PROMPT_TEMPLATE.format(
            root_name=self.root_path.name,
            tree_structure=tree_str,
            content="\n\n".join(file_contents)
        )

    def diff(self) -> str:
        """Git Diff 추출"""
        if not is_git_repo(self.root_path):
            return "❌ Error: Not a git repository."
        
        diff = get_git_diff(self.root_path)
        if not diff.strip():
            return "✨ Clean working tree (No changes)."
            
        return UPDATE_PROMPT_TEMPLATE.format(diff_content=diff)

    def copy_to_clipboard(self, content: str) -> bool:
        try:
            pyperclip.copy(content)
            return True
        except Exception:
            return False

    def save_to_file(self, content: str, filename: str = "codigest_context.txt") -> Path:
        out_path = self.root_path / filename
        out_path.write_text(content, encoding="utf-8")
        return out_path