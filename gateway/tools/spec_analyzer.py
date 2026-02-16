#!/usr/bin/env python3
"""
spec_analyzer.py - AST 기반 명세화 가능 영역 분류

목적: 코드를 분석하여 선언적 로직과 복잡한 로직을 분류함

사용법:
    python spec_analyzer.py <source_file> [--output <output_file>]
"""

import ast
import sys
import json
from pathlib import Path
from typing import Dict, List, Any


class SpecAnalyzer(ast.NodeVisitor):
    """AST 기반 명세화 가능 영역 분류기"""

    def __init__(self):
        self.declarative_logic = []
        self.complex_logic = []

    def visit_FunctionDef(self, node):
        """함수 정의 방문"""
        # 간단한 휴리스틱: 라인 수, 루프 깊이, 조건문 수로 복잡도 판단
        complexity = self._calculate_complexity(node)

        func_info = {
            "name": node.name,
            "lineno": node.lineno,
            "end_lineno": node.end_lineno,
            "complexity": complexity
        }

        if complexity < 5:  # 임계값: 5
            # 선언적 로직 후보 (CRUD, 데이터 변환, 검증)
            self.declarative_logic.append(func_info)
        else:
            # 복잡한 로직 (알고리즘, 동시성, 최적화)
            self.complex_logic.append(func_info)

        self.generic_visit(node)

    def _calculate_complexity(self, node) -> int:
        """단순 복잡도 계산 (순환 복잡도 근사)"""
        complexity = 1  # 기본값

        for child in ast.walk(node):
            # 조건문
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            # 논리 연산자
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """파일 분석"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        analyzer = SpecAnalyzer()
        analyzer.visit(tree)

        return {
            "file": str(file_path),
            "declarative_logic": analyzer.declarative_logic,
            "complex_logic": analyzer.complex_logic,
            "total_functions": len(analyzer.declarative_logic) + len(analyzer.complex_logic)
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e)
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python spec_analyzer.py <source_file> [--output <output_file>]")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    output_file = None

    if "--output" in sys.argv:
        output_index = sys.argv.index("--output")
        if output_index + 1 < len(sys.argv):
            output_file = Path(sys.argv[output_index + 1])

    result = analyze_file(file_path)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"Analysis result saved to {output_file}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
