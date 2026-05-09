from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="hello_airflow_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    tags=["week8", "q1_1"],
) as dag:
    print_hello = BashOperator(
        task_id="print_hello",
        bash_command='echo "Hello Airflow"',
    )
