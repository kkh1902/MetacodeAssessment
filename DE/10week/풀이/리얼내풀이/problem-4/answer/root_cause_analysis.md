# 가설 1
 ---
  버그 1: Kafka heap 256MB (너무 작음)
  os.memory.max=256MB   ← 3-broker 운영에 턱없이 부족
  → JVM GC 발생 시 모든 스레드 정지 (stop-the-world)

  ---
  버그 2: ZooKeeper session timeout 3초 (너무 짧음)
  sessionTimeout=3000
  zookeeper.session.timeout.ms = 3000
  → GC로 스레드 정지된 사이 heartbeat 못 보냄 → 3초 초과 → 세션 만료

  ---
  결과 cascade:
  09:47:31  ZK: Expiring session ... timeout of 6000ms exceeded  ← broker 세션 만료
  09:47:59  ZK: Invalid session ... probably expired             ← 재접속 거부
  10:04:40  Kafka: ERROR node already exists                     ← broker 재등록 실패
  09:58:22  Spark: ERROR BlockManager re-registration failure    ← Spark job 사망

  ZK 세션이 반복적으로 만료되는 게 핵심입니다 (0x...005, 003, 006, 004, 007, 008, 009, 00a, 00b — 총 9개
  세션).

  수정: KAFKA_HEAP_OPTS: "-Xms512m -Xmx1g" + KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS: "18000"

  
  수정 :
        KAFKA_HEAP_OPTS: "-Xms512m -Xmx1g"
      KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS: "18000"


# 문제 4 원인 분석

  ## 가설

  ### 가설 1: Kafka heap 부족으로 GC 발생
  - 검증 방법: `docker logs kafka-zk-broker1 | grep memory.max`
  - 결과: `os.memory.max=256MB` 확인 → 3-broker 운영에 부족, GC 유발

  ### 가설 2: ZooKeeper session timeout이 너무 짧음
  - 검증 방법: `docker logs kafka-zk-broker1 | grep session.timeout.ms`
  - 결과: `zookeeper.session.timeout.ms=3000` 확인 → 기본값(18000)의 1/6

  ### 가설 3: Kafka 네트워크 설정 오류 (배제)
  - 검증 방법: ADVERTISED_LISTENERS 설정 확인
  - 결과: 컨테이너 내부 통신 정상 → 네트워크 설정 문제 아님 → 배제

  ---

  ## 실제 원인 (가설 1 + 2 복합)

  | 설정 | 버그값 | 정상값 |
  |---|---|---|
  | KAFKA_HEAP_OPTS | -Xms256m -Xmx256m | -Xms512m -Xmx1g |
  | KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS | 3000 | 18000 |

  ## 인과관계 (cascade)

  256MB heap → GC stop-the-world 발생
    → heartbeat 전송 불가 → sessionTimeout=3000ms 초과
      → ZK: "Expiring session, timeout of 6000ms exceeded" (9회 반복)
        → Kafka: "ERROR node already exists" (broker 재등록 실패)
          → Spark: "ERROR BlockManager re-registration failure"

  ## 로그 근거

  **Kafka:** `os.memory.max=256MB` / `sessionTimeout=3000` / `ERROR node already exists`
  **ZooKeeper:** `Expiring session 0x... timeout of 6000ms exceeded` (총 9개 세션)
  **Spark:** `ERROR BlockManager: Exiting executor due to block manager re-registration failure`

  ---

  ## 수정 및 결과

  ```yaml
  KAFKA_HEAP_OPTS: "-Xms512m -Xmx1g"
  KAFKA_ZOOKEEPER_SESSION_TIMEOUT_MS: "18000"