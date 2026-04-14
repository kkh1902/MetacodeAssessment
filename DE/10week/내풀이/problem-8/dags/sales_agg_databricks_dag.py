"""
10주차 문제 8 - 참조 DAG
문제 7에서 튜닝한 DAG를 DatabricksSubmitRunOperator로 교체한 버전입니다.

학생이 해야 할 것:
  1. Airflow Admin > Connections > databricks_default 설정
     - Conn Type: Databricks
     - Host: https://<your-workspace>.azuredatabricks.net
     - Password: <Databricks Personal Access Token>

  2. 아래 TODO 항목을 본인 환경에 맞게 수정

  3. 기본 cluster 설정으로 실행 후 성능 확인
"""
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

# TODO: 본인 Databricks 환경에 맞게 수정
DATABRICKS_CONN_ID  = "databricks_default"
DATABRICKS_JOB_PATH = "/Shared/sales_agg_job"   # Databricks workspace notebook 경로
CLUSTER_CONFIG = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id":  "Standard_DS3_v2",          # TODO: 본인 환경에 맞는 node type
    "num_workers":   2,                           # 기본값 — 튜닝 전
    "spark_conf": {
        "spark.executor.memory":        "2g",
        "spark.sql.shuffle.partitions": "200",    # 기본값 — 튜닝 전
    },
}

with DAG(
    dag_id="sales_aggregation_databricks",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-8"],
) as dag:

    run_on_databricks = DatabricksSubmitRunOperator(
        task_id="run_sales_agg_on_databricks",
        databricks_conn_id=DATABRICKS_CONN_ID,
        new_cluster=CLUSTER_CONFIG,
        notebook_task={
            "notebook_path": DATABRICKS_JOB_PATH,
            "base_parameters": {
                "execution_date": "{{ ds }}",
            },
        },
    )
