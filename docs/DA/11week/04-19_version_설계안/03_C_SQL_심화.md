# 설계안 C — SQL 심화 (Q1 + Q5)

## 요약

SQL 비중을 실무 수준으로 끌어올리는 방향. 단순 SELECT/DELETE → **서브쿼리·윈도우 함수·트랜잭션 롤백**으로 교체. SQL 문법 숙련도가 떨어지는 학생에게는 진짜 시험, LLM에게도 여러 개념 조합을 요구하는 스펙이라 저항 ↑.

---

## 변경 전/후 비교

### Q1 — 서브쿼리 + 윈도우 함수

| 항목 | v1 | v2 (C안) |
|---|---|---|
| 쿼리 유형 | 단일 `SELECT ... WHERE Type_1 IN (...)` | **서브쿼리** 또는 **CTE** 필수 |
| 조건 | 특정 type만 | "각 `Type_1`별 **평균 Total 이상**인 포켓몬만 조회" |
| 추가 컬럼 | 없음 | `RANK() OVER (PARTITION BY Type_1 ORDER BY Total DESC)` — type 내 순위 |
| 정렬 | 없음 | Type_1 ASC → rank ASC |
| 결과 검증 | 없음 | "결과 행 수는 **N** (N은 직접 구하시오)", "각 Type_1 그룹 내 rank 1번은 해당 type의 Total 최대값 포켓몬" |

**기대 쿼리 예시 (답지 기준)**:
```sql
WITH type_avg AS (
    SELECT Type_1, AVG(Total) AS avg_total
    FROM pokemon
    GROUP BY Type_1
)
SELECT
    p.*,
    RANK() OVER (PARTITION BY p.Type_1 ORDER BY p.Total DESC) AS rnk
FROM pokemon p
JOIN type_avg t ON p.Type_1 = t.Type_1
WHERE p.Total >= t.avg_total
ORDER BY p.Type_1 ASC, rnk ASC;
```

### Q5 — 트랜잭션 + 롤백

| 항목 | v1 | v2 (C안) |
|---|---|---|
| 주제 | 단순 DELETE + SELECT 검증 | DELETE를 **트랜잭션**으로 감싸고, **예상 삭제 건수와 불일치 시 ROLLBACK** |
| 사전 조건 | 없음 | "삭제 예상 건수 = 30 (변수로 정의)" |
| 실행 흐름 | `cursor.execute("DELETE ...")` → `commit` | `try:` 블록 안에서 `DELETE` → `cursor.rowcount` 확인 → 일치하면 `commit`, 불일치하면 `rollback` 후 `raise` |
| 출력 | 삭제 후 행 수 | 트랜잭션 결과(성공/롤백), 삭제 건수, 최종 남은 행 수 모두 출력 |
| 에러 케이스 | 없음 | "예상 건수를 29로 바꾸면 ROLLBACK 발생, DB 상태 불변" 검증 셀 추가 |

**기대 파이썬 로직 예시**:
```python
EXPECTED_DELETE = 30
try:
    cursor.execute("DELETE FROM pokemon WHERE Type_1 = 'Bug' AND Total < 300;")
    if cursor.rowcount != EXPECTED_DELETE:
        conn.rollback()
        raise ValueError(f"Expected {EXPECTED_DELETE} deletions, got {cursor.rowcount}")
    conn.commit()
    print(f"Deleted {cursor.rowcount} rows (committed)")
except Exception as e:
    print(f"Rolled back: {e}")
```

---

## LLM 저항 포인트

### Q1
1. **CTE vs 상관 서브쿼리 혼동**: LLM은 종종 상관 서브쿼리(`WHERE Total >= (SELECT AVG(Total) FROM pokemon WHERE Type_1 = p.Type_1)`)로 풀기도 함 — 결과는 맞지만 "CTE 사용" 명시하면 감점.
2. **RANK vs ROW_NUMBER vs DENSE_RANK**: tie가 있을 때 차이. 문제지에 "동점 처리는 RANK 사용(같은 순위 부여 후 skip)" 명시.
3. **MySQL 버전 호환성**: 윈도우 함수는 MySQL 8.0+. 8.0 미만 환경이면 서브쿼리로 우회 필요. 수업 환경 확인 후 문제지에 "MySQL 8.0+ 기준" 명기.
4. **Python에서 실행**: `pd.read_sql` 또는 cursor.fetchall → DataFrame 변환까지 요구.

### Q5
1. **`cursor.rowcount` 의미**: LLM은 `len(cursor.fetchall())`로 대체하려는 경향. `rowcount` 명시 강제.
2. **try/except 구조**: except 안에서 rollback 호출을 빼먹거나, commit 후 rollback하는 실수 유발.
3. **autocommit 설정**: 연결 객체의 `autocommit=False` 설정을 명시. LLM은 디폴트가 True인 드라이버에서 rollback이 무의미해짐을 놓침.
4. **raise 후 셀 실행 상태**: `raise` 이후에도 다음 셀이 DB 상태 검증해야 하므로 예외를 try-except 안에서 처리. 스펙 "raise를 catch하되 트랜잭션은 이미 rollback 완료" 명시 필요.

---

## 학생 예상 풀이 시간 / 난이도

| 항목 | v1 | v2 (C안) |
|---|:---:|:---:|
| Q1 소요 | 5~8분 | 20~25분 |
| Q5 소요 | 10분 | 20~25분 |
| 난이도 체감 | Easy / Medium | Hard / Hard |

SQL 수업 분량을 늘린 기수에 적합. 윈도우 함수를 강의에서 다루지 않았다면 매우 벅찬 수준.

---

## 답지 작성 필요 변경 사항

- **Q1 답지**:
  - CTE 기반 쿼리 작성
  - 윈도우 함수 결과 컬럼 포함
  - `pd.read_sql(query, conn)` 로 결과 DataFrame 출력
  - 각 Type_1 그룹의 rank=1 행만 별도 확인 셀 추가
- **Q5 답지**:
  - `autocommit=False` 명시
  - 트랜잭션 블록 + rowcount 검증
  - 성공 케이스와 롤백 케이스 각각 실행해 결과 비교
  - DB 상태를 `SELECT COUNT(*)`로 재확인하는 검증 셀

---

## 리스크

- **MySQL 버전 의존성**: 학생 로컬 MySQL이 5.7이면 윈도우 함수 실패. 사전 공지 또는 Docker MySQL 8.0 이미지 배포 권장.
- **트랜잭션 수업 선행 부재**: Q5의 try/except + rollback 패턴은 DB 트랜잭션 개념을 전제. 강의에서 안 다뤘다면 **문제지에 트랜잭션 구조 템플릿 코드**를 일부 제공해 난이도 조정 권장.
- **Python DB connector 차이**: `PyMySQL`, `mysql-connector-python`에서 `rowcount` 동작 미묘하게 다름. 사용하는 커넥터 명시 필수.

---

## 타 안과 혼용 시

- **C + A**: Q1(C), Q2(A) 조합 → SQL 심화 + Pandas 디테일. SQL·Pandas 두 축 모두 강화.
- **C + B**: Q1(C) + Q4(B) → SQL 실무 + 도메인 몰입도. 서로 영역이 달라 간섭 없음.

---

## 적용 대상 파일

- `DA/11week/11주차_공유용_문제지/04-19_version/11주차_과제_6문제_문제지_v2.ipynb` (Q1, Q5 셀)
- `DA/11week/11주차_공유용_답지/04-19_version/11주차_과제_6문제_답지_v2.ipynb` (Q1, Q5 셀)
