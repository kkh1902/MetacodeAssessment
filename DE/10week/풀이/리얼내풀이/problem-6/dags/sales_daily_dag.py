"""
10주차 문제 6 - 풀이 코드 (버그 수정)
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

    # FIX-1 (BUG-1): datetime.now() 대신 data_interval_end 사용
    # → data_interval_end = 오늘 자정 (daily schedule 기준 당일 날짜)
    execution_date = context["data_interval_end"]
    today = execution_date.date()
    start_ts = datetime.combine(today, datetime.min.time())
    end_ts   = datetime.combine(today, datetime.max.time())

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

    # FIX-2 (BUG-2): DELETE-INSERT 패턴으로 멱등성 보장
    # → 재실행 시 기존 데이터 삭제 후 재적재하여 중복 방지
    cur.execute(
        "DELETE FROM daily_sales WHERE event_time >= %s AND event_time < %s",
        (start_ts, end_ts),
    )
    deleted = cur.rowcount
    print(f"Deleted {deleted} existing rows for {today}")

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
    print(f"Inserted {len(rows)} rows into daily_sales for {today}.")


with DAG(
    dag_id="sales_daily_load",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-6"],
) as dag:

    load_task = PythonOperator(
        task_id="load_daily_sales",
        python_callable=load_daily_sales,
        provide_context=True,
    )
