"""
CLI Entry Point. Routes arguments to the Registry or starts the Shell.
"""
import argparse
from pathlib import Path
from .actions import DigestActions
from .interactive import InteractiveShell
from .commands import registry
from . import handlers  # noqa: F401
class CliContext:
    """Minimal context wrapper for CLI execution of commands."""
    def __init__(self, root_path):
        self.root_path = root_path.resolve()
        self.actions = DigestActions(self.root_path)
        
    def handle_result(self, content, saved_path, label):
        if str(saved_path) == ".":
            print(content)
        else:
            print(f"✅ {label} saved to: {saved_path}")
            print("📋 Copied to clipboard!")

def main():
    parser = argparse.ArgumentParser(description="Codigest: Professional Context Generator")
    parser.add_argument("command", nargs="?", help="Command (init, scan, diff) or Path")
    parser.add_argument("-d", "--diff", action="store_true", help="Shortcut for diff")
    
    args, unknown = parser.parse_known_args()
    current_cwd = Path.cwd()

    # 1. Check if argument matches a registered command (e.g., 'codigest init')
    if args.command:
        cmd_info = registry.get_command(args.command)
        if cmd_info:
            ctx = CliContext(current_cwd)
            cmd_info.func(ctx, unknown)
            return

    # 2. Check if argument is a path (e.g., 'codigest src/')
    target_path = current_cwd
    initial_targets = []
    
    if args.command:
        try:
            possible_path = Path(args.command).resolve()
            if possible_path.exists():
                if possible_path.is_file():
                    target_path = possible_path.parent
                    initial_targets = [possible_path]
                else:
                    target_path = possible_path

                # Run headless scan/diff immediately
                ctx = CliContext(target_path)
                if args.diff:
                    registry.get_command("diff").func(ctx, [])
                else:
                    registry.get_command("scan").func(ctx, initial_targets)
                return
        except OSError:
            pass # Not a path, continue to shell

    # 3. No args -> Interactive Shell
    InteractiveShell(current_cwd).start()

if __name__ == "__main__":
    main()