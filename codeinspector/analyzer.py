from radon.complexity import cc_visit
from radon.metrics import mi_visit
import subprocess


def analyze_complexity(code: str) -> float:
    results = cc_visit(code)
    return sum(r.complexity for r in results) / len(results) if results else 0


def analyze_maintainability(code: str) -> float:
    return mi_visit(code, multi=True)


def analyze_style(file_path: str) -> int:
    result = subprocess.run(["flake8", file_path], capture_output=True, text=True)
    return len(result.stdout.splitlines()) if result.stdout else 0
