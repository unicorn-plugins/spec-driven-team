---
name: remove-ext-skill
description: 외부호출 스킬 제거 유틸리티
user-invocable: true
---

# Remove External Skill

[REMOVE-EXT-SKILL 활성화]

## 목표

기존 ext-{대상플러그인} 스킬을 제거하여
불필요한 외부 플러그인 연동을 정리함.

## 활성화 조건

- 사용자가 `/spec-driven-team:remove-ext-skill` 호출 시
- "외부 스킬 제거", "플러그인 연동 해제" 키워드 감지 시

## 워크플로우

### Step 1. 기존 ext-{} 스킬 목록 조회

`skills/` 디렉토리에서 `ext-` 접두사로 시작하는 하위 디렉토리 탐색:
```bash
ls skills/ | grep "^ext-"
```

ext-{} 스킬이 0개이면:
```
제거할 외부호출 스킬이 없습니다.
```
→ 종료

발견된 ext-{} 스킬 목록을 사용자에게 표시

### Step 2. 제거할 스킬 선택

{tool:AskUserQuestion}으로 제거할 ext-{대상플러그인} 스킬 선택

선택된 스킬의 SKILL.md를 읽어 스킬 정보(name, description) 표시

"정말 제거하시겠습니까?" 최종 확인 (AskUserQuestion: 예/아니오)

사용자가 취소하면 즉시 중단

### Step 3. ext-{대상플러그인} 스킬 디렉토리 삭제

`skills/ext-{대상플러그인}/` 디렉토리 전체 삭제:
```bash
rm -rf skills/ext-{대상플러그인}/
```

삭제 성공 여부 확인

### Step 4. commands/ 진입점 삭제

`commands/ext-{대상플러그인}.md` 파일 삭제:
```bash
rm -f commands/ext-{대상플러그인}.md
```

파일 미존재 시 무시 (이미 삭제된 상태일 수 있음)

### Step 5. help 스킬 업데이트

`skills/help/SKILL.md`의 명령 테이블에서 해당 행 제거:
```markdown
| `/spec-driven-team:ext-{대상플러그인}` | {대상플러그인} 외부호출 |
```
→ 삭제

제거 완료 메시지 출력:
```
✅ ext-{대상플러그인} 외부호출 스킬이 제거되었습니다.
```

## MUST 규칙

- [ ] 삭제 전 반드시 사용자 최종 확인을 받을 것
- [ ] ext-{} 접두사가 아닌 스킬(setup, help 등)은 제거 대상에서 제외할 것
- [ ] help 스킬의 명령 테이블에서 해당 행만 정확히 제거할 것 (다른 행 훼손 금지)

## MUST NOT 규칙

- [ ] ext-{} 접두사가 아닌 스킬 디렉토리를 삭제하지 않을 것
- [ ] 사용자 확인 없이 삭제를 수행하지 않을 것
- [ ] help 스킬의 명령 테이블 구조(헤더, 구분선)를 훼손하지 않을 것

## 검증 체크리스트

- [ ] ext-{} 스킬 0개일 때 조기 종료가 동작하는가
- [ ] 삭제 전 사용자 최종 확인 단계가 존재하는가
- [ ] skills/ext-{대상플러그인}/ 디렉토리가 완전히 삭제되었는가
- [ ] commands/ext-{대상플러그인}.md 파일이 삭제되었는가
- [ ] help 스킬의 명령 테이블에서 해당 행이 제거되었는가
- [ ] 다른 스킬/명령에 부수효과가 없는가
