# DE 과제 채점 가이드

## 공통 원칙

- **0 or 10점 이진 채점** (부분점수 없음)
- 10문제 × 10점 = **100점 만점**
- 문제별 "만점 조건"을 모두 충족 → 10점, 하나라도 미흡 → 0점
- 감점 사유는 `채점기준서.md`와 `풀이`를 근거로 판정
- Excel 결과물 복붙용 피드백 행: **80점 이하는 연한 빨강 4(`F4B084`), 90점 이상은 연노랑(`FFF2CC`)**

## 주차별 파일 위치

### 5주차 (Spark + S3 + Airflow)
- 채점기준서: `5week/채점기준서.md`
- 정답 풀이: `5week/풀이.md`
- 수강생 제출물: `5week/수강생/5주차_이름/`
- 채점 결과: `5week/채점결과.csv`, `5week/채점결과.xlsx`
- xlsx 재생성 스크립트: `5week/채점결과.py`
- 최종 리포트: `5week/5주차_채점_리포트.md`

### 8주차 (Spark + Airflow + K8s)
- 채점기준서: `8week/채점기준서.md`
- 정답 코드: `8week/풀이/` (dags, docker-compose.yml, k8s, scripts)
- 수강생 제출물: `8week/수강생/8주차_이름/`
- 채점 결과: `8week/8주차_채점_리포트.md`
- 채점 스크립트: `8week/채점결과.py`

### 9주차 (Kafka + Spark Streaming)
- 채점기준서: `9week/채점기준서.md`
- 정답 코드: `9week/문제/click_analyzer.py`, `click_producer.py`
- 수강생 제출물: `9week/과제 제출/`
- 최종 리포트: `9week/9주차_채점_리포트.md`
- Docker: `9week/docker-compose.yml`

### 10주차 (Kafka Cluster + PySpark + K8s)
- 채점기준서: `10week/채점기준서.md`
- 문제 소스: `10week/문제_src/problem-1 ~ problem-10/`
- 정답 풀이: `10week/풀이/`, `10week/리얼내풀이/`, `10week/내풀이/`
- 수강생 제출물: `10week/수강생/10주차_이름/`
- 최종 리포트: `10week/10주차_채점_리포트.md`

## 공통 체크리스트 (채점 시 주의)

1. **캡처본 요구 문제**: 단순 코드만 있고 실행 결과 스크린샷 없으면 0점
2. **AWS 키·민감정보**: 공란 또는 환경변수 처리 여부 확인
3. **S3 경로**: `s3a://` 스킴 필수 (Databricks Volumes 사용 시 0점 처리 전례 있음)
4. **파일명 스펙**: 정해진 파일명(예: `kafka_setup.png`, `spark_user_order_dag.py`) 확인
5. **공통 0점 조건**: 과제별로 특정 요구사항이 있으면 그것부터 먼저 체크
   - 예: 10주차 p1 — 모든 캡처에 `date && hostname` 출력 포함 필수
