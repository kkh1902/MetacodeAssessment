"""
문제 1 - Kafka 부하 생성 스크립트
대량 메시지를 발행해서 Kafka broker에 GC 압력을 줍니다.

HEAP 256m 환경에서 이 스크립트 실행 시:
  → GC stop-the-world 발생 (수 초)
  → SESSION_TIMEOUT 3000ms 초과
  → Zookeeper session 만료 → leader election 반복
  → Spark job에서 LeaderNotAvailableException 발생

실행 방법:
  docker exec kafka-zk-broker1 python3 /opt/spark/jobs/kafka_producer.py
  또는
  python3 kafka_producer.py  (로컬에서 kafka-python 설치 후)
"""
from kafka import KafkaProducer
import time

BROKERS = ["localhost:19092", "localhost:19093", "localhost:19094"]
TOPIC = "events"
MESSAGE_SIZE = 5000   # bytes (5KB × 10000건 = 50MB → GC 압력)
TOTAL_MESSAGES = 10000

producer = KafkaProducer(bootstrap_servers=BROKERS)

print(f"[Producer] {TOTAL_MESSAGES}건 메시지 발행 시작 → GC 압력 유도")

for i in range(TOTAL_MESSAGES):
    value = f"msg-{i}-{'x' * MESSAGE_SIZE}".encode()
    producer.send(TOPIC, value=value)

    if i % 1000 == 0:
        print(f"  {i}/{TOTAL_MESSAGES} 발행 완료")
        producer.flush()

producer.flush()
producer.close()
print("[Producer] 완료")
