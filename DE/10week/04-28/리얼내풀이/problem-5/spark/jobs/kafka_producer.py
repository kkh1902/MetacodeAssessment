from kafka import KafkaProducer

BROKERS = ["localhost:19092", "localhost:19093", "localhost:19094"]
TOPIC = "events"
MESSAGE_SIZE = 5000
TOTAL_MESSAGES = 100

producer = KafkaProducer(bootstrap_servers=BROKERS)

print(f"[Producer] {TOTAL_MESSAGES}건 메시지 발행 시작")

for i in range(TOTAL_MESSAGES):
    value = f"msg-{i}-{'x' * MESSAGE_SIZE}".encode()
    producer.send(TOPIC, value=value)

    if i % 1000 == 0:
        print(f"  {i}/{TOTAL_MESSAGES} 발행 완료")
        producer.flush()

producer.flush()
producer.close()
print("[Producer] 완료")
