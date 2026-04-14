from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='hello_airflow_dag',
    default_args=default_args,
    description='Hello Airflow DAG',
    schedule='*/5 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hello'],
) as dag:

    hello_task = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hello Airflow"',
    )
