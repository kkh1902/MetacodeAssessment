# Silent Failure 원인 분석

## 증상

- Airflow DAG: SUCCESS
- Spark job: SUCCESS, 로그에 "Transferred 100 rows" 출력
- `daily_sales_final`: 0 rows

## 데이터 흐름 추적

| 단계 | 위치 | count |
|------|------|-------|
| 1 | Kafka (sales-events) | 100 |
| 2 | staging_sales (Spark 적재) | 100 |
| 3 | daily_sales_final (DAG 이관) | **0** ← 유실 |

→ staging → final 이관 단계에서 데이터 유실

## 원인 가설

### 가설 1: INSERT가 실행되지 않음
- 검증: `cur.rowcount`가 100 반환 → INSERT는 실행됨
- **배제**

### 가설 2: `conn.commit()` 누락 ← **실제 원인**
```python
# transfer_dag.py line 69~74
row_count = cur.rowcount
print(f"Transferred {row_count} rows ...")

# BUG: conn.commit() 없음
cur.close()
conn.close()  # autocommit=False → commit 없이 close → 자동 롤백
```
- psycopg2 기본값: `autocommit=False`
- `conn.close()` 호출 시 미커밋 트랜잭션 자동 롤백
- `cur.rowcount`는 INSERT 실행 시점의 값 → 로그에는 100 찍히지만 실제 DB에는 0

## 수정

```python
# FIX
conn.commit()  # ← 추가
cur.close()
conn.close()
```

## 검증

수정 후 실행 결과: `daily_sales_final` → 100건 정상 적재
