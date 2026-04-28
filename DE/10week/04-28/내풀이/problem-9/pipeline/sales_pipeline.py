"""
문제 9 참조 파이프라인 — 버그 포함

버그:
  products 테이블에 중복 행이 있는 상태에서 INNER JOIN 수행
  → product_id 1, 2는 products에 2건씩 존재
  → JOIN 시 fan-out 발생 → 매출이 실제보다 2배로 집계됨

실행:
  python sales_pipeline.py --date 2025-04-01
"""
import psycopg2
import argparse
from datetime import date

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

    # BUG: products에 중복 행 있음 → fan-out
    # product_id 1, 2: products에 2건 → raw_events 1건이 집계에 2건으로 뻥튀기
    cur.execute("""
        INSERT INTO daily_sales_agg (agg_date, user_id, total_amount, order_count)
        SELECT
            DATE(e.event_time)         AS agg_date,
            e.user_id,
            SUM(e.amount)              AS total_amount,
            COUNT(*)                   AS order_count
        FROM raw_events e
        INNER JOIN products p ON e.product_id = p.product_id
        WHERE DATE(e.event_time) = %s
        GROUP BY DATE(e.event_time), e.user_id
    """, (target_date,))

    inserted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"[{target_date}] Inserted {inserted} rows into daily_sales_agg")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
