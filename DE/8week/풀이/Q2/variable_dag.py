"""
Q2 — PythonOperator + Variable 활용
사전: Airflow Admin > Variables 에 'greeting' 등록
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable


def print_greeting():
    greeting = Variable.get("greeting", default_var="hello!")
    print(f"[Q2] greeting = {greeting}")


with DAG(
    dag_id="variable_dag",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["q2"],
) as dag:
    PythonOperator(task_id="print_greeting", python_callable=print_greeting)
