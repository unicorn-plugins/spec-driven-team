# 설정 클래스 명세

## 개요
- 도메인: 애플리케이션 설정 계층
- 프레임워크: Spring Boot Configuration
- 생성일: 2026-02-17

## 1. 보안 설정 (SecurityConfig)

### 목적
Spring Security 기반 인증/인가 설정

### 주요 설정

#### 보안 필터 체인
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http
        .csrf().disable()
        .cors().configurationSource(corsConfigurationSource())
        .sessionManagement()
            .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
        .authorizeHttpRequests()
            .requestMatchers("/api/v1/auth/**").permitAll()
            .requestMatchers("/swagger-ui/**").permitAll()
            .requestMatchers("/v3/api-docs/**").permitAll()
            .anyRequest().authenticated()
        .addFilterBefore(jwtAuthenticationFilter,
                        UsernamePasswordAuthenticationFilter.class);
}
```

#### CORS 설정
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOrigins(Arrays.asList("http://localhost:3000"));
    configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    configuration.setAllowedHeaders(Arrays.asList("*"));
    configuration.setExposedHeaders(Arrays.asList("Authorization"));
    configuration.setAllowCredentials(true);
    configuration.setMaxAge(3600L);
}
```

#### 비밀번호 인코더
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // strength = 12
}
```

## 2. JWT 설정 (JwtConfig)

### 설정 속성
```yaml
jwt:
  secret: ${JWT_SECRET:phonebill-default-secret-key-for-development-only}
  access-token-validity: 3600  # 1시간 (초)
  refresh-token-validity: 86400  # 24시간 (초)
  issuer: phonebill-service
  audience: phonebill-client
```

### Bean 정의
```java
@Configuration
@ConfigurationProperties(prefix = "jwt")
public class JwtConfig {
    private String secret;
    private long accessTokenValidity;
    private long refreshTokenValidity;
    private String issuer;
    private String audience;
}
```

## 3. Redis 설정 (RedisConfig)

### 연결 설정
```java
@Bean
public LettuceConnectionFactory redisConnectionFactory() {
    RedisStandaloneConfiguration config =
        new RedisStandaloneConfiguration();
    config.setHostName(redisHost);
    config.setPort(redisPort);
    config.setDatabase(redisDatabase);
    if (StringUtils.hasText(redisPassword)) {
        config.setPassword(redisPassword);
    }

    LettucePoolingClientConfiguration poolConfig =
        LettucePoolingClientConfiguration.builder()
            .poolConfig(genericObjectPoolConfig())
            .commandTimeout(Duration.ofSeconds(10))
            .build();

    return new LettuceConnectionFactory(config, poolConfig);
}
```

### 연결 풀 설정
```java
@Bean
public GenericObjectPoolConfig genericObjectPoolConfig() {
    GenericObjectPoolConfig poolConfig = new GenericObjectPoolConfig();
    poolConfig.setMaxTotal(10);
    poolConfig.setMaxIdle(8);
    poolConfig.setMinIdle(2);
    poolConfig.setMaxWaitMillis(5000);
    return poolConfig;
}
```

### RedisTemplate 설정
```java
@Bean
public RedisTemplate<String, Object> redisTemplate() {
    RedisTemplate<String, Object> template = new RedisTemplate<>();
    template.setConnectionFactory(redisConnectionFactory());

    // 직렬화 설정
    template.setKeySerializer(new StringRedisSerializer());
    template.setHashKeySerializer(new StringRedisSerializer());
    template.setValueSerializer(new Jackson2JsonRedisSerializer<>(Object.class));
    template.setHashValueSerializer(new Jackson2JsonRedisSerializer<>(Object.class));

    template.afterPropertiesSet();
    return template;
}
```

### 캐시 매니저
```java
@Bean
public RedisCacheManager cacheManager() {
    RedisCacheConfiguration config = RedisCacheConfiguration
        .defaultCacheConfig()
        .entryTtl(Duration.ofHours(1))
        .serializeKeysWith(RedisSerializationContext.SerializationPair
            .fromSerializer(new StringRedisSerializer()))
        .serializeValuesWith(RedisSerializationContext.SerializationPair
            .fromSerializer(new Jackson2JsonRedisSerializer<>(Object.class)))
        .disableCachingNullValues();

    return RedisCacheManager.builder(redisConnectionFactory())
        .cacheDefaults(config)
        .transactionAware()
        .build();
}
```

## 4. Circuit Breaker 설정 (CircuitBreakerConfig)

### Resilience4j 설정
```java
@Bean
public CircuitBreakerFactory circuitBreakerFactory() {
    CircuitBreakerConfig config = CircuitBreakerConfig.custom()
        .failureRateThreshold(50)  // 실패율 임계값 50%
        .waitDurationInOpenState(Duration.ofSeconds(30))  // Open 상태 유지 시간
        .slidingWindowSize(10)  // 슬라이딩 윈도우 크기
        .permittedNumberOfCallsInHalfOpenState(3)  // Half-Open 시 허용 호출 수
        .automaticTransitionFromOpenToHalfOpenEnabled(true)
        .recordExceptions(IOException.class, TimeoutException.class)
        .ignoreExceptions(BusinessException.class)
        .build();

    CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);

    return new Resilience4JCircuitBreakerFactory(registry, config);
}
```

### 서킷별 커스텀 설정
```java
@Bean
public CircuitBreaker kosCircuitBreaker() {
    return CircuitBreaker.of("kos-service",
        CircuitBreakerConfig.custom()
            .failureRateThreshold(30)  // KOS는 더 민감하게
            .waitDurationInOpenState(Duration.ofSeconds(60))
            .build()
    );
}
```

## 5. JPA 설정 (JpaConfig/JpaAuditingConfig)

### JPA 속성
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        use_sql_comments: true
        default_batch_fetch_size: 100
        jdbc:
          batch_size: 25
        order_inserts: true
        order_updates: true
```

