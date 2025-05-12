from .file_utils import get_python_files


def gather_python_files(directory: str, output_file: str) -> int:
    total_length = 0
    python_files = get_python_files(directory)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for file_path in python_files:
            outfile.write(f"===== {file_path} =====\n")
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    total_length += len(content)
                    outfile.write(content)
                outfile.write("\n\n")
            except Exception as e:
                print(f"[!] Failed to read {file_path}: {e}")

    return total_length
