# DE 과제 채점 가이드

## 공통 원칙

- **0 or 10점 이진 채점** (부분점수 없음)
- 10문제 × 10점 = **100점 만점**
- 문제별 "만점 조건"을 모두 충족 → 10점, 하나라도 미흡 → 0점
- 감점 사유는 `채점기준서.md`와 `풀이`를 근거로 판정
- Excel 결과물 복붙용 피드백 행: **80점 이하는 연한 빨강 4(`F4B084`), 90점 이상은 연노랑(`FFF2CC`)**

### 복붙용 피드백 작성 규칙

- **기술적으로 작성한다** — 막연한 표현 금지. 누락된 파일명·옵션·옵코드·리소스 명시
  - ❌ `Q8 미흡` / `캡처 누락`
  - ✅ `8. capture/postgres_tables.png · capture/postgres_select.png 미제출`
  - ✅ `7. SparkSubmitOperator 사용했으나 application 인자에 Q2_1 .py 경로 누락`
- **감점 시 최소 3줄 이상** — 첫 줄은 총점, 둘째 줄부터 감점 사유 + 각 사유에 **파일 경로·코드 식별자·실제 값** 같은 기술적 디테일 포함하여 사유당 정보 밀도 높게 작성. 만점이면 `100` 한 줄만 (부가 텍스트 금지)
  - 예 (감점):
    ```
    60
    1. Q1/capture/airflow_ui.png 캡쳐 오류 — PDF 요구=hello_airflow_dag Task 성공 화면, 실제 내용=s3_download_dag Audit Log 화면. 코드 dag_id/BashOperator/schedule */5 모두 정상.
    7. Q7/capture/spark_ui.png 우상단 application UI="Streaming Log Processor"=Q5/stream_log_processor.py의 SparkSession.appName과 일치 → silver_spark.py 실행 시 4040 UI(appName="silver_realestate_transform") 아님. 메뉴바 Structured Streaming 탭 존재 + 타임스탬프(19:17:36) Q5 streaming_output.png와 동일.
    ```
  - 예 (만점):
    ```
    100
    ```
- 감점 항목은 `{Q번호}. {기술적 사유}` 형식, 줄바꿈 `\n` 으로 나열
- 사유는 **코드/캡처 파일 기준의 사실**만 — 추측·서술 금지

## 주차별 파일 위치

### 5주차 (Spark + S3 + Airflow)
- 채점기준서: `5week/채점기준서.md`
- 정답 풀이: `5week/풀이.md`
- 수강생 제출물: `5week/수강생/5주차_이름/`
- 채점 결과: `5week/채점결과.csv`, `5week/채점결과.xlsx`
- xlsx 재생성 스크립트: `5week/채점결과.py`
- 최종 리포트: `5week/5주차_채점_리포트.md`

### 8주차 (Spark + Airflow + K8s)
- 문제지: `8week/문제지/` (8주차_문제지.pdf, .docx, images/, data/, generate.py)
- 채점기준서: `8week/채점/채점기준서.md`
- 채점 결과: `8week/채점/채점결과.xlsx`
- 정답 코드 (본인 풀이): `8week/풀이/` (Q1~Q10, docker-compose.yml)
- 수강생 제출물: `8week/수강생/`
- 강사 정답지: `8week/정답지/` (강사 원본 수령 시)

### 9주차 (Kafka + Spark Streaming)
- 문제지: `9week/문제지/`
- 채점기준서: `9week/채점/채점기준서.md`
- 채점 결과: `9week/채점/채점결과.xlsx`
- 정답 코드 (본인 풀이): `9week/풀이/`
- 수강생 제출물: `9week/수강생/`
- 강사 정답지: `9week/정답지/` (강사 원본 수령 시)

### 10주차 (Kafka Cluster + PySpark + K8s)
- 문제지: `10week/문제지/`
- 채점기준서: `10week/채점/채점기준서.md`
- 채점 결과: `10week/채점/채점결과.xlsx`
- 정답 코드 (본인 풀이): `10week/풀이/`
- 수강생 제출물: `10week/수강생/`
- 강사 정답지: `10week/정답지/` (강사 원본 수령 시)

## 공통 체크리스트 (채점 시 주의)

1. **캡처본 요구 문제**: 단순 코드만 있고 실행 결과 스크린샷 없으면 0점
2. **AWS 키·민감정보**: 공란 또는 환경변수 처리 여부 확인
3. **S3 경로**: `s3a://` 스킴 필수 (Databricks Volumes 사용 시 0점 처리 전례 있음)
4. **파일명 스펙**: 정해진 파일명(예: `kafka_setup.png`, `spark_user_order_dag.py`) 확인
5. **공통 0점 조건**: 과제별로 특정 요구사항이 있으면 그것부터 먼저 체크
   - 예: 10주차 p1 — 모든 캡처에 `date && hostname` 출력 포함 필수
