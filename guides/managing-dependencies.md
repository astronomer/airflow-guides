---
title: "Managing Dependencies in Apache Airflow"
description: "An overview of dependencies and triggers in Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "managing-dependencies"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dependencies.png"
tags: ["Best Practices", "Dependencies", "Basics"]
---

## Overview

Dependencies are one of Airflow's most powerful and popular features - they define the [relationships between tasks](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html#relationships).  Dependencies allow you to define flexible pipelines in Airflow that follow data engineering best practices by keeping your tasks atomic. 

In this guide we'll cover the many ways you can implement dependencies in Airflow, including:

- Basic task dependencies
- Dynamic dependencies
- Dependencies with Task Groups
- Dependencies with the TaskFlow API
- Trigger rules

For a detailed presentation of all these topics, check out our webinar on [managing dependencies in Airflow](https://www.astronomer.io/events/webinars/manage-dependencies-between-airflow-deployments-dags-tasks/). 

Note that this guide focuses on within-DAG dependencies (i.e. dependencies between tasks in the same DAG). If you are looking to implement dependencies _between DAGs_, check out our guide on [cross-DAG dependencies](https://www.astronomer.io/guides/cross-dag-dependencies).

## Basic Dependencies

Basic dependencies between Airflow tasks can be set in two ways:

- Using bitshift operators `<<` and `>>`
- Using the `set_upstream` and `set_downstream` methods

For example, if we have a DAG with four sequential tasks, the dependencies can be set in four ways:

- Using `set_downstream()`

    ```python
    t0.set_downstream(t1)
    t1.set_downstream(t2)
    t2.set_downstream(t3)
    ```

- Using `set_upstream()`

    ```python
    t3.set_upstream(t2)
    t2.set_upstream(t1)
    t1.set_upstream(t0)
    ```

- Using `>>`

    ```python
    t0 >> t1 >> t2 >> t3
    ```

- Using `<<`

    ```python
    t3 << t2 << t1 << t0
    ```

All of these methods are equivalent, and result in the following DAG. 

![Basic Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/basic_dependencies.png)

Which method you choose is a matter of personal preference. Best practice is to use one method consistently (i.e. don't mix bitshift operators and `set_upstream`/`set_downstream`).

You can also use lists or tuples to set parallel dependencies. For example: 

- ```python
    t0 >> t1 >> (t2, t3)
    ```

- ```python
    t0 >> t1 >> [t2, t3]
    ```

Both of these are equivalent, and set `t2` and `t3` downstream of `t1`. 

![List Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/list_dependencies.png)

Note that you cannot set dependencies between two lists (e.g. `[t0, t1] >> [t2, t3]` will throw an error). If you need to set parallel cross-dependencies in this manner, you can use Airflow's [`chain` function](https://github.com/apache/airflow/blob/main/airflow/models/baseoperator.py#L1650). To use the `chain` function, you can do something like this:

```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.models.baseoperator import chain

with DAG('dependencies',
         ) as dag:

    t0 = DummyOperator(task_id='t0')
    t1 = DummyOperator(task_id='t1')
    t2 = DummyOperator(task_id='t2')
    t3 = DummyOperator(task_id='t3')
    t4 = DummyOperator(task_id='t4')
    t5 = DummyOperator(task_id='t5')
    t6 = DummyOperator(task_id='t6')

    chain(t0, t1, [t2, t3], [t4, t5], t6)
```

Which results in the following DAG:

![Chain Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/chain.png)

Note that with the `chain` function any lists or tuples included must be the same length.

## Dynamic Dependencies

If you generate tasks dynamically in your DAG, you should also set dependencies dynamically to ensure they reflect any changes in the tasks. This is easy to accomplish: simply define the dependencies within the context of the code used to dynamically create the tasks.

For example, below we generate a set of parallel dynamic tasks by looping through a list of endpoints. We define the dependencies within the loop, which means every `generate_file` task will be downstream of `start` and upstream of `send_email`.


```python
with DAG('covid_data_to_s3') as dag:

    t0 = DummyOperator(task_id='start')

    send_email = EmailOperator(
        task_id='send_email',
        to=email_to,
        subject='Covid to S3 DAG',
        html_content='<p>The Covid to S3 DAG completed successfully. Files can now be found on S3. <p>'
    )
    
    for endpoint in endpoints:
        generate_files = PythonOperator(
            task_id='generate_file_{0}'.format(endpoint),
            python_callable=upload_to_s3,
            op_kwargs={'endpoint': endpoint, 'date': date}
        )
        
        t0 >> generate_files >> send_email
```

The resulting DAG looks like this:

![Dynamic Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/dynamic_tasks.png)


## Dependencies with Task Groups

[Task groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#taskgroups) are a UI grouping concept available in Airflow 2+ that can visually group tasks in the Airflow UI. For more on task groups in general, including how to create them and when to use them, check out our [task groups guide](https://www.astronomer.io/guides/task-groups).

When working with task groups, it is important to note that dependencies can be set both inside and outside the group. For example, in the DAG code below we have a start task, a task group with two dependent tasks, and an end task that need to happen sequentially. The dependencies between the two tasks in the task group are set within the task group's context (`t1 >> t2`). The dependencies between the task group and the start/end tasks are set within the DAG's context (`t0 >> tg1 >> t3`).

```python
t0 = DummyOperator(task_id='start')

# Start Task Group definition
with TaskGroup(group_id='group1') as tg1:
    t1 = DummyOperator(task_id='task1')
    t2 = DummyOperator(task_id='task2')

    t1 >> t2
# End Task Group definition
    
t3 = DummyOperator(task_id='end')

# Set Task Group's (tg1) dependencies
t0 >> tg1 >> t3
```

This code results in a DAG that looks like this:

![Task Group Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/task_group.png)

For more examples of setting dependencies within different types of task groups, check out the guide linked above.

## Dependencies with the TaskFlow API

The [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/concepts/taskflow.html), available in Airflow 2+, provides an easy way to turn Python functions into Airflow tasks using the `@task` decorator. 

If your DAG has only Python functions that are all defined with the decorator, setting dependencies is as easy as invoking the Python functions. For example, in the DAG below we have two dependent tasks, `get_testing_increases` and `analyze_testing_increases`. To set the dependencies, we invoke the functions: `analyze_testing_increases(get_testing_increase(state))`. 

```python
from airflow.decorators import dag, task
from datetime import datetime

import requests
import json

url = 'https://covidtracking.com/api/v1/states/'
state = 'wa'

default_args = {
    'start_date': datetime(2021, 1, 1)
}

@dag('xcom_taskflow_dag', schedule_interval='@daily', default_args=default_args, catchup=False)
def taskflow():

    @task
    def get_testing_increase(state):
        """
        Gets totalTestResultsIncrease field from Covid API for given state and returns value
        """
        res = requests.get(url+'{0}/current.json'.format(state))
        return{'testing_increase': json.loads(res.text)['totalTestResultsIncrease']}

    @task
    def analyze_testing_increases(testing_increase: int):
        """
        Evaluates testing increase results
        """
        print('Testing increases for {0}:'.format(state), testing_increase)
        #run some analysis here

    # Invoke functions to create tasks and define dependencies
    analyze_testing_increases(get_testing_increase(state))

dag = taskflow()
```

The resulting DAG looks like this:

![TaskFlow Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/taskflow.png)

If your DAG has a mix of Python function tasks defined with decorators and tasks defined with traditional operators, you can set the dependencies by assigning the decorated task invocation to a variable and then defining the dependencies as you would normally. For example, in the DAG below the `upload_data_to_s3` task is defined by the `@task` decorator and invoked with `upload_data = upload_data_to_s3(s3_bucket, test_s3_key)`. That `upload_data` variable is then used in the last line to define dependencies.

```python
with DAG('sagemaker_model',
         ) as dag:

    @task
    def upload_data_to_s3(s3_bucket, test_s3_key):
        """
        Uploads validation data to S3 from /include/data 
        """
        s3_hook = S3Hook(aws_conn_id='aws-sagemaker')

        # Take string, upload to S3 using predefined method
        s3_hook.load_file(filename='include/data/test.csv', 
                        key=test_s3_key, 
                        bucket_name=s3_bucket, 
                        replace=True)

    upload_data = upload_data_to_s3(s3_bucket, test_s3_key)

    predict = SageMakerTransformOperator(
        task_id='predict',
        config=transform_config,
        aws_conn_id='aws-sagemaker'
    )

    results_to_redshift = S3ToRedshiftOperator(
            task_id='save_results',
            aws_conn_id='aws-sagemaker',
            s3_bucket=s3_bucket,
            s3_key=output_s3_key,
            schema="PUBLIC",
            table="results",
            copy_options=['csv'],
        )

    upload_data >> predict >> results_to_redshift
```

## Trigger Rules

In Airflow, when you set dependencies between tasks the default behavior is for a task to be run only when all upstream tasks have succeeded. However, you have many other options for when a task gets run that you can control using [trigger rules](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#concepts-trigger-rules).

The options available are:

- **all_success:** (default) all upstream tasks have succeeded
- **all_failed:** all upstream tasks are in a failed or upstream\_failed state
- **all_done:** all upstream tasks are done with their execution
- **one_failed:** runs as soon as at least one upstream task has failed, it does not wait for all upstream tasks to be completed
- **one_success:** runs as soon as at least one upstream task has succeeded, it does not wait for all upstream tasks to be completed
- **dummy:** dependencies are just for show, trigger at will

### Branching and Trigger Rules

One common scenario where you might need to implement trigger rules is if your DAG contains conditional logic like branching. In these cases `one_success` might be a more appropriate rule for tasks directly downstream of branches than the default `all_success`.

For example, in the following DAG we have a simple branch with a downstream task that needs to run if either of the branches are followed. With the `all_success` rule, the `end` task would never run because all but one of the `branch` tasks will always be skipped and therefore will not have a state of 'success'. If we change the trigger rule to `one_success`, then the `end` task can run so long as one of the branches successfully completes.

```python
import random
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime
from airflow.utils.trigger_rule import TriggerRule

def return_branch(**kwargs):
    branches = ['branch_0', 'branch_1', 'branch_2']
    return random.choice(branches)

with DAG(dag_id='branch',
         start_date=datetime(2021, 1, 1),
         max_active_runs=1,
         schedule_interval=None,
         catchup=False
         ) as dag:

    #DummyOperators
    start = DummyOperator(task_id='start')
    end = DummyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ONE_SUCCESS
    )

    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=return_branch,
        provide_context=True
    )

    start >> branching

    for i in range(0, 3):
        d = DummyOperator(task_id='branch_{0}'.format(i))
        branching >> d >> end
```

![Branch Dependencies](https://assets2.astronomer.io/main/guides/managing-dependencies/branch.png)
