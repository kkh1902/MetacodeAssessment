"""
문제 2 - PySpark 배치 Job
Kafka user-events 토픽을 읽어 PostgreSQL user_events_stream 테이블에 저장합니다.

실행 방법: SparkApplication yaml을 통해 spark-operator가 실행합니다.
  kubectl apply -f kafka-to-postgres-batch.yaml

TODO: KAFKA_BOOTSTRAP, PG_URL, PG_PROPS를 본인 환경에 맞게 수정
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType

# TODO: 본인 k8s 환경의 Kafka 서비스명으로 수정
KAFKA_BOOTSTRAP = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
TOPIC           = "user-events"

# TODO: 본인 PostgreSQL 연결 정보로 수정
PG_URL   = "jdbc:postgresql://postgres:5432/userdb"
PG_PROPS = {
    "user":     "postgres",
    "password": "postgres",
    "driver":   "org.postgresql.Driver",
}
TABLE = "user_events_stream"

schema = StructType([
    StructField("user_id",   StringType(), True),
    StructField("event",     StringType(), True),
    StructField("timestamp", StringType(), True),
])

spark = SparkSession.builder \
    .appName("KafkaToPostgresBatch") \
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
    .withColumn("loaded_at", current_timestamp())

row_count = df.count()
print(f"[Spark] Kafka에서 읽은 행 수: {row_count}")

# 매 실행 시 테이블 재생성
df.write \
    .mode("overwrite") \
    .jdbc(PG_URL, TABLE, properties=PG_PROPS)

print(f"[Spark] '{TABLE}' 적재 완료: {row_count} rows")
spark.stop()
