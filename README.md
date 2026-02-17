# Spec-Driven Team

> 느슨한 명세-코드 양방향 동기화로 소프트웨어를 유지보수하는 팀

---

## 개요

Spec-Driven Team은 명세와 코드 간 양방향 동기화를 통해 일관성을 보장하는 DMAP 플러그인입니다.
코드로부터 명세를 자동 생성하고, 명세 변경 시 코드를 자동 재생성하며, AI 어플리케이션 분리를 권고합니다.

**핵심 원칙:**
- 명세 = Single Source of Truth (양방향 동기화)
- 느슨한 결합 — 완벽한 일치가 아닌 실용적 동기화
- 선언적 로직 우선 — 단순 로직은 완전 명세, 복잡한 로직은 스켈레톤
- 개발자 자율성 — 모든 변경은 사용자 승인 기반
- 하위 호환성 — 기존 명세 파괴 금지

**주요 기능:**
- 코드베이스 분석 + 복잡도 기반 분류 (선언적/복잡한 로직)
- 명세 자동 생성 (코드 → 명세) + 코드 자동 재생성 (명세 → 코드)
- 양방향 동기화 (느슨한 동기화) + 실시간 모니터링
- AI 어플리케이션 분리 권고 (MCP 서버, LangChain, Dify)
- 회귀 테스트 + 성능 비교
- 불일치 감지 + 충돌 해소

---

## 설치

### 사전 요구사항

