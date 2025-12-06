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
        
        # 시작할 때 현재 경로를 '저장'은 해둡니다. (나중에 다른 용도로 쓰일 수 있으니)
        # 하지만 시작 시 불러오지는 않습니다.
        self.config_manager.set_last_project_root(str(self.root_path))

    def start(self):
        print("\n🚀 Codigest Shell")
        print(f"📂 Project: {self.root_path}")
        print("💡 Type 'help' for commands.\n")

        while True:
            try:
                # 프롬프트 출력
                cmd_input = input(f"({self.root_path.name}) > ").strip()
                if not cmd_input:
                    continue

                parts = shlex.split(cmd_input)
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ('exit', 'quit', 'q'):
                    print("👋 Bye!")
                    break
                elif cmd in ('clear', 'cls'):
                    print("\033[H\033[J", end="")
                elif cmd == 'help':
                    self._show_help()
                elif cmd == 'cd':
                    self._do_cd(args)
                elif cmd == 'scan':
                    self._do_scan(args)
                elif cmd == 'diff':
                    self._do_diff()
                else:
                    print(f"❓ Unknown command: {cmd}")

            except KeyboardInterrupt:
                # Ctrl+C 입력 시 즉시 종료
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
        
        # 입력받은 경로 처리
        input_path = args[0]
        # '..' 등을 처리하기 위해 resolve() 사용
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
        print("⏳ Scanning...", end="\r")
        # 인자로 들어온 상대 경로들을 절대 경로로 변환
        target_paths = [ (self.root_path / a).resolve() for a in args ] if args else None
        
        result = self.actions.scan(target_paths)
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