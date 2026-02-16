---
name: "setup"
description: "spec-driven-team 플러그인 초기 설정"
user-invocable: true
model: "sonnet"
---

# setup

[spec-driven-team 플러그인 설정 마법사 활성화]

## 목표

spec-driven-team 플러그인의 도구 인프라를 설치하고 설정하여 사용 준비를 완료함.

## 활성화 조건

- 플러그인 최초 설치 후 사용자가 `/spec-driven-team:setup` 호출
- 도구 인프라 업데이트 필요 시

## 워크플로우

### Step 1: 설치 매니페스트 로드
`gateway/install.yaml`을 읽어 설치할 도구 목록 확인:
- MCP 서버: context7 (AI 프레임워크 문서 검색)
- LSP 서버: python-lsp-server, typescript-language-server, rust-analyzer
- 커스텀 도구: spec-watcher, complexity-analyzer, spec-validator

### Step 2: MCP 서버 설치
**context7 서버 설치**:
```bash
claude mcp add-json gateway/mcp/context7.json --scope user
```

설치 확인:
```bash
claude mcp list | grep context7
```

### Step 3: LSP 서버 설치
**Python LSP 서버**:
```bash
# 설치 전 확인
python -m pylsp --version 2>/dev/null || pip install python-lsp-server[all]
```

**TypeScript LSP 서버**:
```bash
# 설치 전 확인
typescript-language-server --version 2>/dev/null || npm install -g typescript typescript-language-server
```

**Rust Analyzer** (선택사항):
```bash
# 설치 전 확인
rust-analyzer --version 2>/dev/null || rustup component add rust-analyzer
```

### Step 4: 커스텀 도구 설치
각 커스텀 도구의 의존성 설치:

**spec-watcher 도구**:
```bash
cd gateway/tools/customs/spec-watcher
pip install -r requirements.txt
```

**complexity-analyzer 도구**:
```bash
cd gateway/tools/customs/complexity-analyzer
pip install -r requirements.txt
```

**spec-validator 도구**:
```bash
cd gateway/tools/customs/spec-validator
npm install
```

### Step 5: 디렉토리 구조 초기화
프로젝트에 필요한 디렉토리 생성:
```bash
mkdir -p specs/ .omc/{reports,state}
```

`.omc/` 디렉토리 설명:
- `reports/`: AI 어플리케이션 권고 레포트 저장
- `state/`: 동기화 상태 및 이력 파일 저장

### Step 6: 사용 범위 설정
사용자에게 플러그인 적용 범위 질문:

**선택지**:
- **모든 프로젝트**: `~/.claude/CLAUDE.md`에 라우팅 테이블 추가
- **이 프로젝트만**: `./CLAUDE.md`에 라우팅 테이블 추가

**라우팅 테이블 예시**:
```markdown
## spec-driven-team 플러그인

다음 요청은 자동으로 spec-driven-team 플러그인이 처리합니다:
- "코드베이스 분석", "명세 생성" → /spec-driven-team:analyze-classify
- "명세 현행화", "코드→명세 동기화" → /spec-driven-team:sync-code-to-spec
- "AI 어플리케이션 권고" → /spec-driven-team:recommend-ai-app
- "동기화 상태 확인" → /spec-driven-team:monitor-sync-status
```

### Step 7: 설치 결과 요약
설치 완료된 도구 목록과 실패한 항목(있는 경우) 요약 보고:

```
🎉 spec-driven-team 플러그인 설정 완료!

✅ 설치 완료:
- MCP 서버: context7
- LSP 서버: python-lsp-server, typescript-language-server
- 커스텀 도구: spec-watcher, complexity-analyzer

⚠️ 선택사항 (미설치):
- rust-analyzer (Rust 프로젝트에서만 필요)

📁 디렉토리 생성:
- specs/ (명세 파일 저장)
- .omc/reports/ (분석 레포트)
- .omc/state/ (동기화 상태)

🚀 사용 준비 완료! 다음 명령으로 시작하세요:
/spec-driven-team:analyze-classify
```

## MUST 규칙

1. `gateway/install.yaml`의 모든 required=true 항목은 반드시 설치 성공해야 함
2. 설치 전 `check` 명령으로 기존 설치 여부 확인하여 중복 설치 방지
3. MCP 서버는 user 스코프로 설치 (프로젝트별 격리 불필요)
4. 사용자에게 적용 범위 선택권 제공 (global vs project)

## MUST NOT 규칙

1. 설치 실패 시에도 계속 진행하지 말고 중단 및 사용자 안내
2. 기존 설치된 도구를 강제로 재설치하지 않음
3. 사용자 동의 없이 시스템 전역 설정 변경 금지
4. 네트워크 연결 없이 온라인 도구 설치 시도 금지

## 검증 체크리스트

- [ ] `gateway/install.yaml`의 모든 required 도구가 정상 설치됨
- [ ] MCP 서버가 `claude mcp list`에서 확인됨
- [ ] LSP 서버가 `--version` 명령으로 동작 확인됨
- [ ] 필수 디렉토리가 올바른 권한으로 생성됨
- [ ] 라우팅 테이블이 선택된 범위에 정확히 추가됨
- [ ] 설치 실패 항목에 대한 명확한 사용자 안내 제공됨