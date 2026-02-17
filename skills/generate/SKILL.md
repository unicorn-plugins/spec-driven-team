---
name: generate
description: 코드 기반 명세 자동 생성
type: core
user-invocable: true
---

# Generate

[GENERATE 활성화]

## 목표

analyzer의 분류 결과를 기반으로 코드로부터 명세를 자동 생성함.
선언적 로직은 완전한 명세로, 복잡한 로직은 스켈레톤 명세로 생성함.

## 활성화 조건

- 사용자가 `/spec-driven-team:generate` 호출 시
- "명세 생성", "스펙 만들어줘", "문서화" 키워드 감지 시

## 워크플로우

### Step 1. 프로젝트 선택

`output/` 디렉토리 하위에서 `project-config.json`이 존재하는 프로젝트 목록을 탐색:
```
output/{project_name}/maintain/project-config.json
```

탐색된 프로젝트 목록에 "신규 프로젝트 (직접 입력)" 옵션을 추가하여
{tool:AskUserQuestion}으로 사용자에게 제시.

**기존 프로젝트 선택 시:**
- 선택된 프로젝트의 `project-config.json`을 읽어 `source_path` 획득
- `source_path`를 프로젝트 루트 경로로 사용

**신규 프로젝트 선택 시:**
- {tool:AskUserQuestion}으로 프로젝트 루트 경로를 직접 입력받음
- 입력받은 경로를 프로젝트 루트 경로로 사용

### Step 1-2. 분석 결과 로드

`./output/{프로젝트명}/explore/codebase-analysis.md` 읽기

분석 결과가 없으면:
```
⚠️  분석 결과가 없습니다.
먼저 /spec-driven-team:analyze를 실행하세요.
```
→ 중단

### Step 2. 명세 생성 대상 확인

{tool:AskUserQuestion}으로 생성 대상 확인:
- 전체 (모든 선언적 로직 + 복잡한 로직)
- 선언적 로직만
- 사용자 지정 (특정 영역 선택)

### Step 3. 명세 생성 → Agent: spec-manager

- **TASK**: 코드로부터 명세 자동 생성
- **EXPECTED OUTCOME**: 명세 파일 (specs/ 디렉토리)
  - 선언적 로직 → 완전한 명세 (Markdown/YAML/JSON)
  - 복잡한 로직 → 스켈레톤 명세 + 구현 참조
- **MUST DO**:
  - Hybrid 형식 선택 (복잡도에 따라)
  - Git 기반 버전 관리
  - 명세 파일 경로: `specs/{domain}/{component}.md`
- **MUST NOT DO**:
  - 코드 수정 금지
  - 복잡한 로직 완전 명세화 시도하지 않음
- **CONTEXT**:
  - 분석 보고서: `./output/{프로젝트명}/explore/codebase-analysis.md`
  - 프로젝트 구조

### Step 4. 명세 검증 → Agent: spec-manager

- **TASK**: 생성된 명세가 코드와 일치하는지 검증
- **EXPECTED OUTCOME**: 검증 결과 (일치/불일치 목록)
- **MUST DO**:
  - 명세-코드 일치 여부 확인
  - 명세 형식 올바른지 확인
- **MUST NOT DO**:
  - 자동 수정하지 않음 (사용자 확인 필요)
- **CONTEXT**: 생성된 명세 파일 목록

### Step 5. 결과 저장

생성 결과를 `./output/{프로젝트명}/explore/` 디렉토리에 저장:
- `generate-result.md` (스킬 실행 요약)
- `specs/` (생성된 명세 파일들)

### Step 6. 사용자에게 결과 보고

생성 결과 요약 출력:
```
✅ 명세 생성 완료!

📝 생성된 명세:
- specs/api/users.md (Markdown, 완전 명세)
- specs/models/user.yaml (YAML, 완전 명세)
- specs/algorithms/sort.md (Markdown, 스켈레톤)

📊 통계:
- 완전 명세: 28개 파일
- 스켈레톤 명세: 7개 파일
- 총 라인: 3,450줄

🔍 검증 결과:
- 일치: 35개 파일 ✅
- 불일치: 0개 파일

📄 명세 위치: specs/

다음 단계:
1. 명세 검토 및 수정 (specs/ 디렉토리)
2. /spec-driven-team:sync - 명세 → 코드 동기화
```

## MUST 규칙

- [ ] spec-manager 에이전트에 위임
- [ ] 분석 결과 없으면 중단
- [ ] 명세 생성 전 사용자 확인
- [ ] Git 버전 관리

## MUST NOT 규칙

- [ ] 코드 수정하지 않음
- [ ] 분석 없이 명세 생성하지 않음
- [ ] 복잡한 로직 완전 명세화 시도하지 않음

## 검증 체크리스트

- [ ] spec-manager 에이전트가 호출되었는가
- [ ] 명세 파일이 생성되었는가
- [ ] 명세 형식이 올바른가
- [ ] Git에 커밋되었는가
- [ ] 사용자에게 결과가 보고되었는가
