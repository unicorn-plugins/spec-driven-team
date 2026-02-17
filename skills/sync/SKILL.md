---
name: sync
description: 명세-코드 양방향 동기화
type: core
user-invocable: true
---

# Sync

[SYNC 활성화]

## 목표

명세와 코드 간 양방향 동기화를 수행함.
명세 변경 → 코드 재생성, 코드 변경 → 명세 현행화 모두 지원함.

## 활성화 조건

- 사용자가 `/spec-driven-team:sync` 호출 시
- "동기화", "sync", "일치시켜줘" 키워드 감지 시

## 워크플로우

### Step 1. 동기화 방향 확인

{tool:AskUserQuestion}으로 동기화 방향 선택:
- 명세 → 코드 (명세 기반 코드 재생성)
- 코드 → 명세 (코드 기반 명세 현행화)
- 자동 감지 (불일치 파일 기준)

### Step 2-A. 명세 → 코드 동기화

#### 2-A-1. 명세 변경 감지

`./output/{프로젝트명}/maintain/sync-pending.json`에서 "명세 변경, 코드 미변경" 파일 목록 로드

#### 2-A-2. 코드 재생성 → Agent: code-generator

- **TASK**: 변경된 명세를 기반으로 코드 재생성
- **EXPECTED OUTCOME**: 재생성된 코드 파일
  - 선언적 로직 → 자동 재생성
  - 복잡한 로직 → TODO 주석 생성
- **MUST DO**:
  - 기존 코드 백업 (`.backup/`)
  - diff 생성 후 사용자 승인
  - LSP 기반 구문 오류 검사
- **MUST NOT DO**:
  - 사용자 승인 없이 덮어쓰지 않음
  - 복잡한 로직 자동 구현하지 않음
- **CONTEXT**:
  - 명세 파일 목록
  - 기존 코드 경로

#### 2-A-3. 회귀 테스트 → Agent: quality-guardian

- **TASK**: 재생성된 코드에 대한 회귀 테스트
- **EXPECTED OUTCOME**: 테스트 결과 보고서
- **MUST DO**:
  - 언어별 테스트 프레임워크 자동 감지
  - 테스트 실행
  - 실패 시 상세 정보 제공
- **MUST NOT DO**:
  - 테스트 수정하지 않음
- **CONTEXT**: 재생성된 코드 파일 목록

### Step 2-B. 코드 → 명세 동기화

#### 2-B-1. 코드 변경 감지

`./output/{프로젝트명}/maintain/sync-pending.json`에서 "코드 변경, 명세 미변경" 파일 목록 로드

#### 2-B-2. 명세 현행화 → Agent: spec-manager

- **TASK**: 변경된 코드를 기반으로 명세 업데이트
- **EXPECTED OUTCOME**: 업데이트된 명세 파일
- **MUST DO**:
  - 명세 diff 생성
  - 사용자 승인 후 업데이트
  - Git 커밋
- **MUST NOT DO**:
  - 코드 수정하지 않음
  - 자동 병합하지 않음
- **CONTEXT**:
  - 변경된 코드 파일 목록
  - 기존 명세 파일

#### 2-B-3. 명세 검증 → Agent: spec-manager

- **TASK**: 업데이트된 명세가 코드와 일치하는지 검증
- **EXPECTED OUTCOME**: 검증 결과
- **MUST DO**:
  - 명세-코드 일치 확인
- **MUST NOT DO**:
  - 자동 수정하지 않음
- **CONTEXT**: 업데이트된 명세 파일 목록

### Step 3. 동기화 상태 업데이트

`./output/{프로젝트명}/maintain/sync-pending.json` 초기화:
```json
{
  "pending": [],
  "last_check": "2025-02-17T03:30:00Z"
}
```

`./output/{프로젝트명}/maintain/sync-history.json` 업데이트:
```json
{
  "history": [
    {
      "timestamp": "2025-02-17T03:30:00Z",
      "direction": "spec_to_code",
      "files": 5,
      "success": true
    }
  ],
  "total_syncs": 1
}
```

### Step 4. 결과 저장

동기화 결과를 `./output/{프로젝트명}/develop/` 디렉토리에 저장:
- `sync-result.md` (스킬 실행 요약)
- `sync-report.md` (상세 동기화 보고서)
- `backups/` (백업 파일들)

### Step 5. 사용자에게 결과 보고

동기화 결과 요약 출력:
```
✅ 동기화 완료!

📝 명세 → 코드:
- 재생성: 5개 파일
- TODO 주석: 2개 파일
- 백업: .backup/2025-02-17-03-30/

🧪 회귀 테스트:
- 전체: 142개 테스트
- 통과: 140개 ✅
- 실패: 2개 ❌

📊 동기화 상태:
- 불일치: 0개 파일
- 마지막 동기화: 2025-02-17 03:30:00

다음 단계:
1. 실패한 테스트 확인 (test_user_validation, test_sort_performance)
2. TODO 주석 구현 (src/sort.py:89-234)
```

## MUST 규칙

- [ ] 동기화 전 사용자 승인
- [ ] 코드 변경 전 백업 생성
- [ ] 회귀 테스트 자동 실행
- [ ] 동기화 이력 기록

## MUST NOT 규칙

- [ ] 사용자 승인 없이 덮어쓰지 않음
- [ ] 복잡한 로직 자동 구현하지 않음
- [ ] 테스트 실패 무시하지 않음

## 검증 체크리스트

- [ ] 동기화 방향이 명확한가
- [ ] 에이전트 위임이 정상 작동하는가
- [ ] 백업이 생성되었는가
- [ ] 회귀 테스트가 실행되었는가
- [ ] 동기화 이력이 기록되었는가
- [ ] 사용자에게 결과가 보고되었는가
