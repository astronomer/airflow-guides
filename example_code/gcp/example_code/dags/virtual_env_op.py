from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import PythonVirtualenvOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup':False
}

dag = DAG('example_dag_python',
          schedule_interval=timedelta(minutes=5),
          default_args=default_args)


def test_func(**kwargs):
    print("HELLO")


def test_func_two():
    import sys
    print(sys.version)
    print("hi")


t1 = PythonOperator(
    task_id='test_task',
    python_callable=test_func,
    provide_context=True,
    dag=dag)

t2 = PythonVirtualenvOperator(
    task_id='test_two',
    python_version='2',
    python_callable=test_func_two,
    dag=dag
)

t1 >> t2
