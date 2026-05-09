"""
Stage 1: raw_events → staging_events

버그 (BUG-1):
  필터 조건이 < 대신 <= 를 사용
  → event_time = '2025-04-02 00:00:00' 이하를 포함하려 했으나
    실제로는 event_time < '2025-04-02 00:00:00' 이어야 함
  → 자정 경계(23:59:59)의 데이터 40건이 누락됨
  → 사용자 수 집계 시 일부 사용자가 사라짐

실행:
  python stage1_raw_to_staging.py --date 2025-04-01
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

    cur.execute("DELETE FROM staging_events")

    # BUG-1: 경계 조건 오류 — BETWEEN 사용 시 end 경계 포함 여부 혼동
    # 실제 의도: 2025-04-01 00:00:00 ~ 2025-04-01 23:59:59
    # 버그: event_time < '2025-04-01' 로 작성 → 해당 날짜 데이터 전부 누락
    cur.execute("""
        INSERT INTO staging_events (event_id, user_id, revenue, event_time)
        SELECT event_id, user_id, revenue, event_time
        FROM raw_events
        WHERE event_time >= %s
          AND event_time < %s
    """, (target_date, target_date))   # BUG: end를 target_date 그대로 사용 → 당일 데이터 0건

    inserted = cur.rowcount
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM staging_events")
    staging_count = cur.fetchone()[0]

    cur.close()
    conn.close()
    print(f"[Stage 1] raw_events → staging_events: {staging_count}건")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.date)
