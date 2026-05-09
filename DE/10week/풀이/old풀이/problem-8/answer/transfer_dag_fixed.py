"""
문제 5 - 풀이 (버그 수정)

[BUG 수정]
  원인: conn.commit() 누락
        psycopg2 기본값(autocommit=False)에서 commit 없이 conn.close() 호출 시
        미완료 트랜잭션이 자동 롤백됨
        cur.rowcount는 INSERT 시도 행 수를 반환하므로 로그에 N rows 찍혀도 실제론 0건

  수정: conn.commit() 추가 (cur.close() 이전)
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


def run_spark_job(**context):
    import subprocess
    result = subprocess.run(
        [
            "spark-submit",
            "--master", "spark://spark-master:7077",
            "/opt/spark/jobs/kafka_to_staging.py",
        ],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Spark job failed:\n{result.stderr}")
    print("Spark job completed successfully.")


def transfer_staging_to_final(**context):
    hook = PostgresHook(postgres_conn_id="postgres_default")
    conn = hook.get_conn()
    cur  = conn.cursor()

    logical_date   = context["data_interval_start"]
    partition_date = logical_date.date()

    cur.execute(
        """
        INSERT INTO daily_sales_final (order_id, user_id, amount, partition_date)
        SELECT order_id, user_id, amount, partition_date
        FROM staging_sales
        WHERE partition_date = %s
        """,
        (partition_date,),
    )

    row_count = cur.rowcount
    print(f"Transferred {row_count} rows to daily_sales_final for {partition_date}")

    # FIX: conn.commit() 추가
    conn.commit()
    cur.close()
    conn.close()


def verify_final_count(**context):
    hook = PostgresHook(postgres_conn_id="postgres_default")
    logical_date   = context["data_interval_start"]
    partition_date = logical_date.date()

    result = hook.get_first(
        "SELECT COUNT(*) FROM daily_sales_final WHERE partition_date = %s",
        parameters=(partition_date,),
    )
    count = result[0]
    print(f"daily_sales_final row count for {partition_date}: {count}")

    if count == 0:
        raise ValueError(f"daily_sales_final has 0 rows for {partition_date}!")


with DAG(
    dag_id="staging_to_final_transfer_fixed",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-5", "fixed"],
) as dag:

    spark_task = PythonOperator(
        task_id="run_spark_job",
        python_callable=run_spark_job,
    )

    transfer_task = PythonOperator(
        task_id="transfer_staging_to_final",
        python_callable=transfer_staging_to_final,
    )

    verify_task = PythonOperator(
        task_id="verify_final_count",
        python_callable=verify_final_count,
    )

    spark_task >> transfer_task >> verify_task
