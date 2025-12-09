"""
Entry Point with Global Error Handling
"""
import sys
import typer
from rich.console import Console
from .commands import init, scan, tree, digest, diff

console = Console()

app = typer.Typer(
    name="codigest",
    help="Semantic Context Manager for LLM-assisted Development",
    add_completion=False,
    no_args_is_help=True
)

app.add_typer(init.app, name="init")
app.add_typer(scan.app, name="scan")
app.add_typer(tree.app, name="tree")
app.add_typer(digest.app, name="digest")
app.add_typer(diff.app, name="diff")

def main():
    try:
        app()
    except Exception as e:
        error_msg = str(e)
        console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()