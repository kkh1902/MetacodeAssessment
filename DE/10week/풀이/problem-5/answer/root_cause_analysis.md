# 문제 2 정답지 — k8s Spark Executor OOMKilled (버그 2개 동시)

## 버그 요약

| # | 위치 | 문제 | 정상값 |
|---|---|---|---|
| Bug 1 | `executor.javaOptions` | `-XX:+UseContainerSupport` 없음 | 반드시 포함 |
| Bug 2 | `executor.resources.limits.memory` | `1200Mi` (실제 필요량보다 낮음) | `1600Mi` 이상 |

---

## 버그 상호작용 메커니즘

### 메모리 계산 구조
```
executor.memory       = 1g    = 1024Mi  (JVM heap)
executor.memoryOverhead = 512m = 512Mi  (off-heap, native)
─────────────────────────────────────────
실제 필요 container 메모리    = 1536Mi

설정된 limits.memory          = 1200Mi  ← 부족
```

### Bug 1 단독 시나리오
```
UseContainerSupport 없음
    └─→ JVM이 container limits(1200Mi) 무시
            └─→ node 전체 메모리(예: 8Gi) 기준으로 ergonomics 계산
                    └─→ JVM heap = node 메모리의 25% = ~2048Mi 할당 시도
                            └─→ container limits 초과 → OOMKilled
```
→ Bug 1만 고치면: JVM이 container limits 인식 → 1024Mi heap 사용
→ 근데 Bug 2 때문에 overhead 포함 1536Mi > limits 1200Mi → 여전히 OOMKilled

### Bug 2 단독 시나리오
```
limits.memory = 1200Mi (낮음)
    └─→ UseContainerSupport 없으니 JVM은 limits 모름
            └─→ node 메모리 기준 heap 계산 → limits 초과 → OOMKilled
```
→ Bug 2만 고쳐서 limits = 1600Mi로 올려도:
→ UseContainerSupport 없으니 JVM이 node 메모리 기준으로 더 큰 heap 잡으려 함
→ 다른 pod OOM 유발 가능, 불안정

**둘 다 고쳐야** 비로소 정상 동작.

---

## 진단 경로 (수강생이 따라가야 할 순서)

### Step 1 — Pod 상태 확인
```bash
kubectl get pods -n spark
```
```
NAME                                READY   STATUS      RESTARTS
kafka-to-postgres-batch-exec-1      0/1     OOMKilled   3
kafka-to-postgres-batch-exec-2      0/1     OOMKilled   3
```

### Step 2 — Pod 상세 이벤트 확인
```bash
kubectl describe pod kafka-to-postgres-batch-exec-1 -n spark
```
```
Limits:
  memory: 1200Mi
Last State: Terminated
  Reason: OOMKilled
  Exit Code: 137
```
→ limits가 1200Mi인 것 확인, OOMKilled Exit Code 137

### Step 3 — 메모리 실사용량 확인
```bash
kubectl top pod -n spark
```
```
NAME                                CPU    MEMORY
kafka-to-postgres-batch-exec-1      890m   1489Mi  ← limits 1200Mi 초과
```
→ 실제 사용량이 limits보다 높음 → limits 자체가 낮거나 JVM이 너무 많이 잡는 것

### Step 4 — JVM 설정 분석
```bash
kubectl exec -n spark kafka-to-postgres-batch-exec-1 -- \
  java -XshowSettings:vm -version 2>&1
```
```
VM settings:
    Max. Heap Size (Estimated): 1.95G   ← container limits 1200Mi를 훨씬 초과
```
→ UseContainerSupport 없어서 JVM이 node 메모리(예: 8Gi) 기준으로 heap 계산

### Step 5 — 수치 검증
```
executor.memory(1g=1024Mi) + memoryOverhead(512Mi) = 1536Mi
limits.memory = 1200Mi
1536 > 1200 → Bug 2 독립적으로도 OOMKilled 발생
```

---

## 정답 수정

```yaml
# spark-application.yaml 수정

executor:
  memory: "1g"
  memoryOverhead: "512m"
  javaOptions: "-Dlog4j.logLevel=INFO -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+UseContainerSupport"  # Bug 1 수정
  resources:
    limits:
      memory: "1600Mi"   # Bug 2 수정: 1024Mi + 512Mi + 여유 64Mi
      cpu: "1"
    requests:
      memory: "1600Mi"
      cpu: "500m"
```

---

## 채점 포인트 (강사용)

- **Bug 1만 찾은 경우 절반 점수**: limits 문제까지 찾아야 완전한 답
- **Bug 2만 찾은 경우 절반 점수**: UseContainerSupport 누락이 근본 원인
- **`kubectl describe` 만 제출**: `kubectl top pod` 또는 JVM settings 확인 없으면 감점 (실측 근거 필수)
- **수치 계산 없이 "메모리 부족"만 쓴 경우 감점**: 1024+512=1536 > 1200 계산 과정 있어야 함
- **두 버그 모두 수정 후 executor Running 상태 캡처**: 최종 제출물 필수
