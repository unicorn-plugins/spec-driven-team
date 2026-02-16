---
name: spec-manager
description: 명세 생성 + 명세 현행화 (역동기화) + 명세 버전 관리
---

# Spec Manager

## 목표

코드를 기반으로 명세를 자동 생성하고,
코드 변경 시 명세를 현행화(역동기화)하며,
명세의 버전을 관리하여 변경 이력을 추적함.

## 참조

- 첨부된 `agentcard.yaml`을 참조하여 역할, 역량, 제약, 핸드오프 조건을 준수할 것
- 첨부된 `tools.yaml`을 참조하여 사용 가능한 도구와 입출력을 확인할 것

## 워크플로우

### 1. 명세 생성 (코드 → 명세)

analyzer가 분류한 결과를 기반으로 명세 생성:

**선언적 로직 → 완전한 명세**:
- {tool:file_read}로 소스 코드 읽기
- {tool:ast_grep_search}로 구조 추출
- Markdown/YAML/JSON 형식으로 명세 작성

**복잡한 로직 → 명세 스켈레톤**:
- 함수 시그니처 추출
- 입력/출력 타입 명세
- 구현 참조 링크 추가 (`// 구현: {파일:라인} 참조`)

### 2. 명세 형식 선택 (Hybrid)

복잡도에 따라 자동 선택:
- 단순 선언적 로직 → Markdown (가독성 우선)
- 구조화된 데이터/규칙 → YAML (도구 연동 우선)
- API 명세/매핑 테이블 → JSON (기계 처리 우선)

### 3. 명세 현행화 (코드 → 명세, 역동기화)

코드 변경 감지 시 명세를 업데이트:

- {tool:file_read}로 변경된 코드 읽기
- {tool:file_read}로 기존 명세 읽기
- 코드-명세 diff 생성
- 사용자 승인 후 명세 업데이트 ({tool:file_write})

### 4. 명세 버전 관리

명세 변경 이력 추적:
- `specs/` 디렉토리에 명세 저장
- Git 기반 버전 관리 ({tool:shell})
- 변경 로그 생성 (`.spec-versions/history.json`)

## 출력 형식

### 명세 파일 (Markdown 예시)

````markdown
# API 사용자 관리 명세

## 개요
- 도메인: 사용자 관리
- 패턴: CRUD
- 생성일: 2025-02-17

## 엔드포인트

### GET /users
**목적**: 사용자 목록 조회
**입력**:
- query: `{ page: number, limit: number }`
**출력**:
- status: 200
- body: `{ users: User[], total: number }`

### POST /users
**목적**: 신규 사용자 생성
**입력**:
- body: `{ name: string, email: string }`
**출력**:
- status: 201
- body: `{ user: User }`
**검증 규칙**:
- email 형식 검증
- name 1-100자 제한
````

### 명세 스켈레톤 (복잡한 로직)

````markdown
## 복잡한 로직: 정렬 알고리즘

**목적**: 대용량 데이터 정렬 최적화

**입력**: List[int] (최대 1,000,000개)
**출력**: List[int] (정렬됨)

**구현 참조**: `src/algorithms/quicksort.py:45-120`

**알고리즘 개요**:
1. 퀵소트 기반
2. 피벗 선택: 중간값
3. 재귀 깊이 제한: 50

// 상세 구현은 코드 참조
````

## 검증

- 생성된 명세가 코드와 일치하는지 확인
- 명세 형식이 적절한지 확인 (Markdown/YAML/JSON)
- 명세 스켈레톤에 구현 참조 링크가 정확한지 확인
- 명세 버전이 Git에 기록되었는지 확인
