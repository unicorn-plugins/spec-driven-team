---
name: code-generator
description: 명세 기반 코드 자동 재생성 (선언적 로직)
---

# Code Generator

## 목표

명세 파일을 기반으로 선언적 로직 코드를 자동 재생성하고,
복잡한 로직에는 TODO 주석을 생성하여 개발자가 수동 구현하도록 안내함.

## 참조

- 첨부된 `agentcard.yaml`을 참조하여 역할, 역량, 제약, 핸드오프 조건을 준수할 것
- 첨부된 `tools.yaml`을 참조하여 사용 가능한 도구와 입출력을 확인할 것

## 워크플로우

### 1. 명세 파일 읽기

{tool:file_read}로 명세 파일 로드:
- Markdown/YAML/JSON 형식 파싱
- 선언적 로직 vs 복잡한 로직 구분

### 2. 선언적 로직 코드 생성

명세를 코드로 자동 변환:

**CRUD 연산 → REST API 코드**:
```python
# 명세: GET /users
def get_users(query):
    page = query.get('page', 1)
    limit = query.get('limit', 10)
    return db.users.find().skip((page-1)*limit).limit(limit)
```

**데이터 변환 → 매핑 함수**:
```python
# 명세: User → UserDTO 변환
def user_to_dto(user):
    return {
        'id': user['_id'],
        'name': user['name'],
        'email': user['email']
    }
```

**규칙 기반 검증 → 검증 함수**:
```python
# 명세: email 형식 검증, name 1-100자
def validate_user(data):
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
        raise ValueError('Invalid email')
    if not (1 <= len(data['name']) <= 100):
        raise ValueError('Name must be 1-100 characters')
```

### 3. 복잡한 로직 TODO 주석 생성

명세 스켈레톤 → TODO 주석:
```python
# TODO: 명세 참조 — src/algorithms/quicksort.py:45-120
# 목적: 대용량 데이터 정렬 최적화
# 입력: List[int] (최대 1,000,000개)
# 출력: List[int] (정렬됨)
# 알고리즘: 퀵소트 기반, 피벗 중간값, 재귀 깊이 50
def quicksort(data):
    # 개발자가 수동으로 구현
    pass
```

### 4. 기존 코드와 비교

{tool:file_read}로 기존 코드 읽기:
- 차이점 식별 (diff)
- 덮어쓰기 전 사용자 확인

### 5. 코드 파일 작성

{tool:file_write}로 생성된 코드를 원본 위치에 저장:
- 기존 파일 백업 (`.backup/`)
- 새 코드 작성
- 포맷 적용 (언어별 린터/포맷터)

## 출력 형식

### 생성 결과 보고서

````markdown
# 코드 생성 결과

## 선언적 로직 (자동 생성 완료)
| 파일 | 라인 | 변경 내용 |
|------|------|----------|
| src/api/users.py | 45-120 | CRUD 함수 재생성 |
| src/transform.py | 23-67 | 매핑 함수 업데이트 |

## 복잡한 로직 (TODO 주석 생성)
| 파일 | 라인 | TODO 내용 |
|------|------|-----------|
| src/sort.py | 89-234 | 퀵소트 알고리즘 구현 필요 |

## 백업
모든 변경 파일은 `.backup/2025-02-17-03-15/`에 백업됨
````

## 검증

- 생성된 코드가 명세와 일치하는지 확인
- 구문 오류가 없는지 확인 ({tool:lsp_diagnostics})
- TODO 주석이 명확하고 구체적인지 확인
- 백업이 정상적으로 생성되었는지 확인
