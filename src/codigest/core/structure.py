from pathlib import Path

def generate_toon(paths: list[Path], root_dir: Path) -> str:
    """(Phase 2: Digest용) TOON 포맷 생성기 (Placeholder)"""
    return "# TOON generation logic here"

def generate_ascii_tree(paths: list[Path], root_dir: Path) -> str:
    """
    [Legacy Style] Generates a standard ASCII directory tree.
    Ref: Ported from original codigest prototype.
    """
    lines = []
    # Set for fast lookup
    path_set = set(paths)
    
    def _walk(current_path: Path, prefix: str = ""):
        try:
            # 현재 디렉토리의 모든 항목 가져오기
            all_items = sorted(current_path.iterdir(), key=lambda x: x.name)
        except PermissionError:
            return

        # 필터링: 스캔된 파일이거나, 스캔된 파일을 포함하는 디렉토리여야 함
        filtered_items = []
        for item in all_items:
            if item.is_file():
                if item in path_set:
                    filtered_items.append(item)
            elif item.is_dir():
                # 디렉토리 안에 유효한 파일이 하나라도 있는지 확인 (Deep Check)
                # 성능 최적화를 위해 문자열 startswith 체크
                item_str = str(item)
                if any(str(p).startswith(item_str) for p in path_set):
                    filtered_items.append(item)

        count = len(filtered_items)
        for i, item in enumerate(filtered_items):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            
            lines.append(f"{prefix}{connector}{item.name}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                _walk(item, prefix + extension)

    _walk(root_dir)
    return "\n".join(lines)