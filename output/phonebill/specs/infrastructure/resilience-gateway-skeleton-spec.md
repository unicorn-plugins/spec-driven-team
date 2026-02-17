# Circuit Breaker & Gateway Filter 통합 스켈레톤 명세

## 개요
- 도메인: 장애 격리 및 API Gateway 필터링
- 복잡도: HIGH (비동기 처리, 상태 관리, 분산 시스템)
- 생성일: 2026-02-17

## Circuit Breaker 구현 (Resilience4j)

### 목적
마이크로서비스 간 장애 전파 방지 및 시스템 복원력 향상

### CircuitBreakerConfig 설정

#### 기본 설정
```java
CircuitBreakerConfig.custom()
    .failureRateThreshold(50)              // 실패율 임계값
    .slowCallRateThreshold(50)             // 느린 호출 임계값
    .slowCallDurationThreshold(Duration.ofSeconds(2))  // 느린 호출 기준
    .waitDurationInOpenState(Duration.ofSeconds(30))   // Open 상태 유지
    .permittedNumberOfCallsInHalfOpenState(3)         // Half-Open 테스트 호출
    .slidingWindowType(SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(10)                 // 슬라이딩 윈도우 크기
    .minimumNumberOfCalls(5)               // 최소 호출 수
    .automaticTransitionFromOpenToHalfOpenEnabled(true)
```

**구현 참조**: `bill-service/src/main/java/com/phonebill/bill/config/CircuitBreakerConfig.java`

### 서비스별 Circuit Breaker

#### KOS 서비스 전용
```
이름: kos-circuit-breaker
실패율 임계값: 30% (더 민감)
대기 시간: 60초 (더 긴 복구 시간)
재시도: 지수 백오프
```

#### 내부 서비스 전용
```
이름: internal-circuit-breaker
실패율 임계값: 70% (더 관대)
대기 시간: 10초 (빠른 복구)
재시도: 고정 간격
```

### 상태 전이 로직

```
        ┌─────────┐
        │ CLOSED  │◄────────────┐
        └────┬────┘             │
             │                  │
     실패율 > 50%          연속 3회 성공
             │                  │
             ▼                  │
        ┌─────────┐        ┌────┴────┐
        │  OPEN   │───────►│HALF_OPEN│
        └─────────┘ 30초후 └─────────┘
                                 │
                            1회 실패
                                 ▼
                           다시 OPEN
```

### 이벤트 처리

```java
circuitBreaker.getEventPublisher()
    .onStateTransition(event ->
        log.warn("Circuit Breaker 상태 변경: {} → {}",
            event.getStateTransition().getFromState(),
            event.getStateTransition().getToState()))
    .onFailureRateExceeded(event ->
        alertService.sendAlert("실패율 초과: " + event.getFailureRate()))
    .onSlowCallRateExceeded(event ->
        metricsCollector.record("slow.calls", event.getSlowCallRate()));
```

**구현 참조**: `CircuitBreakerConfig.java:80-120`

## Gateway Filter 구현 (Spring Cloud Gateway)

### JwtAuthenticationGatewayFilterFactory

#### 목적
API Gateway 레벨에서 JWT 인증 처리 (WebFlux 기반)

#### 필터 체인 구조
```
요청 → [CORS] → [RateLimit] → [JWT Auth] → [Logging] → [Routing] → 서비스
  ↑                                                                      ↓
응답 ← [Response] ← [Metrics] ← [Error Handler] ← [Transform] ← 서비스 응답
```

#### WebFlux 비동기 처리

```java
public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
    return Mono.just(exchange)
        .map(this::extractToken)
        .flatMap(this::validateTokenAsync)
        .flatMap(this::checkBlacklistAsync)
        .flatMap(this::enrichRequest)
        .flatMap(chain::filter)
        .onErrorResume(this::handleAuthError)
        .doFinally(signal -> logRequest(exchange, signal));
}
```

**구현 참조**: `api-gateway/src/main/java/com/unicorn/phonebill/gateway/filter/JwtAuthenticationGatewayFilterFactory.java`

### 필터 우선순위

| 순서 | 필터 | 목적 |
|------|------|------|
| -2 | CorsGatewayFilter | CORS 처리 |
| -1 | RequestRateLimiter | 요청 제한 |
| 0 | JwtAuthentication | 인증 |
| 1 | RequestLogging | 요청 로깅 |
| 2 | CircuitBreaker | 장애 격리 |
| 3 | Retry | 재시도 |
| 10 | RouteToRequestUrl | 라우팅 |

### Rate Limiting 구현

```java
@Component
public class RateLimiterGatewayFilterFactory {

    private final RedisRateLimiter rateLimiter;

    // Token Bucket 알고리즘
    // 버킷 크기: 100
    // 충전 속도: 10/sec
    // 버스트: 200
}
```

**설정**:
- 인증 사용자: 200 req/min
- 미인증 사용자: 100 req/min
- IP 기반: 500 req/min

### Fallback 처리

```java
.route("bill-service", r -> r
    .path("/api/v1/bills/**")
    .filters(f -> f
        .circuitBreaker(config -> config
            .setName("bill-cb")
            .setFallbackUri("forward:/fallback/bill")))
    .uri("lb://BILL-SERVICE"))
```

