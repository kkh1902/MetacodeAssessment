"""
10주차 문제 3 - 풀이 (버그 수정)

[BUG-1 수정]
  datetime.now() → context['data_interval_start']
  Airflow logical_date 기준으로 날짜 범위를 고정
  → 동일 execution_date로 몇 번을 재실행해도 같은 범위만 조회

[BUG-2 수정]
  plain INSERT → DELETE-INSERT (멱등성 보장)
  실행 전 해당 날짜 데이터를 먼저 삭제하고 재적재
  → 재실행 횟수와 무관하게 결과 동일
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


def load_daily_sales(**context):
    hook = PostgresHook(postgres_conn_id="postgres_default")

    # FIX-1: Airflow logical_date(data_interval_start) 사용
    logical_date = context["data_interval_start"]
    start_ts = logical_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_ts   = start_ts + timedelta(days=1)

    rows = hook.get_records(
        """
        SELECT order_id, user_id, amount, event_time
        FROM raw_sales
        WHERE event_time >= %s AND event_time < %s
        """,
        parameters=(start_ts, end_ts),
    )

    if not rows:
        print("No data found.")
        return

    conn = hook.get_conn()
    cur  = conn.cursor()

    # FIX-2: DELETE-INSERT 멱등성 보장
    cur.execute(
        "DELETE FROM daily_sales WHERE DATE(event_time) = %s",
        (start_ts.date(),),
    )
    deleted = cur.rowcount
    print(f"Deleted {deleted} existing rows for {start_ts.date()}")

    cur.executemany(
        """
        INSERT INTO daily_sales (order_id, user_id, amount, event_time)
        VALUES (%s, %s, %s, %s)
        """,
        rows,
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(rows)} rows into daily_sales for {start_ts.date()}.")


with DAG(
    dag_id="sales_daily_load_fixed",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-3", "fixed"],
) as dag:

    load_task = PythonOperator(
        task_id="load_daily_sales",
        python_callable=load_daily_sales,
        provide_context=True,
    )
