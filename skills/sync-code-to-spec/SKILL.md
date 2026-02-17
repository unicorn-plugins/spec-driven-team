---
name: sync-code-to-spec
description: 코드 변경사항을 명세에 수동 반영 - 사용자 승인 기반 역동기화
type: core
user-invocable: false
---

# 코드→명세 수동 동기화 (Reverse Sync)

[sync-code-to-spec 스킬 활성화 - 코드 변경사항을 명세에 반영]

## 목표

코드베이스의 변경사항을 감지하여 해당하는 명세 파일에 반영하는 역동기화를 수행함.
사용자가 선택한 범위(전체/디렉토리/파일/대기 중인 변경사항)에 대해 차이점을 분석하고,
사용자 승인을 받아 명세를 업데이트함.

## 활성화 조건

- 사용자가 "코드를 명세에 반영해줘", "역동기화", "sync-code-to-spec" 명령 시
- 코드 변경 후 명세 업데이트가 필요한 상황
- Git 커밋 전 명세-코드 동기화 확인 시

## 워크플로우

### Step 1: 동기화 범위 선택
사용자에게 동기화 대상 범위 선택 옵션 제공:

```
동기화 범위를 선택하세요:
1. 전체 프로젝트 (all)
2. 특정 디렉토리 (directory)
3. 특정 파일들 (files)
4. 대기 중인 변경사항만 (pending-only)
```

### Step 2: 코드베이스 분석 → Agent: codebase-analyzer
- **TASK**: 선택된 범위의 현재 코드 상태를 분석하고 기존 명세와 비교
- **EXPECTED OUTCOME**: 변경된 함수, 클래스, API, 비즈니스 로직 목록
- **MUST DO**: 각 변경사항의 영향 범위와 명세 파일 매핑 정보 제공
- **MUST NOT DO**: 명세 파일을 직접 수정하거나 변경사항 자동 적용
- **CONTEXT**: 동기화 범위, 기존 분석 결과, .omc/sync-history.json

### Step 3: 명세 차이점 생성 → Agent: spec-generator
- **TASK**: 코드 변경사항을 바탕으로 명세 업데이트 diff 생성
- **EXPECTED OUTCOME**: 명세별 변경 사항 미리보기 (추가/수정/삭제)
- **MUST DO**: 변경사항을 diff 형식으로 명확하게 표시
- **MUST NOT DO**: 사용자 승인 없이 명세 파일 변경
- **CONTEXT**: 분석 결과, 기존 명세 파일들, 패턴 매칭 규칙

### Step 4: 사용자 승인 프로세스
각 명세 파일별로 사용자에게 승인 요청:

```
📄 specs/auth-service.md 변경 사항:

+ ### VERIFY_EMAIL_TOKEN
+   - **입력**: email: string, token: string
+   - **출력**: verified: boolean, expires_at: datetime
+   - **규칙**: 토큰 유효기간 24시간

~ ### LOGIN
~   - **제약**: 실패 횟수 제한
-     - 3회 실패 시 계정 잠금
+     - 5회 실패 시 계정 잠금 (15분간)

선택하세요:
[Y] 승인  [N] 거부  [E] 편집  [S] 건너뛰기  [A] 전체승인  [Q] 중단
```

### Step 5: 명세 업데이트 실행 → Agent: spec-generator
- **TASK**: 사용자가 승인한 변경사항만 명세 파일에 반영
- **EXPECTED OUTCOME**: 업데이트된 명세 파일들과 백업 파일들
- **MUST DO**: 원본 명세 백업 생성, 변경 이력 기록, Git 커밋 준비
- **MUST NOT DO**: 거부된 변경사항 적용, 백업 없는 덮어쓰기
- **CONTEXT**: 사용자 승인 결과, 타임스탬프

### Step 6: 동기화 완료 처리
- `.omc/sync-history.json`에 동기화 이력 기록
- 업데이트된 파일들을 Git 스테이징
- 사용자에게 완료 보고서 표시

## 출력 형식

### 동기화 완료 보고서
```
🔄 코드→명세 동기화 완료

📊 처리 결과:
- 분석된 파일: 15개
- 변경 감지: 8개 파일
- 사용자 승인: 6개 파일
- 업데이트 완료: 6개 명세

📁 업데이트된 명세:
✅ specs/auth-service.md (2개 변경사항)
✅ specs/user-management.md (1개 변경사항)
✅ specs/order-workflow.md (3개 변경사항)
❌ specs/payment-gateway.md (사용자 거부)
⏭️ specs/notification.md (건너뛰기)

🔒 백업 위치: .omc/backups/specs-20240101-120000/
📋 변경 이력: .omc/sync-history.json 업데이트 완료

다음 단계: git commit -m "명세 동기화: 코드 변경사항 6개 반영"
```

## MUST (반드시 수행)

- [ ] 사용자 승인 없이는 절대 명세 파일을 변경하지 않음
- [ ] 모든 원본 명세 파일의 백업을 생성함
- [ ] 변경 이력을 .omc/sync-history.json에 기록함
- [ ] 코드-명세 매핑 관계를 정확히 파악함
- [ ] 사용자에게 명확한 diff 미리보기를 제공함

## MUST NOT (절대 금지)

- [ ] 자동으로 명세를 변경하는 것
- [ ] 백업 없이 파일을 덮어쓰는 것
- [ ] 거부된 변경사항을 적용하는 것
- [ ] 사용자 확인 없이 Git 커밋하는 것
- [ ] 에러 발생 시 부분적으로 변경된 상태로 남기는 것

## 검증 체크리스트

- [ ] 모든 변경사항이 사용자에게 승인받았는가?
- [ ] 백업 파일이 올바른 위치에 생성되었는가?
- [ ] 업데이트된 명세 파일의 마크다운 문법이 유효한가?
- [ ] sync-history.json에 타임스탬프와 변경 내역이 정확히 기록되었는가?
- [ ] 코드와 명세 간의 일관성이 유지되었는가?