---
title: "Importing Custom Hooks & Operators"
description: "How to correctly import custom hooks and operators"
date: 2019-05-29T00:00:00.000Z
slug: "airflow-importing-custom-hooks-operators
heroImagePath: null
tags: ["Airflow"]
---

Custom hooks and operators are a powerful way to extend Airflow to meet your needs. There is however some confusion on the best way to implement them. According to the Airflow documentation, they can be added using Airflow’s `Plugins` mechanism. This however, overcomplicates the issue and leads to confusion for many people. Airflow is even considering deprecating using the `Plugins` mechanism for hooks and operators going forward.

Note: The `Plugins` mechanism still must be used for plugins that make changes to the webserver UI.

Let’s assume you have an `Airflow Home` directory with the following structure.

```
.
├── airflow.cfg
├── airflow.db
├── dags
│   └── my_dag.py
└── plugins
    ├── hooks
    │   └── my_hook.py
    ├── operators
    │   └── my_operator.py
    └── sensors
        └── my_sensor.py
```

We will assume that `my_dag` wants to use `my_operator` and `my_sensor`. Also, `my_operator` wants to use `my_hook`. When Airflow is running, it will add `dags/`, `plugins/`, `and config/` to PATH. So any python files in those folders should be accessible to import. So from our `my_dag.py` file, we can simply use

```
from operators.my_operator import MyOperator
from sensors.my_sensor import MySensor
```
And that's it! There is no need to define an AirflowPlugin class in any of the files.

Note: If you use an IDE and don't want to get import errors, add the `plugins` directory as a source root.

Below is the code for each the files so you can see how all the imports work

##### my_dag.py
```
from airflow import DAG
from datetime import datetime, timedelta
from operators.my_operator import MyOperator
from sensors.my_sensor import MySensor

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2018, 1, 1),
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retry_delay': timedelta(minutes=5),
}


with DAG('example_dag',
		 max_active_runs=3,
		 schedule_interval='@once',
		 default_args=default_args) as dag:

	sens = MySensor(
		task_id='taskA'
	)

	op = MyOperator(
		task_id='taskB',
		my_field='some text'
	)

	sens >> op
```
##### my_sensor.py
```
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class MySensor(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
                 *args,
                 **kwargs):
        super(MySensor, self).__init__(*args, **kwargs)

    def poke(self, context):
        return True
```
##### my_operator.py
```
from airflow.operators.bash_operator import BaseOperator
from airflow.utils.decorators import apply_defaults
from hooks.my_hook import MyHook


class MyOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 my_field,
                 *args,
                 **kwargs):
        super(MyOperator, self).__init__(*args, **kwargs)
        self.my_field = my_field

    def execute(self, context):
        hook = MyHook('my_conn')
        hook.my_method()
```
##### my_hook.py
```
from airflow.hooks.base_hook import BaseHook


class MyHook(BaseHook):

    def my_method(self):
        print("Hello World")s
```
