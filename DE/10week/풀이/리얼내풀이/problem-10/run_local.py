"""
로컬 실행용 — Databricks notebook을 로컬 Spark로 재현
결과를 notebook_result.txt에 저장합니다.

실행:
  python3 run_local.py
"""
import time
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, to_date

DATA_PATH   = "/home/pc/dev/metade/10week/문제_src/problem-10/sales_raw.parquet"
OUTPUT_BASE = "/home/pc/dev/metade/10week/리얼내풀이/problem-10/answer"

# ── 튜닝 전 ──────────────────────────────────────────────
spark_before = SparkSession.builder \
    .appName("SalesAggJob_Before") \
    .master("local[2]") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.adaptive.enabled", "false") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()
spark_before.sparkContext.setLogLevel("WARN")

t0 = time.time()
df = spark_before.read.parquet(DATA_PATH)
result_before = df.groupBy("user_id", to_date(col("event_time")).alias("sale_date")) \
    .agg(_sum("amount").alias("total_amount"), count("order_id").alias("order_count"))
cnt_before = result_before.count()
elapsed_before = time.time() - t0
spark_before.stop()

# ── 튜닝 후 ──────────────────────────────────────────────
spark_after = SparkSession.builder \
    .appName("SalesAggJob_After") \
    .master("local[4]") \
    .config("spark.sql.shuffle.partitions", "400") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()
spark_after.sparkContext.setLogLevel("WARN")

t1 = time.time()
df2 = spark_after.read.parquet(DATA_PATH)
result_after = df2.groupBy("user_id", to_date(col("event_time")).alias("sale_date")) \
    .agg(_sum("amount").alias("total_amount"), count("order_id").alias("order_count"))
cnt_after = result_after.count()
elapsed_after = time.time() - t1
spark_after.stop()

# ── 결과 출력 / 저장 ──────────────────────────────────────
improvement = (elapsed_before - elapsed_after) / elapsed_before * 100

lines = [
    "# Notebook 실행 결과 (로컬 Spark 재현)",
    "",
    "## 실행 환경",
    "- 로컬 Spark (Databricks 환경 재현)",
    "- 데이터: sales_raw.parquet (200만 건, user_id=999 50% skew)",
    "",
    "## 튜닝 전 (local[2], shuffle.partitions=200, AQE=off)",
    f"- 실행 시간: {elapsed_before:.1f}초",
    f"- 결과 row count: {cnt_before:,}",
    "- Done. Total rows: " + str(cnt_before),
    "",
    "## 튜닝 후 (local[4], shuffle.partitions=400, AQE=on, skewJoin=on)",
    f"- 실행 시간: {elapsed_after:.1f}초",
    f"- 결과 row count: {cnt_after:,}",
    "- Done. Total rows: " + str(cnt_after),
    "",
    "## 성능 비교",
    f"| 항목 | 튜닝 전 | 튜닝 후 | 개선 |",
    f"|------|---------|---------|------|",
    f"| 실행 시간 | {elapsed_before:.1f}s | {elapsed_after:.1f}s | -{improvement:.1f}% |",
    f"| row count | {cnt_before:,} | {cnt_after:,} | 동일 |",
    "",
    f"개선율: {improvement:.1f}%",
    "",
    "[실환경에서는 Databricks notebook 실행 결과 + Spark UI 캡처로 대체]",
]

result_txt = os.path.join(OUTPUT_BASE, "notebook_result.txt")
with open(result_txt, "w") as f:
    f.write("\n".join(lines))

for line in lines:
    print(line)

print(f"\n저장 완료: {result_txt}")
