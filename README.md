# Metacode 부트캠프 과제 채점 시스템

메타코드 부트캠프의 트랙별 주차 과제를 관리하고 채점하는 레포지토리입니다.

---

## 트랙 구성

| 트랙 | 폴더 | 상태 |
|------|------|------|
| Data Engineering | `DE/` | 운영 중 (8~10주차) |
| Data Analysis | `DA/` | 운영 중 (8, 12주차) |
| AI LLM | `AILLM/` | 준비 중 |
| AI Service | `AISERVICE/` | 준비 중 |

---

## 폴더 구조

```
Assessment/
├── DE/                          # Data Engineering 트랙
│   ├── 8week/
│   │   ├── 채점기준서.md        # 채점 루브릭 (10문제 × 10점)
│   │   ├── 채점결과.xlsx        # 채점 결과 (수강생 × 문제)
│   │   ├── 8주차_채점_리포트.md  # 통과율, 오답 분석 리포트
│   │   ├── 문제/               # 문제지
│   │   ├── 풀이/               # 참고 풀이 코드
│   │   └── 수강생/             # 수강생 제출물 (로컬 전용, git 미추적)
│   ├── 9week/
│   │   ├── 채점기준서.md
│   │   ├── 문제/
│   │   └── 과제 제출/          # 수강생 제출물 (로컬 전용, git 미추적)
│   └── 10week/
│       ├── 채점기준서.md
│       ├── 채점결과.xlsx
│       ├── 문제_src/           # 문제 소스 템플릿
│       ├── 풀이/               # 참고 풀이
│       └── 수강생/             # 수강생 제출물 (로컬 전용, git 미추적)
│
├── DA/                          # Data Analysis 트랙
│   ├── 8week/
│   │   ├── 채점기준서_8주차.md  # Python Q1~Q9 + Tableau 루브릭
│   │   ├── 문제지/
│   │   ├── 정답지/
│   │   └── 수강생/             # 수강생 제출물 (로컬 전용, git 미추적)
│   └── 12week/
│       ├── 12주차_공유용_문제지/
│       ├── 12주차_답지/
│       └── 수강생/             # 수강생 제출물 (로컬 전용, git 미추적)
│
├── AILLM/                       # AI LLM 트랙 (준비 중)
└── AISERVICE/                   # AI Service 트랙 (준비 중)
```

---

## 채점 방식

### 공통 원칙
- **이진 채점**: O (10점) / X (0점)
- **코드 + 증빙 스크린샷** 모두 필요 (코드만 제출 시 X 처리)
- 스크린샷에는 `date && hostname` 출력 포함 필수 (환경 증명)

### 트랙별 구성

#### Data Engineering
| 주차 | 주요 기술 | 문제 수 | 만점 |
|------|----------|--------|------|
| 8주차 | Airflow DAG, PySpark, S3(LocalStack), Kubernetes | 10 | 100점 |
| 9주차 | Kafka, Spark Streaming, Docker Compose | 10 | 100점 |
| 10주차 | DB 튜닝, Airflow 스케줄링, Spark 파티셔닝, Databricks | 10 | 100점 |

#### Data Analysis
| 주차 | 주요 기술 | 구성 |
|------|----------|------|
| 8주차 | Pandas, 통계 분석, AB 테스트, Tableau | Python Q1~Q9 (90점) + Tableau (10점) |
| 12주차 | Git, Tableau, AI Agent | 복합 과제 |

---

## 수강생 제출물 관리

수강생 제출물 폴더(`수강생/`, `과제 제출/`)는 `.gitignore`로 추적하지 않습니다.  
폴더 구조는 `.gitkeep` 파일로 유지됩니다.

수강생 제출물을 받으면 각 트랙의 수강생 폴더에 로컬로 배치하세요:

```
DE/10week/수강생/<이름_10주차>/
DA/8week/수강생/<이름>/
```

---

## 채점 가이드

1. 해당 주차의 `채점기준서.md` 확인
2. `풀이/` 폴더의 참고 코드와 비교
3. 수강생 코드 + 스크린샷 검토
4. `채점결과.xlsx`에 O/X 기록
5. 주차 완료 후 `채점_리포트.md` 작성

---

## 기술 스택

| 분야 | 기술 |
|------|------|
| 워크플로우 | Apache Airflow 2.7.3 |
| 데이터 처리 | PySpark 3.5 |
| 스트리밍 | Kafka 7.6.0 (Confluent) |
| 컨테이너 | Docker, Docker Compose |
| 오케스트레이션 | Kubernetes (k3d) |
| 스토리지 | AWS S3 / LocalStack |
| 데이터베이스 | PostgreSQL 13 |
| 시각화 | Tableau |
| 분석 | Python, Pandas, Matplotlib |
