"""Q4-(2) Airflow DAG: spark-submit 으로 analyze_csv.py 실행"""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

SPARK_MASTER = "spark://spark-master:7077"
SCRIPT       = "/opt/airflow/scripts/analyze_csv.py"
DATA         = "/opt/airflow/data/data.csv"

with DAG(
    dag_id="run_spark_job",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["q4"],
) as dag:
    BashOperator(
        task_id="submit_spark_job",
        bash_command=f"spark-submit --master {SPARK_MASTER} {SCRIPT} {DATA}",
    )
