"""
10주차 문제 8 - 풀이 (Databricks 클러스터 튜닝)

[수정 내용]
1. num_workers: 2 → 4
   이유: 200만 건 데이터 + skew 처리에 worker 2개는 부족
        worker 늘려 parallelism 확보

2. spark.sql.shuffle.partitions: 200 → 400
   이유: worker 증가에 맞춰 shuffle partition도 비례 증가

3. spark.sql.adaptive.enabled: true
   이유: AQE로 런타임 skew 자동 감지 및 파티션 재조정

4. spark.sql.adaptive.skewJoin.enabled: true
   이유: skew join 자동 분할 처리

5. spark.executor.memory: 2g → 4g
   이유: Databricks 클라우드 환경은 더 큰 메모리 활용 가능
        넉넉하게 할당해 GC overhead 감소

[예상 성능 개선]
  튜닝 전: ~12분 (worker 2, OOM 위험)
  튜닝 후: ~4분  (worker 4, AQE 적용)
  → 약 66% 개선 (실제 수치는 본인 환경 기준으로 작성)
"""
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DATABRICKS_CONN_ID  = "databricks_default"
DATABRICKS_JOB_PATH = "/Shared/sales_agg_job"

CLUSTER_CONFIG_TUNED = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id":  "Standard_DS3_v2",
    "num_workers":   4,                            # FIX-1
    "spark_conf": {
        "spark.executor.memory":                   "4g",   # FIX-5
        "spark.driver.memory":                     "4g",
        "spark.sql.shuffle.partitions":            "400",  # FIX-2
        "spark.sql.adaptive.enabled":              "true", # FIX-3
        "spark.sql.adaptive.skewJoin.enabled":     "true", # FIX-4
    },
}

with DAG(
    dag_id="sales_aggregation_databricks_fixed",
    default_args=default_args,
    start_date=datetime(2025, 4, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-8", "fixed"],
) as dag:

    run_on_databricks = DatabricksSubmitRunOperator(
        task_id="run_sales_agg_on_databricks",
        databricks_conn_id=DATABRICKS_CONN_ID,
        new_cluster=CLUSTER_CONFIG_TUNED,
        notebook_task={
            "notebook_path": DATABRICKS_JOB_PATH,
            "base_parameters": {
                "execution_date": "{{ ds }}",
            },
        },
    )
