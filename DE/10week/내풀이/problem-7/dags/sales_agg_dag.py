"""
10주차 문제 7 - Airflow DAG (버그 포함)
SparkSubmitOperator로 sales_agg_job.py를 실행합니다.

버그:
  - executor-memory / driver-memory 설정 없음 (기본값 1g)
  - spark.sql.shuffle.partitions 기본값(200) 사용
  → skew된 데이터 처리 시 OOM 발생
"""
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sales_aggregation",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-7"],
) as dag:

    aggregate = SparkSubmitOperator(
        task_id="aggregate_sales",
        application="/opt/spark/jobs/sales_agg_job.py",
        conn_id="spark_default",
        # BUG: memory 설정 없음 → 기본값 1g로 실행
        # BUG: shuffle.partitions 기본값(200) 사용 → skew 파티션 OOM
        conf={
            "spark.executor.cores": "1",
        },
        verbose=True,
    )
