import typer
import tomllib
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core import scanner, structure, tags, prompts, processor, shadow

app = typer.Typer()
console = Console()

def _load_config_filters(root_path: Path):
    """
    Load config filters (extensions, exclude_patterns) from .codigest/config.toml
    """
    config_path = root_path / ".codigest" / "config.toml"
    extensions = None
    exclude_patterns = []
    
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                filters = data.get("filter", {})
                
                ext_list = filters.get("extensions", [])
                if ext_list:
                    extensions = set(ext_list)
                
                exclude_patterns = filters.get("exclude_patterns", [])
        except Exception:
            pass 
            
    return extensions, exclude_patterns

@app.callback(invoke_without_command=True)
def handle(
    target: Path = typer.Argument(Path.cwd(), help="Target directory"),
    output: str = typer.Option("snapshot.xml", help="Output filename inside .codigest/"),
    all: bool = typer.Option(False, "--all", "-a", help="Ignore config filters (scan everything)"),
    message: str = typer.Option("", "--message", "-m", help="Add specific instruction (e.g. 'No old typing')")
):
    """
    [Legacy Mode] Scans the codebase using the PromptEngine.
    Generates a human-readable XML snapshot compatible with LLMs.
    """
    root_path = target.resolve()
    artifact_dir = root_path / ".codigest"
    
    # Ensure artifacts directory
    if not artifact_dir.exists():
        console.print("[yellow]⚠️  .codigest directory missing. Running init...[/yellow]")
        try:
            artifact_dir.mkdir(exist_ok=True)
        except PermissionError:
            console.print(f"[red]❌ Error: Cannot create .codigest at {root_path}[/red]")
            raise typer.Exit(1)

    output_path = artifact_dir / output

    # Initialize Engines
    prompt_engine = prompts.get_engine(root_path)
    anchor = shadow.ContextAnchor(root_path)

    extensions, extra_ignores = (None, [])
    if not all:
        extensions, extra_ignores = _load_config_filters(root_path)

    # Start Process
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Scanning Project...[/bold blue]"),
        transient=True,
        console=console
    ):
        
        # File Discovery
        files = scanner.scan_project(root_path, extensions, extra_ignores)

        if anchor.has_history():
            try:
                diff_content = anchor.get_changes(files)
                if diff_content.strip():
                    pre_diff_path = artifact_dir / "previous_changes.diff"
                    pre_diff_path.write_text(diff_content, encoding="utf-8")
            except Exception:
                pass

        # Structure Generation (Legacy ASCII Tree)
        tree_str = structure.generate_ascii_tree(files, root_path)

        # Content Processing & Packing
        file_blocks = []
        for file_path in files:
            rel_path = file_path.relative_to(root_path).as_posix()
            
            try:
                # Read content without line numbers (Legacy clean style)
                content = processor.read_file_content(file_path, add_line_numbers=False)
                
                # [Structure Safety]
                # tags.xml() uses Structure-Aware Dedent.
                # Indentation here in python code is stripped from the output XML tags,
                # but 'content' preserves its own structure (usually starts at col 0).
                block = tags.xml(t"""
                    <file path="{rel_path}">
                    {content}
                    </file>
                """)
                file_blocks.append(block)
                
            except Exception:
                continue

        source_code_blob = "\n\n".join(file_blocks)

        # Final Assembly using Prompt Engine
        try:
            snapshot_content = prompt_engine.render(
                "snapshot",
                project_name=root_path.name,
                tree_structure=tree_str,
                source_code=source_code_blob,
                instruction=message
            )
        except Exception as e:
            console.print(f"[red]❌ Template Rendering Failed:[/red] {e}")
            raise typer.Exit(1)

    # Report Pre-scan Diff
    if anchor.has_history():
        pre_diff_path = artifact_dir / "previous_changes.diff"
        if pre_diff_path.exists() and pre_diff_path.stat().st_size > 0:
            console.print(f"[dim][i] Changes before this scan saved to: {pre_diff_path.name}[/dim]")

    # Update Context Anchor (Shadow Git)
    # This creates the 'Save Point' for future diffs
    try:
        anchor = shadow.ContextAnchor(root_path)
        anchor.update(files) # Pass the list of filtered files we just scanned
    except Exception as e:
        # Scan should succeed even if shadow update fails, but warn user
        console.print(f"[yellow]⚠️  Warning: Failed to update context anchor: {e}[/yellow]")

    # Save to Disk
    try:
        output_path.write_text(snapshot_content, encoding="utf-8")
        
        # Success Report
        console.print("[bold green]✔ Snapshot Saved![/bold green]")
        console.print(f"  📄 Path: [underline]{output_path}[/underline]")
        console.print(f"  📊 Size: {len(snapshot_content) / 1024:.1f} KB")
        console.print(f"  📂 Files: {len(files)}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Save Failed:[/bold red] {e}")
        raise typer.Exit(1)