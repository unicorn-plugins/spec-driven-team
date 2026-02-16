#!/usr/bin/env python3
"""
code_generator.py - 명세 기반 코드 자동 생성

목적: 명세 파일을 읽어 선언적 로직 코드를 생성함

사용법:
    python code_generator.py <spec_file> <output_file> [--language <lang>]
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any


def load_spec(spec_file: Path) -> Dict[str, Any]:
    """명세 파일 로드"""
    ext = spec_file.suffix.lower()

    with open(spec_file, 'r', encoding='utf-8') as f:
        if ext == '.json':
            return json.load(f)
        elif ext in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif ext == '.md':
            # Markdown 파싱 (간단한 구현)
            # 실제로는 더 정교한 파서 필요
            content = f.read()
            return {"type": "markdown", "content": content}
        else:
            raise ValueError(f"Unsupported spec format: {ext}")


def generate_crud_code(spec: Dict[str, Any], language: str = "python") -> str:
    """CRUD 코드 생성"""
    if language == "python":
        template = """
def get_{entity}(id):
    \"\"\"Get {entity} by ID\"\"\"
    # TODO: Implement database query
    pass

def create_{entity}(data):
    \"\"\"Create new {entity}\"\"\"
    # TODO: Implement database insert
    pass

def update_{entity}(id, data):
    \"\"\"Update {entity}\"\"\"
    # TODO: Implement database update
    pass

def delete_{entity}(id):
    \"\"\"Delete {entity}\"\"\"
    # TODO: Implement database delete
    pass
"""
        entity = spec.get("entity", "item")
        return template.format(entity=entity)
    else:
        raise ValueError(f"Unsupported language: {language}")


def generate_code(spec_file: Path, language: str = "python") -> str:
    """명세 기반 코드 생성"""
    spec = load_spec(spec_file)

    # 명세 타입에 따라 적절한 코드 생성
    spec_type = spec.get("type", "unknown")

    if spec_type == "crud" or "crud" in str(spec).lower():
        return generate_crud_code(spec, language)
    elif spec_type == "markdown":
        # Markdown 명세는 TODO 주석으로 변환
        return f"""
# TODO: Implement based on specification
# Spec file: {spec_file}
# Please refer to the spec file for detailed requirements.
"""
    else:
        return f"""
# TODO: Implement based on specification
# Spec type: {spec_type}
# Spec file: {spec_file}
"""


def main():
    if len(sys.argv) < 3:
        print("Usage: python code_generator.py <spec_file> <output_file> [--language <lang>]")
        sys.exit(1)

    spec_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    language = "python"

    if "--language" in sys.argv:
        lang_index = sys.argv.index("--language")
        if lang_index + 1 < len(sys.argv):
            language = sys.argv[lang_index + 1]

    try:
        code = generate_code(spec_file, language)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"Code generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
