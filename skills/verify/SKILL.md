---
name: verify
description: 회귀 테스트 및 성능 비교
type: core
user-invocable: true
---

# Verify

[VERIFY 활성화]

## 목표

재생성된 코드에 대한 회귀 테스트를 실행하고,
기존 코드와 성능을 비교하여 품질을 보증함.

## 활성화 조건

- 사용자가 `/spec-driven-team:verify` 호출 시
- "테스트", "검증", "verify" 키워드 감지 시

## 워크플로우

### Step 1. 검증 대상 확인

{tool:AskUserQuestion}으로 검증 대상 선택:
- 전체 테스트
- 특정 디렉토리 (예: `tests/api/`)
- 특정 파일 목록

### Step 2. 회귀 테스트 실행 → Agent: quality-guardian

- **TASK**: 회귀 테스트 자동 실행
- **EXPECTED OUTCOME**: 테스트 결과 보고서
  - 전체/통과/실패/건너뜀 카운트
  - 실패한 테스트 상세 정보
  - 커버리지 (있는 경우)
- **MUST DO**:
  - 언어별 테스트 프레임워크 자동 감지
    - Python: pytest
    - TypeScript/JavaScript: Jest
    - Java: JUnit
    - 기타: 사용자에게 테스트 명령 문의
  - 테스트 실행
  - 결과 파싱
- **MUST NOT DO**:
  - 테스트 코드 수정하지 않음
  - 실패 무시하지 않음
- **CONTEXT**:
  - 프로젝트 루트 디렉토리
  - 테스트 디렉토리 경로

### Step 3. 성능 비교 → Agent: quality-guardian (선택적)

재생성된 코드가 있는 경우에만 실행

- **TASK**: 기존 코드 vs 재생성 코드 성능 비교
- **EXPECTED OUTCOME**: 성능 비교 보고서
  - 함수별 실행 시간
  - 메모리 사용량
  - 성능 회귀 경고 (10% 이상 느려진 경우)
- **MUST DO**:
  - 벤치마크 실행
  - 성능 회귀 감지
- **MUST NOT DO**:
  - 성능 최적화 시도하지 않음
- **CONTEXT**:
  - 백업 디렉토리 (`.backup/`)
  - 현재 코드

### Step 4. 품질 보증 보고서 생성

`./output/{프로젝트명}/develop/` 디렉토리에 저장:
- `verify-result.md` (스킬 실행 요약)
- `quality-report.md` (품질 보증 보고서)
- `regression-test-results.json` (테스트 결과 원본)
- `performance-comparison.json` (성능 비교 결과)

### Step 5. 사용자에게 결과 보고

검증 결과 요약 출력:
```
✅ 검증 완료!

🧪 회귀 테스트 결과:
- 전체: 142개 테스트
- 통과: 140개 ✅
- 실패: 2개 ❌
- 건너뜀: 0개

### 실패 테스트
1. test_user_validation (src/api/users.py:120)
   - 원인: email 검증 로직 변경
   - 해결: 테스트 업데이트 필요

2. test_sort_performance (src/sort.py:234)
   - 원인: TODO 주석으로 대체됨
   - 해결: 개발자가 구현 필요

⚡ 성능 비교:
| 함수 | 기존 | 재생성 | 변화 |
|------|------|--------|------|
| get_users | 45ms | 43ms | ✅ -4% |
| create_user | 32ms | 35ms | ⚠️ +9% |
| validate_user | 12ms | 11ms | ✅ -8% |

📄 상세 보고서: ./output/{프로젝트명}/develop/quality-report.md

권고사항:
1. test_user_validation 테스트 업데이트
2. test_sort_performance 개발자 구현 필요
3. create_user 성능 검토 (허용 범위 내)
```

## MUST 규칙

- [ ] quality-guardian 에이전트에 위임
- [ ] 테스트 프레임워크 자동 감지
- [ ] 실패한 테스트 상세 정보 제공
- [ ] 품질 보증 보고서 생성

## MUST NOT 규칙

- [ ] 테스트 코드 수정하지 않음
- [ ] 실패 무시하지 않음
- [ ] 자동 최적화하지 않음

## 검증 체크리스트

- [ ] quality-guardian 에이전트가 호출되었는가
- [ ] 테스트가 실행되었는가
- [ ] 실패 원인이 명확히 표시되었는가
- [ ] 성능 비교가 수행되었는가 (해당 시)
- [ ] 품질 보증 보고서가 생성되었는가
- [ ] 사용자에게 결과가 보고되었는가
