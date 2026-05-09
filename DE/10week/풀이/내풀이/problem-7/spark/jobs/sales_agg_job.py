"""
10주차 문제 7 - Spark job (버그 포함)
매출 데이터를 읽어 사용자별/날짜별 집계를 수행합니다.

버그:
  - 데이터 skew: 특정 user_id(999)에 전체 데이터의 80%가 몰려 있음
  - shuffle partition이 기본값(200)으로 설정되어 있어
    skew된 파티션이 executor 메모리를 초과 → OOM 발생
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, to_date

spark = SparkSession.builder \
    .appName("SalesAggJob") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 데이터 로드
df = spark.read.parquet("/opt/spark/data/sales_raw.parquet")

# BUG: skew 처리 없이 바로 groupBy
# user_id=999 데이터가 80%를 차지 → 해당 파티션 OOM
result = df.groupBy("user_id", to_date(col("event_time")).alias("sale_date")) \
    .agg(
        _sum("amount").alias("total_amount"),
        count("order_id").alias("order_count"),
    )

result.write \
    .mode("overwrite") \
    .parquet("/opt/spark/data/sales_aggregated.parquet")

print(f"Done. Total rows: {result.count()}")
spark.stop()
