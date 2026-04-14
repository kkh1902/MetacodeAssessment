# Timezone 불일치 원인 분석

## 상황

- Producer: UTC 기준 timestamp 발행 (`2025-03-31 15:00:00 ~ 23:15:00 UTC`)
- 기대값: KST 기준 날짜 파티션 → 모두 `2025-04-01` 파티션
- 실제값: `2025-03-31` 파티션에 100건 적재 (버그)

## 원인 가설

### 가설 1: `to_date()`가 UTC 기준으로 날짜 추출 ← **실제 원인**
```python
# partition_job.py 43번째 줄
df = df.withColumn("partition_date", to_date(col("event_time")))
```
- Spark 세션 timezone 기본값 = UTC
- `to_date(event_time)` → UTC 날짜 그대로 추출
- UTC `2025-03-31 15:00` → `to_date()` = `2025-03-31` (틀림)
- KST로는 `2025-04-01 00:00`이어야 함

### 가설 2: event_time이 KST로 저장되었을 가능성
- 검증: Producer 코드 확인 → `tzinfo=timezone.utc` 명시 → UTC 저장 확인
- 배제

## 수정

```python
# BUG
df = df.withColumn("partition_date", to_date(col("event_time")))

# FIX
df = df.withColumn("partition_date", to_date(from_utc_timestamp(col("event_time"), "Asia/Seoul")))
```

- `from_utc_timestamp(col("event_time"), "Asia/Seoul")`: UTC timestamp → KST timestamp 변환
- `to_date()`: KST 기준 날짜 추출

## 검증 결과

| | partition_date | count |
|---|---|---|
| 수정 전 (BUG) | 2025-03-31 | 100 |
| 수정 후 (FIX) | **2025-04-01** | **100** |

UTC `2025-03-31 15:00~23:15` 100건이 KST 기준 올바른 `2025-04-01` 파티션에 적재됨.
