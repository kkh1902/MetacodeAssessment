"""
Q03 — Airflow Variable 과 Connection 활용
조건:
  - PostgreSQL 연결 정보를 Connection 으로 관리 (my_postgres_conn)
  - 대상 테이블명은 Variable 로 관리 (target_table)
  - 연결된 DB 에서 SELECT 쿼리 수행
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable


def query_table(**context):
    table = Variable.get("target_table", default_var="public.users")
    hook = PostgresHook(postgres_conn_id="my_postgres_conn")
    sql = f"SELECT * FROM {table} LIMIT 10"
    print(f"[query_table] table={table} sql={sql}")
    rows = hook.get_records(sql)
    for r in rows:
        print(r)
    print(f"[query_table] rows fetched = {len(rows)}")


with DAG(
    dag_id="db_query_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["week8", "q3"],
) as dag:
    select_from_table = PythonOperator(
        task_id="select_from_table",
        python_callable=query_table,
    )
