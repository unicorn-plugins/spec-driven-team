---
name: watch
description: 상태 모니터링 + 불일치 감지 (폴링 방식)
user-invocable: true
---

# Watch

[WATCH 활성화]

## 목표

명세-코드 동기화 상태를 주기적으로 모니터링하고,
불일치를 감지하여 사용자에게 알림함.

## 활성화 조건

- 사용자가 `/spec-driven-team:watch` 호출 시
- "상태 확인", "모니터링", "watch" 키워드 감지 시

## 워크플로우

### Step 1. 모니터링 모드 선택

{tool:AskUserQuestion}으로 모드 선택:
- 즉시 확인 (1회 체크)
- 백그라운드 감시 (폴링, 5초 간격, 안내만)

### Step 2-A. 즉시 확인 모드

#### 2-A-1. 상태 체크 → Agent: quality-guardian

- **TASK**: 명세-코드 동기화 상태 확인 + 불일치 감지
- **EXPECTED OUTCOME**: 상태 보고서
  - 동기화 완료 파일 목록
  - 불일치 파일 목록 (이유 포함)
- **MUST DO**:
  - specs/ 디렉토리와 소스 코드 타임스탬프 비교
  - 불일치 파일을 `.omc/sync-pending.json`에 기록
- **MUST NOT DO**:
  - 자동 수정하지 않음
- **CONTEXT**:
  - specs/ 디렉토리
  - 소스 코드 디렉토리

#### 2-A-2. 결과 출력

```
📊 명세-코드 동기화 상태

✅ 동기화 완료: 27개 파일
⚠️  불일치: 3개 파일

불일치 파일:
1. src/api/users.py (코드 변경, 명세 미변경)
2. src/transform.py (명세 변경, 코드 미변경)
3. src/validate.py (타임스탬프 불일치)

동기화 방법:
1. 자동 동기화: /spec-driven-team:sync
2. 수동 수정 후 재확인: /spec-driven-team:watch
3. 나중에: 작업 계속, 나중에 일괄 처리

마지막 체크: 2025-02-17 03:35:00
```

### Step 2-B. 백그라운드 감시 모드 (안내만)

**중요**: 실제 백그라운드 실행은 지원하지 않음. 폴링 개념만 안내.

사용자에게 안내:
```
⚠️  백그라운드 감시 모드는 현재 지원하지 않습니다.

대안:
1. 수동 확인: /spec-driven-team:watch (즉시 확인 모드)
2. 주기적 확인: 개발 중 정기적으로 /spec-driven-team:watch 실행
3. Git 커밋 전 확인: 커밋 전 /spec-driven-team:watch로 상태 확인

권장 주기: 1일 1회
```

### Step 3. 불일치 파일 기록

`.omc/sync-pending.json` 업데이트:
```json
{
  "pending": [
    {
      "file": "src/api/users.py",
      "spec": "specs/api/users.md",
      "reason": "코드 변경, 명세 미변경",
      "detected_at": "2025-02-17T03:35:00Z"
    }
  ],
  "last_check": "2025-02-17T03:35:00Z"
}
```

## MUST 규칙

- [ ] quality-guardian 에이전트에 위임
- [ ] 불일치 파일을 sync-pending.json에 기록
- [ ] 마지막 체크 시간 기록
- [ ] 동기화 방법 안내

## MUST NOT 규칙

- [ ] 자동 수정하지 않음
- [ ] 백그라운드 실행 시도하지 않음 (안내만)

## 검증 체크리스트

- [ ] quality-guardian 에이전트가 호출되었는가
- [ ] 불일치 파일이 감지되었는가
- [ ] sync-pending.json이 업데이트되었는가
- [ ] 사용자에게 동기화 방법이 안내되었는가
