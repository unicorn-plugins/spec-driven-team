# Repository CRUD 명세

## 개요
- 도메인: 데이터 접근 계층
- 패턴: Spring Data JPA Repository
- 생성일: 2026-02-17

## 1. AuthUserRepository

### 목적
사용자 계정 정보 관리를 위한 CRUD 연산

### 기본 연산 (JpaRepository 상속)
- `save(AuthUserEntity entity)`: 사용자 저장/수정
- `findById(String userId)`: ID로 사용자 조회
- `findAll()`: 전체 사용자 조회
- `delete(AuthUserEntity entity)`: 사용자 삭제
- `existsById(String userId)`: ID 존재 여부 확인

### 커스텀 조회 메서드

#### findByCustomerId
**목적**: 고객 ID로 사용자 조회
**입력**:
- customerId: String
**출력**:
- Optional<AuthUserEntity>
**SQL 매핑**:
```sql
SELECT * FROM auth_users WHERE customer_id = ?
```

#### findByLineNumber
**목적**: 회선번호로 사용자 조회
**입력**:
- lineNumber: String
**출력**:
- Optional<AuthUserEntity>
**SQL 매핑**:
```sql
SELECT * FROM auth_users WHERE line_number = ?
```

#### findByUserIdAndAccountStatus
**목적**: 활성 상태인 사용자만 조회
**입력**:
- userId: String
- status: AccountStatus (ACTIVE/LOCKED/SUSPENDED/INACTIVE)
**출력**:
- Optional<AuthUserEntity>
**SQL 매핑**:
```sql
SELECT * FROM auth_users WHERE user_id = ? AND account_status = ?
```

### 커스텀 업데이트 메서드

#### incrementFailedLoginCount
**목적**: 로그인 실패 횟수 증가
**입력**:
- userId: String
- failedTime: LocalDateTime
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET failed_login_count = failed_login_count + 1,
    last_failed_login_at = ?
WHERE user_id = ?
```
**트랜잭션**: @Modifying 적용 (쓰기 트랜잭션 필요)

#### resetFailedLoginCount
**목적**: 로그인 실패 카운트 초기화
**입력**:
- userId: String
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET failed_login_count = 0,
    last_failed_login_at = NULL
WHERE user_id = ?
```

#### lockAccount
**목적**: 계정 잠금 설정
**입력**:
- userId: String
- lockedUntil: LocalDateTime
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET account_status = 'LOCKED',
    account_locked_until = ?
WHERE user_id = ?
```
**비즈니스 규칙**:
- 5회 로그인 실패 시 자동 잠금
- 잠금 기간: 설정 가능 (기본 30분)

#### unlockAccount
**목적**: 계정 잠금 해제
**입력**:
- userId: String
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET account_status = 'ACTIVE',
    account_locked_until = NULL,
    failed_login_count = 0,
    last_failed_login_at = NULL
WHERE user_id = ?
```

#### updateLastLoginTime
**목적**: 마지막 로그인 시간 업데이트
**입력**:
- userId: String
- loginTime: LocalDateTime
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET last_login_at = ?,
    failed_login_count = 0,
    last_failed_login_at = NULL
WHERE user_id = ?
```

#### updatePassword
**목적**: 비밀번호 업데이트
**입력**:
- userId: String
- passwordHash: String
- passwordSalt: String
- changedTime: LocalDateTime
**출력**:
- int (업데이트된 행 수)
**보안 규칙**:
- 비밀번호는 해시+솔트 형태로 저장
- 평문 비밀번호는 저장하지 않음

#### unlockExpiredAccounts
**목적**: 잠금 해제 시간이 지난 계정들 자동 해제
**입력**:
- currentTime: LocalDateTime
**출력**:
- int (업데이트된 행 수)
**SQL 매핑**:
```sql
UPDATE auth_users
SET account_status = 'ACTIVE',
    account_locked_until = NULL,
    failed_login_count = 0,
    last_failed_login_at = NULL
WHERE account_status = 'LOCKED'
  AND account_locked_until < ?
```
**스케줄링**: 배치 작업으로 주기적 실행 권장

## 2. AuthPermissionRepository

### 기본 연산
- JpaRepository<AuthPermissionEntity, Long> 상속
- 권한 정보 CRUD

## 3. AuthUserPermissionRepository

### 기본 연산
- JpaRepository<AuthUserPermissionEntity, Long> 상속
- 사용자-권한 매핑 관리

## 4. AuthUserSessionRepository

### 기본 연산
- JpaRepository<AuthUserSessionEntity, String> 상속
- 세션 정보 관리

## 5. BillInquiryHistoryRepository

### 목적
요금 조회 이력 관리

### 기본 연산
- JpaRepository<BillInquiryHistoryEntity, Long> 상속
- 조회 이력 저장/조회

## 6. ProductChangeHistoryRepository

### 목적
상품 변경 이력 관리

### 기본 연산
- JpaRepository<ProductChangeHistoryEntity, Long> 상속
- 변경 이력 추적

## 7. ProductRepository (product-service)

### 목적
상품 정보 관리

### 커스텀 메서드
- `findByProductCode(String productCode)`: 상품 코드로 조회
- `findByOperatorCode(String operatorCode)`: 사업자별 상품 조회
- `findByIsActive(boolean isActive)`: 활성/비활성 상품 조회

## 트랜잭션 관리

### 읽기 전용 트랜잭션
- 모든 find* 메서드
- @Transactional(readOnly = true) 권장

### 쓰기 트랜잭션
- @Modifying 어노테이션이 붙은 모든 메서드
- 트랜잭션 격리 수준: READ_COMMITTED

## 예외 처리

### 발생 가능한 예외
- `DataAccessException`: 데이터베이스 접근 오류
- `EntityNotFoundException`: 엔티티를 찾을 수 없음
- `DataIntegrityViolationException`: 무결성 제약 위반
- `OptimisticLockingFailureException`: 동시성 충돌

### 예외 처리 전략
- Service 계층에서 try-catch로 포획
- 비즈니스 예외로 변환하여 전파
- 트랜잭션 롤백 정책 적용

## 성능 최적화

### 인덱스 전략
- userId: PRIMARY KEY
- customerId: UNIQUE INDEX
- lineNumber: INDEX
- account_status + account_locked_until: COMPOSITE INDEX

### 페치 전략
- 기본: LAZY Loading
- 필요시 @EntityGraph 사용

### 쿼리 최적화
- N+1 문제 방지: Fetch Join 사용
- 벌크 연산: @Modifying(clearAutomatically = true)

## 검증 규칙

### 입력 검증
- userId: 필수, 최대 50자
- customerId: 필수, 최대 50자
- lineNumber: 선택, 최대 20자
- password: 필수, 최소 8자

### 비즈니스 규칙 검증
- 계정 상태 전이 규칙 준수
- 중복 userId 방지
- 잠금 해제 시간 유효성 확인