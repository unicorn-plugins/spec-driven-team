# Spec-Driven Team

> 느슨한 명세-코드 양방향 동기화로 소프트웨어를 유지보수하는 팀

---

## 개요

Spec-Driven Team은 명세와 코드 간 양방향 동기화를 통해 일관성을 보장하는 DMAP 플러그인입니다.
코드로부터 명세를 자동 생성하고, 명세 변경 시 코드를 자동 재생성하며, AI 어플리케이션 분리를 권고합니다.

**주요 기능:**
- 코드베이스 분석 + 명세화 가능 영역 분류
- 명세 자동 생성 (코드 → 명세) + 코드 자동 재생성 (명세 → 코드)
- 양방향 동기화 (느슨한 동기화) + 실시간 모니터링
- AI 어플리케이션 분리 권고 (MCP 서버, LangChain)
- 회귀 테스트 + 성능 비교

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
claude plugin install spec-driven-team@unicorn-plugins

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
> - `gateway/install.yaml`을 읽어 필수 MCP 서버 (context7) 자동 설치
> - 초기 디렉토리 생성 (specs/, .omc/, .backup/)
> - 상태 파일 초기화 (sync-pending.json, sync-history.json)

### 처음 GitHub을 사용하시나요?

다음 가이드를 참고하세요:

- [GitHub 계정 생성 가이드](https://github.com/unicorn-plugins/dmap/blob/main/resources/guides/github/github-account-setup.md)
- [Personal Access Token 생성 가이드](https://github.com/unicorn-plugins/dmap/blob/main/resources/guides/github/github-token-guide.md)

---

## 업그레이드

### Git Repository 마켓플레이스

```bash
# 마켓플레이스 업데이트 (최신 커밋 반영)
claude plugin marketplace update unicorn-plugins

# 플러그인 재설치
claude plugin install spec-driven-team@unicorn-plugins

# setup 재실행 (새 도구 설치)
/spec-driven-team:setup
```

### 로컬 마켓플레이스

```bash
# 1. 로컬 플러그인 소스 갱신
cd ~/workspace/spec-driven-team
git pull origin main

# 2. 마켓플레이스 업데이트
claude plugin marketplace update local

# 3. 플러그인 재설치
claude plugin install spec-driven-team@local

# 4. setup 재실행
/spec-driven-team:setup
```

---

## 사용법

### 슬래시 명령

| 명령 | 설명 |
|------|------|
| `/spec-driven-team:setup` | 초기 설정 (MCP 서버, 디렉토리 생성) |
| `/spec-driven-team:analyze` | 코드베이스 분석 + AI 앱 권고 |
| `/spec-driven-team:generate` | 명세 생성 (코드 → 명세) |
| `/spec-driven-team:sync` | 양방향 동기화 (명세 ↔ 코드) |
| `/spec-driven-team:watch` | 상태 모니터링 + 불일치 감지 |
| `/spec-driven-team:verify` | 회귀 테스트 + 성능 비교 |
| `/spec-driven-team:add-ext-skill` | 외부호출 스킬 추가 |
| `/spec-driven-team:remove-ext-skill` | 외부호출 스킬 제거 |
| `/spec-driven-team:help` | 사용 안내 |

### 워크플로우

#### Phase A: Explore (탐색)
```
/spec-driven-team:analyze
→ 코드 분석 + 명세화 영역 분류 + AI 앱 권고

/spec-driven-team:generate
→ 명세 생성 (선언적 로직: 완전 명세, 복잡한 로직: 스켈레톤)
```

#### Phase B: Develop (개발)
```
# specs/ 디렉토리에서 명세 수정

/spec-driven-team:sync
→ 명세 → 코드 자동 재생성

/spec-driven-team:verify
→ 회귀 테스트 + 성능 비교
```

#### Phase C: Maintain (유지)
```
/spec-driven-team:watch
→ 상태 모니터링 (불일치 감지)

# 불일치 감지 시
/spec-driven-team:sync
→ 양방향 동기화
```

### 사용 예시

```
사용자: "프로젝트 코드를 분석해서 명세로 만들어줘"

1. /spec-driven-team:analyze
   → analyzer 에이전트가 전체 코드베이스 분석
   → 선언적 로직 28개, 복잡한 로직 7개 분류
   → AI 어플리케이션 분리 권고 3개 생성

2. /spec-driven-team:generate
   → spec-manager 에이전트가 명세 자동 생성
   → specs/ 디렉토리에 35개 명세 파일 생성
   → Git 커밋

결과: 코드 → 명세 완전 동기화 ✅
```

---

## 에이전트 구성

| 에이전트 | 티어 | 역할 |
|----------|------|------|
| analyzer | HIGH | 코드베이스 분석 + 명세화 영역 분류 + AI 앱 권고 |
| spec-manager | HIGH | 명세 생성 + 명세 현행화 + 명세 버전 관리 |
| code-generator | MEDIUM | 명세 → 코드 자동 재생성 (선언적 로직) |
| quality-guardian | MEDIUM | 동기화 모니터링 + 불일치 감지 + 회귀 테스트 |

---

## 요구사항

### 필수 도구

| 도구 | 유형 | 용도 |
|------|------|------|
| context7 | MCP | AI 프레임워크 공식 문서 검색 (LangChain, MCP) |
| spec_analyzer.py | Custom | AST 기반 명세화 가능 영역 분류 |
| sync_checker.py | Custom | 명세-코드 불일치 감지 |
| code_generator.py | Custom | 명세 → 코드 자동 생성 |

### 런타임 호환성

| 런타임 | 지원 |
|--------|:----:|
| Claude Code | ✅ |
| Codex CLI | 미검증 |
| Gemini CLI | 미검증 |

---

## 디렉토리 구조

```
spec-driven-team/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── core/
│   ├── setup/
│   ├── help/
│   ├── add-ext-skill/
│   ├── remove-ext-skill/
│   ├── analyze/
│   ├── generate/
│   ├── sync/
│   ├── watch/
│   └── verify/
├── agents/
│   ├── analyzer/
│   ├── spec-manager/
│   ├── code-generator/
│   └── quality-guardian/
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
│   ├── setup.md
│   ├── help.md
│   ├── add-ext-skill.md
│   ├── remove-ext-skill.md
│   ├── analyze.md
│   ├── generate.md
│   ├── sync.md
│   ├── watch.md
│   └── verify.md
└── README.md
```

---

## 라이선스

MIT License

---

## 문의 및 피드백

- GitHub: https://github.com/unicorn-plugins/spec-driven-team
- Issues: https://github.com/unicorn-plugins/spec-driven-team/issues
