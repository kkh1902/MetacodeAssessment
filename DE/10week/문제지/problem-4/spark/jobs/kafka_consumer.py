"""
문제 4 - Spark Streaming Job
Kafka에서 events 토픽을 지속적으로 읽습니다.

실행 방법:
  docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/jobs/kafka_consumer.py
"""
from pyspark.sql import SparkSession
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

KAFKA_BROKERS = "kafka-zk-broker1:9092"
TOPIC = "events"

# 토픽 없으면 자동 생성
try:
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKERS)
    admin.create_topics([NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)])
    print(f"[KafkaConsumer] 토픽 '{TOPIC}' 생성 완료")
    admin.close()
except TopicAlreadyExistsError:
    print(f"[KafkaConsumer] 토픽 '{TOPIC}' 이미 존재")

spark = SparkSession.builder \
    .appName("KafkaConsumer-Problem1") \
    .config("spark.driver.host", "spark-master") \
    .config("spark.executor.memory", "512m") \
    .config("spark.executor.memoryOverhead", "96m") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print(f"[KafkaConsumer] Connecting to {KAFKA_BROKERS}, topic={TOPIC}")

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

batch_count = [0]

def process_batch(batch_df, batch_id):
    count = batch_df.count()
    print(f"[KafkaConsumer] ✅ Batch {batch_id} 성공 — {count}건 수신")
    batch_count[0] += 1
    if batch_count[0] >= 3:
        print("[KafkaConsumer] 3회 배치 완료 — 종료합니다.")
        query.stop()

query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .foreachBatch(process_batch) \
    .start()

query.awaitTermination()
