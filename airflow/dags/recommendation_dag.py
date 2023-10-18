from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from modeules.item_based_rec import *

default_args = {
    'owner': 'Bonnie',
    'depends_on_past': False,
    'start_date': '2023-10-15 01:00:00',
    'email': ['hsuu816@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG('item_based_rec', default_args=default_args, schedule_interval='@monthly',)

t1 = EmptyOperator(
    task_id = 'start',
    dag = dag)

t2 = PythonOperator(
    task_id = 'item_based_rec',
    python_callable = item_based_rec,
    dag = dag)

t3 = EmptyOperator(
    task_id = 'end',
    dag = dag)

t1 >> t2 >> t3
