# 문제 1 정답지 — Kafka GC → Zookeeper Session 만료 → Spark 실패 Cascading

## 버그 요약

| # | 위치 | 설정값 | 정상값 |
|---|---|---|---|
| Bug 1 | 모든 Kafka broker | `KAFKA_HEAP_OPTS: "-Xms256m -Xmx256m"` | `-Xms512m -Xmx1g` 이상 |
| Bug 2 | 모든 Kafka broker | `KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS: "6000"` | `18000` (기본값) |

---

## 버그 상호작용 메커니즘

```
KAFKA_HEAP_OPTS 256m
    └─→ JVM Heap 부족 → GC stop-the-world 발생 (수 초 단위)
            └─→ GC 중 Kafka broker thread 전부 정지
                    └─→ Zookeeper heartbeat 전송 불가
                            └─→ SESSION_TIMEOUT 6000ms 초과
                                    └─→ Zookeeper: broker session 만료
                                            └─→ Kafka: leader election 반복
                                                    └─→ Spark: LeaderNotAvailableException
```

**핵심 포인트**: Bug 1 단독 → 간헐적 slow. Bug 2 단독 → 정상(기본값 18s면 GC 여유 있음).
**둘이 합쳐지면** → GC pause(수 초) > session timeout(6초) = 확정 cascade.

---

## 로그 분석 경로 (수강생이 따라가야 할 순서)

### Step 1 — 최초 증상 (Spark 로그)
```
ERROR org.apache.kafka.clients.consumer.internals.ConsumerCoordinator
- [Consumer clientId=...] LeaderNotAvailableException for partition user-events-0
```
→ 얼핏 보면 Kafka broker 자체 문제처럼 보임

### Step 2 — Kafka broker 로그 확인
```bash
docker logs kafka-zk-broker1 2>&1 | grep -E "GC|ZooKeeper|session|leader"
```
```
[GC (Allocation Failure) ...] pause 4.231s
WARN ZooKeeperClient - ZooKeeperClient session expired
INFO KafkaServer - [KafkaServer id=1] shutting down
INFO KafkaServer - [KafkaServer id=1] starting
INFO LeaderAndIsrRequestHandler - Handling LeaderAndIsr request ...
```
→ GC pause가 먼저 나오고, 그 직후 session expired 패턴 확인

### Step 3 — Zookeeper 로그 확인
```bash
docker logs zookeeper 2>&1 | grep -E "session|expire|close"
```
```
WARN  - Expiring session ... (broker가 heartbeat 안 보낸 것)
```
→ Zookeeper 자체는 이상 없음. broker 쪽에서 heartbeat를 못 보낸 것

### Step 4 — 원인 특정
- GC pause duration > SESSION_TIMEOUT_MS → session 만료
- 256m heap은 3-broker 클러스터 운영에 부족 (프로덕션 최소 4~6g)

---

## 정답 수정

```yaml
# docker-compose.yaml 수정

kafka-zk-broker1:
  environment:
    KAFKA_HEAP_OPTS: "-Xms512m -Xmx1g"           # Bug 1 수정
    KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS: "18000"   # Bug 2 수정 (기본값 복원)

# broker2, broker3 동일하게 수정
```

---

## 채점 포인트 (강사용)

- **가설만 쓰고 로그 근거 없으면 감점**: "GC 문제인 것 같다"는 불충분, 로그 라인 인용 필수
- **Bug 1만 찾으면 절반 점수**: SESSION_TIMEOUT까지 연결해야 cascade 설명 완성
- **Spark 로그만 보고 끝낸 경우 0점**: Spark는 피해자, 원인 서비스가 Kafka임을 특정해야 함
- **둘 다 수정하고 재실행 성공 캡처**: 최종 제출물에 `docker ps` + Spark job 성공 로그 필요
