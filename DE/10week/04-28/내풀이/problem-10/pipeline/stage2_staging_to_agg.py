"""
Stage 2: staging_events → agg_daily

버그 (BUG-2):
  DELETE 없이 INSERT만 수행 → 재실행 시 중복 집계
  → 파이프라인을 2번 실행하면 agg_daily 행이 2배로 쌓임
  → total_revenue, user_count 모두 2배

실행:
  python stage2_staging_to_agg.py --date 2025-04-01
  (2번 실행해보면 버그 확인 가능)
"""
import psycopg2
import argparse

CONN = {
    "host": "localhost",
    "port": 5433,
    "dbname": "lineage_db",
    "user": "metade",
    "password": "metade2025",
}

def run(target_date: str):
    conn = psycopg2.connect(**CONN)
    cur  = conn.cursor()

    # BUG-2: DELETE 없음 → 재실행 시 중복 누적
    cur.execute("""
        INSERT INTO agg_daily (agg_date, user_count, total_revenue)
        SELECT
            DATE(event_time)        AS agg_date,
            COUNT(DISTINCT user_id) AS user_count,
            SUM(revenue)            AS total_revenue
        FROM staging_events
        WHERE DATE(event_time) = %s
        GROUP BY DATE(event_time)
    """, (target_date,))

    conn.commit()

    cur.execute("SELECT agg_date, user_count, total_revenue FROM agg_daily WHERE agg_date = %s", (target_date,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    if row:
        print(f"[Stage 2] agg_daily [{row[0]}]: user_count={row[1]}, total_revenue={row[2]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
