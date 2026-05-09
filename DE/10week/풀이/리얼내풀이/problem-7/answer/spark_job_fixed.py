"""
10주차 문제 7 - 참조 코드 (버그 포함)
Kafka에서 sales-events를 읽어 날짜별 파티션으로 PostgreSQL에 적재합니다.
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

# FIX: UTC → KST 변환 후 날짜 추출
# from_utc_timestamp(event_time, "Asia/Seoul") → UTC timestamp를 KST로 변환
# to_date()로 KST 기준 날짜 추출 → 올바른 파티션에 적재
df = df.withColumn("partition_date", to_date(from_utc_timestamp(col("event_time"), "Asia/Seoul")))

df.write \
    .mode("append") \
    .jdbc(PG_URL, "partitioned_sales", properties=PG_PROPS)

print("Job completed.")
spark.stop()
