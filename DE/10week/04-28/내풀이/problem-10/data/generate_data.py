"""
문제 10 샘플 데이터 생성 스크립트
실행: python generate_data.py

생성 데이터:
  - 2025-04-01 UTC 기준 1,000건
  - 일부 이벤트는 자정 경계(23:59:59 ~ 00:00:01) 근처에 배치
    → Stage 1 timestamp 경계 버그에 걸리도록 의도적 설계
"""
import psycopg2
import random
from datetime import datetime, timedelta

CONN = {
    "host": "localhost",
    "port": 5433,
    "dbname": "lineage_db",
    "user": "metade",
    "password": "metade2025",
}

random.seed(7)

conn = psycopg2.connect(**CONN)
cur  = conn.cursor()

rows = []

# 본 데이터: 2025-04-01 00:00:00 ~ 2025-04-01 23:59:58
for _ in range(960):
    rows.append((
        random.randint(1, 500),
        round(random.uniform(5000, 300000), 2),
        datetime(2025, 4, 1) + timedelta(seconds=random.randint(0, 86398)),
    ))

# 경계 데이터: 2025-04-01 23:59:59 (BUG-1 에 걸림 — 필터가 < 대신 <= 로 잘못됨)
for _ in range(40):
    rows.append((
        random.randint(1, 500),
        round(random.uniform(5000, 300000), 2),
        datetime(2025, 4, 1, 23, 59, 59),
    ))

cur.executemany(
    "INSERT INTO raw_events (user_id, revenue, event_time) VALUES (%s, %s, %s)",
    rows,
)
conn.commit()
cur.close()
conn.close()

print(f"Inserted {len(rows)} rows into raw_events")
print(f"  - 정상 데이터: 960건 (00:00:00 ~ 23:59:58)")
print(f"  - 경계 데이터: 40건 (23:59:59) ← Stage 1 버그에 걸림")
