---
title: "Importing Custom Hooks & Operators"
description: "How to correctly import custom hooks and operators."
date: 2019-05-29T00:00:00.000Z
slug: "airflow-importing-custom-hooks-operators"
heroImagePath: null
tags: ["Hooks", "Operators", "Plugins", "Basics"]
---

## Overview

One of the great benefits of Airflow is its vast network of provider packages that provide hooks, operators, and sensors for many common use cases. But another great benefit of Airflow is that because everything is defined in Python code, it is highly customizable. If a hook, operator, or sensor you need doesn't exist in the open source, you can easily define your own. 

In this guide, we'll cover everything you need to know to make your custom code available to your DAGs. We'll touch briefly on defining custom operators, but will mostly focus on how to add them to your Airflow project. Throughout, we'll focus on custom operators to keep things simple, but the same concepts apply to custom hooks or sensors.

## Defining a Custom Operator

At a high level, creating a custom operator is straight forward. It should inherit from the `BaseOperator`, and define `Constructor` and `Execute` classes. This will look something like the code below:

```python
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

If your custom operator is modifying functionality of an existing operator, your class may inherit from the operator you are building off of instead of the `BaseOperator`. For more detailed instructions on defining custom operators, check out the [Apache Airflow How-to Guide](https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html).

## Importing Custom Operators

Once you have your custom operator defined, you need to make it available to your DAGs. Some legacy Airflow documentation or forums may reference registering your custom operator as an Airflow plugin, but this is not necessary. In general, the file containing your custom operator needs to be in a directory that is present in your `PYTHONPATH` for you to import it into your DAG file.

Airflow by default will add the `dags/` and `plugins/` directories in a project to the `PYTHONPATH`, so those are the most natural choices for storing custom operator files (check out the [Airflow Module Management](https://airflow.apache.org/docs/apache-airflow/stable/modules_management.html) docs for more info). Your project structure may vary depending on your team and your use case. At Astronomer, we use the structure shown below, and recommend putting custom operator files in the `plugins/` directory with sub-folders for readability.

```bash
.
├── dags/                    
│   ├── example-dag.py
├── Dockerfile                  
├── include/                 
│   └── sql/
│       └── transforms.sql
├── packages.txt     
├── plugins/             
│   └── hooks/
│       └── my_operator.py
│   └── sensors/
│       └── my_sensor.py
└── requirements.txt    
```

For more details on why we recommend this project structure, check out our [Managing Airflow Code](https://www.astronomer.io/guides/managing-airflow-code) guide.

> Note: If you use an IDE and don't want to see import errors, add the `plugins` directory as a source root.

Once you have your custom operators added to the project like this, you can easily import them in your DAG like you would any other Python package:

```python
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

And that's it! There is no need to define an AirflowPlugin class in any of the files.
