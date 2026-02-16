---
name: analyze
description: 코드베이스 분석 + AI 어플리케이션 권고
user-invocable: true
---

# Analyze

[ANALYZE 활성화]

## 목표

전체 코드베이스를 분석하여 구조·비즈니스 로직·의존성을 파악하고,
명세화 가능 영역을 분류하며, AI 어플리케이션으로 분리 가능한 영역을 권고함.

## 활성화 조건

- 사용자가 `/spec-driven-team:analyze` 호출 시
- "코드 분석", "분석해줘", "코드 탐색" 키워드 감지 시

## 워크플로우

### Step 1. 대상 디렉토리 확인

{tool:AskUserQuestion}으로 분석 대상 확인:
- 전체 프로젝트
- 특정 디렉토리 (예: `src/`)
- 특정 파일 목록

### Step 2. 코드베이스 분석 → Agent: analyzer

- **TASK**: 전체 코드베이스 구조 파악 + 비즈니스 로직 분석 + 명세화 가능 영역 분류
- **EXPECTED OUTCOME**: 구조화된 분석 보고서 (Markdown)
  - 프로젝트 개요 (언어, 규모, 프레임워크)
  - 비즈니스 로직 요약
  - 선언적 로직 목록 (완전 명세화 가능)
  - 복잡한 로직 목록 (스켈레톤 명세)
- **MUST DO**:
  - 모든 소스 파일 스캔
  - LSP 기반 심볼 분석 (가능한 경우)
  - AST 기반 패턴 매칭
- **MUST NOT DO**:
  - 코드 수정 금지
  - 명세 생성하지 않음 (분류만 수행)
- **CONTEXT**: `gateway/runtime-mapping.yaml` 참조하여 도구 사용

### Step 3. AI 어플리케이션 분리 권고 → Agent: analyzer

- **TASK**: 선언적 로직 중 AI 어플리케이션으로 분리 가능한 영역 식별
- **EXPECTED OUTCOME**: 권고 레포트 (`.omc/reports/ai-application-recommendations.md`)
  - 권고 #N: 대상 영역, 추천 기술, 기대 효과
- **MUST DO**:
  - context7 MCP로 AI 프레임워크 문서 검색 (LangChain, MCP)
  - 실현 가능한 권고만 제시
- **MUST NOT DO**:
  - 비현실적인 권고 금지
- **CONTEXT**: 프로젝트 도메인 및 기술 스택 고려

### Step 4. 분석 결과 저장

분석 보고서를 `.omc/reports/codebase-analysis.md`에 저장

### Step 5. 사용자에게 결과 보고

분석 결과 요약 출력:
```
✅ 코드베이스 분석 완료!

📊 프로젝트 개요:
- 언어: Python
- 규모: 45개 파일, 12,450 라인
- 프레임워크: FastAPI, SQLAlchemy

📝 명세화 가능 영역:
- 선언적 로직: 28개 (CRUD 15개, 데이터 변환 8개, 검증 5개)
- 복잡한 로직: 7개 (알고리즘 3개, 동시성 4개)

🤖 AI 어플리케이션 권고:
- 3개 권고 사항 (MCP 서버 2개, LangChain 1개)

📄 상세 보고서:
- .omc/reports/codebase-analysis.md
- .omc/reports/ai-application-recommendations.md

다음 단계:
/spec-driven-team:generate - 명세 생성
```

## MUST 규칙

- [ ] analyzer 에이전트에 위임 (직접 분석하지 않음)
- [ ] 분석 결과를 파일로 저장
- [ ] 사용자에게 요약 보고
- [ ] AI 권고는 실현 가능한 것만

## MUST NOT 규칙

- [ ] 코드 수정하지 않음
- [ ] 명세 생성하지 않음 (분석만)
- [ ] 사용자 확인 없이 진행하지 않음

## 검증 체크리스트

- [ ] analyzer 에이전트가 호출되었는가
- [ ] 분석 보고서가 생성되었는가
- [ ] AI 권고 레포트가 생성되었는가
- [ ] 사용자에게 결과가 보고되었는가
