"""
10주차 문제 4 - 풀이 (버그 수정)

[BUG 수정]
  to_date(event_time)  →  to_date(from_utc_timestamp(event_time, "Asia/Seoul"))

  원인:
    event_time은 UTC 기준 타임스탬프
    Spark의 to_date()는 세션 timezone(기본 UTC) 기준으로 날짜를 추출
    UTC 2025-03-31 15:00 ~ 23:59 = KST 2025-04-01 00:00 ~ 08:59
    → 버그: 2025-03-31 파티션에 저장됨 (올바른 파티션: 2025-04-01)

  수정:
    event_time(UTC)를 먼저 KST로 변환한 뒤 날짜 추출
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date, from_utc_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

KAFKA_BOOTSTRAP = "kafka-zk-broker1:9092"
TOPIC           = "sales-events"
PG_URL          = "jdbc:postgresql://postgres:5432/airflow"
PG_PROPS        = {"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}

schema = StructType([
    StructField("order_id",   StringType(), True),
    StructField("user_id",    StringType(), True),
    StructField("amount",     DoubleType(), True),
    StructField("event_time", StringType(), True),  # UTC ISO string
])

spark = SparkSession.builder \
    .appName("SalesPartitionJobFixed") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df_raw = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

df = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_time", col("event_time").cast("timestamp"))

# FIX: UTC → KST 변환 후 날짜 추출
df = df.withColumn(
    "event_time_kst",
    from_utc_timestamp(col("event_time"), "Asia/Seoul")
).withColumn(
    "partition_date",
    to_date(col("event_time_kst"))
)

df.write \
    .mode("append") \
    .partitionBy("partition_date") \
    .jdbc(PG_URL, "partitioned_sales", properties=PG_PROPS)

print("Job completed.")
spark.stop()
