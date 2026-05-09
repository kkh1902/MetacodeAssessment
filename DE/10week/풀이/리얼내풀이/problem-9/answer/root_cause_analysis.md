# Root Cause 분석

## 증상

- Spark job 10회 실행 중 3~4회 간헐적 실패
- 실패 시점마다 다른 에러 메시지 (OOM, TaskNotSerializable, ConnectionTimeout 혼재)

## Root Cause

**`process_and_load.py` PG_URL_WRITE에 `socketTimeout=5000` 설정**

```python
# BUG
PG_URL_WRITE = (
    "jdbc:postgresql://postgres:5432/airflow"
    "?socketTimeout=5000"     # ← 5초 타임아웃
    "&connectTimeout=3000"
)
```

- `socketTimeout=5000`: JDBC write 중 소켓 응답이 5초 초과하면 강제 종료
- 50,000건 데이터를 8개 파티션으로 나눠 write → 파티션당 약 6,250건
- 파티션 크기에 따라 write 소요 시간이 5초를 초과하는 경우 발생 → 간헐적 실패

## 수정

```python
# FIX: socketTimeout 제거
PG_URL_WRITE = "jdbc:postgresql://postgres:5432/airflow"
```

## 검증

수정 후 5회 연속 실행 → 모두 SUCCESS (SocketTimeoutException 없음)
