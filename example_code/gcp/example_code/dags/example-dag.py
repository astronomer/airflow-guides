from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2018, 1, 1),
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retry_delay': timedelta(minutes=5),
}

dag = DAG('example_dag',
			schedule_interval=timedelta(minutes=5),
			default_args=default_args)

t1 = BashOperator(
	task_id='print_date1',
	bash_command='sleep 2m',
	dag=dag)

t2 = BashOperator(
	task_id='print_date2',
	bash_command='sleep 2m',
	dag=dag)

t3 = BashOperator(
	task_id='print_date3',
	bash_command='sleep 2m',
	dag=dag)

t4 = BashOperator(
	task_id='print_date4',
	bash_command='sleep 2m',
	dag=dag)

t5 = BashOperator(
	task_id='print_date5',
	bash_command='sleep 2m',
	dag=dag)

t6 = BashOperator(
	task_id='print_date6',
	bash_command='sleep 2m',
	dag=dag)

t7 = BashOperator(
	task_id='print_date7',
	bash_command='sleep 2m',
	dag=dag)

t8 = BashOperator(
	task_id='print_date8',
	bash_command='sleep 2m',
	dag=dag)

t2.set_upstream(t1)
t3.set_upstream(t2)
t4.set_upstream(t3)
t5.set_upstream(t3)
t6.set_upstream(t3)
t7.set_upstream(t3)
t8.set_upstream(t3)

t9 = BashOperator(
	task_id='print_date9',
	bash_command='sleep 2m',
	dag=dag)

t10 = BashOperator(
	task_id='print_date10',
	bash_command='sleep 2m',
	dag=dag)

t11 = BashOperator(
	task_id='print_date11',
	bash_command='sleep 2m',
	dag=dag)

t12 = BashOperator(
	task_id='print_date12',
	bash_command='sleep 2m',
	dag=dag)

t9.set_upstream(t8)
t10.set_upstream(t8)
t11.set_upstream(t8)
t12.set_upstream(t8)