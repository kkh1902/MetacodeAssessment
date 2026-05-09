"""
문제 1 - Kafka Producer (로컬 실행)
k3d 클러스터 내부 Kafka로 user-events 메시지를 발행합니다.

실행 전 확인:
  pip install kafka-python

실행:
  python3 producer.py
"""
import json
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

# k3d NodePort (외부 접근)
BOOTSTRAP_SERVERS = "localhost:30092"
TOPIC = "user-events"

EVENTS = ["login", "purchase", "view", "logout", "signup"]

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

print(f"Connected to Kafka: {BOOTSTRAP_SERVERS}")
print(f"Publishing to topic: {TOPIC}\n")

for i in range(100):
    msg = {
        "user_id": f"user_{random.randint(1, 500):04d}",
        "event": random.choice(EVENTS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    producer.send(TOPIC, value=msg)
    print(f"[{i+1:03d}] Sent: {msg}")
    time.sleep(0.05)

producer.flush()
producer.close()
print(f"\nDone. 100 events → topic '{TOPIC}'")
