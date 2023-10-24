from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from modules.ptt_crawler import *
from modules.drama_comment import *

default_args = {
    'owner': 'Bonnie',
    'depends_on_past': False,
    'start_date': '2023-09-27 4:00:00',
    'email': ['hsuu816@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'catchup': False
}

dag = DAG('crawler_data_into_mongodb', default_args=default_args, schedule_interval='@once')

t1 = EmptyOperator(
    task_id = 'start',
    dag = dag)

t2 = PythonOperator(
    task_id = 'fetch_all_ptt_china_drama_data',
    python_callable = fetch_all_ptt_comments,
    op_args = ['https://www.ptt.cc/bbs/China-Drama/index1800.html'],
    dag = dag)

t3 = PythonOperator(
    task_id = 'fetch_all_ptt_korean_drama_data',
    python_callable = fetch_all_ptt_comments,
    op_args = ['https://www.ptt.cc/bbs/KoreaDrama/index2700.html'],
    dag = dag)

t4 = PythonOperator(
    task_id = 'fetch_all_ptt_japan_drama_data',
    python_callable = fetch_all_ptt_comments,
    op_args = ['https://www.ptt.cc/bbs/Japandrama/index2800.html'],
    dag = dag)

t5 = PythonOperator(
    task_id = 'fetch_all_ptt_taiwan_drama_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/TaiwanDrama/index2350.html'],
    dag = dag)

t6 = PythonOperator(
    task_id = 'fetch_ptt_ea_series_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/EAseries/index2500.html'],
    dag = dag)

t7 = PythonOperator(
    task_id = 'comment_to_drama',
    python_callable = comment_to_drama,
    dag = dag)

t1 >> [t2, t3, t4, t5, t6] >> t7
