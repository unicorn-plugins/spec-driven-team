#!/usr/bin/env python3
"""
sync_checker.py - 명세-코드 불일치 감지

목적: 명세 파일과 코드 파일의 타임스탬프를 비교하여 불일치를 감지함

사용법:
    python sync_checker.py <specs_dir> <source_dir> [--output <output_file>]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def get_file_mtime(file_path: Path) -> float:
    """파일 수정 시간 가져오기"""
    return file_path.stat().st_mtime


def find_spec_files(specs_dir: Path) -> List[Path]:
    """명세 파일 찾기"""
    spec_files = []
    for ext in ['.md', '.yaml', '.yml', '.json']:
        spec_files.extend(specs_dir.rglob(f'*{ext}'))
    return spec_files


def find_source_files(source_dir: Path) -> List[Path]:
    """소스 파일 찾기"""
    source_files = []
    for ext in ['.py', '.ts', '.tsx', '.js', '.jsx', '.java', '.go', '.rs', '.c', '.cpp', '.h']:
        source_files.extend(source_dir.rglob(f'*{ext}'))
    return source_files


def match_spec_to_source(spec_file: Path, source_files: List[Path]) -> Path | None:
    """명세 파일에 대응하는 소스 파일 찾기 (휴리스틱)"""
    spec_stem = spec_file.stem  # 파일명 (확장자 제외)

    # 1. 정확한 이름 매칭
    for source_file in source_files:
        if source_file.stem == spec_stem:
            return source_file

    # 2. 부분 매칭 (예: users.md → users.py, user_api.py 등)
    for source_file in source_files:
        if spec_stem in source_file.stem or source_file.stem in spec_stem:
            return source_file

    return None


def check_sync(specs_dir: Path, source_dir: Path) -> Dict[str, Any]:
    """동기화 상태 체크"""
    spec_files = find_spec_files(specs_dir)
    source_files = find_source_files(source_dir)

    pending = []
    synced = []

    for spec_file in spec_files:
        source_file = match_spec_to_source(spec_file, source_files)

        if source_file is None:
            # 대응하는 소스 파일 없음
            continue

        spec_mtime = get_file_mtime(spec_file)
        source_mtime = get_file_mtime(source_file)

        if abs(spec_mtime - source_mtime) > 60:  # 1분 이상 차이
            reason = ""
            if spec_mtime > source_mtime:
                reason = "명세 변경, 코드 미변경"
            else:
                reason = "코드 변경, 명세 미변경"

            pending.append({
                "spec": str(spec_file),
                "source": str(source_file),
                "reason": reason,
                "detected_at": datetime.now().isoformat()
            })
        else:
            synced.append({
                "spec": str(spec_file),
                "source": str(source_file)
            })

    return {
        "pending": pending,
        "synced": synced,
        "total_pending": len(pending),
        "total_synced": len(synced),
        "last_check": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python sync_checker.py <specs_dir> <source_dir> [--output <output_file>]")
        sys.exit(1)

    specs_dir = Path(sys.argv[1])
    source_dir = Path(sys.argv[2])
    output_file = None

    if "--output" in sys.argv:
        output_index = sys.argv.index("--output")
        if output_index + 1 < len(sys.argv):
            output_file = Path(sys.argv[output_index + 1])

    result = check_sync(specs_dir, source_dir)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"Sync check result saved to {output_file}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
