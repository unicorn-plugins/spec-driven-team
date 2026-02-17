# 검증 서비스 명세

## 개요
- 도메인: 비즈니스 검증 로직
- 패턴: 규칙 기반 검증 (Rule-based Validation)
- 생성일: 2026-02-17

## ProductValidationService

### 목적
상품 변경 요청에 대한 사전 검증을 수행하여 변경 가능 여부를 판단

### 주요 기능
1. 상품 판매 가능 여부 확인
2. 회선 상태 검증
3. 사업자 일치 확인 (선택적)
4. 검증 결과 상세 정보 제공

### 메서드 명세

#### validateProductChange
**목적**: 상품변경 사전체크 메인 로직
**입력**:
```java
ProductChangeValidationRequest {
    String lineNumber;       // 필수, 회선번호
    String currentProductCode; // 필수, 현재 상품코드
    String targetProductCode;  // 필수, 변경 대상 상품코드
}
```
**출력**:
```java
ProductChangeValidationResponse {
    boolean success;
    String message;
    ValidationData {
        ValidationResult validationResult; // SUCCESS|FAILURE|WARNING
        List<ValidationDetail> validationDetails;
        String failureReason;
    }
}
```
**처리 흐름**:
```
1. 로깅: 검증 시작
2. 검증 수행:
   a. validateProductAvailability() 호출
   b. validateLineStatus() 호출
   c. validateOperatorMatch() 호출 (주석 처리됨)
3. 결과 집계:
   - 모든 검증 통과 → SUCCESS
   - 하나라도 실패 → FAILURE
4. 응답 생성 및 반환
5. 예외 처리: 시스템 오류 시 FAILURE 반환
```

#### validateProductAvailability (private)
**목적**: 대상 상품의 판매 가능 여부 검증
**처리 로직**:
```
1. 캐시 조회:
   - productCacheService.getProductStatus(targetProductCode)
   - 캐시 히트 시 → 즉시 반환
2. 캐시 미스 시:
   - productRepository.findByProductCode(targetProductCode)
   - 상품 존재 여부 확인
   - isActive() 상태 확인
3. 캐시 저장:
   - productCacheService.cacheProductStatus()
4. 검증 결과 기록
```
**검증 규칙**:
- 상품 코드 존재 여부
- 상품 활성 상태 (isActive = true)
- 상품 상태가 "AVAILABLE"인지 확인

**반환값**:
- true: 판매 가능
- false: 판매 불가 또는 존재하지 않음

#### validateLineStatus (private)
**목적**: 회선 상태가 상품 변경 가능한 상태인지 검증
**처리 로직**:
```
1. 캐시 조회:
   - productCacheService.getLineStatus(lineNumber)
   - 캐시 히트 시 → 상태 검증
2. 캐시 미스 시:
   - getLineStatusFromRepository(lineNumber) 호출
   - TODO: 실제 KOS 연동 필요 (현재 모의 구현)
3. 캐시 저장:
   - productCacheService.cacheLineStatus()
4. 상태 유효성 확인:
   - isValidLineStatus(status)
```
**유효한 회선 상태**:
- ACTIVE: 정상 (변경 가능)
- SUSPENDED: 정지 (변경 불가)
- TERMINATED: 해지 (변경 불가)

#### validateOperatorMatch (private, 현재 비활성)
**목적**: 현재 상품과 변경 대상 상품의 사업자 일치 여부 확인
**처리 로직**:
```
1. 현재 상품 정보 조회:
   - getCurrentProductInfo(currentProductCode)
2. 대상 상품 정보 조회:
   - getCurrentProductInfo(targetProductCode)
3. 사업자 코드 비교:
   - currentProduct.operatorCode == targetProduct.operatorCode
```
**비활성 사유**: 비즈니스 요구사항 변경으로 사업자 간 변경 허용

### 캐시 전략

#### 캐시 키 구조
- 상품 상태: `product:status:{productCode}`
- 회선 상태: `line:status:{lineNumber}`
- 상품 정보: `product:info:{productCode}`

#### TTL 설정
- 상품 상태: 1시간
- 회선 상태: 5분 (자주 변경될 수 있음)
- 상품 정보: 24시간

