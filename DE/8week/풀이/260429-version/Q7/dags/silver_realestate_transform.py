"""
Q7 — Silver Transform DAG
ExternalTaskSensor 로 Q6(Bronze) 완료 대기 후 silver_spark.py 실행.
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor

with DAG(
    dag_id="silver_realestate_transform",
    description="Bronze XML → PySpark 정제 → Silver parquet (S3)",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=True,
    tags=["q7", "silver", "realestate"],
) as dag:

    wait_bronze = ExternalTaskSensor(
        task_id="wait_bronze",
        external_dag_id="bronze_realestate_collect",
        external_task_id=None,            # DAG 전체 완료 대기
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60 * 6,
        allowed_states=["success"],
    )

    run_silver = BashOperator(
        task_id="run_silver_spark",
        bash_command=(
            "spark-submit "
            "--master spark://spark-master:7077 "
            "--packages com.databricks:spark-xml_2.12:0.18.0 "
            "/opt/airflow/scripts/q7/silver_spark.py "
            "{{ logical_date.strftime('%Y%m') }}"
        ),
    )

    wait_bronze >> run_silver
