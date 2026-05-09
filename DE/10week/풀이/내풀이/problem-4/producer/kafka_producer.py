"""
문제 4 - Kafka Producer
UTC 기준 타임스탬프로 이벤트를 발행합니다.
날짜 경계(UTC 2025-04-01 00:00 ~ 08:59) 부근 데이터 100건을 발행합니다.
"""
import json
import time
import random
from datetime import datetime, timezone, timedelta
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "localhost:19092"
TOPIC = "sales-events"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# UTC 2025-04-01 00:00 ~ 08:59 범위 (KST 기준으로는 2025-04-01 09:00 ~ 17:59)
base = datetime(2025, 4, 1, 0, 0, 0, tzinfo=timezone.utc)

for i in range(100):
    event_time = base + timedelta(minutes=i * 5)  # 5분 간격, 총 500분 = 8시간20분
    event = {
        "order_id": f"ORD-{i:05d}",
        "user_id": random.randint(1, 1000),
        "amount": round(random.uniform(1000, 100000), 2),
        "event_time": event_time.strftime("%Y-%m-%d %H:%M:%S"),  # UTC
    }
    producer.send(TOPIC, value=event)
    print(f"Sent: {event['order_id']} | event_time(UTC): {event['event_time']}")

producer.flush()
print("\nDone. 100 events sent.")
print("기대값: 모두 2025-04-01 파티션에 적재되어야 함 (KST 기준)")
