from pathlib import Path
from typing import List, Optional, Tuple
from .core import ProjectScanner, ScanLimitError
from .git_ops import get_git_diff, is_git_repo
from .prompts import DEFAULT_PROMPTS
from .output_handler import ArtifactManager
from .tags import xml  # Python 3.14 Tag Processor
from .config import SNAPSHOT_FILENAME, DIFF_FILENAME

class DigestActions:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.io = ArtifactManager(self.root_path)
        
        # Load user config or fallback to defaults
        user_config = self.io.load_config()
        self.prompts = user_config.get("prompts", DEFAULT_PROMPTS) if user_config else DEFAULT_PROMPTS

    def scan_and_save(self, target_paths: Optional[List[Path]] = None) -> Tuple[str, Path]:
        """
        Scans the project, generates an XML-structured snapshot, and saves it.
        """
        try:
            scanner = ProjectScanner(self.root_path)
            tree_str = scanner.generate_tree()
            
            # [Fix 2] Restore filtering logic for target_paths
            full_scan = scanner.scan()
            
            if target_paths:
                paths_to_scan = []
                for p in target_paths:
                    if p.is_dir():
                        paths_to_scan.extend([f for f in full_scan if str(f).startswith(str(p))])
                    else:
                        paths_to_scan.append(p)
                paths_to_scan = sorted(list(set(paths_to_scan)))
            else:
                paths_to_scan = full_scan

            file_contents = []
            for file_path in paths_to_scan:
                try:
                    rel_path = file_path.relative_to(self.root_path).as_posix()
                    text = file_path.read_text(encoding="utf-8")
                    
                    # ✅ PEP 750 Proper Usage:
                    # 1. t"..." creates a Template object capturing 'rel_path' and 'text'
                    # 2. xml(...) processes it, escaping 'text' but keeping tags safe
                    block = xml(t"""<file path="{rel_path}">
{text}
</file>""")
                    file_contents.append(block)
                except Exception: pass

            result = self.prompts["snapshot"].format(
                root_name=self.root_path.name,
                tree_structure=tree_str,
                content="\n".join(file_contents)
            )

            saved_path = self.io.save_file(SNAPSHOT_FILENAME, result)
            self.io.copy_to_clipboard(result)
            return result, saved_path

        except ScanLimitError as e:
            return f"❌ Safety Stop: {e}", Path(".")
        except Exception as e:
            return f"❌ Unexpected Error: {e}", Path(".")

    def diff_and_save(self) -> Tuple[str, Path]:
        """
        Extracts git diff, formats it, and saves it.
        """
        if not is_git_repo(self.root_path):
            return "❌ Error: Not a git repository.", Path(".")
        
        diff = get_git_diff(self.root_path)
        if not diff.strip():
            return "✨ Clean working tree (No changes).", Path(".")
            
        formatted_diff = self.prompts["diff"].format(diff_content=diff)
        saved_path = self.io.save_file(DIFF_FILENAME, formatted_diff)
        self.io.copy_to_clipboard(formatted_diff)

        return formatted_diff, saved_path