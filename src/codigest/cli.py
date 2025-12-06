import argparse
import sys
from pathlib import Path
from .actions import DigestActions
from .interactive import InteractiveShell

def main():
    parser = argparse.ArgumentParser(description="Codigest: Professional Context Generator")
    parser.add_argument("path", nargs="?", help="Target path (file or dir)")
    parser.add_argument("-d", "--diff", action="store_true", help="Capture git diff only")
    
    args = parser.parse_args()

    # Path Resolution Logic
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
            content, saved_path = actions.diff_and_save()
            label = "Diff"
        else:
            print(f"⚡ Scanning {root.name}...")
            content, saved_path = actions.scan_and_save(initial_targets)
            label = "Snapshot"

        if content.startswith("❌") or content.startswith("✨"):
            print(content)
        else:
            print(f"\n✅ {label} generated successfully!")
            print(f"   📂 Location: {saved_path.relative_to(root)}")
            print(f"   📋 Clipboard: Copied ({len(content)} chars)")
            
    else:
        shell = InteractiveShell(root)
        shell.start()

if __name__ == "__main__":
    main()