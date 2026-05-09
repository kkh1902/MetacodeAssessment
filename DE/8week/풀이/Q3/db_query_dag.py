"""
Q3 — Airflow Variable + Connection 활용 (PostgreSQL SELECT)
사전:
  - Connection: postgres_default (Postgres)
  - Variable:   target_table = dag (예시)
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable


def run_query():
    table = Variable.get("target_table", default_var="dag")
    hook = PostgresHook(postgres_conn_id="postgres_default")
    sql = f"SELECT * FROM {table} LIMIT 5;"
    print(f"[Q3] SQL: {sql}")
    rows = hook.get_records(sql)
    print(f"[Q3] {len(rows)} rows:")
    for r in rows:
        print(r)


with DAG(
    dag_id="db_query_dag",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["q3"],
) as dag:
    PythonOperator(task_id="run_select", python_callable=run_query)
