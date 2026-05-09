"""
문제 5 - Spark 배치 Job (정상 코드)
Kafka sales-events 토픽을 읽어 PostgreSQL staging_sales 테이블에 적재합니다.

이 파일은 정상 동작합니다.
문제 5의 버그는 이 파일이 아닌 Airflow DAG(transfer_dag.py)에 있습니다.
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
    StructField("event_time", StringType(), True),
])

spark = SparkSession.builder \
    .appName("KafkaToStaging") \
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
    .withColumn("event_time", col("event_time").cast("timestamp")) \
    .withColumn(
        "event_time_kst",
        from_utc_timestamp(col("event_time"), "Asia/Seoul")
    ) \
    .withColumn("partition_date", to_date(col("event_time_kst")))

df_out = df.select("order_id", "user_id", "amount", "partition_date")

row_count = df_out.count()
print(f"[Spark] Kafka에서 읽은 행 수: {row_count}")

df_out.write \
    .mode("append") \
    .jdbc(PG_URL, "staging_sales", properties=PG_PROPS)

print(f"[Spark] staging_sales 적재 완료: {row_count} rows")
spark.stop()
