import os
import pathspec


def load_gitignore(directory: str) -> pathspec.PathSpec | None:
    gitignore_path = os.path.join(directory, ".gitignore")
    if not os.path.isfile(gitignore_path):
        return None

    with open(gitignore_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def get_python_files(directory: str) -> list[str]:
    spec = load_gitignore(directory)
    matched_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, start=directory)

            if spec and spec.match_file(rel_path):
                continue

            matched_files.append(full_path)

    return matched_files
