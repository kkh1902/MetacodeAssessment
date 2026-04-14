# Databricks Notebook — Sales Aggregation Job (기본 설정)
# 경로: /Shared/sales_agg_job
# 클러스터: Standard_DS3_v2 × 2 workers, shuffle.partitions=200

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, to_date

spark = SparkSession.builder \
    .appName("SalesAggJob") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Databricks DBFS 경로 (수강생이 업로드한 parquet)
DATA_PATH = "dbfs:/FileStore/sales_raw.parquet"

df = spark.read.parquet(DATA_PATH)

result = df.groupBy("user_id", to_date(col("event_time")).alias("sale_date")) \
    .agg(
        _sum("amount").alias("total_amount"),
        count("order_id").alias("order_count"),
    )

result.write \
    .mode("overwrite") \
    .parquet("dbfs:/FileStore/sales_aggregated.parquet")

count = result.count()
print(f"Done. Total rows: {count}")

# Databricks display
display(result.limit(10))
