# Databricks Notebook — Sales Aggregation Job (튜닝 후)
# 경로: /Shared/sales_agg_job_tuned
# 클러스터: Standard_DS3_v2 × 4 workers (FIX-1)
#
# [튜닝 내용]
# FIX-1: num_workers 2 → 4 (parallelism 2배 확보)
# FIX-2: shuffle.partitions 200 → 400 (worker 증가에 비례)
# FIX-3: AQE 활성화 (런타임 skew 자동 감지)
# FIX-4: skewJoin 활성화 (skew 파티션 자동 분할)
# FIX-5: executor.memory 2g → 4g (GC overhead 감소)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, to_date

spark = SparkSession.builder \
    .appName("SalesAggJob_Tuned") \
    .config("spark.sql.shuffle.partitions", "400") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

DATA_PATH = "dbfs:/FileStore/sales_raw.parquet"

df = spark.read.parquet(DATA_PATH)

result = df.groupBy("user_id", to_date(col("event_time")).alias("sale_date")) \
    .agg(
        _sum("amount").alias("total_amount"),
        count("order_id").alias("order_count"),
    )

result.write \
    .mode("overwrite") \
    .parquet("dbfs:/FileStore/sales_aggregated_tuned.parquet")

count = result.count()
print(f"Done. Total rows: {count}")

display(result.limit(10))
