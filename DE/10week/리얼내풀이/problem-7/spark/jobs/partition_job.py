"""
10주차 문제 7 - 참조 코드 (버그 포함)
Kafka에서 sales-events를 읽어 날짜별 파티션으로 PostgreSQL에 적재합니다.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
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
    .appName("SalesPartitionJob") \
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

# BUG: timezone 변환 없이 바로 날짜 추출
# event_time은 UTC 기준이지만, to_date()는 Spark 세션 timezone(기본 UTC) 기준으로 날짜를 추출
# UTC 2025-04-01 00:00 ~ 08:59 데이터는 KST로 2025-04-01이지만
# 이 코드는 UTC 날짜 그대로 사용 → 2025-04-01 00:00 데이터가 2025-03-31 파티션에 들어감
df = df.withColumn("partition_date", to_date(col("event_time")))

df.write \
    .mode("append") \
    .partitionBy("partition_date") \
    .jdbc(PG_URL, "partitioned_sales", properties=PG_PROPS)

print("Job completed.")
spark.stop()
