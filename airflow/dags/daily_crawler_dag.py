from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from modeules.yahoo_crawler import *
from modeules.ptt_crawler_daily import *
from modeules.drama_comment import *

default_args = {
    'owner': 'Bonnie',
    'depends_on_past': False,
    'start_date': '2023-09-22 08:30:00',
    'schedule_interval': '@hourly',
    'email': ['hsuu816@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG('daily_crawler_data_into_mongodb', default_args=default_args)

t1 = EmptyOperator(
    task_id = 'start',
    dag = dag)

t2 = PythonOperator(
    task_id = 'fetch_yahoo_drama_data',
    python_callable = fetch_drama_data,
    op_args = [3],
    dag = dag)

t3 = PythonOperator(
    task_id = 'fetch_ptt_china_drama_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/China-Drama/index.html', 3],
    dag = dag)

t4 = PythonOperator(
    task_id = 'fetch_ptt_korean_drama_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc//bbs/KoreaDrama/index.html', 3],
    dag = dag)

t5 = PythonOperator(
    task_id = 'fetch_ptt_japan_drama_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/Japandrama/index.html', 3],
    dag = dag)

t6 = PythonOperator(
    task_id = 'fetch_ptt_taiwan_drama_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/TaiwanDrama/index.html', 3],
    dag = dag)

t7 = PythonOperator(
    task_id = 'fetch_ptt_ea_series_data',
    python_callable = get_all_articles,
    op_args = ['https://www.ptt.cc/bbs/EAseries/index.html', 3],
    dag = dag)

t8 = PythonOperator(
    task_id = 'comment_to_drama',
    python_callable = comment_to_drama,
    dag = dag)

t9 = EmptyOperator(
    task_id = 'end',
    dag = dag)

t1 >> t2 >> [t3, t4, t5, t6, t7] >> t8 >> t9
