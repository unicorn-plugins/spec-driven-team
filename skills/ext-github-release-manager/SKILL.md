---
name: ext-github-release-manager
description: github-release-manager 외부호출
user-invocable: true
---

# External: github-release-manager

## 목표

github-release-manager 플러그인의 워크플로우를 실행함.
spec-driven-team 프로젝트의 릴리스 문서를 자동 생성·수정·삭제하거나 구성을 추천받음.

## 활성화 조건

- 사용자가 `/spec-driven-team:ext-github-release-manager` 호출 시
- "릴리스 생성", "release 만들기", "release notes" 키워드 감지 시

## 도메인 컨텍스트 수집

프로젝트 특화 컨텍스트를 수집하여 외부 플러그인에 전달:

| 수집 대상 | 소스 | 용도 |
|----------|------|------|
| 프로젝트 디렉토리 | 현재 작업 디렉토리 (cwd) | `project_dir` ARGS 키 |
| 기존 릴리스 목록 | `gh release list --limit 10` | 경로 분기 판단 (첫 릴리스 여부) |
| Git 태그 목록 | `git tag --sort=-v:refname` | 버전 결정, `base_ref` 추론 |
| 최근 커밋 이력 | `git log {last_tag}..HEAD --oneline` | Release 본문 자동 생성 소스 |
| 릴리스 구성 파일 | `.github/release.yml` 존재 여부 | 경로 분기 판단 |
| 패키지 버전 | `package.json`, `pyproject.toml` 등 | 릴리스 버전 자동 추론 |

## 워크플로우

### Step 1. 컨텍스트 준비

아래 정보를 수집하여 실행 경로를 결정:

1. `gh release list --limit 10` 실행 → 기존 릴리스 목록 확인
2. `git tag --sort=-v:refname` 실행 → 현재 버전 태그 확인
3. `.github/release.yml` 존재 여부 확인
4. `package.json` 또는 `pyproject.toml`에서 버전 필드 추출

**경로 분기 판단:**

| 조건 | 실행 경로 |
|------|----------|
| 기존 릴리스 0건 또는 `.github/release.yml` 미존재 | Recommend → Create |
| 기존 릴리스 1건 이상 + `.github/release.yml` 존재 | Direct Create |
| 사용자가 특정 릴리스 수정 요청 | Direct Edit |
| 사용자가 특정 릴리스 삭제 요청 | Direct Delete |

### Step 2. 외부 스킬 호출 (경로별)

**경로 A: Recommend → Create**

→ Skill: github-release-manager:recommend-template
- **INTENT**: spec-driven-team 프로젝트 분석 후 Release 문서 구성 추천
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}"
  }
- **RETURN**: Release 구성 추천안 확보 후 create-release 호출

→ Skill: github-release-manager:create-release
- **INTENT**: 추천 구성 기반 Release 문서 생성
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "version": "{추론된 버전}"
  }
- **RETURN**: Release 문서 생성 완료

**경로 B: Direct Create**

→ Skill: github-release-manager:create-release
- **INTENT**: Release 문서 직접 생성
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "version": "{버전}",
    "base_ref": "{이전 태그}"
  }
- **RETURN**: Release 문서 생성 완료

**경로 C: Direct Edit**

→ Skill: github-release-manager:edit-release
- **INTENT**: 기존 Release 문서 수정
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "version": "{수정 대상 버전}",
    "changes": "{수정 내용}"
  }
- **RETURN**: Release 문서 수정 완료

**경로 D: Direct Delete**

→ Skill: github-release-manager:delete-release
- **INTENT**: Release 문서 삭제
- **ARGS**: {
    "source_plugin": "spec-driven-team",
    "project_dir": "{cwd}",
    "version": "{삭제 대상 버전}",
    "delete_tag": false
  }
- **RETURN**: Release 문서 삭제 완료

## MUST 규칙

- [ ] 도메인 컨텍스트(기존 릴리스, 태그, 버전)를 반드시 수집하여 전달
- [ ] `source_plugin` 값은 항상 `"spec-driven-team"` 으로 설정
- [ ] 경로 분기 판단 후 적절한 스킬 선택

## MUST NOT 규칙

- [ ] 외부 플러그인 내부 구현에 의존하지 않음
- [ ] `project_dir` 없이 스킬 호출하지 않음

## 검증 체크리스트

- [ ] 외부 스킬 호출이 정상 작동하는가
- [ ] 실행 경로 분기가 올바르게 판단되었는가
- [ ] Release 문서가 생성/수정/삭제되었는가
