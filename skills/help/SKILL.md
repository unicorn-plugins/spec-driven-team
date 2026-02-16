---
name: "help"
description: "spec-driven-team 플러그인 사용 안내"
user-invocable: true
model: "haiku"
---

# help

## 목표

spec-driven-team 플러그인의 기능과 사용법을 즉시 안내함.

## 워크플로우

### 즉시 출력: 플러그인 개요 및 사용법

```markdown
# 🔧 spec-driven-team 플러그인 도움말

## 개요
명세-코드 양방향 동기화로 어플리케이션을 유지보수하는 Specification-Driven Development 플러그인입니다.

**핵심 가치**: 명세 = 코드의 단일 진실 원천 (양방향 동기화 지원)

## 주요 기능

### 📊 Phase A: 초기 명세화 (코드 → 명세)
- **분석 및 분류**: 전체 코드베이스를 분석하여 명세화 가능 영역 분류
- **자동 명세 생성**: 선언적 로직 → 완전한 명세, 복잡한 로직 → 스켈레톤 명세
- **AI 어플리케이션 권고**: AI 에이전트, MCP 서버, LLM 변환 후보 식별

### 🔄 Phase B: 명세 기반 개발 (명세 → 코드)
- **변경 감지**: 명세 파일 변경사항 자동 감지
- **코드 재생성**: 선언적 로직 자동 재생성, 복잡한 로직 TODO 주석 생성

### ⚡ Phase C: 명세 현행화 (코드 → 명세)
- **불일치 감지**: 명세-코드 간 동기화 상태 모니터링
- **역동기화**: 코드 변경 → 명세 자동 현행화 (사용자 승인 기반)
- **상태 관리**: 동기화 이력 추적 및 알림

## 사용 가능한 명령

### 초기 설정
- `/spec-driven-team:setup` - 플러그인 초기 설정 및 도구 설치

### Phase A: 초기 명세화
- `/spec-driven-team:analyze-classify` - 코드베이스 분석 및 분류
- `/spec-driven-team:generate-spec` - 명세 자동 생성
- `/spec-driven-team:recommend-ai-app` - AI 어플리케이션 분리 권고

### Phase B: 명세 기반 개발
- `/spec-driven-team:watch-spec` - 명세 변경 감지 및 코드 재생성
- `/spec-driven-team:sync-spec` - 명세 → 코드 수동 동기화

### Phase C: 명세 현행화
- `/spec-driven-team:sync-code-to-spec` ⭐ - 코드 → 명세 수동 역동기화
- `/spec-driven-team:monitor-sync-status` - 동기화 상태 확인
- `/spec-driven-team:resolve-conflict` - 동기화 충돌 해소

### 검증 및 유틸리티
- `/spec-driven-team:verify-regenerated` - 재생성된 코드 검증
- `/spec-driven-team:help` - 이 도움말 표시

## 자동 라우팅

다음과 같은 요청은 자동으로 해당 스킬이 처리합니다:
- "코드베이스 분석", "명세 생성" → analyze-classify
- "명세 현행화", "코드→명세 동기화" → sync-code-to-spec
- "AI 어플리케이션 권고" → recommend-ai-app
- "동기화 상태 확인" → monitor-sync-status

## 시작 가이드

### 1단계: 플러그인 설정
```
/spec-driven-team:setup
```

### 2단계: 코드베이스 분석
```
/spec-driven-team:analyze-classify
```

### 3단계: 명세 생성
```
/spec-driven-team:generate-spec
```

### 4단계: AI 어플리케이션 권고 (선택)
```
/spec-driven-team:recommend-ai-app
```

## 출력 파일 위치

- **명세 파일**: `specs/`
- **분석 레포트**: `.omc/reports/`
- **동기화 상태**: `.omc/state/`
- **변경 이력**: `.omc/sync-history.json`

## 지원 언어

Python, TypeScript/JavaScript, Java, C#, Rust, Go

## 문제 해결

**설치 문제**: `/spec-driven-team:setup` 재실행
**동기화 문제**: `/spec-driven-team:monitor-sync-status`로 상태 확인
**명세 생성 문제**: `/spec-driven-team:analyze-classify`로 재분석

## 추가 정보

- 라이선스: MIT
- 저장소: https://github.com/unicorn-plugins/spec-driven-team
- 문서: README.md 참조
```

## MUST 규칙

1. 즉시 출력으로 전체 도움말 내용을 한 번에 표시
2. 모든 사용 가능한 명령어를 누락 없이 포함
3. 자동 라우팅 정보를 정확히 안내

## MUST NOT 규칙

1. 에이전트에 위임하지 않고 직접 출력
2. 불완전하거나 오래된 정보 제공 금지
3. 사용자 추가 질문 요구 금지 (즉시 완전한 답변)

## 검증 체크리스트

- [ ] 모든 스킬 명령어가 정확히 나열됨
- [ ] 자동 라우팅 패턴이 올바르게 설명됨
- [ ] 출력 파일 위치가 정확히 안내됨
- [ ] 지원 언어 목록이 최신 상태임