### Auditing 설정
```java
@Configuration
@EnableJpaAuditing
public class JpaAuditingConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
            .map(SecurityContext::getAuthentication)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName);
    }
}
```

## 6. RestTemplate 설정 (RestTemplateConfig)

### 기본 RestTemplate
```java
@Bean
public RestTemplate restTemplate() {
    HttpComponentsClientHttpRequestFactory factory =
        new HttpComponentsClientHttpRequestFactory();
    factory.setConnectionRequestTimeout(5000);
    factory.setConnectTimeout(5000);
    factory.setReadTimeout(10000);

    RestTemplate restTemplate = new RestTemplate(factory);

    // 인터셉터 추가
    restTemplate.setInterceptors(Arrays.asList(
        new LoggingInterceptor(),
        new JwtInterceptor()
    ));

    // 에러 핸들러
    restTemplate.setErrorHandler(new CustomResponseErrorHandler());

    return restTemplate;
}
```

### 로드밸런싱 RestTemplate
```java
@Bean
@LoadBalanced
public RestTemplate loadBalancedRestTemplate() {
    return new RestTemplateBuilder()
        .setConnectTimeout(Duration.ofSeconds(5))
        .setReadTimeout(Duration.ofSeconds(10))
        .interceptors(new LoadBalancerInterceptor())
        .build();
}
```

## 7. Swagger 설정 (SwaggerConfig)

### OpenAPI 설정
```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title("PhoneBill API")
            .version("1.0.0")
            .description("MVNO 통신요금 조회 서비스 API")
            .contact(new Contact()
                .name("개발팀")
                .email("dev@phonebill.com")))
        .addSecurityItem(new SecurityRequirement().addList("bearerAuth"))
        .components(new Components()
            .addSecuritySchemes("bearerAuth", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")));
}
```

### 그룹별 API 문서
```java
@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder()
        .group("public")
        .pathsToMatch("/api/v1/auth/**")
        .build();
}

@Bean
public GroupedOpenApi privateApi() {
    return GroupedOpenApi.builder()
        .group("private")
        .pathsToMatch("/api/v1/**")
        .pathsToExclude("/api/v1/auth/**")
        .build();
}
```

