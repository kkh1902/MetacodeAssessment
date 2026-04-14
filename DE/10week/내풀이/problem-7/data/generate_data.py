"""
OOM 유발용 샘플 데이터 생성 스크립트
실행: python generate_data.py

데이터 skew 구조:
  - user_id=999: 전체 80% (OOM 유발)
  - 나머지 user_id 1~998: 20% 균등 분배
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

OUTPUT_PATH = "/opt/spark/data/sales_raw.parquet"
TOTAL_ROWS  = 2_000_000

print(f"Generating {TOTAL_ROWS:,} rows...")

np.random.seed(42)

# skew: 80%는 user_id=999
n_skew   = int(TOTAL_ROWS * 0.8)
n_normal = TOTAL_ROWS - n_skew

skew_data = {
    "order_id":  [f"ORD-{i:08d}" for i in range(n_skew)],
    "user_id":   [999] * n_skew,
    "amount":    np.round(np.random.uniform(1000, 100000, n_skew), 2),
    "event_time": [
        datetime(2025, 4, 1) + timedelta(seconds=int(s))
        for s in np.random.randint(0, 86400, n_skew)
    ],
}

normal_data = {
    "order_id":  [f"ORD-{i:08d}" for i in range(n_skew, TOTAL_ROWS)],
    "user_id":   np.random.randint(1, 999, n_normal),
    "amount":    np.round(np.random.uniform(1000, 100000, n_normal), 2),
    "event_time": [
        datetime(2025, 4, 1) + timedelta(seconds=int(s))
        for s in np.random.randint(0, 86400, n_normal)
    ],
}

df = pd.concat([pd.DataFrame(skew_data), pd.DataFrame(normal_data)], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_parquet(OUTPUT_PATH, index=False)
print(f"Saved to {OUTPUT_PATH}")
print(f"user_id=999 비율: {(df['user_id']==999).sum() / len(df) * 100:.1f}%")
