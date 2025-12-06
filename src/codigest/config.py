"""
Configuration constants for codeinspector.
"""

# 파일 확장자 필터 (분석 대상)
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

# 기본적으로 무시할 디렉토리 및 패턴
DEFAULT_IGNORE_PATTERNS: list[str] = [
    ".git/",
    ".venv/", "venv/", "env/",
    "__pycache__/",
    "node_modules/",
    "dist/", "build/", "wheels/",
    ".idea/", ".vscode/", ".mypy_cache/",
    "*.pyc", "*.DS_Store", "*.egg-info"
]