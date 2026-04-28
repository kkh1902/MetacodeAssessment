"""
10주차 문제 7 - 풀이 (DAG 튜닝)

[수정 내용]
1. executor/driver memory 명시 (1g → 2g)
   이유: 기본 1g로는 skew 파티션(user_id=999, 전체 80%) 처리 불가

2. spark.sql.shuffle.partitions 증가 (200 → 400)
   이유: 파티션 수를 늘려 skew 파티션 크기를 분산

3. spark.sql.adaptive.enabled = true
   이유: AQE가 런타임에 skew join/partition을 자동 감지 및 재분배

4. spark.sql.adaptive.skewJoin.enabled = true
   이유: skew join 자동 처리 (skew 파티션을 여러 task로 분할)
"""
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sales_aggregation_fixed",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-7", "fixed"],
) as dag:

    aggregate = SparkSubmitOperator(
        task_id="aggregate_sales",
        application="/opt/spark/jobs/sales_agg_job.py",
        conn_id="spark_default",
        conf={
            "spark.executor.memory":                   "2g",   # FIX-1
            "spark.driver.memory":                     "2g",   # FIX-1
            "spark.executor.cores":                    "1",
            "spark.sql.shuffle.partitions":            "400",  # FIX-2
            "spark.sql.adaptive.enabled":              "true", # FIX-3
            "spark.sql.adaptive.skewJoin.enabled":     "true", # FIX-4
        },
        verbose=True,
    )
