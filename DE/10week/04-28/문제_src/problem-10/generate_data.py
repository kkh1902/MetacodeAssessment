"""
문제 10 - 데이터 생성 스크립트
sales_raw.parquet를 생성하여 Databricks DBFS에 업로드합니다.

[실행 방법]
  pip install pandas pyarrow
  python3 generate_data.py

[생성 데이터 특성]
  - 총 200만 건 (2,000,000 rows)
  - user_id: 1~999, 단 user_id=999에 전체 50% 집중 (skew 유발)
  - event_time: 2024-01-01 ~ 2024-03-31 (3개월)
  - amount: 1,000~100,000 (원)

[DBFS 업로드]
  Databricks CLI 설치 후:
    databricks fs cp sales_raw.parquet dbfs:/FileStore/sales_raw.parquet

  또는 Databricks UI:
    Data > Add Data > Upload File > sales_raw.parquet
"""

import pandas as pd
import numpy as np

SEED        = 42
TOTAL_ROWS  = 2_000_000
SKEW_USER   = 999          # 이 user_id에 50% 집중
SKEW_RATIO  = 0.5          # skew user 비율

np.random.seed(SEED)

# skew user 행수
skew_rows   = int(TOTAL_ROWS * SKEW_RATIO)
normal_rows = TOTAL_ROWS - skew_rows

# 일반 user_id (1~998)
normal_user_ids = np.random.randint(1, SKEW_USER, size=normal_rows)
skew_user_ids   = np.full(skew_rows, SKEW_USER)
user_ids        = np.concatenate([normal_user_ids, skew_user_ids])

# order_id
order_ids = np.arange(1, TOTAL_ROWS + 1)

# event_time: 2024-01-01 ~ 2024-03-31 (microsecond 단위)
start_ts = pd.Timestamp("2024-01-01", tz="UTC")
end_ts   = pd.Timestamp("2024-03-31 23:59:59", tz="UTC")
seconds_range = int((end_ts - start_ts).total_seconds())
random_seconds = np.random.randint(0, seconds_range, size=TOTAL_ROWS)
event_times = pd.to_datetime(
    start_ts.value + random_seconds * 1_000_000_000,
    utc=True,
).astype("datetime64[us, UTC]")

# amount: 1,000 ~ 100,000
amounts = np.random.randint(1_000, 100_001, size=TOTAL_ROWS)

df = pd.DataFrame({
    "order_id":   order_ids,
    "user_id":    user_ids,
    "event_time": event_times,
    "amount":     amounts,
})

# shuffle
df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

output = "sales_raw.parquet"
df.to_parquet(output, index=False, engine="pyarrow")

print(f"생성 완료: {output}")
print(f"  총 rows      : {len(df):,}")
print(f"  user_id 종류 : {df['user_id'].nunique()}")
print(f"  user_id=999  : {(df['user_id'] == SKEW_USER).sum():,} rows ({SKEW_RATIO*100:.0f}%)")
print(f"  기간         : {df['event_time'].min()} ~ {df['event_time'].max()}")
print(f"  amount 범위  : {df['amount'].min():,} ~ {df['amount'].max():,}")
print()
print("다음 단계: Databricks DBFS에 업로드")
print("  databricks fs cp sales_raw.parquet dbfs:/FileStore/sales_raw.parquet")
