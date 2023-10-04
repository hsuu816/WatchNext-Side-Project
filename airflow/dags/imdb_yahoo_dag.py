from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from modeules.imdb_to_yahoo import *

default_args = {
    'owner': 'Bonnie',
    'depends_on_past': False,
    'start_date': '2023-09-23 08:30:00',
    'email': ['hsuu816@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG('imdb_yahoo_match', default_args=default_args, schedule_interval='@once',)

t1 = EmptyOperator(
    task_id = 'start',
    dag = dag)

t2 = PythonOperator(
    task_id = 'fetch_2021_imdb_data',
    python_callable = imdb_yahoo_match,
    op_args = ['2021'],
    dag = dag)

t3 = PythonOperator(
    task_id = 'fetch_2020_imdb_data',
    python_callable = imdb_yahoo_match,
    op_args = ['2020'],
    dag = dag)

t4 = PythonOperator(
    task_id = 'fetch_2019_imdb_data',
    python_callable = imdb_yahoo_match,
    op_args = ['2019'],
    dag = dag)

t5 = EmptyOperator(
    task_id = 'end',
    dag = dag)

t1 >> t2 >> t3 >> t4 >> t5
