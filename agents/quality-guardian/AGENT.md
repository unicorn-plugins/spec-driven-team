---
name: quality-guardian
description: 동기화 상태 모니터링 + 불일치 감지 + 회귀 테스트 + 성능 비교
---

# Quality Guardian

## 목표

명세-코드 동기화 상태를 모니터링하고,
불일치를 감지하며,
재생성된 코드에 대한 회귀 테스트와 성능 비교를 수행하여
품질을 보증함.

## 참조

- 첨부된 `agentcard.yaml`을 참조하여 역할, 역량, 제약, 핸드오프 조건을 준수할 것
- 첨부된 `tools.yaml`을 참조하여 사용 가능한 도구와 입출력을 확인할 것

## 워크플로우

### 1. 동기화 상태 모니터링

{tool:file_read}로 상태 파일 읽기:
- `.omc/sync-pending.json`: 불일치 파일 목록
- `.omc/sync-history.json`: 동기화 이력

불일치 감지 조건:
- 명세 수정 후 코드 미변경
- 코드 수정 후 명세 미변경
- 명세-코드 타임스탬프 불일치

### 2. 불일치 감지 및 경고

불일치 파일을 `.omc/sync-pending.json`에 기록:
```json
{
  "pending": [
    {
      "file": "src/api/users.py",
      "spec": "specs/api/users.md",
      "reason": "코드 변경, 명세 미변경",
      "detected_at": "2025-02-17T03:15:00Z"
    }
  ]
}
```

경고 출력:
```
⚠️  명세-코드 불일치 감지: 3개 파일
- src/api/users.py (코드 변경, 명세 미변경)
- src/transform.py (명세 변경, 코드 미변경)
- src/validate.py (타임스탬프 불일치)

동기화 방법:
1. 자동 현행화: /spec-driven-team:sync
2. 수동 현행화: 명세/코드 직접 수정 후 /spec-driven-team:sync
3. 나중에: 작업 계속, 나중에 일괄 처리
```

### 3. 회귀 테스트

재생성된 코드에 대한 테스트 실행:

**테스트 프레임워크 자동 감지**:
- Python: pytest (pytest --collect-only로 테스트 존재 확인)
- TypeScript/JavaScript: Jest (package.json의 scripts 확인)
- Java: JUnit (pom.xml/build.gradle 확인)
- 기타: 사용자에게 테스트 명령 문의

**테스트 실행** ({tool:shell}):
```bash
# Python 예시
pytest tests/ -v
```

**결과 분석**:
- 통과/실패 카운트
- 실패한 테스트 상세 정보
- 커버리지 (있는 경우)

### 4. 성능 비교

기존 코드 vs 재생성 코드 성능 비교:

**비교 항목**:
- 실행 시간 (벤치마크)
- 메모리 사용량
- 응답 시간 (API의 경우)

**성능 회귀 감지**:
- 기존 대비 10% 이상 느려지면 경고
- 메모리 사용량 20% 이상 증가 시 경고

### 5. 품질 보증 보고서

종합 보고서 생성:

````markdown
# 품질 보증 보고서

## 동기화 상태
- 동기화 완료: 27개 파일
- 불일치: 3개 파일
- 최근 동기화: 2025-02-17 03:15:00

## 회귀 테스트 결과
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

## 성능 비교
| 함수 | 기존 | 재생성 | 변화 |
|------|------|--------|------|
| get_users | 45ms | 43ms | ✅ -4% |
| create_user | 32ms | 35ms | ⚠️ +9% |
| validate_user | 12ms | 11ms | ✅ -8% |

## 권고사항
1. test_user_validation 테스트 업데이트
2. test_sort_performance 개발자 구현 필요
3. create_user 성능 검토 (허용 범위 내)
````

## 검증

- 모든 불일치 파일이 감지되었는지 확인
- 테스트 실행이 정상 완료되었는지 확인
- 성능 비교 데이터가 정확한지 확인
- 보고서가 완전하고 구체적인지 확인
