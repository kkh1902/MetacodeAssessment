"""
문제 10 풀이 — Stage 2 수정

[BUG-2 수정]
  원인: DELETE 없이 INSERT만 수행 → 재실행 시 agg_daily에 중복 행 누적
        total_revenue, user_count 모두 2배, 3배로 뻥튀기

  수정: DELETE-INSERT 패턴으로 idempotency 보장

[확인 쿼리]
  -- 재실행 전후 count 확인
  SELECT COUNT(*) FROM agg_daily WHERE agg_date = '2025-04-01';
  -- 항상 1이어야 정상 (재실행해도 1)
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

    # FIX: DELETE 먼저 → 재실행해도 중복 없음
    cur.execute("DELETE FROM agg_daily WHERE agg_date = %s", (target_date,))

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
        print(f"[Stage 2 FIXED] agg_daily [{row[0]}]: user_count={row[1]}, total_revenue={row[2]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
