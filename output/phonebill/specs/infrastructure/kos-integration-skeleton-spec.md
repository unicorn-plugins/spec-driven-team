# KOS 외부 시스템 연동 스켈레톤 명세

## 개요
- 도메인: 외부 시스템 연동 계층
- 복잡도: HIGH (Circuit Breaker, 재시도, 장애 처리)
- 생성일: 2026-02-17

## KosClientService (복잡한 로직)

### 목적
KOS(통신사 시스템)와의 안정적인 통신 및 장애 격리

### 인터페이스 계약

#### inquireBill
**목적**: 요금 정보 조회
**입력**:
```java
KosBillInquiryRequest {
    String lineNumber,
    String inquiryMonth,
    String customerId
}
```
**출력**: KosBillInquiryResponse
**SLA**:
- 정상 응답: < 2초
- 타임아웃: 10초
- 재시도: 3회

#### changeProduct
**목적**: 상품 변경 요청
**입력**:
```java
KosProductChangeRequest {
    String lineNumber,
    String currentProductCode,
    String targetProductCode,
    LocalDate changeDate
}
```
**출력**: KosProductChangeResponse
**처리 방식**: 비동기 (요청 ID 반환)

### Circuit Breaker 패턴 구현

#### 상태 전이
```
CLOSED → OPEN
├─ 조건: 실패율 > 50% (10개 요청 중)
└─ 동작: 모든 요청 즉시 실패

OPEN → HALF_OPEN
├─ 조건: 30초 대기 후
└─ 동작: 제한된 요청 허용 (3개)

HALF_OPEN → CLOSED
├─ 조건: 연속 3회 성공
└─ 동작: 정상 서비스 재개

HALF_OPEN → OPEN
├─ 조건: 1회 실패
└─ 동작: 다시 차단
```

**구현 참조**: `bill-service/src/main/java/com/phonebill/bill/service/KosClientService.java`

### 재시도 전략

```java
@Retry(
    maxAttempts = 3,
    backoff = @Backoff(
        delay = 1000,      // 초기 대기: 1초
        multiplier = 2,    // 지수 백오프: 2배
        maxDelay = 10000   // 최대 대기: 10초
    ),
    include = {
        ConnectException.class,
        SocketTimeoutException.class
    },
    exclude = {
        BusinessException.class  // 비즈니스 오류는 재시도 안함
    }
)
```

### Fallback 처리

#### inquireBill Fallback
```
1차 Fallback: 캐시된 데이터 반환
2차 Fallback: 기본값 응답
3차 Fallback: 503 Service Unavailable
```

#### changeProduct Fallback
```
1차 Fallback: 대기열에 저장
2차 Fallback: 수동 처리 요청
```

**구현 참조**: `KosClientService.java:150-200`

### HTTP 클라이언트 설정

#### RestTemplate 설정
```java
ConnectionTimeout: 5초
ReadTimeout: 10초
MaxConnections: 100
MaxConnectionsPerRoute: 20
KeepAlive: 60초
```

#### 연결 풀 관리
```
유휴 연결 정리: 30초마다
연결 검증: 2초 (stale check)
DNS 캐시: 60초
```

### 요청/응답 처리

#### 요청 변환
```
1. DTO → KOS 형식 변환
   └─ 구현: KosRequestMapper.java

2. 인증 헤더 추가
   └─ API Key 또는 OAuth2 토큰

3. 요청 로깅
   └─ 민감 정보 마스킹
```

#### 응답 처리
```
1. 상태 코드 확인
   ├─ 2xx: 정상 처리
   ├─ 4xx: 비즈니스 오류
   └─ 5xx: 시스템 오류 (재시도)

2. 응답 변환
   └─ KOS 형식 → DTO

3. 응답 검증
   └─ 필수 필드 확인
```

## KOS Mock 서비스

### 목적
개발/테스트 환경에서 KOS 시스템 시뮬레이션

