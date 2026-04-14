# 문제 5 - Root Cause Analysis

## 증상
- Airflow DAG `staging_to_final_transfer`: **SUCCESS**
- Spark job `kafka_to_staging`: **SUCCESS**
- `staging_sales` 테이블: 100 rows (정상)
- `daily_sales_final` 테이블: **0 rows** ← 이상

## 데이터 흐름 추적

| 단계 | 테이블/컴포넌트 | row count | 상태 |
|------|---------------|-----------|------|
| 1 | Kafka offset | 100 | 정상 |
| 2 | Spark read (Kafka) | 100 | 정상 |
| 3 | Spark write → `staging_sales` | 100 | 정상 |
| 4 | Airflow transfer → `daily_sales_final` | **0** | **이상** |

데이터 유실 지점: **Airflow transfer task** (`transfer_staging_to_final`)

## 가설

### 가설 1: staging_sales에 데이터가 없음
- 검증: `SELECT COUNT(*) FROM staging_sales WHERE partition_date = '2025-04-01';`
- 결과: 100 rows → 기각

### 가설 2: WHERE 조건 불일치 (날짜 필터 오류)
- 검증: `SELECT DISTINCT partition_date FROM staging_sales;`
- 결과: 2025-04-01 존재 → 기각

### 가설 3 (실제 원인): conn.commit() 누락으로 트랜잭션 롤백
- 검증: `transfer_dag.py`의 `transfer_staging_to_final()` 함수 확인
- `conn.commit()` 없이 `conn.close()` 호출
- psycopg2 기본값: `autocommit=False`
- `conn.close()` 호출 시 미완료 트랜잭션 자동 롤백
- `cur.rowcount`는 INSERT 시도 행 수를 반환 → 로그에 "Transferred 100 rows" 출력 → 정상처럼 보임

## 근거 로그 라인

```
[2025-04-01 09:05:12] {transfer_dag.py:52} INFO - Transferred 100 rows to daily_sales_final for 2025-04-01
```

`cur.rowcount = 100`이지만 `commit()` 없이 `close()` → 롤백.

## 수정 방법

`transfer_dag.py`의 `transfer_staging_to_final()` 함수에 `conn.commit()` 추가.

```python
# 수정 전
cur.close()
conn.close()

# 수정 후
conn.commit()   # ← 추가
cur.close()
conn.close()
```
