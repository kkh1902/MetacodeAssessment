"""
Q01_2 — S3 에서 데이터 가져오기 (Airflow + boto3)
조건:
  - PythonOperator 사용
  - AWS 연결은 Airflow Connection (aws_default 또는 사용자 정의) 으로 구성
  - 다운로드 파일 저장 경로: /opt/airflow/data/data.csv
"""
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

S3_BUCKET = os.environ.get("S3_BUCKET", "metacode-de-8week")
S3_KEY = "data.csv"
LOCAL_DIR = "/opt/airflow/data"
LOCAL_PATH = f"{LOCAL_DIR}/data.csv"


def download_from_s3(**context):
    os.makedirs(LOCAL_DIR, exist_ok=True)
    hook = S3Hook(aws_conn_id="aws_default")
    s3_client = hook.get_conn()
    s3_client.download_file(S3_BUCKET, S3_KEY, LOCAL_PATH)
    print(f"Downloaded s3://{S3_BUCKET}/{S3_KEY} -> {LOCAL_PATH}")
    print(f"size = {os.path.getsize(LOCAL_PATH)} bytes")


with DAG(
    dag_id="s3_download_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["week8", "q1_2"],
) as dag:
    download_from_s3_task = PythonOperator(
        task_id="download_from_s3",
        python_callable=download_from_s3,
    )
