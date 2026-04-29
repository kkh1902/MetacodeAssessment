"""
Q1 — 첫 번째 DAG 만들기
BashOperator로 "Hello, Airflow!" 출력
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="hello_airflow_dag",
    description="Q1 — Hello Airflow 출력 DAG",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",   # 매 5분마다
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=1)},
    tags=["q1"],
) as dag:

    BashOperator(
        task_id="say_hello",
        bash_command='echo "Hello, Airflow!"',
    )
