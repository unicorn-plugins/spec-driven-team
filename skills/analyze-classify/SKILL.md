---
name: analyze-classify
description: 코드베이스 분석 및 명세화 가능 영역 자동 분류
user-invocable: true
model: opus
context: ["codebase-analysis", "classification"]
---

# 코드베이스 분석 및 분류

[analyze-classify 스킬 활성화]

## 목표

전체 코드베이스를 분석하여 명세화 가능한 영역(선언적 로직)과 복잡한 로직을 자동으로 분류함.
LSP 서버와 정적 분석 도구를 활용하여 비즈니스 로직 패턴을 인식하고 복잡도 메트릭을 측정함.

## 활성화 조건

- 사용자가 "코드 분석", "명세화 분류", "analyze-classify" 명령 시
- 처음 명세를 생성하기 전
- 대규모 리팩토링 후 재분석이 필요할 때

## 워크플로우

### Phase 0: 도구 준비
LSP 서버 및 린터 설치 확인. 미설치 시 setup 스킬 안내.

### Phase 1: 언어 감지 → Agent: codebase-analyzer
- **TASK**: 프로젝트 루트에서 언어 및 프레임워크 감지
- **EXPECTED OUTCOME**: 감지된 언어 목록, 프로젝트 유형
- **MUST DO**: package.json, pyproject.toml, Cargo.toml 등 확인
- **MUST NOT DO**: 사용자 확인 없이 LSP 서버 자동 설치
- **CONTEXT**: 프로젝트 루트 경로

### Phase 2: 코드베이스 분석 → Agent: codebase-analyzer
- **TASK**: LSP 서버 실행 및 전체 코드 분석
- **EXPECTED OUTCOME**: 함수, 클래스, 모듈 목록 및 의존성 그래프
- **MUST DO**: LSP diagnostics, document_symbols 활용
- **MUST NOT DO**: 코드 수정
- **CONTEXT**: 언어별 LSP 서버 설정

### Phase 3: 비즈니스 로직 패턴 인식 → Agent: codebase-analyzer
- **TASK**: CRUD, 데이터 변환, 규칙 기반 검증 패턴 자동 인식
- **EXPECTED OUTCOME**: 패턴별 코드 영역 매핑
- **MUST DO**: AST 분석 및 패턴 매칭
- **MUST NOT DO**: 복잡도 분석 없이 패턴만 판단
- **CONTEXT**: 분석 결과, 도메인 용어

### Phase 4: 명세화 가능 영역 분류 → Agent: codebase-analyzer
- **TASK**: 선언적 로직 vs 복잡한 로직 자동 분류
- **EXPECTED OUTCOME**: 복잡도 메트릭 (순환 복잡도, 중첩 깊이, 라인 수)
- **MUST DO**: 복잡도 기준 적용 (순환 복잡도 > 10 → 복잡한 로직)
- **MUST NOT DO**: 사용자 확인 없이 분류 확정
- **CONTEXT**: 비즈니스 로직 패턴 분석 결과

### Phase 5: 분석 결과 리뷰 (사용자 개입)
- 감지된 언어, 비즈니스 로직 패턴, 분류 결과 표시
- 사용자가 분류 결과 검토 및 수동 조정
- 결과 저장: `.omc/analysis-report.json`

## 출력 형식

```json
{
  "languages": ["python", "typescript"],
  "project_type": "fullstack",
  "total_files": 156,
  "declarative_logic": {
    "count": 89,
    "files": ["src/api/users.py", ...]
  },
  "complex_logic": {
    "count": 67,
    "files": ["src/algorithms/sort.py", ...]
  },
  "patterns": {
    "crud": 45,
    "data_transformation": 23,
    "validation": 21
  }
}
```

## MUST 규칙

- [ ] LSP 서버 미설치 시 setup 스킬 안내
- [ ] 모든 언어별 LSP 서버 실행
- [ ] 복잡도 메트릭 기준 명확히 적용
- [ ] 분석 결과를 .omc/analysis-report.json에 저장
- [ ] 사용자에게 분류 결과 리뷰 기회 제공

## MUST NOT 규칙

- [ ] 코드 파일 수정 금지
- [ ] 사용자 확인 없이 LSP 서버 자동 설치 금지
- [ ] 복잡도 분석 없이 패턴만으로 분류 금지
- [ ] 분석 결과 없이 다음 단계 진행 금지

## 검증 체크리스트

- [ ] 모든 소스 파일이 분석되었는가?
- [ ] LSP 서버가 정상 실행되었는가?
- [ ] 복잡도 메트릭이 모든 파일에 적용되었는가?
- [ ] analysis-report.json 파일이 생성되었는가?
- [ ] 사용자가 분류 결과를 검토했는가?
