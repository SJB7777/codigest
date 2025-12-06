"""
Git operations using subprocess.
"""
import subprocess
from pathlib import Path
from .config import TARGET_EXTENSIONS

def is_git_repo(root_path: Path) -> bool:
    return (root_path / ".git").exists()

def get_git_diff(root_path: Path) -> str:
    """
    Fetches both staged/unstaged diffs and untracked file contents.
    """
    try:
        # 1. Modified/Staged files
        diff_output = subprocess.check_output(
            ["git", "diff", "HEAD"], 
            cwd=root_path, 
            text=True, 
            encoding='utf-8',
            stderr=subprocess.DEVNULL 
        )
        
        # 2. Untracked files
        untracked_files = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root_path,
            text=True,
            encoding='utf-8',
            stderr=subprocess.DEVNULL
        ).splitlines()
        
        full_output = diff_output
        
        if untracked_files:
            new_files_content = ""
            has_new_files = False
            
            for f in untracked_files:
                file_path = root_path / f
                if not file_path.is_file(): continue
                
                # Filter check
                is_valid_ext = file_path.suffix.lower() in TARGET_EXTENSIONS
                is_config_file = file_path.name in {".gitignore", "Dockerfile", "Makefile", "pyproject.toml"}
                
                if not (is_valid_ext or is_config_file): continue

                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Manually construct a diff-like header for untracked files
                    new_files_content += f"diff --git a/{f} b/{f}\n"
                    new_files_content += "new file mode 100644\n"
                    new_files_content += f"--- /dev/null\n+++ b/{f}\n@@ -0,0 +1,{len(content.splitlines())} @@\n{content}\n"
                    has_new_files = True
                except (UnicodeDecodeError, Exception):
                    pass

            if has_new_files:
                full_output += "\n# Untracked (New) Source Files:\n" + new_files_content

        return full_output
    except subprocess.CalledProcessError:
        return "Error: Failed to run git diff."