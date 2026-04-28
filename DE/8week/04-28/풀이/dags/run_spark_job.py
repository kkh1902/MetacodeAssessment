from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='run_spark_job',
    default_args=default_args,
    description='Run Spark CSV analysis job',
    schedule='*/5 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['spark'],
) as dag:

    spark_submit_task = BashOperator(
        task_id='submit_spark_job',
        bash_command=(
            'spark-submit '
            '--master spark://spark-master:7077 '
            '/opt/airflow/scripts/analyze_csv.py'
        ),
    )
