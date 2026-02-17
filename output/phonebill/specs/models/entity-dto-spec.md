# Entity & DTO 모델 명세

## 개요
- 도메인: 데이터 모델 계층
- 패턴: JPA Entity + DTO Pattern
- 생성일: 2026-02-17

## 1. Entity 명세

### AuthUserEntity

#### 테이블 매핑
- 테이블명: auth_users
- 스키마: PostgreSQL

#### 필드 명세

| 필드명 | 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|--------|------|----------|------|
| userId | user_id | String(50) | @Id, NOT NULL | 사용자 ID (PK) |
| password | password | String(255) | NOT NULL | 암호화된 비밀번호 (deprecated) |
| passwordHash | password_hash | String(255) | NOT NULL | 비밀번호 해시값 |
| passwordSalt | password_salt | String(100) | NOT NULL | 비밀번호 솔트 |
| customerId | customer_id | String(50) | NOT NULL, UNIQUE | 고객 ID |
| lineNumber | line_number | String(20) | NULL | 회선 번호 |
| userName | user_name | String(100) | NULL | 사용자명 |
| enabled | enabled | Boolean | NOT NULL, Default=true | 활성화 여부 |
| locked | locked | Boolean | NOT NULL, Default=false | 잠금 여부 |
| accountStatus | account_status | Enum(20) | Default=ACTIVE | 계정 상태 |
| failedLoginCount | failed_login_count | Integer | Default=0 | 로그인 실패 횟수 |
| lastFailedLoginAt | last_failed_login_at | LocalDateTime | NULL | 마지막 실패 시간 |
| accountLockedUntil | account_locked_until | LocalDateTime | NULL | 잠금 해제 시간 |
| lastLoginAt | last_login_at | LocalDateTime | NULL | 마지막 로그인 시간 |
| lastPasswordChangedAt | last_password_changed_at | LocalDateTime | NULL | 비밀번호 변경 시간 |

#### AccountStatus Enum
```java
ACTIVE    // 활성
LOCKED    // 잠금
SUSPENDED // 정지
INACTIVE  // 비활성
```

#### 비즈니스 메서드

| 메서드명 | 목적 | 입력 | 출력 | 비즈니스 로직 |
|----------|------|------|------|---------------|
| incrementFailedLoginCount() | 로그인 실패 카운트 증가 | - | void | failedLoginCount++, 시간 갱신 |
| resetFailedLoginCount() | 실패 카운트 초기화 | - | void | count=0, 시간 null |
| lockAccount(long duration) | 계정 잠금 | duration(ms) | void | status=LOCKED, 해제시간 설정 |
| unlockAccount() | 계정 잠금 해제 | - | void | status=ACTIVE, 카운트 초기화 |
| isAccountLocked() | 잠금 상태 확인 | - | boolean | 상태 확인 + 자동 해제 |
| updateLastLogin() | 로그인 시간 갱신 | - | void | 시간 갱신 + 카운트 초기화 |
| updatePassword() | 비밀번호 변경 | hash, salt | void | 해시/솔트 저장 + 시간 갱신 |
| isAccountActive() | 활성 상태 확인 | - | boolean | ACTIVE && !locked |

### BaseTimeEntity (추상 클래스)

#### 필드
- createdAt: LocalDateTime - 생성 시간
- updatedAt: LocalDateTime - 수정 시간

#### 어노테이션
- @CreatedDate
- @LastModifiedDate
- @EntityListeners(AuditingEntityListener.class)

## 2. DTO 명세

### 인증 관련 DTO

#### LoginRequest
**용도**: 로그인 요청
```json
{
  "userId": "string (필수, 4-50자)",
  "password": "string (필수, 8-100자)"
}
```

#### LoginResponse
**용도**: 로그인 응답
```json
{
  "accessToken": "string (JWT 토큰)",
  "tokenType": "Bearer",
  "expiresIn": "long (만료 시간, 초)",
  "userId": "string",
  "customerId": "string",
  "lineNumber": "string",
  "userName": "string"
}
```

#### RefreshTokenRequest
**용도**: 토큰 갱신 요청
```json
{
  "refreshToken": "string (필수)"
}
```

#### RefreshTokenResponse
**용도**: 토큰 갱신 응답
```json
{
  "accessToken": "string (새 JWT 토큰)",
  "tokenType": "Bearer",
  "expiresIn": "long"
}
```

### 요금 조회 관련 DTO

#### BillInquiryRequest
**용도**: 요금 조회 요청
```json
{
  "lineNumber": "string (필수, 회선번호)",
  "inquiryMonth": "string (선택, YYYYMM 형식)",
  "customerId": "string (필수)"
}
```

