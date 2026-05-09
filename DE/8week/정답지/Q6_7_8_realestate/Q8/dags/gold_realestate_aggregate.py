"""
Q08 — Gold DAG
- ExternalTaskSensor 로 Q7 DAG 완료 대기
- gold_spark_sql.py 실행
- 적재 후 검증 task: 5개 테이블 row count > 0 확인
"""
from datetime import datetime
from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator

GOLD_TABLES = [
    "gold_realestate_district_avg",
    "gold_realestate_top10",
    "gold_realestate_size_dist",
    "gold_realestate_age_avg",
    "gold_realestate_mom_change",
]


def verify_tables(**context):
    hook = PostgresHook(postgres_conn_id="my_postgres_conn")
    for tbl in GOLD_TABLES:
        cnt = hook.get_first(f"SELECT COUNT(*) FROM {tbl}")[0]
        print(f"{tbl} row_count={cnt}")
        assert cnt > 0, f"{tbl} 0 rows"


with DAG(
    dag_id="gold_realestate_aggregate",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=True,
    max_active_runs=1,
    tags=["week8", "q8", "gold"],
) as dag:
    wait_silver = ExternalTaskSensor(
        task_id="wait_silver",
        external_dag_id="silver_realestate_transform",
        external_task_id="silver_transform",
        allowed_states=["success"],
        timeout=60 * 60,
        poke_interval=60,
        mode="reschedule",
    )

    aggregate = SparkSubmitOperator(
        task_id="gold_aggregate",
        application="/opt/airflow/scripts/gold_spark_sql.py",
        conn_id="spark_default",
        application_args=[
            "realestate-홍길동",
            "jdbc:postgresql://postgres:5432/airflow",
            "airflow",
            "airflow",
        ],
        packages="org.postgresql:postgresql:42.7.3,org.apache.hadoop:hadoop-aws:3.3.4",
        verbose=True,
    )

    verify = PythonOperator(
        task_id="verify_tables",
        python_callable=verify_tables,
    )

    wait_silver >> aggregate >> verify
