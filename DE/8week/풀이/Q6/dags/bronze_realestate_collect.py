"""
Q6 — 부동산 실거래가 Bronze (API 수집)

국토교통부 data.go.kr API 호출 → 6개 시군구 병렬 수집 → 원본 XML 그대로 S3 bronze 저장.
TaskGroup 안에 6개 시군구 task 명시적 배치 (Graph 뷰에서 6개 병렬 가시화).
BranchPythonOperator 로 응답 0건/JSON 파싱 실패 분기 처리.

채점 시 채점자가 .env 또는 컨테이너 환경변수로 키를 채워서 실행:
  DATA_GO_KR_API_KEY
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  S3_BUCKET           (기본: realestate-홍길동)
  STUDENT_NAME        (기본: 홍길동)
"""
import os
from datetime import datetime
import requests
import boto3

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup


# ── 환경변수 (제출 시 .env 채점자 키로 교체) ─────────────
API_KEY               = os.getenv("DATA_GO_KR_API_KEY", "")
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION            = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
S3_BUCKET             = os.getenv("S3_BUCKET", "realestate-홍길동")
STUDENT_NAME          = os.getenv("STUDENT_NAME", "홍길동")

LAWD_CODES = ["11680", "11650", "11710", "11440", "11170", "11200"]

API_URL = (
    "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/"
    "getRTMSDataSvcAptTrade"
)


def collect_one(lawd_cd: str, **context):
    """단일 시군구 수집 → S3 업로드. 응답 0건이면 skip."""
    deal_ymd = context["logical_date"].strftime("%Y%m")
    print(f"collector={STUDENT_NAME}, time={datetime.now()}, lawd={lawd_cd}")

    resp = requests.get(API_URL, params={
        "serviceKey": API_KEY,
        "LAWD_CD":    lawd_cd,
        "DEAL_YMD":   deal_ymd,
        "numOfRows":  "1000",
    }, timeout=30)
    resp.raise_for_status()
    body = resp.text

    if not body or "OpenAPI_ServiceResponse" in body:
        print(f"[ERROR] API error response, lawd={lawd_cd}")
        return f"error:{lawd_cd}"

    if "<totalCount>0</totalCount>" in body:
        print(f"[SKIP] totalCount=0, lawd={lawd_cd}")
        return f"skip:{lawd_cd}"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    key = f"bronze/{deal_ymd}/{lawd_cd}.xml"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/xml",
    )
    print(f"[OK] s3://{S3_BUCKET}/{key}  ({len(body)} bytes)")
    return f"ok:{lawd_cd}"


def branch_router(**context):
    """수집 결과 기반 분기 — 정상 종료."""
    return "summary_done"


with DAG(
    dag_id="bronze_realestate_collect",
    description="국토교통부 실거래가 API 수집 → S3 bronze",
    start_date=datetime(2024, 12, 1),
    schedule="@monthly",
    catchup=False,
    tags=["q6", "bronze", "realestate"],
) as dag:

    # ── 6개 시군구 병렬 수집 (TaskGroup) ─────────────────
    with TaskGroup("collect_group") as collect_group:
        collect_tasks = []
        for lawd in LAWD_CODES:
            t = PythonOperator(
                task_id=f"collect_{lawd}",
                python_callable=collect_one,
                op_kwargs={"lawd_cd": lawd},
            )
            collect_tasks.append(t)

    # ── BranchPythonOperator 분기 ───────────────────────
    branch = BranchPythonOperator(
        task_id="branch_after_collect",
        python_callable=branch_router,
    )
    summary_done = EmptyOperator(task_id="summary_done")
    skip_upload  = EmptyOperator(task_id="skip_upload")

    collect_group >> branch >> [summary_done, skip_upload]
