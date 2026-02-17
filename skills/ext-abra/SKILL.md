---
name: ext-abra
description: abra 외부호출
user-invocable: true
---

# External: abra

## 목표

abra 플러그인의 워크플로우를 실행함.
spec-driven-team 프로젝트에서 Dify 워크플로우 기반 AI Agent를 자동 개발 및 배포함.

## 활성화 조건

- 사용자가 `/spec-driven-team:ext-abra` 호출 시
- "AI Agent 개발", "Dify 워크플로우 생성", "에이전트 자동화" 키워드 감지 시

## 도메인 컨텍스트 수집

프로젝트 특화 컨텍스트를 수집하여 외부 플러그인에 전달:

| 수집 대상 | 소스 | 용도 |
|----------|------|------|
| 플러그인 메타데이터 | `.claude-plugin/plugin.json` | `source_plugin`, 서비스 목적 파악 |
| 요구사항 정의서 | `.dmap/spec-driven-team/requirements.md` | `service_purpose`, `requirement` ARGS 키 |
| 에이전트 정보 | `agents/*/AGENT.md` (있는 경우) | 에이전트 역할 파악 |
| 프로젝트 디렉토리 | 현재 작업 디렉토리 (cwd) | `project_dir` ARGS 키 |
| 참고 자료 | `resources/` 하위 파일 (있는 경우) | `references` ARGS 키 |

## 워크플로우

### Step 1. 컨텍스트 준비

아래 정보를 수집하여 실행 경로를 결정:

1. `.claude-plugin/plugin.json` 읽기 → 플러그인명 확인
2. `.dmap/spec-driven-team/requirements.md` 읽기 → 서비스 목적 및 요구사항 추출
3. `resources/` 디렉토리 존재 여부 확인 → 참고 자료 목록화
4. 사용자에게 실행 경로 선택 확인

**경로 분기 판단:**

| 조건 | 실행 경로 |
|------|----------|
| Dify 워크플로우가 필요한 경우 | Full Path (scenario → dsl-generate → prototype → dev-plan → develop) |
| 코드 개발만 필요한 경우 (Dify 불필요) | Short Path (dev-plan → develop) |

### Step 2. 외부 스킬 호출 (Full Path)

**Phase 2-1: scenario 호출**

→ Skill: abra:scenario

- **INTENT**: spec-driven-team 서비스의 요구사항 시나리오 생성
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "service_purpose": "{requirements.md에서 추출한 서비스 목적}",
    "project_dir": "{cwd}",
    "domain_context": "명세-코드 양방향 동기화 플러그인. 코드 수정이 아닌 명세 수정으로 어플리케이션을 유지보수하는 팀을 위한 도구.",
    "requirement": "{requirements.md에서 추출한 요구사항}",
    "references": "{resources/ 하위 참고 자료 경로 목록}"
  }
- **RETURN**: 시나리오 파일 생성 완료 후 dev-plan 호출

**Phase 2-2: dev-plan 호출**

→ Skill: abra:dev-plan

- **INTENT**: spec-driven-team 프로젝트의 AI Agent 개발계획서 작성
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "domain_context": "명세-코드 양방향 동기화 플러그인. Python(분석 도구) + TypeScript(웹 에디터) 혼합 스택."
  }
- **RETURN**: 개발계획서 파일 생성 완료 후 develop 호출

**Phase 2-3: develop 호출**

→ Skill: abra:develop

- **INTENT**: spec-driven-team용 AI Agent 개발 및 배포
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}"
  }
- **RETURN**: Agent 개발 및 배포 완료

### Step 3. 외부 스킬 호출 (Short Path)

**Phase 3-1: dev-plan 호출**

→ Skill: abra:dev-plan

- **INTENT**: spec-driven-team 프로젝트의 AI Agent 개발계획서 작성 (코드 기반)
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "domain_context": "명세-코드 양방향 동기화 플러그인. Python(분석 도구) + TypeScript(웹 에디터) 혼합 스택.",
    "no_workflow": "true",
    "allowed_options": ["B", "C"]
  }
- **RETURN**: 개발계획서 파일 생성 완료 후 develop 호출

**Phase 3-2: develop 호출**

→ Skill: abra:develop

- **INTENT**: spec-driven-team용 AI Agent 개발 및 배포 (코드 기반)
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}"
  }
- **RETURN**: Agent 개발 및 배포 완료

## MUST 규칙

- [ ] 도메인 컨텍스트(요구사항, 기술 스택)를 반드시 수집하여 전달
- [ ] `source_plugin` 값은 항상 `"spec-driven-team"` 으로 설정
- [ ] `project_dir` 값은 현재 작업 디렉토리로 설정
- [ ] 실행 경로(Full/Short) 결정 전 사용자 확인

## MUST NOT 규칙

- [ ] 외부 플러그인 내부 구현에 의존하지 않음
- [ ] `project_dir` 없이 스킬 호출하지 않음
- [ ] abra 플러그인 미설치 상태에서 호출하지 않음

## 검증 체크리스트

- [ ] 외부 스킬 호출이 정상 작동하는가
- [ ] 실행 경로 분기가 올바르게 판단되었는가
- [ ] AI Agent 개발 및 배포가 완료되었는가
