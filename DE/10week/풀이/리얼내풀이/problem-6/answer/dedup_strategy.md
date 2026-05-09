# 중복 방지 전략 및 멱등성 설계

## 발견된 버그

### BUG-1: `datetime.now()` 사용으로 인한 날짜 불일치
```python
# 버그 코드
today = datetime.now().date()
```
- **문제**: DAG 재실행 시점이 달라도 항상 "지금" 기준 날짜로 조회
- **결과**: logical_date(실행 대상 날짜)와 무관하게 오늘 데이터를 계속 삽입 → 중복

### BUG-2: INSERT만 사용하여 멱등성 미확보
```python
# 버그 코드
cur.executemany("INSERT INTO daily_sales ...", rows)
```
- **문제**: 동일 날짜로 재실행 시 기존 데이터 삭제 없이 새로 삽입
- **결과**: 재실행마다 동일 데이터 누적 → 중복

---

## 수정 전략

### FIX-1: `data_interval_end` 사용
```python
execution_date = context["data_interval_end"]
today = execution_date.date()
```
- `@daily` 스케줄에서 `data_interval_end`는 논리적 실행 날짜의 자정(00:00:00)
- 언제 재실행해도 동일한 날짜 범위를 조회하므로 결정론적(deterministic)

### FIX-2: DELETE-INSERT 패턴
```python
cur.execute(
    "DELETE FROM daily_sales WHERE event_time >= %s AND event_time < %s",
    (start_ts, end_ts),
)
cur.executemany("INSERT INTO daily_sales ...", rows)
conn.commit()
```
- 재실행 전 해당 날짜 데이터를 먼저 삭제 후 재삽입
- 몇 번을 실행해도 결과가 동일 → 멱등성(idempotency) 확보

---

## 검증 결과

| 실행 횟수 | total_rows | unique_orders | duplicate_rows |
|-----------|------------|---------------|----------------|
| 1회       | 100        | 100           | 0              |
| 2회       | 100        | 100           | 0              |

→ DAG 재실행 후에도 중복 없음