### Mock 데이터 생성
```java
@Component
@Profile("dev")
public class KosMockService {
    // 정상 응답 (80%)
    // 지연 응답 (10%)
    // 오류 응답 (10%)
}
```

**구현 참조**: `kos-mock/src/main/java/com/phonebill/kosmock/`

## 모니터링 및 알림

### 메트릭 수집
```java
@Timed("kos.request.duration")
@Counted("kos.request.count")
@ExceptionMetered("kos.request.errors")
```

### 주요 지표
- 응답 시간 (p50, p95, p99)
- 성공률/실패율
- Circuit Breaker 상태
- 활성 연결 수

### 알림 조건
| 조건 | 임계값 | 액션 |
|------|--------|------|
| 응답시간 > 5초 | 5분간 지속 | 경고 |
| 실패율 > 30% | 즉시 | 알림 |
| Circuit Open | 즉시 | 긴급 |
| 연결풀 고갈 | 80% 이상 | 경고 |

## 보안 고려사항

### API 인증
```
방식: API Key 또는 OAuth2
헤더: X-API-Key 또는 Authorization
로테이션: 월 1회
```

### 데이터 암호화
```
전송: TLS 1.2 이상
민감정보: AES-256 암호화
로깅: PII 마스킹
```

## 장애 시나리오 및 대응

### 시나리오 1: KOS 전체 장애
```
감지: Circuit Breaker OPEN
대응:
1. 캐시 데이터 활용
2. 조회 서비스만 제공
3. 변경 요청 대기열 저장
```

### 시나리오 2: 간헐적 지연
```
감지: p95 > 5초
대응:
1. 타임아웃 동적 조정
2. 재시도 간격 증가
3. 비필수 요청 제한
```

### 시나리오 3: 부분 장애
```
감지: 특정 API만 실패
대응:
1. API별 Circuit Breaker
2. 기능별 Degradation
3. 대체 경로 활성화
```

## 성능 최적화

### 병렬 처리
```java
CompletableFuture<Response1> future1 =
    CompletableFuture.supplyAsync(() -> kosClient.api1());
CompletableFuture<Response2> future2 =
    CompletableFuture.supplyAsync(() -> kosClient.api2());

CompletableFuture.allOf(future1, future2).join();
```

### 배치 처리
```
요청 집계: 100ms 윈도우
배치 크기: 최대 50개
처리 방식: 벌크 API
```

### 캐싱 전략
```
조회 API: 1시간 캐시
변경 상태: 5분 캐시
메타데이터: 24시간 캐시
```

## 테스트 전략

### 단위 테스트
- Mock 서버 응답
- 재시도 로직
- Circuit Breaker 상태 전이

### 통합 테스트
- 실제 Mock 서비스 연동
- 타임아웃 시나리오
- 장애 복구 시나리오

### 카오스 엔지니어링
```java
@Test
@ChaosMonkey(
    latency = @Latency(chance = 0.1, range = 1000-5000),
    exceptions = @Exception(chance = 0.05)
)
```

## 운영 가이드

### 배포 전 체크리스트
- [ ] Circuit Breaker 설정 검토
- [ ] 타임아웃 값 확인
- [ ] API 키 로테이션
- [ ] Mock/Real 모드 확인

### 롤백 계획
```
1. Circuit Breaker 강제 OPEN
2. 이전 버전으로 라우팅
3. 캐시 데이터 활용
4. 수동 처리 모드 전환
```

### SLA 관리
- 가용성: 99.9%
- 응답시간: p95 < 2초
- 에러율: < 0.1%

## 향후 개선사항

1. **GraphQL 도입**
   - Over-fetching 방지
   - 네트워크 호출 감소

2. **gRPC 전환**
   - 성능 향상
   - 스트리밍 지원

3. **이벤트 기반 통합**
   - Kafka/RabbitMQ
   - 비동기 처리 확대

4. **서비스 메시**
   - Istio/Linkerd
   - 트래픽 관리 고도화