"""
Q02_2 — Airflow 로 Spark 작업 자동화하기
조건:
  - SparkSubmitOperator 사용
  - Spark 코드는 Q02_1 의 analyze_csv.py 활용
  - 스케줄은 매 5 분
"""
from datetime import datetime
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="run_spark_job",
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    tags=["week8", "q2_2"],
) as dag:
    spark_submit = SparkSubmitOperator(
        task_id="run_analyze_csv",
        application="/opt/airflow/dags/analyze_csv.py",
        conn_id="spark_default",
        application_args=["/opt/airflow/data/data.csv", "age"],
        conf={"spark.master": "local[*]"},
        verbose=True,
    )
