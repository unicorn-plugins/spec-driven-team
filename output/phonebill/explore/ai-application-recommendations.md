# AI 어플리케이션 분리 권고 - PhoneBill

## 권고 #1: MCP 서버 - 요금 조회 자동화
- **대상 영역**: `bill-service` (요금 조회 서비스)
- **추천 기술**: Node/TypeScript + MCP SDK
- **기대 효과**: LLM 기반 자연어 요금 조회 지원, 요금 계산 로직 명세화

## 권고 #2: LangChain - 상품 추천 워크플로우
- **대상 영역**: `product-service` (상품 변경 서비스)
- **추천 기술**: Python + LangChain
- **기대 효과**: 고객 사용 패턴 기반 상품 추천, 자연어 기반 상품 상담 지원

## 권고 #3: MCP 서버 - API Gateway 인텔리전스
- **대상 영역**: `api-gateway`
- **추천 기술**: Node/TypeScript + MCP
- **기대 효과**: 동적 라우팅 규칙 관리, 요청 패턴 분석 및 최적화

## 권고 #4: LangChain - 테스트 데이터 생성
- **대상 영역**: `kos-mock` (Mock 서비스)
- **추천 기술**: Python + LangChain + Faker
- **기대 효과**: 실제와 유사한 테스트 데이터 자동 생성, 다양한 시나리오 테스트 케이스 생성
