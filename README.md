# Spec-Driven Team

> 명세 중심 개발 플러그인 - 명세와 코드의 양방향 동기화로 유지보수 효율 극대화

---

## 개요

Spec-Driven Team은 명세(Specification)를 코드의 단일 진실 원천(Single Source of Truth)으로 활용하여 애플리케이션을 유지보수하는 DMAP 플러그인입니다. 코드베이스를 분석하여 자동으로 명세를 생성하고, 명세 수정 시 코드를 재생성하며, 코드 변경 시 명세를 현행화하는 느슨한 양방향 동기화를 제공합니다.

**주요 기능:**
- 전체 코드베이스 자동 분석 및 명세 생성 (선언적 로직 완전 명세화)
- 명세 → 코드 자동 재생성 (변경 감지 + 자동 적용)
- **코드 → 명세 역동기화** ⭐ (수동 실행 + 파일별 승인/거부)
- 명세-코드 동기화 상태 모니터링 (불일치 파일 추적)
- AI 어플리케이션 분리 권고 (AI 에이전트, MCP 서버 후보 식별)

---

## 설치

### 사전 요구사항

- [Claude Code](https://claude.com/claude-code) CLI 설치
- Python 3.9+ (LSP 서버용)
- Node.js 18+ (TypeScript LSP 서버용)

### 플러그인 설치

**방법 1: 마켓플레이스 — GitHub (권장)**

```bash
# 1. GitHub 저장소를 마켓플레이스로 등록
claude plugin marketplace add {owner}/spec-driven-team

# 2. 플러그인 설치
claude plugin install spec-driven-team@{marketplace-name}

# 3. 설치 확인
claude plugin list
```

**방법 2: 마켓플레이스 — 로컬**

```bash
# 1. 로컬 경로를 마켓플레이스로 등록
claude plugin marketplace add ~/workspace/spec-driven-team

# 2. 플러그인 설치
claude plugin install spec-driven-team@local

# 3. 설치 확인
claude plugin list
```

> **설치 후 setup 스킬 실행:**
> ```
> /spec-driven-team:setup
> ```
> - LSP 서버 자동 설치 (Python, TypeScript)
> - MCP 서버 설치 (Context7)
> - 플러그인 활성화 확인

---

## 업그레이드

### Git Repository 마켓플레이스

```bash
# 마켓플레이스 업데이트
claude plugin marketplace update {marketplace-name}

# 플러그인 재설치
claude plugin install spec-driven-team@{marketplace-name}
```

### 로컬 마켓플레이스

로컬 디렉토리 변경 후 플러그인 재설치:

```bash
claude plugin install spec-driven-team@local
```

---

## 사용법

### 1. 초기 명세화 (코드 → 명세)

```bash
# Step 1-2: 코드베이스 분석 + 명세화 가능 영역 분류
/spec-driven-team:analyze-classify

# Step 3: 명세 자동 생성
/spec-driven-team:generate-spec

# Step 4: AI 어플리케이션 분리 권고
/spec-driven-team:recommend-ai-app
```

**출력:**
- `specs/v1.0.0/{domain}/{component}.md` - 생성된 명세 파일
- `.omc/analysis-report.json` - 분석 결과
- `.omc/reports/ai-application-recommendations.md` - AI 어플리케이션 권고

### 2. 명세 기반 개발 (명세 → 코드)

```bash
# 명세 파일 수정 후:
/spec-driven-team:sync-spec

# 또는 자동 감시 모드:
/spec-driven-team:watch-spec
```

### 3. 코드 변경 후 명세 현행화 (코드 → 명세) ⭐

```bash
# 수동 역동기화 실행
/spec-driven-team:sync-code-to-spec
```

**워크플로우:**
1. 대상 선택: 전체 / 특정 디렉토리 / 특정 파일 / 불일치 파일만
2. 코드 분석 및 명세 diff 생성
3. 파일별 승인/거부 선택
4. 승인된 항목만 명세 업데이트
5. Git 커밋 + 동기화 이력 기록

### 4. 동기화 상태 모니터링

```bash
# 명세-코드 동기화 상태 확인
/spec-driven-team:monitor-sync-status

# 불일치 해소
/spec-driven-team:resolve-conflict
```

### 5. 검증

```bash
# 회귀 테스트 + 성능 비교
/spec-driven-team:verify-regenerated
```

---

## 명령어

| 명령 | 설명 |
|------|------|
| `/spec-driven-team:setup` | 플러그인 초기 설정 |
| `/spec-driven-team:help` | 사용 안내 |
| `/spec-driven-team:analyze-classify` | 코드베이스 분석 + 명세화 가능 영역 분류 |
| `/spec-driven-team:generate-spec` | 명세 자동 생성 |
| `/spec-driven-team:recommend-ai-app` | AI 어플리케이션 분리 권고 |
| `/spec-driven-team:watch-spec` | 명세 변경 감지 (백그라운드) |
| `/spec-driven-team:sync-spec` | 명세 → 코드 동기화 |
| `/spec-driven-team:sync-code-to-spec` | **코드 → 명세 역동기화 (수동)** ⭐ |
| `/spec-driven-team:monitor-sync-status` | 동기화 상태 확인 |
| `/spec-driven-team:resolve-conflict` | 불일치 해소 |
| `/spec-driven-team:verify-regenerated` | 회귀 테스트 + 성능 비교 |
| `/spec-driven-team:add-ext-skill` | 외부 플러그인 호출 스킬 추가 |
| `/spec-driven-team:remove-ext-skill` | 외부 플러그인 호출 스킬 제거 |

---

## 요구사항

### 필수 도구

플러그인이 자동으로 설치를 시도합니다 (`/spec-driven-team:setup`):

- **LSP 서버:**
  - `python-lsp-server` - Python 코드 분석
  - `typescript-language-server` - JavaScript/TypeScript 코드 분석
  
- **MCP 서버:**
  - `context7` - AI 프레임워크 공식 문서 검색

### 선택 도구

- `rust-analyzer` - Rust 코드 분석 (Rust 프로젝트인 경우)

---

## 동기화 모델

### 느슨한 양방향 동기화 (Loose Bidirectional Sync)

```
명세 ↔ 코드 (양방향)
- 완벽한 일치 불필요
- 일시적 불일치 허용
- 주기적 동기화
```

### 성공 사례 참조

- **OpenAPI/Swagger**: 스펙 ↔ 코드 동기화
- **GraphQL**: 스키마 ↔ 리졸버 동기화
- **gRPC/Protobuf**: .proto ↔ 코드 동기화

---

## 디렉토리 구조

```
{프로젝트}/
├── specs/                          # 명세 파일 (버전별)
│   └── v1.0.0/
│       ├── auth/
│       │   └── login.md
│       └── user/
│           └── crud.md
├── .omc/                           # 플러그인 작업 디렉토리
│   ├── analysis-report.json       # 코드베이스 분석 결과
│   ├── sync-pending.json          # 불일치 파일 목록
│   ├── sync-history.json          # 동기화 이력
│   └── reports/
│       └── ai-application-recommendations.md
└── src/                            # 소스 코드
```

---

## 라이선스

MIT License
