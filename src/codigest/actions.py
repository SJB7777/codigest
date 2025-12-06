import pyperclip
from pathlib import Path
from typing import List, Optional
from .core import ProjectScanner, ScanLimitError
from .git_ops import get_git_diff, is_git_repo
from .prompts import INITIAL_PROMPT_TEMPLATE, UPDATE_PROMPT_TEMPLATE

class DigestActions:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()

    def scan(self, target_paths: Optional[List[Path]] = None) -> str:
        """전체 스캔 (안전 장치 포함)"""
        try:
            scanner = ProjectScanner(self.root_path)
            
            # 1. 트리 생성
            tree_str = scanner.generate_tree()
            
            # 2. 파일 스캔 (여기서 제한 걸림)
            file_contents = []
            
            if target_paths:
                # 특정 경로만 스캔할 때는 전체 스캔 대신 효율적으로 처리하거나,
                # 전체 스캔 후 필터링 (구현 편의상 필터링 방식 유지하되, 전체 스캔 시 안전장치 작동)
                scanner.scan()
                paths_to_scan = []
                # ... (필터링 로직) ...
                # (이전 코드와 동일, 생략)
                # 여기서는 간단히 전체 scan() 호출만 보여드림
                pass 
                # 실제 구현부:
                scan_result = scanner.scan() # 여기서 예외 발생 가능
                paths_to_scan = []
                for p in target_paths:
                     if p.is_dir():
                         paths_to_scan.extend([f for f in scan_result if str(f).startswith(str(p))])
                     else:
                         paths_to_scan.append(p)
                paths_to_scan = sorted(list(set(paths_to_scan)))

            else:
                # 전체 스캔
                paths_to_scan = scanner.scan()

            # 3. 내용 읽기
            for file_path in paths_to_scan:
                try:
                    rel_path = file_path.relative_to(self.root_path).as_posix()
                except ValueError:
                    rel_path = file_path.name
                
                try:
                    text = file_path.read_text(encoding="utf-8")
                    file_contents.append(f'<file path="{rel_path}">\n{text}\n</file>')
                except Exception: pass

            return INITIAL_PROMPT_TEMPLATE.format(
                root_name=self.root_path.name,
                tree_structure=tree_str,
                content="\n\n".join(file_contents)
            )

        except ScanLimitError as e:
            return f"❌ Safety Stop: {e}\n   To fix: Add a .gitignore file or scan specific folders."
        except Exception as e:
            return f"❌ Unexpected Error: {e}"

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