#### Cache-Aside 패턴
```
읽기:
1. 캐시 조회
2. 캐시 미스 → DB/외부 시스템 조회
3. 캐시 저장
4. 데이터 반환

쓰기:
1. DB/외부 시스템 업데이트
2. 캐시 무효화
```

### 검증 상세 타입

#### CheckType (열거형)
```java
PRODUCT_AVAILABLE  // 상품 판매 여부
OPERATOR_MATCH    // 사업자 일치
LINE_STATUS       // 회선 상태
```

#### CheckResult (열거형)
```java
PASS     // 통과
FAIL     // 실패
WARNING  // 경고 (진행 가능하나 주의 필요)
```

#### ValidationResult (열거형)
```java
SUCCESS  // 모든 검증 통과
FAILURE  // 하나 이상 실패
WARNING  // 경고 있으나 진행 가능
```

### 헬퍼 메서드

#### getCurrentProductInfo (private)
**목적**: 상품 정보 조회 (캐시 우선)
**처리**:
```
1. 캐시 조회: productCacheService.getCurrentProductInfo()
2. 캐시 미스 시:
   - productRepository.findByProductCode()
   - Entity → DTO 변환
   - 캐시 저장
3. 반환: ProductInfoDto 또는 null
```

#### getLineStatusFromRepository (private)
**목적**: 회선 상태 조회
**현재 구현**: 임시로 "ACTIVE" 반환
**TODO**: KOS 시스템 연동 구현 필요

#### isValidLineStatus (private)
**목적**: 회선 상태 유효성 판단
**규칙**: status == "ACTIVE" 인 경우만 true

#### getLineStatusMessage (private)
**목적**: 회선 상태별 메시지 생성
**매핑**:
- ACTIVE → "회선이 정상 상태입니다"
- SUSPENDED → "회선이 정지 상태입니다"
- TERMINATED → "회선이 해지된 상태입니다"
- 기타 → "알 수 없는 회선 상태입니다: {status}"

#### addValidationDetail (private)
**목적**: 검증 결과 상세 정보 추가
**입력**:
- List<ValidationDetail> details
- CheckType checkType
- boolean success
- String message

### 의존성

#### 외부 의존성
- ProductRepository: 상품 정보 조회
- ProductCacheService: 캐시 관리
- Logger (SLF4J): 로깅

#### 트랜잭션
- 읽기 전용 트랜잭션
- 격리 수준: READ_COMMITTED

### 예외 처리

#### 처리 가능한 예외
- NullPointerException: null 체크 후 기본값 처리
- DataAccessException: 캐시 실패 시 DB 직접 조회
- 외부 시스템 오류: Circuit Breaker 패턴 적용

#### 예외 발생 시 동작
```java
catch (Exception e) {
    logger.error("검증 중 오류", e);
    return ProductChangeValidationResponse.failure(
        "시스템 오류로 인해 사전체크를 완료할 수 없습니다",
        errorDetails
    );
}
```

### 로깅 전략

#### 로그 레벨
- INFO: 검증 시작/완료
- DEBUG: 각 검증 단계
- ERROR: 예외 발생

#### 로그 포맷
```
INFO: 상품변경 사전체크 시작: lineNumber={}, current={}, target={}
DEBUG: 상품 판매 가능 여부 검증: {}
INFO: 상품변경 사전체크 완료: lineNumber={}, result={}
ERROR: 상품변경 사전체크 중 오류 발생: lineNumber={}
```

### 성능 최적화

#### 캐시 적중률 향상
- 자주 조회되는 상품 정보 사전 캐싱
- 캐시 워밍업 배치 작업

#### 병렬 처리
- 독립적인 검증 로직 병렬 실행 고려
- CompletableFuture 활용

### 테스트 시나리오

#### 정상 케이스
1. 모든 검증 통과
2. 캐시 히트 시나리오
3. 캐시 미스 시나리오

#### 실패 케이스
1. 판매 중단 상품
2. 존재하지 않는 상품
3. 비정상 회선 상태
4. 시스템 오류 발생

#### 경계 케이스
1. null 입력값
2. 빈 문자열 입력
3. 캐시 만료 직전
4. 동시 요청 처리