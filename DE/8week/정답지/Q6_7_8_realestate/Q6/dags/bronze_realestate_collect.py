"""
Q06 — 부동산 실거래가 Bronze (API 수집)
- DAG: bronze_realestate_collect
- 스케줄: @monthly, catchup=True
- TaskGroup 으로 6개 시군구 병렬 수집
- BranchPythonOperator 로 응답 0건/JSON 파싱 실패 분기
- S3: s3://realestate-{이름}/bronze/{yyyymm}/{LAWD_CD}.xml

채점 시 채점자가 SERVICE_KEY, AWS 키 채워서 실행.
"""
import os
from datetime import datetime
from urllib.parse import urlencode
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

# 본인이름·기수·키는 채점 시 채워서 실행
COLLECTOR_NAME = "홍길동"
SERVICE_KEY = ""  # data.go.kr 서비스 키
S3_BUCKET = f"realestate-{COLLECTOR_NAME}"

API_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
LAWD_CODES = ["11680", "11650", "11710", "11440", "11170", "11200"]


def collect_one(lawd_cd: str, **context):
    print(f"collector={COLLECTOR_NAME}, time={datetime.now()}, lawd={lawd_cd}")
    deal_ymd = context["logical_date"].strftime("%Y%m")
    params = {
        "serviceKey": SERVICE_KEY,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
        "numOfRows": 1000,
        "pageNo": 1,
    }
    res = requests.get(f"{API_URL}?{urlencode(params)}", timeout=30)
    res.raise_for_status()
    xml_text = res.text

    s3 = S3Hook(aws_conn_id="aws_default")
    key = f"bronze/{deal_ymd}/{lawd_cd}.xml"
    s3.load_string(xml_text, key=key, bucket_name=S3_BUCKET, replace=True)

    context["ti"].xcom_push(key=f"size_{lawd_cd}", value=len(xml_text))
    return len(xml_text)


def branch_after_collect(**context):
    """수집 결과 검증 — 모든 task 실패/0건이면 skip_upload 로 분기"""
    ti = context["ti"]
    sizes = [ti.xcom_pull(key=f"size_{cd}", task_ids=f"collect_group.collect_{cd}")
             for cd in LAWD_CODES]
    sizes = [s for s in sizes if s]
    if not sizes or all(s == 0 for s in sizes):
        return "skip_upload"
    return "summary_done"


with DAG(
    dag_id="bronze_realestate_collect",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=True,
    max_active_runs=1,
    tags=["week8", "q6", "bronze"],
) as dag:

    with TaskGroup(group_id="collect_group") as collect_group:
        for cd in LAWD_CODES:
            PythonOperator(
                task_id=f"collect_{cd}",
                python_callable=collect_one,
                op_kwargs={"lawd_cd": cd},
            )

    branch = BranchPythonOperator(
        task_id="branch_after_collect",
        python_callable=branch_after_collect,
        trigger_rule="all_done",
    )

    summary_done = EmptyOperator(task_id="summary_done")
    skip_upload = EmptyOperator(task_id="skip_upload")

    collect_group >> branch >> [summary_done, skip_upload]
