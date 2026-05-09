# 문제 6 - Root Cause Analysis

## 증상
- 10회 실행 중 3~4회 실패
- 실패 로그: ConnectionTimeout, OOM, TaskNotSerializable 혼재
- 실패 시점마다 에러 메시지가 다르게 보임

## Root Cause

**JDBC URL의 `socketTimeout=5000` 설정** (5초 타임아웃)

```python
# process_and_load.py 버그 라인
PG_URL_WRITE = (
    "jdbc:postgresql://postgres:5432/airflow"
    "?socketTimeout=5000"   # ← 원인
    "&connectTimeout=3000"
)
```

- Spark가 DataFrame을 PostgreSQL에 write할 때 파티션별로 JDBC 연결을 사용
- 파티션당 처리 데이터 양이 많을 경우 write 시간이 5초를 초과
- `socketTimeout=5000`으로 인해 `SocketTimeoutException` 발생 → task 실패
- 파티션 크기는 실행마다 달라지므로 간헐적 실패 (3~4/10)

## 가설

### 가설 1: OOM으로 인한 executor 종료
- 검증: 정상 실행 로그에도 동일 OOM GC 경고 존재
- "worker continued execution" 명시 → 기각

### 가설 2: TaskNotSerializable로 인한 task 실패
- 검증: 로그에 "retried and succeeded" 명시
- 실패 실행/성공 실행 모두에서 발생 → 기각

### 가설 3 (실제 원인): JDBC socketTimeout 설정
- 검증: 실패 3건 모두 `PSQLException: SocketTimeoutException` 포함
- 성공 실행에서는 해당 에러 없음
- 실패 task의 처리 시간: RUN#2 task6 = 6초 (09:14:41~09:14:47), timeout=5초 초과 → 확인

## 수정 방법

`socketTimeout` 제거 또는 충분히 크게 설정.

```python
# 수정 전
PG_URL_WRITE = "jdbc:postgresql://postgres:5432/airflow?socketTimeout=5000&connectTimeout=3000"

# 수정 후
PG_URL_WRITE = "jdbc:postgresql://postgres:5432/airflow"
```

## 수정 후 안정성 증명 기준

5회 연속 실행 시 모두 SUCCESS (실패 0건)
각 실행 시 `date && hostname` 출력 포함 캡처 제출
