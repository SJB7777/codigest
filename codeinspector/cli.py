import argparse

from .file_utils import get_python_files
from .analyzer import analyze_complexity, analyze_maintainability, analyze_style
from .report import summarize_analysis
from .gather import gather_python_files
from .profile import profile_function


def run_analysis(directory: str) -> list[dict[str, float]]:
    print("\n[+] Analyzing project...")
    results = []
    for file_path in get_python_files(directory):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            result = {
                "file": file_path,
                "complexity": analyze_complexity(code),
                "maintainability": analyze_maintainability(code),
                "flake8_issues": analyze_style(file_path),
            }
            results.append(result)
        except Exception as e:
            print(f"[!] Skipping {file_path}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze Python project quality.")
    parser.add_argument("directory", help="Target project directory")
    parser.add_argument("--gather", help="Output path to save all source texts")
    parser.add_argument(
        "--profile", action="store_true", help="Save profiling.log during run"
    )
    args = parser.parse_args()

    if args.gather:
        total_len = gather_python_files(args.directory, args.gather)
        print(f"[+] Total characters gathered: {total_len}")

    if args.profile:
        results = profile_function(run_analysis, args.directory)
    else:
        results = run_analysis(args.directory)

    print(summarize_analysis(results))


if __name__ == "__main__":
    main()
