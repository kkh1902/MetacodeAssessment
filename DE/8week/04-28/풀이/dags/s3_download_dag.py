from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
import boto3
import os


def download_from_s3(**kwargs):
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


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='s3_download_dag',
    default_args=default_args,
    description='Download CSV from S3',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['s3'],
) as dag:

    download_task = PythonOperator(
        task_id='download_csv_from_s3',
        python_callable=download_from_s3,
    )
