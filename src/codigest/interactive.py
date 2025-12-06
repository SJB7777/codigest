"""
Interactive Shell loop leveraging the Command Registry.
"""
import shlex
import os
import subprocess
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from .actions import DigestActions
from .commands import registry
from . import handlers  # noqa: F401
class InteractiveShell:
    def __init__(self, initial_path: Path):
        self.root_path = initial_path.resolve()
        self._update_cwd()
        self.session = PromptSession()

    def _update_cwd(self):
        """Updates internal state when changing directories."""
        try:
            os.chdir(self.root_path)
        except OSError: pass
        # Re-initialize actions for the new root
        self.actions = DigestActions(self.root_path)

    def handle_result(self, content, saved_path, label):
        """Standardized result handler called by command handlers."""
        if str(saved_path) == ".":
            print(content)
            return
        
        try:
            rel = saved_path.relative_to(self.root_path)
        except ValueError:
            rel = saved_path
            
        print(f"✅ {label} saved to: ./{rel}")
        print(f"📋 Copied to clipboard! ({len(content)} chars)")

    def start(self):
        print("\n🚀 Codigest Shell (v2.0 - Python 3.14 Edition)")
        print(f"📂 Project: {self.root_path}")
        print("💡 Type 'help' for commands. Use '!' for system commands.\n")

        style = Style.from_dict({'path': 'ansicyan bold', 'arrow': '#ff0066 bold'})

        while True:
            try:
                # Prompt UI
                msg = [('class:path', f"({self.root_path.name}) "), ('class:arrow', "> ")]
                cmd_input = self.session.prompt(msg, style=style).strip()
                
                if not cmd_input: continue
                
                # System command fallback (e.g., !ls)
                if cmd_input.startswith("!"):
                    subprocess.run(cmd_input[1:], shell=True, cwd=self.root_path)
                    continue

                parts = shlex.split(cmd_input)
                cmd_name = parts[0].lower()
                args = parts[1:]

                # Built-in control commands
                if cmd_name in ['exit', 'quit', 'q']:
                    print("👋 Bye!"); break

                if cmd_name in ['help', 'h', '?']:
                    print(registry.get_help_text()); continue

                # CD Logic (Needs state access, so usually kept in Shell)
                if cmd_name == 'cd':
                    self._do_cd(args); continue

                # Registry Command Execution
                command = registry.get_command(cmd_name)
                if command:
                    try: 
                        command.func(self, args)
                    except Exception as e: 
                        print(f"❌ Command Error: {e}")
                else:
                    print(f"❓ Unknown command: {cmd_name}")

            except (KeyboardInterrupt, EOFError):
                break

    def _do_cd(self, args):
        if not args:
            print(self.root_path)
            return
        try:
            # Expand user (~) and resolve path
            new_path = Path(args[0]).expanduser().resolve()
            if not new_path.is_absolute():
                new_path = (self.root_path / args[0]).resolve()
                
            if new_path.is_dir():
                self.root_path = new_path
                self._update_cwd()
            else:
                print(f"❌ Not a directory: {args[0]}")
        except Exception as e:
            print(f"❌ Error: {e}")