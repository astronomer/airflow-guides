---
title: "Airflow Pools"
description: "Using pools to control task parallelism in Airflow."
date: 2021-09-01T00:00:00.000Z
slug: "airflow-pools"
tags: ["Parallelism", "Tasks"]
---

## Overview

One of the great benefits to Apache Airflow is that it is built to scale. With the right supporting infrastructure, you can run many tasks in parallel seamlessly. But sometimes that horizontal scalability also necessitates some guardrails. For example, you might have many tasks that interact with the same source system, like an API or database, that you don't want to be overwhelmed with requests. Fortunately, Airflow's [pools](https://airflow.apache.org/docs/apache-airflow/stable/concepts/pools.html) are designed for exactly this use case.

Pools allow you to limit parallelism for an arbitrary set of tasks, giving you fine grained control over when your tasks are run. They are often used in cases where you want to limit the number of parallel tasks that *do a certain thing.* For example, tasks that make requests to the same API or database, or tasks that will run on a GPU node of a Kubernetes cluster.

In this guide, we will cover the basic concepts of Airflow pools including how to create them, how to assign them, and what you can and can't do with them. We will also walk through some sample DAGs that use pools to fulfill a simple use case. 

## Creating a Pool

There are three ways you can create and manage a pool in Airflow.

- **Create a pool through the Airflow UI:** Go to `Admin` → `Pools` and add a new record. You can define a name, the number of slots, and a description.

    ![Pools UI](https://assets2.astronomer.io/main/guides/airflow-pools/pools_ui.png)

- **Create a pool using the Airflow CLI with the `airflow pools` command:** The `set` subcommand can be used to create a new pool. Check out the [Airflow CLI documentation](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html#pools) for the full list of pool commands. With the CLI, you can also import pools from a JSON file with the `import` subcommand. This can be useful if you have a large number of pools to define and doing so programmatically would be more efficient.
- **Create a pool using the Airflow REST API:** Note that this is only available if you are using Airflow 2.0+. To create a pool, simply submit a POST request with the name and number of slots as the payload. For more information on working with pools from the API, check out the [API documentation](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_pool).

Note that you can also update the number of slots in the `default_pool` using any of the above methods (more on this below).

## Assigning Tasks to a Pool

By default, all tasks in Airflow get assigned to the `default_pool` which has 128 slots. You can modify this value, but you can't remove the default pool. Tasks can be assigned to any other pool by updating the `pool` parameter. This parameter is part of the `BaseOperator`, so it can be used with any operator.

```python
task_a = PythonOperator(
        task_id='task_a',
        python_callable=sleep_function,
        pool='single_task_pool'
    )
```

When tasks are assigned to a pool, they will be scheduled as normal until all of the pool's slots are filled. As slots open up, the remaining queued tasks will start running. 

> **Note:** If you assign a task to a pool that doesn't exist, then the task will not be scheduled when the DAG runs. There are currently no errors or checks for this in the Airflow UI, so be sure to double check the name of the pool that you're assigning a task to.

You can control which tasks within the pool are run first by assigning [priority weights](https://airflow.apache.org/docs/apache-airflow/stable/concepts/priority-weight.html#concepts-priority-weight). These are assigned at the pool level with the `priority_weights` parameter. The values can be any arbitrary integer (default is 1), and higher values get higher priority in the executor queue.

For example, in the DAG snippet below `task_a` and `task_b` are both assigned to the `single_task_pool` which has one slot. `task_b` has a priority weight of 2, while `task_a` has the default priority weight of 1. Therefore, `task_b` would be executed first.

```python
with DAG('pool_dag',
         start_date=datetime(2021, 8, 1),
         schedule_interval=timedelta(minutes=30),
         catchup=False,
         default_args=default_args
         ) as dag:

    task_a = PythonOperator(
        task_id='task_a',
        python_callable=sleep_function,
        pool='single_task_pool'
    )

    task_b = PythonOperator(
        task_id='task_b',
        python_callable=sleep_function,
        pool='single_task_pool',
        priority_weight=2
    )
```

Additionally, you can configure the number of slots occupied by a task by updating the `pool_slots` parameter (the default is 1). Modifying this value could be useful in cases where you are using pools to manage resource utilization. 

## Limitations of Pools

When working with pools, there are a couple of limitations to keep in mind:

- Each task can only be assigned to a single pool.
- If you are using SubDAGs, pools must be applied directly on tasks inside the SubDAG. Pools set within the `SubDAGOperator` will not be honored.
- Pools are meant to control parallelism for Task Instances. If instead you are looking to place limits on the number of concurrent DagRuns for a single DAG or all DAGs, check out the `max_active_runs` and `core.max_active_runs_per_dag` parameters respectively.

## Example: Limit Tasks Hitting an API Endpoint

Below we show a simple example of how to implement a pool to control the number of tasks hitting an API endpoint. 

In this scenario, we have five tasks across two different DAGs that hit the API and that may run concurrently based on the DAG schedules. But we only want a maximum of three tasks hitting the API at a time, so we create a pool called `api_pool` with three slots. We want the tasks in the `pool_priority_dag` to be prioritized if the pool is filled.

In the `pool_priority_dag` below, all three of the tasks hit the API endpoint and should all be assigned to the pool, so we define the `pool` argument in the DAG `default_args` to apply to all tasks. We also want all three of these tasks to have the same priority weight and for them to be prioritized over tasks in the second DAG, so we assign a `priority_weight` of 3 as a default argument. Note that this value is arbitrary: we could have assigned any integer that is higher than the priority weights defined in the second DAG to prioritize these tasks.

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time
import requests

def api_function(**kwargs):
    url = 'https://covidtracking.com/api/v1/states/'
    filename = '{0}/{1}.csv'.format('wa', '2020-03-31')
    res = requests.get(url+filename)

with DAG('pool_priority_dag',
         start_date=datetime(2021, 8, 1),
         schedule_interval=timedelta(minutes=30),
         catchup=False,
         default_args={
             'pool': 'api_pool',
             'retries': 1,
             'retry_delay': timedelta(minutes=5),
             'priority_weight': 3
         }
         ) as dag:

    task_a = PythonOperator(
        task_id='task_a',
        python_callable=api_function
    )

    task_b = PythonOperator(
        task_id='task_b',
        python_callable=api_function
    )

    task_c = PythonOperator(
        task_id='task_c',
        python_callable=api_function
    )
```

Then we have the second DAG, `pool_unimportant_dag` as defined below. In this DAG, we have two tasks that hit the API endpoint and should be assigned to the pool, but we also have two other tasks that do not hit the API. Therefore, we assign the pool and priority weights within the `PythonOperator` instantiations. 

We also want to prioritize `task_x` over `task_y` while keeping both at a lower priority than the tasks in the first DAG. To do this we assign `task_x` a priority weight of 2 and leave `task_y` with the default priority weight of 1. 

```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time
import requests

def api_function(**kwargs):
    url = 'https://covidtracking.com/api/v1/states/'
    filename = '{0}/{1}.csv'.format('wa', '2020-03-31')
    res = requests.get(url+filename)

with DAG('pool_unimportant_dag',
         start_date=datetime(2021, 8, 1),
         schedule_interval=timedelta(minutes=30),
         catchup=False,
         default_args={
             'retries': 1,
             'retry_delay': timedelta(minutes=5)
         }
         ) as dag:

    task_w = DummyOperator(
        task_id='start'
    )

    task_x = PythonOperator(
        task_id='task_x',
        python_callable=api_function,
        pool='api_pool',
        priority_weight=2
    )

    task_y = PythonOperator(
        task_id='task_y',
        python_callable=api_function,
        pool='api_pool'
    )

    task_z = DummyOperator(
        task_id='end'
    )

    task_w >> [task_x, task_y] >> task_z
```

This is a simple example, but hopefully it inspires you to think about how the pools feature can be used to make Airflow a truly powerful orchestrator. No matter your use case, Airflow has you covered.
