"""
Q8 — 부동산 실거래가 Gold (집계 + PostgreSQL 적재)

ExternalTaskSensor 로 Q7 silver DAG 완료 대기 →
SparkSubmitOperator 로 gold_spark_sql.py 실행 →
적재된 5개 테이블 row count 검증.

채점자가 채울 키 (제출 시 빈 문자열):
  AWS_ACCESS_KEY_ID      = ''
  AWS_SECRET_ACCESS_KEY  = ''
  POSTGRES_CONN_ID       = 'postgres_default'

본인 이름:
  STUDENT_NAME = '홍길동'   ← 본인 이름으로 변경
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook


STUDENT_NAME = "홍길동"  # ← 본인 이름

GOLD_TABLES = [
    "gold_realestate_district_avg",
    "gold_realestate_top10",
    "gold_realestate_size_dist",
    "gold_realestate_age_avg",
    "gold_realestate_mom_change",
]


def verify_tables_have_rows(**context):
    """5개 gold 테이블 모두 row count > 0 인지 확인."""
    hook = PostgresHook(postgres_conn_id="postgres_default")
    failures = []
    for tbl in GOLD_TABLES:
        cnt = hook.get_first(f"SELECT COUNT(*) FROM {tbl}")[0]
        print(f"[{STUDENT_NAME}] {tbl}: {cnt} rows")
        if cnt == 0:
            failures.append(tbl)
    if failures:
        raise ValueError(f"empty tables: {failures}")
    print(f"[{STUDENT_NAME}] 모든 gold 테이블 row count > 0 검증 통과")


default_args = {
    "owner": STUDENT_NAME,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="gold_realestate_aggregate",
    default_args=default_args,
    description="부동산 실거래가 Gold 집계 → PostgreSQL 적재",
    start_date=datetime(2024, 1, 1),
    schedule="@monthly",
    catchup=True,
    tags=["realestate", "gold", "spark", "postgres", STUDENT_NAME],
) as dag:

    wait_silver = ExternalTaskSensor(
        task_id="wait_silver",
        external_dag_id="silver_realestate_transform",
        external_task_id=None,  # 전체 DAG 완료 대기
        allowed_states=["success"],
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60,
    )

    run_gold_spark = SparkSubmitOperator(
        task_id="run_gold_spark",
        application="/opt/airflow/scripts/q8/gold_spark_sql.py",
        application_args=["{{ ds_nodash[:6] }}"],  # yyyymm
        conn_id="spark_default",
        packages="org.postgresql:postgresql:42.7.3,org.apache.hadoop:hadoop-aws:3.3.4",
        verbose=True,
    )

    verify = PythonOperator(
        task_id="verify_table_rows",
        python_callable=verify_tables_have_rows,
    )

    wait_silver >> run_gold_spark >> verify
