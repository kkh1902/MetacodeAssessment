"""
Q07 — Silver DAG
- ExternalTaskSensor 로 Q6 DAG 완료 대기
- silver_spark.py 실행 (SparkSubmitOperator)
"""
from datetime import datetime
from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="silver_realestate_transform",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=True,
    max_active_runs=1,
    tags=["week8", "q7", "silver"],
) as dag:
    wait_bronze = ExternalTaskSensor(
        task_id="wait_bronze",
        external_dag_id="bronze_realestate_collect",
        external_task_id="summary_done",
        allowed_states=["success"],
        timeout=60 * 60,
        poke_interval=60,
        mode="reschedule",
    )

    transform = SparkSubmitOperator(
        task_id="silver_transform",
        application="/opt/airflow/scripts/silver_spark.py",
        conn_id="spark_default",
        application_args=["realestate-홍길동", "{{ logical_date.strftime('%Y%m') }}"],
        packages="org.apache.hadoop:hadoop-aws:3.3.4",
        verbose=True,
    )

    wait_bronze >> transform
