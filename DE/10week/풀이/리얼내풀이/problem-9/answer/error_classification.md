# 에러 분류표

## 로그 분석 대상: `logs/error_log.txt` (10회 실행 중 3회 실패)

| 에러 | 분류 | 근거 |
|------|------|------|
| `java.lang.OutOfMemoryError: GC overhead limit exceeded` | **로그 트랩 (무관)** | GC pressure 경고이며 "worker continued execution" 명시. 실제 작업 중단 없음 |
| `org.apache.spark.SparkException: Task not serializable` | **로그 트랩 (무관)** | "retried and succeeded" 명시. UDF 직렬화 최적화 경고로 실패 원인 아님 |
| `org.postgresql.util.PSQLException: SocketTimeoutException` | **진짜 원인** | 3회 실패 모두 공통으로 등장. task 최종 실패 직전에 발생 |

## 시계열 분석

- RUN #2, #5, #8 실패 — 모두 동일 패턴:
  1. GC overhead 경고 → 작업 계속
  2. TaskNotSerializable 경고 → retry 성공
  3. **PSQLException: SocketTimeoutException → task 4회 재시도 후 Job abort**

## 결론

- OOM / TaskNotSerializable은 매 실행마다 발생하지만 성공 실행에도 나타남 → 원인 아님
- PSQLException은 **실패 실행에서만** 최종 에러로 등장 → root cause