**Fallback 응답**:
```json
{
    "success": false,
    "error": {
        "code": "SERVICE_UNAVAILABLE",
        "message": "서비스가 일시적으로 이용할 수 없습니다",
        "retryAfter": 30
    }
}
```

## 통합 모니터링

### Actuator 엔드포인트

```yaml
/actuator/circuitbreakers        # CB 상태
/actuator/circuitbreakerevents   # CB 이벤트
/actuator/gateway/routes         # 라우트 정보
/actuator/gateway/filters        # 필터 정보
/actuator/metrics/gateway.requests  # 요청 메트릭
```

### Prometheus 메트릭

```java
resilience4j.circuitbreaker.state
resilience4j.circuitbreaker.failure.rate
resilience4j.circuitbreaker.calls
gateway.requests.duration
gateway.requests.count
```

### Grafana 대시보드

```
- Circuit Breaker 상태 시각화
- 서비스별 응답 시간
- 실패율 추이
- 트래픽 패턴
```

## 복잡한 시나리오 처리

### 다중 Circuit Breaker

```java
@Component
public class MultiCircuitBreakerService {

    @CircuitBreaker(name = "primary", fallbackMethod = "primaryFallback")
    @CircuitBreaker(name = "secondary", fallbackMethod = "secondaryFallback")
    public Response callService() {
        // 이중 보호
    }
}
```

### 부분 장애 처리

```java
public Mono<AggregatedResponse> aggregateResponses() {
    return Mono.zip(
        callServiceA().onErrorReturn(defaultA),
        callServiceB().onErrorReturn(defaultB),
        callServiceC().onErrorReturn(defaultC)
    ).map(tuple -> combine(tuple.getT1(), tuple.getT2(), tuple.getT3()));
}
```

### 동적 라우팅

```java
@Component
public class DynamicRoutingFilter implements GlobalFilter {

    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Circuit Breaker 상태에 따른 동적 라우팅
        if (circuitBreaker.getState() == State.OPEN) {
            // 백업 서비스로 라우팅
            exchange.getAttributes().put(GATEWAY_REQUEST_URL_ATTR,
                URI.create("http://backup-service"));
        }
        return chain.filter(exchange);
    }
}
```

## 성능 최적화

### 캐싱 레이어

```java
@Component
public class CachingGatewayFilter {

    private final Cache<String, Response> cache;

    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String key = generateCacheKey(exchange);

        return Mono.justOrEmpty(cache.getIfPresent(key))
            .switchIfEmpty(chain.filter(exchange)
                .then(Mono.fromCallable(() -> cacheResponse(exchange))))
            .then();
    }
}
```

### 병렬 필터 실행

```java
Mono.zip(
    authFilter.filter(exchange),
    rateLimitFilter.filter(exchange),
    loggingFilter.filter(exchange)
).flatMap(tuple -> routingFilter.filter(exchange));
```

## 보안 고려사항

### DDoS 방어

```java
@Component
public class DdosProtectionFilter {

    private final LoadingCache<String, AtomicInteger> requestCounts;

    // IP별 요청 추적
    // 임계값 초과 시 차단
    // 블랙리스트 관리
}
```

### 헤더 검증

```java
private Mono<Void> validateHeaders(ServerWebExchange exchange) {
    HttpHeaders headers = exchange.getRequest().getHeaders();

    // Content-Type 검증
    // User-Agent 검증
    // Origin 검증
    // Referer 검증
}
```

## 장애 복구 전략

### 자동 복구

```
1. Health Check 주기: 10초
2. 복구 감지: 연속 3회 성공
3. 트래픽 점진적 증가: 10% → 50% → 100%
```

### 수동 개입

```
POST /actuator/circuitbreaker/{name}/reset
POST /actuator/gateway/refresh
POST /actuator/gateway/routes/{id}/disable
```

## 테스트 전략

### 단위 테스트

```java
@Test
void testCircuitBreakerStateTransition() {
    // Given: 10개 요청 중 6개 실패
    // When: 실행
    // Then: Circuit Open
}
```

### 통합 테스트

```java
@Test
@TestWithCircuitBreaker
void testFallbackResponse() {
    // Circuit Open 상태에서 Fallback 응답 확인
}
```

### 부하 테스트

```bash
# Gatling 시나리오
- 동시 사용자: 1000
- 램프업: 60초
- 지속 시간: 10분
- 목표 RPS: 5000
```

## 운영 가이드

### 알람 규칙

| 메트릭 | 임계값 | 액션 |
|--------|--------|------|
| CB Open Rate > 10% | 5분 | 경고 |
| 평균 응답시간 > 1초 | 10분 | 알림 |
| 에러율 > 1% | 즉시 | 긴급 |
| 메모리 > 80% | 지속 | 스케일링 |

### 튜닝 가이드

```yaml
# Circuit Breaker 튜닝
- 트래픽 패턴 분석
- 실패율 임계값 조정
- 윈도우 크기 최적화
- 복구 시간 조정

# Gateway 튜닝
- Worker Thread 수 조정
- Connection Pool 크기
- Buffer 크기 최적화
- Timeout 값 조정
```