- [Claude Code](https://claude.com/claude-code) CLI 설치
- Python 3.8+ (커스텀 도구 실행용)

### 플러그인 설치

**방법 1: 마켓플레이스 — GitHub (권장)**

```bash
# 1. GitHub 저장소를 마켓플레이스로 등록
claude plugin marketplace add unicorn-plugins/spec-driven-team

# 2. 플러그인 설치
claude plugin install spec-driven-team@spec-driven-team

# 3. 설치 확인
claude plugin list
```

**방법 2: 마켓플레이스 — 로컬**

```bash
# 1. 로컬 경로를 마켓플레이스로 등록
claude plugin marketplace add ~/workspace/spec-driven-team

# 2. 플러그인 설치
claude plugin install spec-driven-team@spec-driven-team

# 3. 설치 확인
claude plugin list
```

> **설치 후 setup 스킬 실행:**
> ```
> /spec-driven-team:setup
> ```
> - `gateway/install.yaml`을 읽어 필수 MCP 서버 (context7) 자동 설치
> - 초기 디렉토리 생성 (specs/, .omc/)
> - 상태 파일 초기화 (sync-pending.json, sync-history.json)

### 처음 GitHub을 사용하시나요?

다음 가이드를 참고하세요:

- [GitHub 계정 생성 가이드](https://github.com/unicorn-plugins/dmap/blob/main/resources/guides/github/github-account-setup.md)
- [Personal Access Token 생성 가이드](https://github.com/unicorn-plugins/dmap/blob/main/resources/guides/github/github-token-guide.md)

---

## 업그레이드

```bash
# 마켓플레이스 업데이트 (최신 커밋 반영)
claude plugin marketplace update unicorn-plugins

# 플러그인 재설치
claude plugin update spec-driven-team@spec-driven-team

# setup 재실행 (새 도구 설치)
/spec-driven-team:setup
```


---

## 아키텍처

### 3단계 워크플로우

```
Phase A: 탐색 (Explore)        Phase B: 개발 (Develop)       Phase C: 유지 (Maintain)
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ analyze-classify     │    │ sync-spec            │    │ sync-code-to-spec   │
│ generate-spec        │    │ watch-spec           │    │ monitor-sync-status │
│ recommend-ai-app     │    │                      │    │ resolve-conflict    │
│                      │    │                      │    │ verify-regenerated  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
        ↓                          ↓                          ↓
   /analyze               /sync                      /watch
   /generate              /verify                     /sync
                                                      /verify
```

### 복잡도 기반 분류 기준

| 구분 | 선언적 로직 (완전 명세) | 복잡한 로직 (스켈레톤) |
|------|------------------------|----------------------|
| 순환 복잡도 | ≤ 10 | > 10 |
| 중첩 깊이 | ≤ 4 | > 4 |
| 함수 크기 | ≤ 50 LOC | > 50 LOC |
| 예시 | CRUD, 데이터 변환, 유효성 검증 | 멀티스레딩, 실시간 처리, 성능 알고리즘 |

---

## 사용법

### 슬래시 명령 (Public API)

| 명령 | 설명 |
|------|------|
| `/spec-driven-team:setup` | 초기 설정 (MCP 서버, 디렉토리 생성) |
| `/spec-driven-team:analyze` | 코드베이스 분석 + 명세화 영역 분류 + AI 앱 권고 |
| `/spec-driven-team:generate` | 명세 생성 (코드 → 명세) |
| `/spec-driven-team:sync` | 양방향 동기화 (명세 ↔ 코드) |
| `/spec-driven-team:watch` | 상태 모니터링 + 불일치 감지 |
| `/spec-driven-team:verify` | 회귀 테스트 + 성능 비교 |
| `/spec-driven-team:add-ext-skill` | 외부호출 스킬 추가 |
| `/spec-driven-team:remove-ext-skill` | 외부호출 스킬 제거 |
| `/spec-driven-team:help` | 사용 안내 |

### 전체 스킬 구성 (19개)

#### 코어/유틸리티 (5개)

| 스킬 | 호출 방식 | 설명 |
|------|----------|------|
| core | 내부 | 플러그인 핵심 행동 규범 |
| setup | 사용자 | 초기 설정 + MCP 서버 설치 |
| help | 사용자 | 사용 안내 |
| add-ext-skill | 사용자 | 외부호출 스킬 추가 |
| remove-ext-skill | 사용자 | 외부호출 스킬 제거 |

#### Phase A: 탐색 — 초기 명세화 (3개)

| 스킬 | 호출 방식 | 설명 |
|------|----------|------|
| analyze-classify | 내부 (`analyze`가 호출) | LSP 기반 코드 분석 + 복잡도 분류 |
| generate-spec | 내부 (`generate`가 호출) | 코드 → 명세 자동 생성 (선언적: 완전, 복잡: 스켈레톤) |
| recommend-ai-app | 내부 (`analyze`가 호출) | AI 어플리케이션 분리 권고 (ROI 기반 우선순위) |

#### Phase B: 개발 — 명세 기반 개발 (2개)

| 스킬 | 호출 방식 | 설명 |
|------|----------|------|
| sync-spec | 내부 (`sync`가 호출) | 명세 → 코드 수동 재생성 (사용자 승인 기반) |
| watch-spec | 내부 (`watch`가 호출) | 명세 디렉토리 감시 + 변경 감지 시 자동 재생성 |

#### Phase C: 유지 — 명세 유지보수 (5개)

| 스킬 | 호출 방식 | 설명 |
|------|----------|------|
| sync-code-to-spec | 내부 (`sync`가 호출) | 코드 → 명세 역동기화 (파일별 승인/거부) |
| monitor-sync-status | 내부 (`watch`가 호출) | 동기화 상태 조회 + 7일 초과 불일치 경고 |
| resolve-conflict | 내부 (`sync`가 호출) | 불일치 해소 (자동 업데이트/수동 편집/코드 롤백/보류) |
| verify-regenerated | 내부 (`verify`가 호출) | 재생성 코드 회귀 테스트 + 성능 벤치마크 |
| watch | 사용자 | 상태 모니터링 (폴링 방식 불일치 감지) |

#### 상위 래퍼 스킬 (4개)

| 스킬 | 호출 방식 | 내부 호출 |
|------|----------|----------|
| analyze | 사용자 | analyze-classify → recommend-ai-app |
| generate | 사용자 | generate-spec |
| sync | 사용자 | sync-spec 또는 sync-code-to-spec (사용자 선택) |
| verify | 사용자 | verify-regenerated |

---

### 워크플로우

#### Phase A: 탐색 (Explore)

**목표:** 기존 코드베이스를 분석하고 명세를 자동 생성

```
/spec-driven-team:analyze
→ codebase-analyzer가 전체 코드 분석
→ 선언적 로직 vs 복잡한 로직 분류 (복잡도 기반)
→ AI 어플리케이션 분리 권고 생성

/spec-driven-team:generate
→ spec-generator가 명세 자동 생성
→ specs/v1.0.0/ 디렉토리에 명세 파일 저장
→ 선언적 로직: 완전 명세 / 복잡한 로직: 스켈레톤
```

#### Phase B: 개발 (Develop)

**목표:** 명세를 수정하고 코드를 자동 재생성

```
# specs/ 디렉토리에서 명세 수정

/spec-driven-team:sync
→ 명세 → 코드 자동 재생성 (sync-spec)
→ 선언적 로직: 자동 생성 / 복잡한 로직: 변경 제안만
→ 변경 전 자동 백업

/spec-driven-team:verify
→ 회귀 테스트 실행 (프레임워크 자동 감지)
→ 성능 비교 (변경 전후)
```

#### Phase C: 유지 (Maintain)

**목표:** 코드 변경 시 명세를 최신 상태로 유지

```
/spec-driven-team:watch
→ 동기화 상태 모니터링 (불일치 감지)
→ 7일 초과 불일치 파일 경고

# 불일치 감지 시
/spec-driven-team:sync
→ 코드 → 명세 역동기화 (sync-code-to-spec)
→ 파일별 승인/거부 선택
→ 충돌 시 resolve-conflict로 해소
```

---

## 에이전트 구성

### 운영 에이전트 (7개)

| 에이전트 | 티어 | 역할 |
|----------|------|------|
| codebase-analyzer | HIGH | 코드 구조 분석 + 복잡도 기반 분류 |
| spec-generator | HIGH | 코드 → 명세 변환 + 역동기화 |
| code-regenerator | MEDIUM | 명세 → 코드 자동 재생성 |
| verification-engineer | MEDIUM | 회귀 테스트 + 성능 벤치마크 |
| ai-app-advisor | MEDIUM | AI 어플리케이션 분리 권고 |
| spec-versioner | LOW | 명세 버전 관리 + 변경 감지 |
| sync-monitor | LOW | 동기화 상태 모니터링 + 드리프트 감지 |

### 에이전트 역할 매트릭스

| 에이전트 | 코드 읽기 | 분석 | 명세 생성 | 코드 생성 | 테스트 |
|----------|:-:|:-:|:-:|:-:|:-:|
| codebase-analyzer | O | O | - | - | - |
| spec-generator | O | - | O | - | - |
| code-regenerator | O | - | - | O | - |
| verification-engineer | O | - | - | - | O |
| ai-app-advisor | O | O | O | - | - |
| spec-versioner | O | - | - | - | - |
| sync-monitor | O | - | - | - | - |

---

## 요구사항

### 필수 도구

| 도구 | 유형 | 용도 |
|------|------|------|
| context7 | MCP | AI 프레임워크 공식 문서 검색 (LangChain, MCP, Dify) |
| spec_analyzer.py | Custom | AST 기반 명세화 가능 영역 분류 |
| sync_checker.py | Custom | 명세-코드 불일치 감지 |
| code_generator.py | Custom | 명세 → 코드 자동 생성 |

### 런타임 호환성

| 런타임 | 지원 |
|--------|:----:|
| Claude Code | O |
| Codex CLI | 미검증 |
| Gemini CLI | 미검증 |

---

## 디렉토리 구조

### 플러그인 구조

```
spec-driven-team/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/                         # 19개 스킬
│   ├── core/                       # 핵심 행동 규범
│   ├── setup/                      # 초기 설정
│   ├── help/                       # 사용 안내
│   ├── add-ext-skill/              # 외부호출 스킬 추가
│   ├── remove-ext-skill/           # 외부호출 스킬 제거
│   ├── analyze/                    # [래퍼] 코드베이스 분석
│   ├── analyze-classify/           # [내부] 복잡도 기반 분류
│   ├── generate/                   # [래퍼] 명세 생성
│   ├── generate-spec/              # [내부] 코드 → 명세 변환
│   ├── recommend-ai-app/           # [내부] AI 앱 분리 권고
│   ├── sync/                       # [래퍼] 양방향 동기화
│   ├── sync-spec/                  # [내부] 명세 → 코드
│   ├── sync-code-to-spec/          # [내부] 코드 → 명세
│   ├── watch/                      # [래퍼] 상태 모니터링
│   ├── watch-spec/                 # [내부] 명세 감시
│   ├── monitor-sync-status/        # [내부] 동기화 상태 조회
│   ├── resolve-conflict/           # [내부] 충돌 해소
│   ├── verify/                     # [래퍼] 회귀 테스트
│   └── verify-regenerated/         # [내부] 재생성 코드 검증
├── agents/                         # 10개 에이전트
│   ├── codebase-analyzer/
│   ├── spec-generator/
│   ├── code-regenerator/
│   ├── verification-engineer/
│   ├── ai-app-advisor/
│   ├── spec-versioner/
│   ├── sync-monitor/
│   ├── analyzer/                   # (레거시)
│   ├── spec-manager/               # (레거시)
│   └── quality-guardian/           # (레거시)
├── gateway/
│   ├── install.yaml
│   ├── runtime-mapping.yaml
│   ├── mcp/
│   │   └── context7.json
│   └── tools/
│       ├── spec_analyzer.py
│       ├── sync_checker.py
│       └── code_generator.py
├── commands/
├── resources/
├── requirements.md
└── README.md
```

### 사용자 프로젝트에 생성되는 출력 구조

```
your-project/
├── specs/                          # 명세 파일 (사용자 편집 가능)
│   └── v1.0.0/
│       ├── auth/
│       ├── api/
│       └── models/
├── output/                         # 모든 스킬 실행 결과
│   └── {project-name}/
│       ├── explore/                # Phase A: 탐색
│       │   ├── analyze-result.md
│       │   ├── codebase-analysis.md
│       │   ├── ai-application-recommendations.md
│       │   ├── generate-result.md
│       │   └── specs/
│       ├── develop/                # Phase B: 개발
│       │   ├── sync-result.md
│       │   ├── sync-report.md
│       │   ├── verify-result.md
│       │   ├── quality-report.md
│       │   ├── regression-test-results.json
│       │   ├── performance-comparison.json
│       │   └── backups/
│       └── maintain/               # Phase C: 유지
│           ├── watch-result.md
│           ├── sync-pending.json
│           ├── sync-history.json
│           ├── drift-detection-log.json
│           └── watch-status.json
└── .omc/                           # 상태 관리
    ├── analysis-report.json
    ├── sync-pending.json
    ├── sync-history.json
    ├── sync-state.json
    ├── watch-status.json
    ├── verification-report.json
    └── reports/
        └── ai-application-recommendations.md
```

**프로젝트명 결정 규칙:**
1. 사용자 명시적 지정
2. Git 저장소명
3. package.json의 name
4. 현재 디렉토리명
5. 기본값: `project`

---

## 사용 예시

### 프로젝트 처음 시작할 때

```
사용자: "프로젝트 코드를 분석해서 명세로 만들어줘"

1. /spec-driven-team:analyze
   → codebase-analyzer가 전체 코드베이스 분석
   → 선언적 로직 28개, 복잡한 로직 7개 분류
   → AI 어플리케이션 분리 권고 3개 생성

2. /spec-driven-team:generate
   → spec-generator가 명세 자동 생성
   → specs/v1.0.0/ 디렉토리에 35개 명세 파일 생성

결과: 코드 → 명세 완전 동기화
```

### 명세 기반 개발

```
1. specs/v1.0.0/features/ 에 새 명세 작성

2. /spec-driven-team:sync
   → 명세 → 코드 자동 재생성
   → 선언적 로직만 완전 재생성
   → 복잡한 로직은 변경 제안만 제공

3. /spec-driven-team:verify
   → 회귀 테스트 실행
   → 성능 비교 (변경 전후)
```

### 코드 수정 후 명세 업데이트

```
# 코드 수정 후

/spec-driven-team:watch
→ 불일치 감지 (3개 파일)

/spec-driven-team:sync
→ 코드 → 명세 역동기화
→ 파일별 승인/거부 선택
→ 승인된 변경만 명세에 반영
```

### AI 어플리케이션 분리

```
/spec-driven-team:analyze
→ AI 어플리케이션 분리 권고 자동 생성
→ "spec_analyzer를 MCP 서버로 분리 권장 (ROI: HIGH)"
→ 프레임워크 추천: LangChain, Dify, MCP SDK
```

---

## 라이선스

MIT License

---

## 문의 및 피드백

- GitHub: https://github.com/unicorn-plugins/spec-driven-team
- Issues: https://github.com/unicorn-plugins/spec-driven-team/issues
