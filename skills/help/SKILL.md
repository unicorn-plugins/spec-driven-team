---
name: help
description: spec-driven-team 플러그인 사용 안내
type: utility
user-invocable: true
---

# Help

[HELP 활성화]

## 목표

spec-driven-team 플러그인의 사용법을 사용자에게 안내함.
모든 명령어, 워크플로우, 예시를 포함한 종합 가이드를 즉시 출력함.

## 활성화 조건

- 사용자가 `/spec-driven-team:help` 호출 시
- "도움말", "사용법", "명령어" 키워드 감지 시

## 출력 (즉시 출력)

```markdown
# spec-driven-team Plugin 사용 안내

## 개요
명세-코드 양방향 동기화로 소프트웨어를 유지보수하는 팀

## 주요 기능
✅ 코드베이스 분석 + 명세화 가능 영역 분류
✅ 명세 자동 생성 (코드 → 명세)
✅ 코드 자동 재생성 (명세 → 코드)
✅ 양방향 동기화 (느슨한 동기화)
✅ AI 어플리케이션 분리 권고

## 명령어

| 명령 | 설명 (한글) | 설명 (English) |
|------|------------|----------------|
| `/spec-driven-team:setup` | 초기 설정 | Initial setup |
| `/spec-driven-team:analyze` | 코드베이스 분석 및 명세화 영역 분류 | Codebase analysis and specifiable area classification |
| `/spec-driven-team:generate` | 코드 기반 명세 자동 생성 | Code-to-spec automatic generation |
| `/spec-driven-team:sync` | 명세-코드 양방향 동기화 | Spec-code bidirectional synchronization |
| `/spec-driven-team:verify` | 회귀 테스트 및 성능 비교 | Regression testing and performance comparison |
| `/spec-driven-team:watch` | 동기화 상태 모니터링 및 불일치 감지 | Sync status monitoring and inconsistency detection |
| `/spec-driven-team:add-ext-skill` | 외부호출 스킬 추가 | Add external skill |
| `/spec-driven-team:remove-ext-skill` | 외부호출 스킬 제거 | Remove external skill |
| `/spec-driven-team:help` | 사용 안내 | Usage guide |

## 워크플로우

### Phase A: 탐색 (Explore)

**핵심 스킬:**
- **코드베이스 분석** (`analyze`) — 코드베이스 분석 및 명세화 영역 분류
- **명세 생성** (`generate`) — 코드 기반 명세 자동 생성

**실행:**
1. `/spec-driven-team:analyze` - 코드 분석 + 명세화 영역 분류
2. `/spec-driven-team:generate` - 명세 생성
3. 사용자가 명세 검토 및 수정

### Phase B: 개발 (Develop)

**핵심 스킬:**
- **양방향 동기화** (`sync`) — 명세-코드 양방향 동기화
- **검증 및 테스트** (`verify`) — 회귀 테스트 및 성능 비교

**실행:**
1. 명세 파일 수정 (specs/ 디렉토리)
2. `/spec-driven-team:sync` - 명세 → 코드 자동 재생성
3. `/spec-driven-team:verify` - 회귀 테스트

### Phase C: 유지 (Maintain)

**핵심 스킬:**
- **상태 모니터링** (`watch`) — 동기화 상태 모니터링 및 불일치 감지

**실행:**
1. `/spec-driven-team:watch` - 상태 모니터링
2. 불일치 감지 시 자동 알림
3. `/spec-driven-team:sync` - 동기화

## 예시

### 1. 신규 프로젝트 명세화
```
/spec-driven-team:setup
/spec-driven-team:analyze
/spec-driven-team:generate
```

### 2. 명세 기반 개발
```
# specs/api/users.md 수정
/spec-driven-team:sync
/spec-driven-team:verify
```

### 3. 코드 변경 후 명세 현행화
```
# src/api/users.py 수정
/spec-driven-team:watch
→ 불일치 감지 → 사용자 선택 (자동/수동/나중에)
```

## 디렉토리 구조

```
your-project/
├── specs/              # 명세 파일 (Markdown/YAML/JSON)
│   ├── api/
│   ├── models/
│   └── config/
├── .omc/               # 플러그인 상태 파일
│   ├── sync-pending.json
│   ├── sync-history.json
│   └── reports/
└── .backup/            # 코드 변경 백업
```

## FAQ

**Q: 명세 형식은 무엇을 사용하나요?**
A: Hybrid 방식 — 복잡도에 따라 Markdown/YAML/JSON 자동 선택

**Q: 모든 코드를 명세화해야 하나요?**
A: 아니요. 선언적 로직(CRUD, 데이터 변환, 검증)만 완전 명세화.
   복잡한 로직은 스켈레톤 + 구현 참조 링크만 생성

**Q: 코드를 직접 수정하면 어떻게 되나요?**
A: watch 스킬이 불일치를 감지하고 알림.
   자동 현행화 / 수동 수정 / 나중에 중 선택 가능

**Q: AI 어플리케이션 분리 권고는 무엇인가요?**
A: 선언적 로직 중 MCP 서버, LangChain 등으로 분리 가능한
   영역을 자동 식별하여 권고 레포트 생성

## 문의 및 피드백
GitHub: https://github.com/unicorn-plugins/spec-driven-team
```

## MUST 규칙

- [ ] 모든 명령어를 빠짐없이 나열
- [ ] 워크플로우 예시 포함
- [ ] 즉시 출력 (에이전트 위임 없음)

## MUST NOT 규칙

- [ ] 에이전트에 위임하지 않음 (직결형 스킬)
- [ ] 파일 읽기/쓰기 하지 않음

## 검증 체크리스트

- [ ] 모든 명령어가 나열되어 있는가
- [ ] 워크플로우 예시가 명확한가
- [ ] FAQ가 유용한가
