---
name: setup
description: spec-driven-team 플러그인 초기 설정
user-invocable: true
---

# Setup

[SETUP 활성화]

## 목표

spec-driven-team 플러그인을 처음 사용하기 위한 초기 설정을 수행함.
MCP 서버 설치, 디렉토리 생성, 상태 파일 초기화를 자동으로 처리함.

## 활성화 조건

- 사용자가 `/spec-driven-team:setup` 호출 시
- "설정", "초기 설정", "플러그인 설정" 키워드 감지 시

## 워크플로우

### Step 1. gateway/install.yaml 읽기

{tool:Read}로 `gateway/install.yaml` 파일을 읽어 설치 항목 확인:
- MCP 서버 목록
- 커스텀 도구 목록
- 필수 여부 확인

### Step 2. MCP 서버 설치

context7 MCP 서버 설치 (필수):
```bash
claude mcp add-json gateway/mcp/context7.json
```

설치 검증:
```bash
claude mcp list | grep context7
```

설치 실패 시:
- 오류 메시지 표시
- 사용자에게 수동 설치 안내
- context7 없이는 AI 프레임워크 권고 기능 제한됨을 알림

### Step 3. 초기 디렉토리 생성

프로젝트 루트에 필요한 디렉토리 생성:
```bash
mkdir -p specs/
mkdir -p .omc/
mkdir -p .omc/reports/
mkdir -p .backup/
```

### Step 4. 상태 파일 초기화

`.omc/sync-pending.json` 생성:
```json
{
  "pending": [],
  "last_check": null
}
```

`.omc/sync-history.json` 생성:
```json
{
  "history": [],
  "total_syncs": 0
}
```

### Step 5. 설정 완료 안내

설치 결과 요약:
```
✅ spec-driven-team 설정 완료!

설치된 항목:
✅ context7 MCP 서버
✅ 초기 디렉토리 (specs/, .omc/, .backup/)
✅ 상태 파일 (.omc/sync-*.json)

다음 단계:
1. 코드 분석: /spec-driven-team:analyze
2. 명세 생성: /spec-driven-team:generate
3. 도움말: /spec-driven-team:help

커스텀 도구:
⚠️  spec_analyzer.py, sync_checker.py, code_generator.py는
    필요 시 자동으로 다운로드됩니다.
```

## MUST 규칙

- [ ] MCP 서버 설치 전 이미 설치 여부 확인
- [ ] 디렉토리 생성 전 이미 존재 여부 확인 (중복 생성 방지)
- [ ] 상태 파일 초기화 시 기존 데이터 백업
- [ ] 설치 실패 시 명확한 오류 메시지 제공

## MUST NOT 규칙

- [ ] 기존 상태 파일을 백업 없이 덮어쓰지 않음
- [ ] 필수 항목(context7) 설치 실패 시 무시하지 않음
- [ ] 사용자 확인 없이 프로젝트 파일 수정하지 않음

## 검증 체크리스트

- [ ] context7 MCP 서버가 정상 설치되었는가
- [ ] 모든 디렉토리가 생성되었는가
- [ ] 상태 파일이 올바른 형식으로 초기화되었는가
- [ ] 설정 완료 메시지가 표시되었는가
