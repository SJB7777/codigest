import argparse
import sys
from pathlib import Path
from .actions import DigestActions
from .interactive import InteractiveShell

def main():
    parser = argparse.ArgumentParser(description="Codigest: CLI Code Context Generator")
    parser.add_argument("path", nargs="?", help="Target path (file or dir)")
    parser.add_argument("-d", "--diff", action="store_true", help="Get git diff only")
    
    args = parser.parse_args()

    if args.path:
        target_path = Path(args.path).resolve()
    else:

        target_path = Path.cwd()

    if target_path.is_file():
        root = target_path.parent
        initial_targets = [target_path]
    else:
        root = target_path
        initial_targets = None

    if not root.exists():
        print(f"❌ Path not found: {root}")
        sys.exit(1)

    is_headless = args.diff or (args.path is not None)

    if is_headless:
        actions = DigestActions(root)
        
        if args.diff:
            print(f"⚡ Fetching diff for {root.name}...")
            content = actions.diff()
        else:
            print(f"⚡ Scanning {root.name}...")
            content = actions.scan(initial_targets)

        if content.startswith("❌") or content.startswith("✨"):
            print(content)
        else:
            actions.save_to_file(content)
            if actions.copy_to_clipboard(content):
                print(f"✅ Copied to clipboard ({len(content)} chars)")
            else:
                print(content)
    else:
        shell = InteractiveShell(root)
        shell.start()

if __name__ == "__main__":
    main()