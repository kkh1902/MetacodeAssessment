"""
문제 10 풀이 — Stage 1 수정

[BUG-1 수정]
  원인: end 경계를 target_date 그대로 사용 → 당일 데이터 전부 누락
        WHERE event_time >= '2025-04-01' AND event_time < '2025-04-01'
        → 항상 0건

  수정: end 경계를 다음날 00:00:00 으로 설정
        WHERE event_time >= '2025-04-01' AND event_time < '2025-04-02'

[확인 쿼리]
  -- Stage 1 후 count 확인
  SELECT COUNT(*) FROM raw_events WHERE DATE(event_time) = '2025-04-01';
  SELECT COUNT(*) FROM staging_events;
  -- 두 값이 같아야 정상
"""
import psycopg2
import argparse
from datetime import date, timedelta

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

    cur.execute("DELETE FROM staging_events")

    # FIX: end 경계를 다음날로 설정
    d = date.fromisoformat(target_date)
    next_day = d + timedelta(days=1)

    cur.execute("""
        INSERT INTO staging_events (event_id, user_id, revenue, event_time)
        SELECT event_id, user_id, revenue, event_time
        FROM raw_events
        WHERE event_time >= %s
          AND event_time < %s
    """, (target_date, str(next_day)))   # FIX: next_day 사용

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM staging_events")
    staging_count = cur.fetchone()[0]

    cur.close()
    conn.close()
    print(f"[Stage 1 FIXED] raw_events → staging_events: {staging_count}건")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
