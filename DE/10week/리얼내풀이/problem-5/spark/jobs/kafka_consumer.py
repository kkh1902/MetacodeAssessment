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
