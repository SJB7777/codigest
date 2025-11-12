import os
from pathlib import Path
import pathspec

def load_gitignore_patterns(root_dir="."):
    """
    .gitignore 파일을 읽어 pathspec 객체로 반환
    """
    gitignore_path = Path(root_dir) / ".gitignore"
    if not gitignore_path.exists():
        return None
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        patterns = f.read().splitlines()
    
    # 빈 줄과 주석 제거
    patterns = [p.strip() for p in patterns if p.strip() and not p.startswith('#')]
    
    # gitwildmatch 포맷으로 spec 생성
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def should_ignore(path, spec, root_dir):
    """
    경로가 .gitignore 규칙에 의해 무시되어야 하는지 확인
    """
    if spec is None:
        return False
    
    # 루트 디렉토리 기준 상대 경로로 변환
    try:
        relative_path = os.path.relpath(path, root_dir)
        if relative_path == '.':
            return False
        # 디렉토리는 뒤에 '/'를 붙여서 gitignore 규칙과 일치시킴
        if path.is_dir():
            relative_path += '/'
        return spec.match_file(relative_path)
    except:
        return False

def print_project_tree(
    root_dir=".",
    ignore_dirs=None,  # 기본값 None으로 변경
    ignore_files=None,
    max_depth=None,
    use_gitignore=True,  # .gitignore 사용 여부
    indent="",
    is_last=True,
    depth=0,
    spec=None  # gitignore spec
):
    """
    파이썬 프로젝트 구조를 트리 형태로 출력 (.gitignore 지원)
    """
    if ignore_dirs is None:
        ignore_dirs = set()
    if ignore_files is None:
        ignore_files = set()
    
    root_path = Path(root_dir)
    
    # 최초 호출시 .gitignore 로드
    if depth == 0 and use_gitignore:
        spec = load_gitignore_patterns(root_dir)
    
    # 최초 호출일 때만 제목 출력
    if depth == 0:
        print(f"{root_path.absolute().name}/")
    
    # 깊이 제한 체크
    if max_depth is not None and depth >= max_depth:
        return
    
    # 디렉토리와 파일 목록 가져오기
    try:
        items = sorted([p for p in root_path.iterdir() 
                       if p.is_dir() or p.is_file()])
    except PermissionError:
        return
    
    # 필터링
    filtered_items = []
    for p in items:
        # 하드코딩된 무시 목록 확인
        if p.is_dir() and p.name in ignore_dirs:
            continue
        if p.is_file() and p.name in ignore_files:
            continue
        
        # .gitignore 규칙 확인
        if use_gitignore and spec and should_ignore(p, spec, root_path.absolute()):
            continue
        
        filtered_items.append(p)
    
    for i, path in enumerate(filtered_items):
        # 마지막 항목인지 체크
        is_last_item = (i == len(filtered_items) - 1)
        
        # 브랜치 기호 설정
        branch = "└── " if is_last_item else "├── "
        
        # 들여쓰기 설정
        current_indent = indent + ("    " if is_last else "│   ")
        
        # 출력
        print(f"{current_indent}{branch}{path.name}{'/' if path.is_dir() else ''}")
        
        # 재귀 호출 (디렉토리일 경우)
        if path.is_dir():
            next_indent = indent + ("    " if is_last_item else "│   ")
            print_project_tree(
                path,
                ignore_dirs,
                ignore_files,
                max_depth,
                use_gitignore,
                next_indent,
                is_last_item,
                depth + 1,
                spec
            )

# ✅ 사용 예시:
if __name__ == "__main__":
    # .gitignore 자동 적용
    # print_project_tree()
    # 특정 디렉토리 추가로 무시
    project_root: Path = Path(r"D:\02_Projects\Dev\X-ray_AI\Reflecto")
    print_project_tree(project_root, ignore_dirs={".git", ".ruff_cache"})