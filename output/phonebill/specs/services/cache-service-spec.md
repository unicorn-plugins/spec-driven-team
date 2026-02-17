# 캐시 서비스 명세

## 개요
- 도메인: 캐시 관리 계층
- 패턴: Cache-Aside Pattern
- 구현: Redis + Spring Cache
- 생성일: 2026-02-17

## 1. BillCacheService

### 목적
요금조회 데이터 캐싱으로 외부 시스템 연동 부하 감소 및 응답 속도 향상

### 캐시 전략

#### TTL 설정
| 데이터 유형 | TTL | 설명 |
|------------|-----|------|
| 요금 데이터 | 1시간 | 외부 시스템 부하 감소 |
| 고객 정보 | 4시간 | 변경 빈도 낮음 |
| 조회 가능 월 | 24시간 | 일별 업데이트 |

#### 캐시 키 구조
- 요금 데이터: `bill:data:{lineNumber}:{inquiryMonth}`
- 고객 정보: `bill:customer:{customerId}`
- 조회 가능 월: `bill:months:{customerId}`

### 메서드 명세

#### getCachedBillData
**목적**: 캐시에서 요금 데이터 조회
**입력**:
- lineNumber: String (회선번호)
- inquiryMonth: String (조회월, YYYYMM)
**출력**:
- BillInquiryResponse (캐시 히트)
- null (캐시 미스)
**처리 로직**:
```
1. 캐시 키 생성: bill:data:{lineNumber}:{inquiryMonth}
2. Redis 조회: redisTemplate.opsForValue().get(key)
3. 캐시 히트:
   - Object → BillInquiryResponse 변환
   - INFO 로그 기록
   - 데이터 반환
4. 캐시 미스:
   - DEBUG 로그 기록
   - null 반환
5. 예외 처리:
   - ERROR 로그 기록
   - null 반환 (fail-safe)
```
**Spring Cache 어노테이션**:
```java
@Cacheable(value = "billData",
           key = "#lineNumber + ':' + #inquiryMonth",
           unless = "#result == null")
```

#### cacheBillData
**목적**: 요금 데이터를 캐시에 저장
**입력**:
- lineNumber: String
- inquiryMonth: String
- billData: BillInquiryResponse
**출력**: void
**처리 로직**:
```
1. null 체크: billData == null → return
2. 캐시 키 생성
3. Redis 저장:
   - redisTemplate.opsForValue().set(key, billData, TTL)
   - TTL: 1시간
4. INFO 로그 기록
5. 예외 처리:
   - ERROR 로그만 기록
   - 캐시 실패가 서비스 중단으로 이어지지 않도록 처리
```

#### evictBillDataCache
**목적**: 특정 요금 데이터 캐시 무효화
**입력**:
- lineNumber: String
- inquiryMonth: String
**출력**: void
**Spring Cache 어노테이션**:
```java
@CacheEvict(value = "billData",
            key = "#lineNumber + ':' + #inquiryMonth")
```

#### evictAllBillDataForLine
**목적**: 특정 회선의 모든 요금 데이터 캐시 무효화
**입력**:
- lineNumber: String
**처리 로직**:
```
1. 패턴 키 생성: bill:data:{lineNumber}:*
2. 매칭되는 모든 키 조회
3. 벌크 삭제 실행
4. 삭제 건수 로그 기록
```

### 고객 정보 캐싱

#### getCachedCustomerInfo
**캐시 키**: `bill:customer:{customerId}`
**TTL**: 4시간
**용도**: 자주 변경되지 않는 고객 기본 정보 캐싱

#### cacheCustomerInfo
**저장 형식**: JSON 직렬화
**압축**: 선택적 (데이터 크기 > 1KB인 경우)

### 조회 가능 월 캐싱

#### getCachedAvailableMonths
**캐시 키**: `bill:months:{customerId}`
**TTL**: 24시간
**데이터 형식**: List<String> (YYYYMM 형식)
**갱신 전략**: 매일 자정 배치 갱신

## 2. ProductCacheService

### 목적
상품 정보 및 검증 데이터 캐싱으로 성능 최적화

### 캐시 전략

#### TTL 설정
| 데이터 유형 | TTL | 설명 |
|------------|-----|------|
| 상품 상태 | 1시간 | 판매 여부 변경 가능 |
| 상품 정보 | 24시간 | 상품 상세 정보 |
| 회선 상태 | 5분 | 자주 변경 가능 |

