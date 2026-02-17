# 코드베이스 분석 보고서 - PhoneBill MVNO 서비스

## 1. 프로젝트 개요

- **언어/런타임**: Java 21, Spring Boot 3.3.0
- **규모**: 203개 Java 파일, 총 2,629라인
- **프레임워크**: Spring Boot (WebFlux for Gateway, Web for services), Spring Data JPA, Spring Security, Spring Cloud Gateway
- **주요 의존성**:
  - JWT (jsonwebtoken 0.12.5)
  - Redis (캐싱 및 세션 관리)
  - PostgreSQL (데이터 저장소)
  - Resilience4j (Circuit Breaker)
  - SpringDoc OpenAPI 2.5.0 (API 문서화)
  - MapStruct 1.5.5 (DTO 매핑)

## 2. 비즈니스 로직 요약

### 핵심 도메인
MVNO(가상이동통신망사업자) 고객을 위한 통신요금 조회 및 상품변경 서비스

### 주요 기능
1. **사용자 인증/인가** (user-service) - JWT 기반 토큰 인증, 로그인/로그아웃, RBAC, 세션 관리
2. **요금 조회** (bill-service) - 실시간 요금 조회, KOS 시스템 연동, Cache-Aside 패턴, 조회 이력
3. **상품 변경** (product-service) - 변경 요청/검증, 상품 조회, KOS 연동, 변경 이력
4. **API Gateway** (api-gateway) - 라우팅, JWT 검증, CORS, Fallback 처리
5. **KOS Mock** (kos-mock) - 외부 통신사 시스템 시뮬레이션

### 데이터 흐름
```
Client → API Gateway → Microservices → KOS System (Mock/Real)
                    ↓
                Redis Cache / PostgreSQL DB
```

## 3. 명세화 가능 영역 분류

### 3.1 선언적 로직 (완전 명세화 가능)

| 영역 | 파일 경로 | 패턴 | 설명 |
|------|----------|------|------|
| CRUD 연산 | `user-service/repository/*Repository.java` | JPA Repository | 사용자, 권한, 세션 관리 |
| CRUD 연산 | `bill-service/repository/*Repository.java` | JPA Repository | 요금 조회 이력 관리 |
| CRUD 연산 | `product-service/repository/*Repository.java` | JPA Repository | 상품 변경 이력 관리 |
| 데이터 변환 | 모든 서비스의 `dto/*.java` | DTO 매핑 | 요청/응답 데이터 변환 |
| 검증 로직 | `product-service/ProductValidationService.java` | 규칙 기반 검증 | 상품 변경 가능 여부 체크 |
| 캐시 관리 | `*/service/*CacheService.java` | Cache-Aside | Redis 캐시 읽기/쓰기 |
| REST API | `*/controller/*Controller.java` | Spring MVC | HTTP 엔드포인트 정의 |
| 설정 관리 | `*/config/*.java` | Spring Configuration | 보안, Redis, JPA 설정 |
| 예외 처리 | `*/exception/GlobalExceptionHandler.java` | Exception Handler | 전역 에러 처리 |
| 엔티티 정의 | `*/entity/*Entity.java` | JPA Entity | 도메인 모델 정의 |

### 3.2 복잡한 로직 (스켈레톤 명세)

| 영역 | 파일 경로 | 이유 | 설명 |
|------|----------|------|------|
| 외부 시스템 연동 | `*/service/KosClientService.java` | Circuit Breaker 복잡성 | KOS 시스템 통신 및 장애 처리 |
| JWT 토큰 처리 | `common/security/JwtTokenProvider.java` | 보안 알고리즘 | 토큰 생성/검증 로직 |
| 인증 필터 | `gateway/filter/JwtAuthenticationGatewayFilterFactory.java` | WebFlux 비동기 처리 | 게이트웨이 레벨 인증 |
| 트랜잭션 관리 | `*/service/*ServiceImpl.java` | 복합 트랜잭션 | 다중 저장소 트랜잭션 |
| Circuit Breaker | `*/config/CircuitBreakerConfig.java` | Resilience4j 설정 | 장애 격리 패턴 구현 |
| 비동기 처리 | `product-service/ProductServiceImpl` | 비동기 워크플로우 | 상품 변경 비동기 처리 |
| 토큰 블랙리스트 | `user-service/TokenBlacklistService.java` | 동시성 제어 | Redis 기반 토큰 무효화 |

## 4. 아키텍처 특징

- **API Gateway Pattern**: 단일 진입점
- **Circuit Breaker Pattern**: 장애 격리
- **Cache-Aside Pattern**: 성능 최적화
- **Repository Pattern**: 데이터 접근 추상화
- **JWT 기반 stateless 인증** + Redis 토큰 블랙리스트

## 5. 개선 기회

1. 테스트 코드 부재 → TDD 도입 권고
2. API 문서 자동화 미흡
3. 중앙화된 로깅 시스템 구축 필요
4. 동기식 통신 → 메시지 큐 도입 검토
5. Flyway/Liquibase 도입 권고
