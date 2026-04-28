"""
10주차 문제 6 - 참조 코드
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

    today = datetime.now().date()
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
