"""
Context Anchor Engine.
"""
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Set
from loguru import logger

class ContextAnchor:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.anchor_dir = root_path / ".codigest" / "anchor"
        self.git_dir = self.anchor_dir / ".git"

    def has_history(self) -> bool:
        """Checks if a valid anchor (git repo with commits) exists."""
        return self.git_dir.exists() and (self.anchor_dir / ".git" / "HEAD").exists()

    def _run_git(self, args: list[str], cwd: Path = None, check=True) -> str:
        target_dir = cwd or self.anchor_dir
        cmd = ["git"] + args
        result = subprocess.run(
            cmd, cwd=target_dir, capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if check and result.returncode != 0:
            logger.debug(f"Shadow Git Warning: {result.stderr}")
        return (result.stdout or "").strip()

    def update(self, source_files: List[Path]):
        if not self.git_dir.exists():
            self.anchor_dir.mkdir(parents=True, exist_ok=True)
            self._run_git(["init"])
            self._run_git(["config", "user.email", "codigest@ai"])
            self._run_git(["config", "user.name", "Context Manager"])
            self._run_git(["config", "core.autocrlf", "false"])
            self._run_git(["config", "gc.auto", "0"])

        for item in self.anchor_dir.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        for src in source_files:
            if ".git" in src.parts:
                continue
            try:
                rel = src.relative_to(self.root)
                dest = self.anchor_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            except Exception:
                continue

        self._run_git(["add", "."])
        if self._run_git(["status", "--porcelain"]):
            self._run_git(["commit", "-m", f"Snapshot: {int(time.time())}"])
            logger.info("Context anchor updated.")

    def get_changes(self, current_files: List[Path]) -> str:
        if not self.git_dir.exists():
            return ""

        temp_current = self.root / ".codigest" / "temp_diff_current"
        temp_baseline = self.root / ".codigest" / "temp_diff_baseline"
        
        for d in [temp_current, temp_baseline]:
            if d.exists(): shutil.rmtree(d)
            d.mkdir(parents=True)

        try:
            current_rel_paths = set()
            for src in current_files:
                if ".git" in src.parts:
                    continue
                try:
                    rel = src.relative_to(self.root)
                    current_rel_paths.add(rel)
                    dest = temp_current / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                except Exception:
                    continue

            subprocess.run(
                ["git", "--git-dir", str(self.git_dir), "--work-tree", str(temp_baseline), "checkout", "HEAD", "--", "."],
                capture_output=True, check=False
            )

            self._prune_ignored_files(temp_baseline, current_rel_paths)

            result = subprocess.run(
                ["git", "diff", "--no-index", "--no-prefix", "temp_diff_baseline", "temp_diff_current"],
                cwd=self.root / ".codigest",
                capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            
            diff_text = (result.stdout or "")
            diff_text = diff_text.replace("temp_diff_baseline/", "").replace("temp_diff_current/", "")
            return diff_text

        finally:
            for d in [temp_current, temp_baseline]:
                if d.exists():
                    shutil.rmtree(d)

    def _prune_ignored_files(self, baseline_dir: Path, valid_rel_paths: Set[Path]):
        for file_path in baseline_dir.rglob("*"):
            if file_path.is_file() and ".git" not in file_path.parts:
                try:
                    rel_path = file_path.relative_to(baseline_dir)
                    if rel_path in valid_rel_paths:
                        continue
                    
                    real_file = self.root / rel_path
                    if real_file.exists():
                        file_path.unlink()
                except Exception:
                    continue

    def get_last_update_time(self) -> str:
        if not self.git_dir.exists():
            return "Never"
        try:
            return self._run_git(["log", "-1", "--format=%cr"])
        except:
            return "Unknown"
