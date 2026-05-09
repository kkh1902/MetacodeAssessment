# 문제 6 - 에러 분류표

## 에러 목록 (error_log.txt 기준)

| # | 에러 메시지 | 분류 | 분류 근거 |
|---|------------|------|----------|
| 1 | `java.lang.OutOfMemoryError: GC overhead limit exceeded` | **무관 (irrelevant)** | spark-worker GC 로그에서 발생. "worker continued execution" 명시. 실제 task 실패로 이어지지 않음. 정상 실행에서도 동일하게 출력됨 |
| 2 | `org.apache.spark.SparkException: Task not serializable` | **무관 (irrelevant)** | Spark 내부 최적화 과정의 경고. "retried and succeeded" 명시. 실패 실행과 성공 실행 모두에서 발생. 실제 job abort 원인이 아님 |
| 3 | `PSQLException: An I/O error occurred ... SocketTimeoutException` | **관련 (relevant)** | 3번의 실패 실행 모두에서 등장. task abort의 직접 원인. 정상 실행에서는 미등장 |

## 무관 로그 배제 이유

- **OOM (GC overhead)**: 정상 실행(RUN #1, #3 등)에서도 동일 경고 출력. 워커가 계속 실행됨. job abort와 시계열 연관 없음.
- **TaskNotSerializable**: "retried and succeeded"로 명시. 실패/성공 실행 구분 없이 발생. 재시도 후 성공하는 경고성 메시지.

## Root Cause

`PSQLException: SocketTimeoutException` — JDBC URL의 `socketTimeout=5000` 설정

- 5초 이내에 write가 완료되는 파티션 → 성공
- 5초를 초과하는 파티션(데이터 양 많음) → Read timed out → task 실패
- 파티션 크기가 실행마다 달라지므로 간헐적 실패 발생

## 시계열 분석 (RUN #2 기준)

```
09:14:33  OOM GC warning (무관)
09:14:35  DAG Submitting tasks
09:14:38  TaskNotSerializable warning (무관, retried)
09:14:41  Task 6 시작
09:14:47  SocketTimeoutException → task 6 실패   ← 6초 소요, timeout=5초 초과
09:14:47  Job aborted
```

OOM과 TaskNotSerializable은 task 실패 이전에 발생했지만, 실패 직접 원인이 아님.
실제 실패는 09:14:47의 SocketTimeoutException이 트리거.
