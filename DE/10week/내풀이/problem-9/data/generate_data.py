"""
문제 9 샘플 데이터 생성 스크립트
실행: python generate_data.py

생성 데이터:
  - 정상 기간 (2025-03-25 ~ 2025-03-31): product_id 3,4,5 위주 (fan-out 없음)
  - 이상 기간 (2025-04-01 ~ 2025-04-07): product_id 1,2 포함 (fan-out 발생)
"""
import psycopg2
import random
from datetime import datetime, timedelta

CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sales_db",
    "user": "metade",
    "password": "metade2025",
}

random.seed(42)

conn = psycopg2.connect(**CONN)
cur  = conn.cursor()

rows = []

# 정상 기간: product_id 3,4,5만 사용 → JOIN해도 각 1건 매칭 → 정상 집계
for day_offset in range(7):
    dt = datetime(2025, 3, 25) + timedelta(days=day_offset)
    for _ in range(200):
        rows.append((
            random.randint(1, 100),
            random.choice([3, 4, 5]),   # 중복 없는 product_id
            round(random.uniform(10000, 200000), 2),
            dt + timedelta(seconds=random.randint(0, 86399)),
        ))

# 이상 기간: product_id 1,2 포함 → JOIN 시 fan-out → 매출 2배
for day_offset in range(7):
    dt = datetime(2025, 4, 1) + timedelta(days=day_offset)
    for _ in range(200):
        rows.append((
            random.randint(1, 100),
            random.choice([1, 2, 3, 4, 5]),  # 1,2는 products에 2건씩 → fan-out
            round(random.uniform(10000, 200000), 2),
            dt + timedelta(seconds=random.randint(0, 86399)),
        ))

cur.executemany(
    "INSERT INTO raw_events (user_id, product_id, amount, event_time) VALUES (%s, %s, %s, %s)",
    rows,
)
conn.commit()
cur.close()
conn.close()

print(f"Inserted {len(rows)} rows into raw_events")
print("정상 기간(3/25~3/31): product_id 3,4,5 → fan-out 없음")
print("이상 기간(4/1~4/7):   product_id 1,2,3,4,5 → 1,2는 products 중복으로 fan-out 발생")
