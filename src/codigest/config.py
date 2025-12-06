"""
Configuration constants for codigest.
"""

ARTIFACT_DIR_NAME = ".codigest"
SNAPSHOT_FILENAME = "snapshot.txt"
DIFF_FILENAME = "changes.diff"

# File Extension Filters
TARGET_EXTENSIONS: set[str] = {
    # Python
    ".py", ".pyi",
    # Web / JS
    ".ts", ".tsx", ".js", ".jsx", ".json",
    ".css", ".scss", ".html",
    # Config / Docs
    ".md", ".yaml", ".yml", ".toml", ".xml",
    ".gitignore", ".dockerignore", "Dockerfile"
}

# Default Ignore Patterns
DEFAULT_IGNORE_PATTERNS: list[str] = [
    ".git/",
    f"{ARTIFACT_DIR_NAME}/",  # Ignore our own output folder
    ".venv/", "venv/", "env/",
    "__pycache__/",
    "node_modules/",
    "dist/", "build/", "wheels/",
    ".idea/", ".vscode/", ".mypy_cache/",
    "*.pyc", "*.DS_Store", "*.egg-info"
]