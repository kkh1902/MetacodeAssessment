"""
문제 9 풀이 — Join fan-out 수정

[수정 내용]
1. products 중복 제거 후 JOIN
   이유: products 테이블에 product_id 중복 행이 있어 INNER JOIN 시 fan-out 발생
        → SUM(amount)가 실제의 2배로 집계됨

   수정 방법: products를 DISTINCT로 dedupe 후 JOIN
             또는 products INSERT 시 중복 제거 (UNIQUE 제약 추가)

2. Idempotency 보장 (DELETE-INSERT)
   이유: 재실행 시 중복 집계 방지

[확인 쿼리]
  -- fan-out 진단
  SELECT product_id, COUNT(*) FROM products GROUP BY product_id HAVING COUNT(*) > 1;

  -- 수정 전/후 매출 비교
  SELECT agg_date, SUM(total_amount) FROM daily_sales_agg GROUP BY agg_date ORDER BY agg_date;
"""
import psycopg2
import argparse

CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sales_db",
    "user": "metade",
    "password": "metade2025",
}

def run(target_date: str):
    conn = psycopg2.connect(**CONN)
    cur  = conn.cursor()

    # FIX-1: Idempotency — 해당 날짜 기존 집계 삭제 후 재삽입
    cur.execute("DELETE FROM daily_sales_agg WHERE agg_date = %s", (target_date,))

    # FIX-2: products DISTINCT로 fan-out 제거
    cur.execute("""
        INSERT INTO daily_sales_agg (agg_date, user_id, total_amount, order_count)
        SELECT
            DATE(e.event_time)         AS agg_date,
            e.user_id,
            SUM(e.amount)              AS total_amount,
            COUNT(*)                   AS order_count
        FROM raw_events e
        INNER JOIN (
            SELECT DISTINCT product_id FROM products   -- FIX: 중복 제거
        ) p ON e.product_id = p.product_id
        WHERE DATE(e.event_time) = %s
        GROUP BY DATE(e.event_time), e.user_id
    """, (target_date,))

    inserted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"[{target_date}] Inserted {inserted} rows into daily_sales_agg (fan-out fixed)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
