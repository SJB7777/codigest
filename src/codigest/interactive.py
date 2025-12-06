import sys
import os
import shlex
import subprocess
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import NestedCompleter, PathCompleter
from prompt_toolkit.styles import Style

from .actions import DigestActions
from .config_manager import ConfigManager
from .git_ops import is_git_repo

class InteractiveShell:
    def __init__(self, initial_path: Path):
        self.config_manager = ConfigManager()
        self.root_path = initial_path.resolve()

        try:
            os.chdir(self.root_path)
        except OSError:
            pass

        self.actions = DigestActions(self.root_path)
        self.config_manager.set_last_project_root(str(self.root_path))

        self.history = InMemoryHistory()

        self.completer = NestedCompleter.from_nested_dict({
            'cd': PathCompleter(only_directories=True),
            'ls': None,
            'dir': None,
            'history': None,
            'pwd': None,
            'scan': PathCompleter(),
            'diff': None,
            'exit': None,
            'quit': None,
            'help': None,
            'clear': None,
        })
        
        self.session = PromptSession(
            completer=self.completer,
            history=self.history
        )

    def start(self):
        print("\n🚀 Codigest Shell")
        print(f"📂 Project: {self.root_path}")
        print("💡 Type 'help' for commands. Use '!' for system commands (PowerShell).\n")

        while True:
            try:
                style = Style.from_dict({
                    'path': 'ansicyan bold',
                    'arrow': '#ff0066 bold',
                })

                message = [
                    ('class:path', f"({self.root_path.name}) "),
                    ('class:arrow', "> "),
                ]
                
                cmd_input = self.session.prompt(message, style=style).strip()
                
                if not cmd_input:
                    continue

                if cmd_input.startswith("!"):
                    self._run_system_command(cmd_input[1:])
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
                    
                    case 'clear' | 'cls':
                        print("\033[H\033[J", end="")

                    case 'help' | 'h' | '?':
                        self._show_help()

                    case 'pwd':
                        print(f"{self.root_path}")

                    case 'ls' | 'dir':
                        self._do_ls(args)

                    case 'history':
                        self._do_history()

                    case 'cd':
                        self._do_cd(args)

                    case 'scan':
                        self._do_scan(args)

                    case 'diff':
                        self._do_diff()

                    case _:
                        print(f"❓ Unknown command: {cmd}")

            except KeyboardInterrupt:
                continue
            except EOFError:
                print("\n👋 Bye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error: {e}")

    def _run_system_command(self, command: str):
        """!로 시작하는 명령어: Windows면 PowerShell, 그 외엔 기본 Shell"""
        try:
            if os.name == 'nt':
                subprocess.run(["powershell", "-Command", command], cwd=self.root_path)
            else:
                subprocess.run(command, shell=True, cwd=self.root_path)
        except Exception as e:
            print(f"❌ Execution failed: {e}")

    def _show_help(self):
        print(" Internal Commands:")
        print("  ls / dir        : List directory contents")
        print("  cd <path>       : Change directory")
        print("  pwd             : Print working directory")
        print("  history         : Show command history")
        print("  scan [path]     : Scan project")
        print("  diff            : Copy git diff")
        print("  exit            : Quit")
        print("\n System Commands:")
        print("  !cmd            : Run command in PowerShell (Windows) or Bash (Mac/Linux)")

    def _do_cd(self, args):
        if not args:
            print(f"{self.root_path}")
            return
        
        target = args[0]
        try:
            expanded_path = Path(target).expanduser()
            new_path = (self.root_path / expanded_path).resolve()
        except Exception as e:
            print(f"❌ Invalid path syntax: {e}")
            return
        
        if new_path.exists() and new_path.is_dir():
            self.root_path = new_path
            # Actions 객체도 새 경로로 재생성
            self.actions = DigestActions(self.root_path) 
            self.config_manager.set_last_project_root(str(new_path))

            try:
                os.chdir(self.root_path)
            except Exception as e:
                print(f"⚠️ Failed to change system CWD: {e}")
        else:
            print(f"The system cannot find the path specified: {target}")

    def _do_ls(self, args):
        extra_args = " " + " ".join(args) if args else ""
        if os.name == 'nt':
            os.system('dir' + extra_args)
        else:
            os.system('ls --color=auto' + extra_args)

    def _do_history(self):
        history_list = self.history.get_strings()
        for i, cmd in enumerate(history_list):
            print(f"{i + 1}: {cmd}")

    def _do_scan(self, args):
        print("⏳ Scanning...", end="\r")
        target_paths = [ (self.root_path / a).resolve() for a in args ] if args else None
        
        # [수정됨] scan -> scan_and_save (반환값: content, path)
        content, saved_path = self.actions.scan_and_save(target_paths)
        self._handle_result(content, saved_path, "Snapshot")

    def _do_diff(self):
        if not is_git_repo(self.root_path):
            print("❌ Not a git repo.")
            return
        
        print("🔍 Checking diff...", end="\r")
        # [수정됨] diff -> diff_and_save (반환값: content, path)
        content, saved_path = self.actions.diff_and_save()
        self._handle_result(content, saved_path, "Git Diff")

    def _handle_result(self, content: str, saved_path: Path, label: str):
        """결과 처리 공통 로직 (저장은 이미 완료된 상태)"""
        # 에러 메시지나 상태 메시지(✨, ❌)인 경우 경로가 비어있음
        if str(saved_path) == ".": 
            print(content)
            return

        # 성공 시 출력
        if content.startswith("❌"):
            print(content)
            return

        try:
            rel_path = saved_path.relative_to(self.root_path)
        except ValueError:
            rel_path = saved_path

        print(f"✅ {label} saved to: ./{rel_path}    ", end="")

        print(f"\n📋 Copied to clipboard! ({len(content)} chars)")
