import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

DEFAULT_CONFIG = """# Codigest Configuration File
[project]
description = "Auto-generated context configuration"

[filter]
max_file_size_kb = 100 
extensions = [
    ".py", ".pyi",
    ".ts", ".tsx", ".js", ".jsx",
    ".json", ".html", ".css",
    ".md", ".toml", ".yaml", ".yml", ".xml"
]
exclude_patterns = [
    "*.lock",
    "dist/",
    "build/",
    "node_modules/",
    "__pycache__/"
]

[output]
format = "xml"
structure = "toon"
"""

@app.callback(invoke_without_command=True)
def handle(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """
    Initialize the .codigest environment.
    """
    root_path = Path.cwd()
    config_dir = root_path / ".codigest"
    config_file = config_dir / "config.toml"
    gitignore_file = root_path / ".gitignore"

    console.print(Panel(f"[bold blue]Initializing Codigest[/bold blue]\n📂 Location: {root_path}", expand=False))

    if not config_dir.exists():
        config_dir.mkdir()
        console.print("  [green]✔[/green] Created [bold].codigest/[/bold] directory")
    
    if not config_file.exists() or force:
        config_file.write_text(DEFAULT_CONFIG, encoding="utf-8")
        console.print("  [green]✔[/green] Created [bold]config.toml[/bold]")
    else:
        console.print("  [yellow]![/yellow] Config exists. Use --force to overwrite.")

    _update_gitignore(gitignore_file)
    console.print("\n[bold green]✨ Ready to digest![/bold green] Try running: [cyan]codigest digest[/cyan]")

def _update_gitignore(path: Path):
    entry = ".codigest/"
    if not path.exists():
        path.write_text(f"# Git Ignore\n{entry}\n", encoding="utf-8")
        return
    
    if entry not in path.read_text(encoding="utf-8"):
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n{entry}\n")
        console.print("  [green]✔[/green] Added [bold].codigest/[/bold] to .gitignore")