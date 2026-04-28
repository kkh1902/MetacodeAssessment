from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from datetime import datetime, timedelta
import psycopg2


def query_postgres(**kwargs):
    conn_info = BaseHook.get_connection('postgres_default')
    target_table = Variable.get('target_table', default_var='sample_table')

    connection = psycopg2.connect(
        host=conn_info.host,
        port=conn_info.port,
        dbname=conn_info.schema,
        user=conn_info.login,
        password=conn_info.password,
    )

    cursor = connection.cursor()

    # 테이블이 없으면 생성
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {target_table} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            value INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # 샘플 데이터 삽입
    cursor.execute(f"""
        INSERT INTO {target_table} (name, value)
        VALUES ('test_entry', 42)
        ON CONFLICT DO NOTHING;
    """)
    connection.commit()

    # SELECT 쿼리 수행
    cursor.execute(f"SELECT * FROM {target_table} LIMIT 10;")
    rows = cursor.fetchall()
    print(f"Query result from {target_table}:")
    for row in rows:
        print(row)

    cursor.close()
    connection.close()


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='db_query_dag',
    default_args=default_args,
    description='Query PostgreSQL using Connection and Variable',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['postgres'],
) as dag:

    query_task = PythonOperator(
        task_id='query_postgres_table',
        python_callable=query_postgres,
    )
