"""
Configuration constants for codigest.
"""

# [NEW] Artifact Configuration (이 부분이 누락되었을 가능성이 높음)
ARTIFACT_DIR_NAME = ".codigest"
SNAPSHOT_FILENAME = "snapshot.txt"
DIFF_FILENAME = "changes.diff"
CONFIG_FILENAME = "config.json"

# File Extension Filters
TARGET_EXTENSIONS: set[str] = {
    # Python
    ".py", ".pyi",
    # Web / JS
    ".ts", ".tsx", ".js", ".jsx", ".json",
    ".css", ".scss", ".html",
    # Config / Docs
    ".md", ".yaml", ".yml", ".toml", ".xml",
    ".gitignore", ".dockerignore", "Dockerfile", "Makefile"
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