#### BillInquiryResponse
**용도**: 요금 조회 응답
```json
{
  "lineNumber": "string",
  "inquiryMonth": "string",
  "basicFee": "BigDecimal (기본료)",
  "callFee": "BigDecimal (통화료)",
  "dataFee": "BigDecimal (데이터료)",
  "smsFee": "BigDecimal (SMS료)",
  "additionalFee": "BigDecimal (부가서비스료)",
  "totalFee": "BigDecimal (총 요금)",
  "taxAmount": "BigDecimal (세금)",
  "totalAmount": "BigDecimal (청구 금액)",
  "currency": "string (통화, 기본 KRW)",
  "billDate": "LocalDate (청구일)",
  "dueDate": "LocalDate (납부기한)"
}
```

#### BillMenuResponse
**용도**: 요금 조회 메뉴 정보
```json
{
  "customerInfo": {
    "customerId": "string",
    "lineNumber": "string",
    "productName": "string"
  },
  "availableMonths": [
    "YYYYMM (조회 가능한 월 리스트)"
  ]
}
```

### 상품 관련 DTO

#### ProductInfoDto
**용도**: 상품 정보
```json
{
  "productCode": "string (상품 코드)",
  "productName": "string (상품명)",
  "monthlyFee": "BigDecimal (월 기본료)",
  "dataAllowance": "string (데이터 제공량)",
  "voiceAllowance": "string (음성 제공량)",
  "smsAllowance": "string (SMS 제공량)",
  "operatorCode": "string (사업자 코드)",
  "description": "string (상품 설명)",
  "isAvailable": "boolean (판매 여부)"
}
```

#### ProductChangeRequest
**용도**: 상품 변경 요청
```json
{
  "lineNumber": "string (필수)",
  "customerId": "string (필수)",
  "currentProductCode": "string (현재 상품)",
  "targetProductCode": "string (변경할 상품)",
  "changeDate": "LocalDate (변경 희망일)",
  "reason": "string (변경 사유)"
}
```

#### ProductChangeResponse
**용도**: 상품 변경 응답
```json
{
  "requestId": "string (요청 ID)",
  "status": "PENDING|APPROVED|REJECTED|COMPLETED",
  "message": "string (처리 메시지)",
  "scheduledDate": "LocalDate (변경 예정일)",
  "estimatedCompletion": "LocalDateTime"
}
```

#### ProductChangeValidationRequest
**용도**: 상품 변경 사전체크 요청
```json
{
  "lineNumber": "string (필수)",
  "currentProductCode": "string (필수)",
  "targetProductCode": "string (필수)"
}
```

#### ProductChangeValidationResponse
**용도**: 상품 변경 사전체크 응답
```json
{
  "success": "boolean",
  "message": "string",
  "validationData": {
    "validationResult": "SUCCESS|FAILURE|WARNING",
    "validationDetails": [
      {
        "checkType": "PRODUCT_AVAILABLE|OPERATOR_MATCH|LINE_STATUS",
        "result": "PASS|FAIL|WARNING",
        "message": "string (상세 메시지)"
      }
    ],
    "failureReason": "string (실패 사유)"
  }
}
```

### 공통 응답 DTO

#### ApiResponse<T>
**용도**: 표준 API 응답 래퍼
```json
{
  "success": "boolean (성공 여부)",
  "data": "T (제네릭 데이터)",
  "error": {
    "code": "string (에러 코드)",
    "message": "string (에러 메시지)",
    "details": "object (상세 정보)"
  },
  "timestamp": "LocalDateTime (응답 시간)",
  "path": "string (요청 경로)"
}
```

## 3. DTO 변환 규칙

### MapStruct 매핑

#### Entity to DTO
```java
@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDto toDto(AuthUserEntity entity);
    AuthUserEntity toEntity(UserDto dto);
}
```

#### 매핑 규칙
- null 값: 무시 (NullValuePropertyMappingStrategy.IGNORE)
- 날짜 형식: ISO-8601
- BigDecimal: 소수점 2자리
- Enum: String 변환

### 검증 규칙

#### Bean Validation
- @NotNull: 필수 필드
- @Size: 문자열 길이 제한
- @Pattern: 정규식 검증
- @Valid: 중첩 객체 검증

#### 커스텀 검증
- 회선번호: ^01[0-9]{8,9}$
- 조회월: ^[0-9]{6}$ (YYYYMM)
- 금액: 0 이상의 양수

## 4. 직렬화 설정

### Jackson 설정
```java
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
```

### 날짜 형식
- LocalDateTime: "yyyy-MM-dd'T'HH:mm:ss"
- LocalDate: "yyyy-MM-dd"

### 숫자 형식
- BigDecimal: 문자열로 직렬화 (정밀도 보장)
- Long: 문자열로 직렬화 (JavaScript 호환성)