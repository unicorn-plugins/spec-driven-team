# REST API 명세

## 개요
- 도메인: HTTP REST API 계층
- 프레임워크: Spring Boot 3.3.0 + Spring Web
- 문서화: SpringDoc OpenAPI 2.5.0
- 생성일: 2026-02-17

## 1. 인증 API (AuthController)

### 기본 정보
- Base Path: `/api/v1/auth`
- Content-Type: application/json
- 인증: 불필요 (공개 API)

### 엔드포인트

#### POST /api/v1/auth/login
**목적**: 사용자 로그인
**요청**:
```json
{
  "userId": "string (필수, 4-50자)",
  "password": "string (필수, 8-100자)"
}
```
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "accessToken": "string",
    "expiresIn": 3600,
    "userId": "string",
    "customerId": "string",
    "lineNumber": "string",
    "userName": "string",
    "corp": "unicorn"

  }
}
```
**에러 응답**:
- 401: 인증 실패 (잘못된 ID/비밀번호)
- 423: 계정 잠금
- 500: 서버 오류

#### POST /api/v1/auth/logout
**목적**: 사용자 로그아웃
**인증**: Bearer Token 필요
**요청 헤더**:
```
Authorization: Bearer {token}
```
**응답 (200 OK)**:
```json
{
  "success": true,
  "message": "로그아웃되었습니다"
}
```
**처리 로직**:
- 토큰을 블랙리스트에 추가
- Redis에서 세션 정보 삭제

#### POST /api/v1/auth/refresh
**목적**: 액세스 토큰 갱신
**요청**:
```json
{
  "refreshToken": "string (필수)"
}
```
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "accessToken": "string",
    "tokenType": "Bearer",
    "expiresIn": 3600
  }
}
```

## 2. 사용자 API (UserController)

### 기본 정보
- Base Path: `/api/v1/users`
- 인증: Bearer Token 필요
- 권한: USER, ADMIN

### 엔드포인트

#### GET /api/v1/users/me
**목적**: 현재 사용자 정보 조회
**인증**: Bearer Token
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "userId": "string",
    "customerId": "string",
    "lineNumber": "string",
    "userName": "string",
    "accountStatus": "ACTIVE",
    "lastLoginAt": "2026-02-17T10:00:00"
  }
}
```

#### PUT /api/v1/users/me/password
**목적**: 비밀번호 변경
**요청**:
```json
{
  "currentPassword": "string (필수)",
  "newPassword": "string (필수, 8-100자)",
  "confirmPassword": "string (필수)"
}
```
**검증 규칙**:
- 현재 비밀번호 일치 확인
- 새 비밀번호와 확인 비밀번호 일치
- 비밀번호 복잡도 검증

## 3. 요금 조회 API (BillController)

### 기본 정보
- Base Path: `/api/v1/bills`
- 인증: Bearer Token 필요
- 태그: Bill Inquiry

### 엔드포인트

#### GET /api/v1/bills/menu
**목적**: 요금조회 메뉴 정보
**설명**: UFR-BILL-010 요구사항 구현
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "customerInfo": {
      "customerId": "CUST001",
      "lineNumber": "01012345678",
      "productName": "5G 프리미엄"
    },
    "availableMonths": [
      "202602", "202601", "202512",
      "202511", "202510", "202509"
    ]
  }
}
```

#### POST /api/v1/bills/inquiry
**목적**: 요금 조회 요청
**설명**: UFR-BILL-020 요구사항 구현
**요청**:
```json
{
  "lineNumber": "01012345678 (필수)",
  "inquiryMonth": "202602 (선택, 기본: 당월)",
  "customerId": "CUST001 (필수)"
}
```
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "lineNumber": "01012345678",
    "inquiryMonth": "202602",
    "basicFee": 50000.00,
    "callFee": 12000.00,
    "dataFee": 0.00,
    "smsFee": 2000.00,
    "additionalFee": 5000.00,
    "totalFee": 69000.00,
    "taxAmount": 6900.00,
    "totalAmount": 75900.00,
    "currency": "KRW",
    "billDate": "2026-02-25",
    "dueDate": "2026-03-10"
  }
}
```
**캐시 전략**:
- Cache-Aside 패턴 적용
- TTL: 1시간
- Key: `bill:{lineNumber}:{inquiryMonth}`

#### GET /api/v1/bills/history
**목적**: 요금 조회 이력
**설명**: UFR-BILL-040 요구사항 구현
**쿼리 파라미터**:
- page: int (기본 0)
- size: int (기본 20, 최대 100)
- sort: string (기본 inquiryDate,desc)
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "historyId": 1,
        "lineNumber": "01012345678",
        "inquiryMonth": "202602",
        "inquiryDate": "2026-02-17T10:30:00",
        "totalAmount": 75900.00
      }
    ],
    "pageInfo": {
      "page": 0,
      "size": 20,
      "totalElements": 150,
      "totalPages": 8
    }
  }
}
```

