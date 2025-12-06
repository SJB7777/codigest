import sys
import shlex
from pathlib import Path
from .actions import DigestActions
from .config_manager import ConfigManager
from .git_ops import is_git_repo

class InteractiveShell:
    def __init__(self, initial_path: Path):
        self.config_manager = ConfigManager()
        self.root_path = initial_path
        self.actions = DigestActions(self.root_path)
        self.config_manager.set_last_project_root(str(self.root_path))

    def start(self):
        print("\n🚀 Codigest Shell")
        print(f"📂 Project: {self.root_path}")
        print("💡 Type 'help' for commands.\n")

        while True:
            try:
                cmd_input = input(f"({self.root_path.name}) > ").strip()
                if not cmd_input:
                    continue

                parts = shlex.split(cmd_input)
                if not parts: 
                    continue

                cmd = parts[0].lower()
                args = parts[1:]

                match cmd:
                    case 'exit' | 'quit' | 'q':
                        print("👋 Bye!")
                        break
                    
                    case 'clear' | 'cls':  # 화면 지우기 (보너스)
                        print("\033[H\033[J", end="")

                    case 'help' | 'h' | '?':
                        self._show_help()

                    case 'cd':
                        self._do_cd(args)

                    case 'scan':
                        self._do_scan(args)

                    case 'diff':
                        self._do_diff()

                    case _:
                        print(f"❓ Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\n\n👋 Bye! (Interrupted)")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error: {e}")

    def _show_help(self):
        print(" Commands:")
        print("  scan [path]   : Scan project (or specific file/folder)")
        print("  diff          : Copy git diff")
        print("  cd <path>     : Change project root")
        print("  exit          : Quit")

    def _do_cd(self, args):
        if not args:
            print(f"📂 Current: {self.root_path}")
            return

        input_path = args[0]
        try:
            new_path = (self.root_path / input_path).resolve()
        except Exception as e:
            print(f"❌ Invalid path: {e}")
            return
        
        if new_path.exists() and new_path.is_dir():
            self.root_path = new_path
            self.actions = DigestActions(new_path)
            self.config_manager.set_last_project_root(str(new_path))
            print(f"✅ Changed to: {self.root_path}")
        else:
            print(f"❌ Invalid directory: {new_path}")

    def _do_scan(self, args):
        # [안전 장치 1] .gitignore 체크
        gitignore_path = self.root_path / ".gitignore"
        if not gitignore_path.exists():
            print("⚠️  [Warning] No .gitignore found in root!")
            print("   Scanning might include unnecessary files (node_modules, venv, etc).")
            try:
                confirm = input("   Continue anyway? [y/N] ").lower()
            except KeyboardInterrupt:
                print("\n❌ Cancelled.")
                return
                
            if confirm not in ('y', 'yes'):
                print("❌ Scan cancelled.")
                return

        print("⏳ Scanning...", end="\r")
        target_paths = [ (self.root_path / a).resolve() for a in args ] if args else None
        
        # [안전 장치 2] actions.scan 내부의 ScanLimitError 처리
        result = self.actions.scan(target_paths)
        
        # 에러 메시지인지 확인 (간단한 체크)
        if result.startswith("❌ Safety Stop"):
            print("\n" + result) # 줄바꿈 후 에러 출력
        else:
            self._handle_result(result, "Context")

    def _do_diff(self):
        if not is_git_repo(self.root_path):
            print("❌ Not a git repo.")
            return
        
        print("🔍 Checking diff...", end="\r")
        result = self.actions.diff()
        
        if result.startswith("❌") or result.startswith("✨"):
            print(result)
        else:
            self._handle_result(result, "Git Diff")

    def _handle_result(self, content: str, label: str):
        try:
            saved_path = self.actions.save_to_file(content)
            print(f"💾 Saved: {saved_path.name}   ", end="")
        except Exception as e:
            print(f"⚠️ Save failed: {e}   ", end="")

        if self.actions.copy_to_clipboard(content):
            print(f"📋 Copied {label} to clipboard! ({len(content)} chars)")
        else:
            print("⚠️ Clipboard failed.")