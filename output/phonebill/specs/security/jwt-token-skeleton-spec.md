# JWT 토큰 처리 스켈레톤 명세

## 개요
- 도메인: 보안 인증 계층
- 복잡도: HIGH (보안 알고리즘 및 암호화)
- 생성일: 2026-02-17

## JwtTokenProvider (복잡한 로직)

### 목적
JWT 토큰의 생성, 검증, 파싱을 담당하는 핵심 보안 컴포넌트

### 인터페이스 계약

#### resolveToken
**목적**: HTTP 요청에서 JWT 토큰 추출
**입력**: HttpServletRequest request
**출력**: String (토큰) 또는 null
**계약**:
- Authorization 헤더에서 "Bearer " 접두사 제거
- 토큰이 없거나 형식이 잘못된 경우 null 반환

#### validateToken
**목적**: JWT 토큰 유효성 검증
**입력**: String token
**출력**: boolean
**검증 항목**:
- 서명 유효성
- 토큰 만료 여부
- 토큰 형식
- 지원되는 알고리즘
**구현 참조**: `common/src/main/java/com/phonebill/common/security/JwtTokenProvider.java:57-74`

#### getUserId
**목적**: JWT 토큰에서 사용자 ID 추출
**입력**: String token
**출력**: String userId
**구현 참조**: `common/src/main/java/com/phonebill/common/security/JwtTokenProvider.java:79-87`

#### createToken (미구현, 인터페이스만)
**목적**: 새로운 JWT 토큰 생성
**입력**:
```java
{
    String userId,
    String customerId,
    String lineNumber,
    String authority
}
```
**출력**: String (JWT 토큰)
**토큰 구조**:
```
Header: {
    "alg": "HS256",
    "typ": "JWT"
}
Payload: {
    "sub": userId,
    "customerId": customerId,
    "lineNumber": lineNumber,
    "authority": authority,
    "iat": issuedAt,
    "exp": expiration
}
Signature: HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
```

### 보안 고려사항

#### 시크릿 키 관리
- 최소 256비트 (32바이트) 이상
- 환경 변수로 외부화
- 주기적 로테이션 필요
- **구현 참조**: `JwtTokenProvider.java:31-40`

#### 알고리즘
- 사용: HMAC-SHA256 (HS256)
- 비대칭 키 고려: RS256 for 마이크로서비스

#### 토큰 수명
- Access Token: 1시간
- Refresh Token: 24시간
- 설정 가능: application.yml

### 예외 처리 전략

| 예외 유형 | 처리 방식 | HTTP 상태 |
|----------|----------|-----------|
| SecurityException | 잘못된 서명 | 401 |
| ExpiredJwtException | 토큰 만료 | 401 |
| MalformedJwtException | 형식 오류 | 400 |
| UnsupportedJwtException | 지원하지 않는 토큰 | 400 |

**상세 구현**: `JwtTokenProvider.java:64-73`

## JwtAuthenticationGatewayFilterFactory (복잡한 로직)

### 목적
Spring Cloud Gateway에서 JWT 인증을 처리하는 WebFlux 기반 필터

### 인터페이스 계약

#### apply
**목적**: Gateway 필터 생성
**입력**: Config config
**출력**: GatewayFilter
**비동기 처리**: Mono/Flux 기반

### 처리 흐름 (스켈레톤)

```
1. 토큰 추출
   └─ 구현: gateway/filter/JwtAuthenticationGatewayFilterFactory.java:45-50

2. 토큰 검증 (비동기)
   └─ 구현: gateway/filter/JwtAuthenticationGatewayFilterFactory.java:52-65

3. 블랙리스트 확인 (Redis 조회)
   └─ 구현: gateway/filter/JwtAuthenticationGatewayFilterFactory.java:67-75

4. 사용자 정보 추가
   └─ 구현: gateway/filter/JwtAuthenticationGatewayFilterFactory.java:77-85

5. 다운스트림 전달
   └─ 구현: gateway/filter/JwtAuthenticationGatewayFilterFactory.java:87-90
```

### WebFlux 특이사항

#### 리액티브 스트림
```java
return Mono.just(token)
    .filter(this::validateToken)
    .flatMap(this::checkBlacklist)
    .map(this::extractUserInfo)
    .switchIfEmpty(Mono.error(new UnauthorizedException()))
```

#### 백프레셔 처리
- 요청 제한: 1000 req/sec
- 버퍼 크기: 256

**구현 참조**: `api-gateway/src/main/java/com/unicorn/phonebill/gateway/filter/`

## TokenBlacklistService (복잡한 로직)

### 목적
로그아웃된 토큰을 블랙리스트로 관리 (동시성 제어)

### 인터페이스 계약

#### addToBlacklist
**목적**: 토큰을 블랙리스트에 추가
**입력**: String token, long ttl
**출력**: void
**동시성**: Redis SETNX 사용

#### isBlacklisted
**목적**: 토큰 블랙리스트 여부 확인
**입력**: String token
**출력**: boolean
**성능**: O(1) 조회

### 동시성 제어 전략

```
1. Redis 원자적 연산 사용 (SETNX, EXPIRE)
2. Lua 스크립트로 트랜잭션 보장
3. 분산 락 불필요 (Redis 단일 스레드)
```

**구현 참조**: `user-service/src/main/java/com/phonebill/user/service/TokenBlacklistService.java`

### 메모리 관리

- TTL 기반 자동 만료
- 최대 크기: 100만 토큰
- 메모리 초과 시: LRU 정책

## JwtAuthenticationFilter (복잡한 로직)

### 목적
Spring Security 필터 체인에서 JWT 인증 처리

### 처리 흐름 (스켈레톤)

```
1. 토큰 추출
   └─ shouldNotFilter() 체크

2. 토큰 검증
   └─ JwtTokenProvider.validateToken()

3. Authentication 생성
   └─ UsernamePasswordAuthenticationToken

4. SecurityContext 설정
   └─ SecurityContextHolder.setAuthentication()

5. 필터 체인 진행
   └─ chain.doFilter()
```

**구현 참조**: 각 서비스의 `security/JwtAuthenticationFilter.java`

## 토큰 갱신 로직 (RefreshTokenService)

### 인터페이스 계약

#### refreshAccessToken
**목적**: Refresh Token으로 새 Access Token 발급
**입력**: String refreshToken
**출력**: TokenResponse
**검증**:
1. Refresh Token 유효성
2. 만료 여부
3. 사용자 상태
4. 토큰 페어 일치

### 토큰 저장 전략

```
Access Token: 클라이언트 메모리
Refresh Token: HttpOnly Cookie + Redis
```

## 성능 최적화 고려사항

### 캐싱
- 검증된 토큰: 5분 캐시
- 사용자 권한: 30분 캐시

### 비동기 처리
- Gateway: WebFlux
- 서비스: @Async 검증

## 보안 모범 사례

1. **시크릿 로테이션**
   - 주기: 90일
   - 이중 키 지원 (신규/기존)

2. **토큰 저장**
   - localStorage 금지
   - sessionStorage 또는 메모리

3. **HTTPS 필수**
   - 중간자 공격 방지
   - 토큰 탈취 방지

4. **Rate Limiting**
   - 토큰 발급: 10회/분
   - 갱신: 100회/시간

## 테스트 시나리오

### 단위 테스트
- 토큰 생성/검증
- 만료 처리
- 예외 케이스

### 통합 테스트
- 필터 체인 동작
- 블랙리스트 동작
- 갱신 플로우

### 보안 테스트
- 토큰 위조 시도
- 만료된 토큰 사용
- 권한 상승 시도