#### GET /api/v1/bills/status/{requestId}
**목적**: 비동기 조회 상태 확인
**설명**: UFR-BILL-030 요구사항 구현
**경로 변수**:
- requestId: string (요청 ID)
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "requestId": "REQ-20260217-001",
    "status": "COMPLETED",
    "progress": 100,
    "result": { /* BillInquiryResponse */ }
  }
}
```
**상태 값**:
- PENDING: 처리 대기
- PROCESSING: 처리 중
- COMPLETED: 완료
- FAILED: 실패

## 4. 상품 변경 API (ProductController)

### 기본 정보
- Base Path: `/api/v1/products`
- 인증: Bearer Token 필요

### 엔드포인트

#### GET /api/v1/products
**목적**: 상품 목록 조회
**쿼리 파라미터**:
- operatorCode: string (선택, 사업자 필터)
- isActive: boolean (선택, 기본 true)
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "productCode": "PROD-5G-001",
      "productName": "5G 프리미엄",
      "monthlyFee": 89000.00,
      "dataAllowance": "무제한",
      "voiceAllowance": "무제한",
      "smsAllowance": "무제한",
      "operatorCode": "SKT",
      "description": "5G 최고 요금제",
      "isAvailable": true
    }
  ]
}
```

#### GET /api/v1/products/{productCode}
**목적**: 특정 상품 상세 조회
**경로 변수**:
- productCode: string
**캐시**:
- TTL: 24시간
- Key: `product:{productCode}`

#### POST /api/v1/products/change/validate
**목적**: 상품 변경 사전체크
**요청**:
```json
{
  "lineNumber": "01012345678",
  "currentProductCode": "PROD-5G-001",
  "targetProductCode": "PROD-5G-002"
}
```
**응답 (200 OK)**:
```json
{
  "success": true,
  "data": {
    "validationResult": "SUCCESS",
    "validationDetails": [
      {
        "checkType": "PRODUCT_AVAILABLE",
        "result": "PASS",
        "message": "판매중인 상품입니다"
      },
      {
        "checkType": "LINE_STATUS",
        "result": "PASS",
        "message": "회선이 정상 상태입니다"
      }
    ]
  }
}
```
**검증 항목**:
1. 상품 판매 여부
2. 회선 상태
3. 사업자 일치 (선택)

#### POST /api/v1/products/change
**목적**: 상품 변경 요청
**요청**:
```json
{
  "lineNumber": "01012345678",
  "customerId": "CUST001",
  "currentProductCode": "PROD-5G-001",
  "targetProductCode": "PROD-5G-002",
  "changeDate": "2026-03-01",
  "reason": "더 나은 요금제로 변경"
}
```
**응답 (202 Accepted)**:
```json
{
  "success": true,
  "data": {
    "requestId": "CHG-20260217-001",
    "status": "PENDING",
    "message": "상품 변경 요청이 접수되었습니다",
    "scheduledDate": "2026-03-01",
    "estimatedCompletion": "2026-03-01T00:00:00"
  }
}
```

#### GET /api/v1/products/change/history
**목적**: 상품 변경 이력 조회
**페이징**: 지원 (page, size, sort)

## 5. API Gateway 라우팅

### Gateway 설정
- Base URL: http://gateway:8080

### 라우팅 규칙

| 경로 패턴 | 대상 서비스 | 필터 |
|-----------|------------|-------|
| /api/v1/auth/** | user-service:8081 | - |
| /api/v1/users/** | user-service:8081 | JWT 인증 |
| /api/v1/bills/** | bill-service:8082 | JWT 인증 |
| /api/v1/products/** | product-service:8083 | JWT 인증 |

### Gateway 필터

#### JWT 인증 필터
- 토큰 유효성 검증
- 토큰 블랙리스트 확인
- 권한 검증

#### CORS 필터
```yaml
allowed-origins: ["http://localhost:3000"]
allowed-methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allowed-headers: ["*"]
expose-headers: ["Authorization"]
```

#### Rate Limiting
- 기본: 100 requests/minute
- 인증된 사용자: 200 requests/minute

## 6. 에러 응답 형식

### 표준 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 친화적 메시지",
    "details": {
      "field": "추가 정보"
    }
  },
  "timestamp": "2026-02-17T10:00:00",
  "path": "/api/v1/resource"
}
```

### 에러 코드 체계

| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| AUTH_001 | 401 | 인증 실패 |
| AUTH_002 | 401 | 토큰 만료 |
| AUTH_003 | 403 | 권한 부족 |
| AUTH_004 | 423 | 계정 잠금 |
| BILL_001 | 404 | 요금 정보 없음 |
| BILL_002 | 503 | KOS 시스템 연동 실패 |
| PROD_001 | 404 | 상품 정보 없음 |
| PROD_002 | 400 | 상품 변경 불가 |
| SYS_001 | 500 | 서버 내부 오류 |
| SYS_002 | 503 | 서비스 일시 중단 |

## 7. API 보안

### 인증 방식
- JWT Bearer Token
- 토큰 위치: Authorization Header
- 형식: `Authorization: Bearer {token}`

### 토큰 관리
- Access Token TTL: 1시간
- Refresh Token TTL: 24시간
- 블랙리스트: Redis 저장

### 권한 체계
- ROLE_USER: 기본 사용자
- ROLE_ADMIN: 관리자
- ROLE_SYSTEM: 시스템

## 8. API 버전 관리

### 버전 정책
- URL Path 버전: /api/v{version}
- 하위 호환성 유지
- Deprecation 정책: 6개월 유예

### 현재 버전
- v1: 현재 운영 (2026-02)
- v2: 계획 중 (2026-08)