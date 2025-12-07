import typer
import tomllib
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Core modules
from ..core import scanner, structure, tags, prompts, processor

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
):
    """
    [Legacy Mode] Scans the codebase using the PromptEngine.
    Generates a human-readable XML snapshot compatible with LLMs.
    """
    root_path = target.resolve()
    artifact_dir = root_path / ".codigest"
    
    # 0. Ensure artifacts directory
    if not artifact_dir.exists():
        console.print("[yellow]⚠️  .codigest directory missing. Running init...[/yellow]")
        try:
            artifact_dir.mkdir(exist_ok=True)
        except PermissionError:
            console.print(f"[red]❌ Error: Cannot create .codigest at {root_path}[/red]")
            raise typer.Exit(1)

    output_path = artifact_dir / output

    # 1. Initialize Engines
    prompt_engine = prompts.get_engine(root_path)
    
    extensions, extra_ignores = (None, [])
    if not all:
        extensions, extra_ignores = _load_config_filters(root_path)

    # 2. Start Process
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Scanning Project...[/bold blue]"),
        transient=True,
        console=console
    ) as progress:
        
        # Step A: File Discovery
        files = scanner.scan_project(root_path, extensions, extra_ignores)
        
        # Step B: Structure Generation (Legacy ASCII Tree)
        tree_str = structure.generate_ascii_tree(files, root_path)

        # Step C: Content Processing & Packing
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

        # Step D: Final Assembly using Prompt Engine
        try:
            snapshot_content = prompt_engine.render(
                "snapshot",
                project_name=root_path.name,
                tree_structure=tree_str,
                source_code=source_code_blob
            )
        except Exception as e:
            console.print(f"[red]❌ Template Rendering Failed:[/red] {e}")
            raise typer.Exit(1)

    # 3. Save to Disk
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