#### 캐시 키 구조
- 상품 상태: `product:status:{productCode}`
- 상품 정보: `product:info:{productCode}`
- 회선 상태: `line:status:{lineNumber}`

### 메서드 명세

#### getProductStatus
**목적**: 상품 판매 상태 조회
**입력**: productCode: String
**출력**: String (AVAILABLE/UNAVAILABLE)
**캐시 전략**: Read-Through

#### cacheProductStatus
**목적**: 상품 판매 상태 저장
**입력**:
- productCode: String
- status: String
**TTL**: 1시간

#### getCurrentProductInfo
**목적**: 상품 상세 정보 조회
**입력**: productCode: String
**출력**: ProductInfoDto
**캐시 전략**: Cache-Aside
**TTL**: 24시간

#### cacheCurrentProductInfo
**목적**: 상품 상세 정보 저장
**입력**:
- productCode: String
- productInfo: ProductInfoDto
**직렬화**: Jackson ObjectMapper

#### getLineStatus
**목적**: 회선 상태 조회
**입력**: lineNumber: String
**출력**: String (ACTIVE/SUSPENDED/TERMINATED)
**TTL**: 5분 (자주 변경될 수 있음)

#### cacheLineStatus
**목적**: 회선 상태 저장
**입력**:
- lineNumber: String
- status: String
**갱신 전략**: Write-Through

## 3. 공통 캐시 관리

### Redis 설정

#### 연결 설정
```yaml
spring:
  redis:
    host: localhost
    port: 6379
    database: 0
    timeout: 10s
    lettuce:
      pool:
        max-active: 10
        max-idle: 8
        min-idle: 2
```

#### 직렬화 설정
- Key: StringRedisSerializer
- Value: Jackson2JsonRedisSerializer
- Hash Key: StringRedisSerializer
- Hash Value: Jackson2JsonRedisSerializer

### 캐시 워밍업

#### 시작 시 워밍업
```java
@PostConstruct
public void warmupCache() {
    // 인기 상품 TOP 100 사전 캐싱
    // 최근 조회된 회선 정보 캐싱
}
```

#### 배치 워밍업
- 스케줄: 매일 새벽 3시
- 대상: 자주 조회되는 데이터
- 전략: 점진적 로딩 (부하 분산)

### 캐시 모니터링

#### 메트릭 수집
- 캐시 히트율
- 캐시 미스율
- 평균 응답 시간
- 캐시 크기

#### 알람 설정
- 히트율 < 60%: 캐시 전략 재검토
- 메모리 사용률 > 80%: 캐시 정리
- 응답 시간 > 100ms: 성능 최적화

### 캐시 무효화 전략

#### 이벤트 기반 무효화
```java
@EventListener
public void handleProductUpdateEvent(ProductUpdateEvent event) {
    evictProductCache(event.getProductCode());
}
```

#### TTL 기반 자동 만료
- 데이터 신선도와 캐시 효율성 균형
- 비즈니스 요구사항에 따른 TTL 조정

#### 수동 무효화 API
```
POST /admin/cache/evict/{type}/{key}
DELETE /admin/cache/flush
```

### 장애 처리

#### Cache-Aside Pattern
```
1. 캐시 실패 시 DB 직접 조회
2. 캐시 저장 실패는 무시 (fail-safe)
3. 서비스 연속성 보장
```

#### Circuit Breaker
```java
@CircuitBreaker(name = "redis")
public Object getFromCache(String key) {
    // Redis 장애 시 자동 차단
    // Fallback: DB 직접 조회
}
```

### 성능 최적화

#### 파이프라이닝
```java
// 여러 캐시 키 동시 조회
List<Object> results = redisTemplate.executePipelined(
    (RedisCallback<Object>) connection -> {
        // 벌크 연산
    }
);
```

#### 압축
- 1KB 이상 데이터: Gzip 압축
- 압축률: 평균 70% 절감

#### 샤딩
- 데이터 유형별 Redis 인스턴스 분리
- 일관된 해싱으로 부하 분산

## 4. 테스트 전략

### 단위 테스트
- 캐시 히트/미스 시나리오
- TTL 만료 테스트
- 동시성 테스트

### 통합 테스트
- Redis 연결 테스트
- 캐시 워밍업 테스트
- 장애 복구 테스트

### 부하 테스트
- 대용량 캐시 처리
- 동시 접근 시나리오
- 메모리 한계 테스트