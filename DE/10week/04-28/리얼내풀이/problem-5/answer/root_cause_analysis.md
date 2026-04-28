# Problem 2: k8s Spark Executor OOMKilled — 원인 분석

## 환경 정보

- 날짜: Fri Apr  3 12:02:03 KST 2026
- 호스트: DESKTOP-C6I91MV
- k3d 클러스터: spark-cluster (server 1, agents 2)
- Spark 버전: 3.5.4
- Spark Operator: v1.4.6 (v1beta2 API)

---

## 현상

```
kubectl get pods -n spark
NAME                                   READY   STATUS      RESTARTS   AGE
memory-stress-driver                   1/1     Running     0          30s
memorystress-d185ea9d5140ba54-exec-1   0/1     OOMKilled   0          8s
memorystress-d185ea9d5140ba54-exec-2   0/1     OOMKilled   0          8s
```

- driver pod: 정상 Running
- executor pod 2개: 기동 후 7~8초 만에 **OOMKilled (Exit Code 137)**
- executor가 반복 재시도 후 SparkApplication FAILED

---

## 원인 가설

### 가설 1: executor Python 프로세스의 off-heap 메모리가 container limit 초과
- Spark executor는 JVM + Python worker 프로세스로 구성
- Python worker가 JVM heap 외부에 메모리를 할당하면 container 전체 limit에 걸림
- `memoryOverhead`가 너무 작으면 Python off-heap 영역이 부족해 OOMKilled 발생

### 가설 2: javaOptions에 deprecated GC 플래그로 JVM 초기화 실패
- `-XX:+PrintGCDetails`, `-XX:+PrintGCDateStamps`는 JDK 9+ 에서 deprecated/removed
- JVM 옵션 오류 시 executor 프로세스가 비정상 종료될 수 있음

---

## 실제 원인 (버그 2개)

### Bug 1: `memoryOverhead` 부족 (주원인)

**설정값:**
```yaml
executor:
  memory: "512m"
  memoryOverhead: "64m"
```

**메모리 계산:**
```
container limit = memory + memoryOverhead
               = 512m + 64m
               = 576m

Python 프로세스 할당 시도: 700MB
700MB > 576MB → OOMKilled (Exit Code 137)
```

**JVM 확인:**
```
Max. Heap Size (Estimated): 348.00M  ← JVM heap은 512m 이내
```
JVM heap 자체는 limit 내에 있으나, Python worker가 JVM 외부에서 700MB 할당을 시도하면서 container limit(576m)을 초과.

### Bug 2: deprecated javaOptions (부가 원인)

**설정값:**
```yaml
javaOptions: "-XX:+PrintGCDetails -XX:+PrintGCDateStamps"
```

- `-XX:+PrintGCDetails`: JDK 9에서 deprecated, JDK 14에서 제거
- `-XX:+PrintGCDateStamps`: 동일하게 deprecated
- 현재 JVM: OpenJDK 11.0.25 → 플래그는 경고 출력 후 무시되나, 운영환경에서 불필요한 GC 로그를 stderr에 출력해 로그 분석을 방해

---

## 버그 단독 수정 시 동작 차이

| 수정 케이스 | 결과 |
|---|---|
| Bug 1만 수정 (overhead 증가) | executor 정상 완료 가능하나 javaOptions 경고 잔존 |
| Bug 2만 수정 (javaOptions 제거) | 여전히 OOMKilled (700MB > 576MB) |
| **Bug 1 + Bug 2 모두 수정** | executor 정상 Completed ✅ |

Bug 1이 실제 OOMKilled의 직접 원인이며, Bug 2는 설정 품질 문제.  
**두 버그 모두 수정해야 완전한 해결.**

---

## 수정 방법

```yaml
executor:
  memory: "1g"           # 700MB Python 할당 + JVM heap 여유 확보
  memoryOverhead: "1g" # off-heap 영역 충분히 확보
  # javaOptions 제거    # deprecated 플래그 삭제
```

**수정 후 container limit 계산:**
```
container limit (executor) = 1g + 1g = 2g
container limit (driver)  = 1g + 512m = 1.5g
Python 700MB << 2g → OOMKilled 없음 ✅
```
