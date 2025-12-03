from pathlib import Path
import sys

# Configuration: File types to include
TARGET_EXTENSIONS: set[str] = {
    ".py", ".pyi",              # Python
    ".ts", ".tsx", ".js", ".jsx", ".json",  # React/JS
    ".css", ".scss",            # Styles
    ".md", ".yaml", ".yml",     # Config/Docs
    ".toml", ".xml", ".html"
}

# Configuration: Directories to strictly ignore
IGNORE_DIRS: set[str] = {
    "node_modules", 
    "__pycache__", 
    ".git", 
    ".venv", "venv", "env",
    "dist", "build", ".next", ".idea", ".vscode",
    "coverage"
}

def generate_tree(root_path: Path) -> str:
    """Generates a visual tree structure string of the project."""
    tree_str = ["# Project Directory Structure", "."]
    
    # Walk creates a generator, but we need sorted order for consistent tree
    # Using a simplified recursive approach for visual tree
    def _add_to_tree(dir_path: Path, prefix: str = ""):
        # Get valid items
        try:
            items = sorted(list(dir_path.iterdir()), key=lambda x: (x.is_file(), x.name))
        except PermissionError:
            return

        # Filter items
        filtered_items = []
        for item in items:
            if item.name.startswith('.'): continue
            if item.is_dir() and item.name in IGNORE_DIRS: continue
            if item.is_file() and item.suffix.lower() not in TARGET_EXTENSIONS: continue
            filtered_items.append(item)

        total = len(filtered_items)
        for i, item in enumerate(filtered_items):
            is_last = (i == total - 1)
            connector = "└── " if is_last else "├── "
            tree_str.append(f"{prefix}{connector}{item.name}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                _add_to_tree(item, prefix + extension)

    _add_to_tree(root_path)
    return "\n".join(tree_str)

def read_all(source_path: Path | str, output_filename: str = "project_context.txt") -> None:
    root_path = Path(source_path)
    if not root_path.exists():
        raise ValueError(f"Path not found: {root_path}")

    output_path = Path.cwd() / output_filename
    print(f"Scanning: {root_path}")
    print(f"Writing to: {output_path}")

    with output_path.open('w', encoding='utf-8') as f_out:
        # 1. Write Context Header (Prompt Engineering)
        f_out.write(f"<project_root>\n{root_path.name}\n</project_root>\n\n")
        
        # 2. Write Directory Tree (The Map)
        print("Generating directory tree...")
        tree_view = generate_tree(root_path)
        f_out.write(f"<project_structure>\n{tree_view}\n</project_structure>\n\n")
        
        f_out.write("<source_code>\n\n")

        # 3. Write File Contents
        # Python 3.12+ walk is great
        for root, dirs, files in root_path.walk(on_error=print):
            # Prune directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
            
            for file_name in sorted(files):
                file_path = root / file_name
                
                if file_path.suffix.lower() in TARGET_EXTENSIONS:
                    # Get path relative to project root for clarity
                    try:
                        rel_path = file_path.relative_to(root_path)
                    except ValueError:
                        rel_path = file_path.name # Fallback

                    # XML-style wrapping is very robust for LLMs
                    header = f'<file path="{rel_path}">'
                    footer = f'</file>'
                    
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        f_out.write(f"{header}\n{content}\n{footer}\n\n")
                    except Exception as e:
                        f_out.write(f"{header}\n[ERROR reading file: {e}]\n{footer}\n\n")

        f_out.write("</source_code>")

    print("Done. formatted for LLM context.")

if __name__ == "__main__":
    # Update this path
    project_dir = Path(r"D:\02_Projects\Dev\Web\reflX-monorepo\invix-ai")
    
    try:
        read_all(project_dir)
    except Exception as e:
        print(f"Execution failed: {e}", file=sys.stderr)