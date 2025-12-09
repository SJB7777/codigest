import typer
import pyperclip
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core import scanner, structure, processor, tags

app = typer.Typer()
console = Console()

@app.command()
def digest(
    token_limit: int = typer.Option(20000, help="Soft token budget limit"),
    copy: bool = typer.Option(True, help="Auto-copy to clipboard"),
    save: bool = typer.Option(False, help="Save to .codigest/digest.xml")
):
    """
    Generates a semantic XML digest with TOON structure for LLMs.
    """
    root_path = Path.cwd()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Digesting codebase...[/bold green]"),
        transient=True
    ) as progress:
        task = progress.add_task("Scanning", total=None)
        
        # 1. Scan Files
        files = scanner.scan_project(root_path) # Assumed implemented
        progress.update(task, description=f"Found {len(files)} files")
        
        # 2. Build Structure (TOON)
        toon_tree = structure.generate_toon(files, root_path)
        
        # 3. Process Content (With Budgeting Logic - MVP simplified)
        file_blocks = []

        for file_path in files:
            # MVP: Skip binary/large files check logic for brevity
            content = processor.read_with_line_numbers(file_path)
            rel_path = file_path.relative_to(root_path).as_posix()
            
            # t-string for File Block
            block = tags.xml(t"""
            <file path="{rel_path}">
            {content}
            </file>
            """)
            
            file_blocks.append(block)
            
        # 4. Final Assembly
        full_digest = tags.xml(t"""
        [SYSTEM: CODIGEST CONTEXT]
        
        <structure format="TOON">
        {toon_tree}
        </structure>
        
        <source_code>
        {"\n".join(file_blocks)}
        </source_code>
        """)

    # Output
    console.print(f"[bold green]✔ Digest Generated![/bold green] ({len(full_digest)} chars)")
    
    if copy:
        pyperclip.copy(full_digest)
        console.print("[dim]📋 Copied to clipboard[/dim]")
        
    if save:
        out_path = root_path / ".codigest" / "digest.xml"
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(full_digest, encoding="utf-8")
        console.print(f"[dim]💾 Saved to {out_path}[/dim]")