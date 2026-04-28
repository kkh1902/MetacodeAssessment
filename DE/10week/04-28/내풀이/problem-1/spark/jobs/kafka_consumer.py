"""
문제 1 - Spark Streaming Job
Kafka에서 events 토픽을 지속적으로 읽습니다.

Kafka 버그(HEAP 256m + SESSION_TIMEOUT 6000ms) 발생 시:
  → org.apache.kafka.common.errors.LeaderNotAvailableException
  → org.apache.kafka.common.errors.NotLeaderOrFollowerException
  → KafkaProducer: Leader not available for partition

실행 방법:
  docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/jobs/kafka_consumer.py
"""
from pyspark.sql import SparkSession
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

KAFKA_BROKERS = "kafka-zk-broker1:9092,kafka-zk-broker2:9092,kafka-zk-broker3:9092"
TOPIC = "events"

# 토픽 없으면 자동 생성
try:
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKERS)
    admin.create_topics([NewTopic(name=TOPIC, num_partitions=3, replication_factor=3)])
    print(f"[KafkaConsumer] 토픽 '{TOPIC}' 생성 완료")
    admin.close()
except TopicAlreadyExistsError:
    print(f"[KafkaConsumer] 토픽 '{TOPIC}' 이미 존재")

spark = SparkSession.builder \
    .appName("KafkaConsumer-Problem1") \
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

query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
