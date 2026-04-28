"""
문제 8 - 참조 코드 (버그 포함)

파이프라인 구조:
  [Kafka] → [Spark: kafka_to_staging] → [staging_sales] → [이 DAG] → [daily_sales_final]

증상:
  - Spark job: SUCCESS (staging_sales에 데이터 적재됨)
  - Airflow DAG: SUCCESS (에러 없음)
  - daily_sales_final: 0 rows  ← 이상
  - 로그: "Transferred N rows" 출력됨 (정상처럼 보임)

BUG: transfer_staging_to_final() 함수에서 conn.commit() 누락
     → psycopg2 기본값(autocommit=False)으로 트랜잭션이 열린 상태에서
       conn.close() 호출 시 자동 롤백
     → cur.rowcount는 INSERT 행 수를 반환하므로 로그엔 N rows 찍히지만 실제 DB엔 0건
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
    """Spark job 실행 (실제 환경에서는 SparkSubmitOperator 사용)"""
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

    # staging → final 이관
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

    # BUG: conn.commit() 누락
    # psycopg2는 autocommit=False가 기본값
    # → INSERT는 트랜잭션 내에서 실행되지만 commit 없이 close() 호출 시 롤백
    # → cur.rowcount는 정상적으로 N을 반환하므로 로그만 봐서는 정상처럼 보임
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
    # 검증 없이 그냥 출력만 → 0이어도 SUCCESS 반환


with DAG(
    dag_id="staging_to_final_transfer",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-8"],
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