## 8. Gateway 설정 (GatewayConfig)

### 라우팅 설정
```java
@Bean
public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("user-service", r -> r.path("/api/v1/users/**", "/api/v1/auth/**")
            .filters(f -> f
                .rewritePath("/api/v1/(?<segment>.*)", "/${segment}")
                .addRequestHeader("X-Service", "user-service"))
            .uri("lb://USER-SERVICE"))
        .route("bill-service", r -> r.path("/api/v1/bills/**")
            .filters(f -> f
                .rewritePath("/api/v1/(?<segment>.*)", "/${segment}")
                .circuitBreaker(config -> config.setName("bill-cb")))
            .uri("lb://BILL-SERVICE"))
        .route("product-service", r -> r.path("/api/v1/products/**")
            .filters(f -> f
                .rewritePath("/api/v1/(?<segment>.*)", "/${segment}")
                .retry(config -> config.setRetries(3)))
            .uri("lb://PRODUCT-SERVICE"))
        .build();
}
```

### 글로벌 필터
```java
@Bean
public GlobalFilter customGlobalFilter() {
    return (exchange, chain) -> {
        exchange.getRequest().mutate()
            .header("X-Request-Id", UUID.randomUUID().toString())
            .build();
        return chain.filter(exchange);
    };
}
```

## 9. WebFlux 설정 (WebFluxConfig)

### CORS 설정
```java
@Bean
public CorsWebFilter corsWebFilter() {
    CorsConfiguration corsConfig = new CorsConfiguration();
    corsConfig.setAllowedOrigins(Arrays.asList("*"));
    corsConfig.setMaxAge(3600L);
    corsConfig.addAllowedMethod("*");
    corsConfig.addAllowedHeader("*");

    UrlBasedCorsConfigurationSource source =
        new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", corsConfig);

    return new CorsWebFilter(source);
}
```

## 10. 외부 시스템 설정 (KosProperties)

### KOS 시스템 연동 설정
```java
@Component
@ConfigurationProperties(prefix = "kos")
public class KosProperties {
    private String baseUrl = "http://localhost:8090";
    private int connectionTimeout = 5000;
    private int readTimeout = 10000;
    private int maxRetries = 3;
    private String apiKey;
    private boolean useMock = true;
}
```

## 11. 데이터 초기화 (DataInitializer)

### 개발 환경 초기 데이터
```java
@Component
@Profile("dev")
public class DataInitializer implements ApplicationRunner {

    @Override
    public void run(ApplicationArguments args) {
        // 테스트 사용자 생성
        createTestUser("test01", "password123", "CUST001");

        // 기본 권한 생성
        createPermission("USER", "일반 사용자");
        createPermission("ADMIN", "관리자");

        // 샘플 상품 데이터
        createSampleProducts();
    }
}
```

## 12. 인증 설정 (AuthConfig)

### 로그인 정책
```java
@Component
@ConfigurationProperties(prefix = "auth")
public class AuthConfig {
    private int maxFailedAttempts = 5;  // 최대 실패 횟수
    private long lockoutDuration = 1800000;  // 30분 (밀리초)
    private boolean requirePasswordChange = false;  // 비밀번호 변경 강제
    private int passwordExpiryDays = 90;  // 비밀번호 만료 기간
}
```

## 설정 우선순위

1. 명령줄 인자
2. 환경 변수
3. application-{profile}.yml
4. application.yml
5. @ConfigurationProperties 기본값

## 프로파일별 설정

### 개발 환경 (dev)
- 디버그 로깅 활성화
- Swagger UI 활성화
- Mock 서비스 사용
- H2 인메모리 DB (선택적)

### 운영 환경 (prod)
- 정보 레벨 로깅
- Swagger UI 비활성화
- 실제 KOS 시스템 연동
- PostgreSQL DB

### 테스트 환경 (test)
- 테스트용 설정
- 임베디드 Redis
- 모든 Mock 활성화