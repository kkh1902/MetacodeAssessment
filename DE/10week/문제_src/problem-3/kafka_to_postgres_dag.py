"""
문제 3 - Airflow DAG: SparkKubernetesOperator로 Kafka→PostgreSQL 배치 자동화

전제 조건:
  - 문제 2의 SparkApplication이 정상 실행되는 환경
  - Airflow가 k8s에 배포되어 있고 localhost:30097 접근 가능
  - Airflow Connection 설정:
      Admin > Connections > Add
      Conn Id: kubernetes_default
      Conn Type: Kubernetes Cluster Connection

TODO:
  1. application_file 경로를 실제 SparkApplication yaml 경로 또는 ConfigMap으로 수정
  2. namespace를 본인 환경에 맞게 수정
  3. schedule_interval 조정 (@daily, @hourly 등)
  4. DAG 실행 후 PostgreSQL에 데이터 추가 적재 확인
"""

from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator

default_args = {
    "owner":           "airflow",
    "depends_on_past": False,
    "start_date":      datetime(2025, 1, 1),
    "retries":         1,
}

with DAG(
    dag_id="kafka_to_postgres_spark_batch",
    default_args=default_args,
    # TODO: 원하는 실행 주기로 변경
    schedule_interval="@daily",
    catchup=False,
    tags=["problem-3", "kafka", "spark", "postgres"],
) as dag:

    spark_batch = SparkKubernetesOperator(
        task_id="run_kafka_to_postgres_batch",
        # TODO: 실제 SparkApplication yaml 경로로 수정
        application_file="TODO_PATH_TO_SPARK_APPLICATION_YAML",
        kubernetes_conn_id="kubernetes_default",
        namespace="default",
        do_xcom_push=False,
    )
