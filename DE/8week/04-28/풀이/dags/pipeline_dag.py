from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
import boto3
import os
import psycopg2


def download_csv_from_s3(**kwargs):
    conn = BaseHook.get_connection('aws_default')
    extras = conn.extra_dejson

    s3_client = boto3.client(
        's3',
        aws_access_key_id=extras.get('aws_access_key_id', ''),
        aws_secret_access_key=extras.get('aws_secret_access_key', ''),
        region_name=extras.get('region_name', 'ap-northeast-2'),
    )

    bucket_name = 'subway-assignment-meta'
    s3_key = 'data.csv'
    local_path = '/opt/airflow/data/data.csv'

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3_client.download_file(bucket_name, s3_key, local_path)
    print(f"Downloaded s3://{bucket_name}/{s3_key} -> {local_path}")


def check_postgres_table(**kwargs):
    conn_info = BaseHook.get_connection('postgres_default')

    connection = psycopg2.connect(
        host=conn_info.host,
        port=conn_info.port,
        dbname=conn_info.schema,
        user=conn_info.login,
        password=conn_info.password,
    )
    cursor = connection.cursor()

    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    tables = cursor.fetchall()
    print("Tables in database:")
    for t in tables:
        print(f"  - {t[0]}")

    target_table = 'sample_table'
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        );
    """, (target_table,))
    exists = cursor.fetchone()[0]
    print(f"\nTable '{target_table}' exists: {exists}")

    cursor.close()
    connection.close()


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='pipeline_dag',
    default_args=default_args,
    description='End-to-end data pipeline',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['pipeline'],
) as dag:

    # Step 1: Hello message
    hello_task = BashOperator(
        task_id='hello_message',
        bash_command='echo "Pipeline started - Hello Airflow! Pipeline will complete successfully."',
    )

    # Step 2: Download CSV from S3
    download_task = PythonOperator(
        task_id='download_csv_from_s3',
        python_callable=download_csv_from_s3,
    )

    # Step 3: Check PostgreSQL table
    check_db_task = PythonOperator(
        task_id='check_postgres_table',
        python_callable=check_postgres_table,
    )

    # Step 4: Success message
    success_task = BashOperator(
        task_id='pipeline_success',
        bash_command='echo "Pipeline completed successfully!"',
    )

    hello_task >> download_task >> check_db_task >> success_task
