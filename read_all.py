from pathlib import Path


def read_all(path: Path | str) -> None:
    """
    Reads the entire content of a python project directory file.
    """
    path = Path(path)
    if not path.exists():
        raise ValueError(f"The provided path '{path}' is not a valid path.")

    results: list[str] = []
    for root, dirs, files in path.walk(on_error=print):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        pyfiles = [f for f in files if f.endswith('.py') or f.endswith('.css')]
        for file in pyfiles:
            file_path = Path(root) / file
            results.append(f"'''{file_path}'''")
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
                results.append(content)

    with Path('.\\code.txt').open('w', encoding='utf-8') as f:
        f.write('\n'.join(results))


if __name__ == "__main__":
    project_dir: Path = Path(r"D:\02_Projects\Dev\Web\xrr_ai_fitting")
    read_all(Path(project_dir))
