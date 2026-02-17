# 상세 동기화 보고서

## 1. 명세 변경 내용 (rest-api-spec.md)

### 신규 추가
- `GET /api/v1/bills/status/{requestId}` (UFR-BILL-030)
  - 비동기 조회 상태 확인 엔드포인트
  - 응답: requestId, status(PENDING/PROCESSING/COMPLETED/FAILED), progress(0~100), result

### 수정
- `GET /api/v1/bills/history`
  - 기존: lineNumber, startDate, endDate, page(1부터), size, status 파라미터
  - 변경: page(0부터), size(최대100), sort(기본 inquiryDate,desc) 파라미터

## 2. 코드 변경 상세

### BillStatusResponse.java
```java
// 추가된 필드
private Integer progress;
private BillInquiryResponse result;
```

### BillInquiryService.java
```java
// 추가된 메소드
BillStatusResponse getBillStatus(String requestId);
BillHistoryResponse getBillHistory(Integer page, Integer size, String sort);
```

### BillInquiryServiceImpl.java
- `getBillStatus()`: 이력 DB 조회 → 상태별 progress 계산(PROCESSING=50, COMPLETED=100, FAILED=0)
- `getBillHistory()`: page/size/sort 파라미터로 단순화

### BillHistoryService.java
- `getBillInquiryResult()`: COMPLETED 상태 시 resultSummary 파싱 → BillInfo 구성
  - 형식: `"상품명, 금액원"` → productName, totalAmount 추출

### BillController.java
- `GET /status/{requestId}` 엔드포인트 추가
- `GET /history` 파라미터 변경 반영
- 완료된 TODO 주석 제거

## 3. 회귀 테스트

| 테스트 클래스 | 케이스 | 결과 |
|---|---|---|
| BillInquiryServiceImplTest | getBillStatus COMPLETED → progress 100 | ✅ |
| BillInquiryServiceImplTest | getBillStatus PROCESSING → progress 50 | ✅ |
| BillInquiryServiceImplTest | getBillStatus FAILED → progress 0 | ✅ |
| BillInquiryServiceImplTest | getBillStatus 미존재 → 예외 | ✅ |
| BillInquiryServiceImplTest | getBillHistory 파라미터 위임 | ✅ |
| BillHistoryServiceTest | COMPLETED + summary → BillInfo 반환 | ✅ |
| BillHistoryServiceTest | PROCESSING → billInfo null | ✅ |
| BillHistoryServiceTest | 미존재 → null 반환 | ✅ |
| BillHistoryServiceTest | 쉼표 없는 summary → productName만 설정 | ✅ |

## 4. 동기화 상태

- 불일치 파일: 0개
- 전체 명세: 9개 / 동기화: 9개 (100%)
