from pathlib import Path
from typing import List, Optional, Tuple
from .core import ProjectScanner, ScanLimitError
from .git_ops import get_git_diff, is_git_repo
from .prompts import INITIAL_PROMPT_TEMPLATE, UPDATE_PROMPT_TEMPLATE
from .output_handler import ArtifactManager

class DigestActions:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.io = ArtifactManager(self.root_path)

    def scan_and_save(self, target_paths: Optional[List[Path]] = None) -> Tuple[str, Path]:
        """Scans the codebase, generates context, saves to .codigest/snapshot.txt"""
        try:
            scanner = ProjectScanner(self.root_path)
            
            # 1. Generate Tree
            tree_str = scanner.generate_tree()
            
            # 2. Determine Paths
            if target_paths:
                # Optimized for specific targets, but using full scan for safety in this version
                full_scan = scanner.scan()
                paths_to_scan = []
                for p in target_paths:
                    if p.is_dir():
                        paths_to_scan.extend([f for f in full_scan if str(f).startswith(str(p))])
                    else:
                        paths_to_scan.append(p)
                paths_to_scan = sorted(list(set(paths_to_scan)))
            else:
                paths_to_scan = scanner.scan()

            # 3. Read Content
            file_contents = []
            for file_path in paths_to_scan:
                try:
                    rel_path = file_path.relative_to(self.root_path).as_posix()
                    text = file_path.read_text(encoding="utf-8")
                    file_contents.append(f'<file path="{rel_path}">\n{text}\n</file>')
                except Exception: pass

            result = INITIAL_PROMPT_TEMPLATE.format(
                root_name=self.root_path.name,
                tree_structure=tree_str,
                content="\n\n".join(file_contents)
            )

            # Save via ArtifactManager
            saved_path = self.io.save_snapshot(result)
            self.io.copy_to_clipboard(result)
            
            return result, saved_path

        except ScanLimitError as e:
            return f"❌ Safety Stop: {e}", Path("")
        except Exception as e:
            return f"❌ Unexpected Error: {e}", Path("")

    def diff_and_save(self) -> Tuple[str, Path]:
        """Extracts git diff, saves to .codigest/changes.diff"""
        if not is_git_repo(self.root_path):
            return "❌ Error: Not a git repository.", Path("")
        
        diff = get_git_diff(self.root_path)
        if not diff.strip():
            return "✨ Clean working tree (No changes).", Path("")
            
        formatted_diff = UPDATE_PROMPT_TEMPLATE.format(diff_content=diff)
        
        # Save via ArtifactManager
        saved_path = self.io.save_diff(formatted_diff)
        self.io.copy_to_clipboard(formatted_diff)

        return formatted_diff, saved_path