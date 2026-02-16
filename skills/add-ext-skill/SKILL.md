---
name: add-ext-skill
description: 외부호출 스킬 추가 유틸리티
user-invocable: true
---

# Add External Skill

[ADD-EXT-SKILL 활성화]

## 목표

외부 플러그인을 호출하는 ext-{대상플러그인} 스킬을 추가하여
크로스-플러그인 기능을 확장함.

## 활성화 조건

- 사용자가 `/spec-driven-team:add-ext-skill` 호출 시
- "외부 스킬 추가", "플러그인 연동" 키워드 감지 시

## 워크플로우

### Step 1. 대상 플러그인 탐색

dmap 리소스 마켓플레이스에서 플러그인 카탈로그 다운로드:
```bash
curl https://raw.githubusercontent.com/unicorn-plugins/dmap/refs/heads/main/resources/plugin-resources.md > .dmap/plugin-resources.md
```

다운로드 실패 시:
- `.dmap/plugin-resources.md` 캐시 파일이 있으면 재사용
- 없으면 사용자에게 대상 플러그인명을 직접 입력받음

### Step 2. 대상 플러그인 선택

{tool:AskUserQuestion}으로 추가할 대상 플러그인 선택:
- 플러그인 목록 표시
- 이미 ext-{대상플러그인} 스킬이 존재하면 중복 안내 후 중단

### Step 3. 플러그인 명세서 다운로드

선택한 플러그인의 명세서를 dmap 리소스 마켓플레이스에서 다운로드:
```bash
curl https://raw.githubusercontent.com/unicorn-plugins/dmap/refs/heads/main/resources/plugins/{분류}/{name}.md > .dmap/plugins/{name}.md
```

다운로드 실패 시:
- 캐시 파일이 있으면 재사용
- 없으면 사용자에게 안내하고 중단

### Step 4. 도메인 컨텍스트 수집

프로젝트 컨텍스트 읽기:
- `.dmap/spec-driven-team/requirements.md` (요구사항 정의서)
- `.claude-plugin/plugin.json` (플러그인 메타데이터)

### Step 5. ext-{대상플러그인} External 스킬 생성

External 유형 표준 골격을 기반으로 생성:
- `skills/ext-{대상플러그인}/SKILL.md` 파일 작성
- 명세서의 제공 스킬(FQN), ARGS 스키마, 실행 경로 반영
- 도메인 컨텍스트 수집 가이드 포함

### Step 6. commands/ 진입점 생성

`commands/ext-{대상플러그인}.md` 파일 작성:
```yaml
---
description: {대상플러그인} 외부호출
allowed-tools: Skill
---

Use the Skill tool to invoke the `spec-driven-team:ext-{대상플러그인}` skill with all arguments passed through.
```

### Step 7. help 스킬 업데이트

`skills/help/SKILL.md`의 명령 테이블에 추가:
```markdown
| `/spec-driven-team:ext-{대상플러그인}` | {대상플러그인} 외부호출 |
```

## 참고사항 — External 유형 표준 골격

External 유형 스킬의 필수 구조:

```yaml
---
name: ext-{대상플러그인}
description: {대상플러그인} 외부호출
user-invocable: true
---

# External: {대상플러그인}

## 목표
{대상플러그인} 플러그인의 워크플로우를 실행함.

## 활성화 조건
- 사용자가 `/spec-driven-team:ext-{대상플러그인}` 호출 시

## 도메인 컨텍스트 수집
프로젝트 특화 컨텍스트를 수집하여 외부 플러그인에 전달:
- [프로젝트별 컨텍스트]

## 워크플로우
### Step 1. 컨텍스트 준비
### Step 2. 외부 스킬 호출 → Skill: {대상플러그인}:{스킬명}
- **INTENT**: [호출 목적]
- **ARGS**: [전달 인자]
- **RETURN**: [복귀 조건]

## MUST 규칙
- [ ] 도메인 컨텍스트를 반드시 수집하여 전달

## MUST NOT 규칙
- [ ] 외부 플러그인 내부 구현에 의존하지 않음

## 검증 체크리스트
- [ ] 외부 스킬 호출이 정상 작동하는가
```

## MUST 규칙

- [ ] 대상 플러그인 명세서 다운로드 전 캐시 확인
- [ ] ext-{} 스킬 생성 전 중복 확인
- [ ] help 스킬 업데이트 시 테이블 구조 훼손 금지

## MUST NOT 규칙

- [ ] 명세서 없이 ext-{} 스킬 생성하지 않음
- [ ] 기존 ext-{} 스킬 덮어쓰지 않음

## 검증 체크리스트

- [ ] 명세서가 정상 다운로드되었는가
- [ ] ext-{} 스킬이 생성되었는가
- [ ] commands/ 진입점이 생성되었는가
- [ ] help 스킬이 업데이트되었는가
