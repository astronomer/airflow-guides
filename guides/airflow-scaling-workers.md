---
title: "Scaling Out Airflow"
description: "How to scale out Airflow workers and the settings needed to maximize parallelism"
date: 2019-03-13T00:00:00.000Z
slug: "airflow-scaling-workers"
heroImagePath: null
tags: ["Workers", "Concurrency", "Parallelism", "DAGs"]
---
<!-- markdownlint-disable-file -->

## Overview

One of Apache Airflow's biggest strengths is its scalability. To make the most of Airflow, there are a few key settings that you should consider modifying as you scale up your data pipelines.

Airflow exposes a number of parameters that are closely related to DAG and task-level performance. These fall into 3 categories:

- Environment-level settings
- DAG-level settings
- Operator-level settings

Environment-level settings are generally set in the `airflow.cfg` file or through environment variables, while DAG and task-level settings are typically specified in code.

In this guide, we'll walk through key values in each category in the context of scale and performance.

## Environment-level Airflow Settings

Environment-level settings are typically set in the `airflow.cfg` file, which is required in all Airflow projects. All settings in this file have a default value that can be overridden by modifying the file directly. Default values are taken from the [default_airflow.cfg file](https://github.com/apache/airflow/blob/master/airflow/config_templates/default_airflow.cfg) in Airflow project source code.

To check current values for an existing Airflow environment, go to **Admin** > **Configurations** in the Airflow UI. For more information, read [Setting Configuration Options](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html) or [Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html) in Airflow documentation.

> **Note:** If you're running on Astronomer, these settings can be modified via Environment Variables. For more information, read [Environment Variables on Astronomer](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables).

### Default Values

<table>
  <tr>
    <td align="center"><b>airflow.cfg name</b></td>
    <td align="center"><b>Environment Variable</b></td>
    <td align="center"><b>Default Value</b></td>
  </tr>
  <tr>
    <td>parallelism</td>
    <td>AIRFLOW__CORE__PARALLELISM</td>
    <td align="center">32</td>
  </tr>
  <tr>
    <td>dag_concurrency</td>
    <td>AIRFLOW__CORE__DAG_CONCURRENCY</td>
    <td align="center">16</td>
  </tr>
  <tr>
    <td>worker_concurrency</td>
    <td>AIRFLOW__CELERY__WORKER_CONCURRENCY</td>
    <td align="center">16</td>
  </tr>
  <tr>
    <td>parsing_processes</td>
    <td>AIRFLOW__SCHEDULER__PARSING_PROCESSES</td>
    <td align="center">2</td>
  </tr>
    <td>max_active_runs_per_dag</td>
    <td>AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG</td>
    <td align="center">16</td>
  </tr>
</table>

### Setting Descriptions

- **`parallelism`** is the maximum number of tasks that can run concurrently within a single Airflow environment. If this setting is set to 32, no more than 32 tasks can run at once across all DAGs. Think of this as "maximum active tasks anywhere." If you notice that tasks are stuck in a queue for extended periods of time, this is a value you may want to increase.

- **`dag_concurrency`** determines how many task instances the Airflow Scheduler is able to schedule at once per DAG. Think of this as "maximum tasks that can be scheduled at once, per DAG."

  If you increase the amount of resources available to Airflow (such as Celery Workers or Kubernetes Pods) and notice that tasks are still not running as expected, you might have to increase the values of both `parallelism` and `dag_concurrency`.

- **`worker_concurrency`** is only applicable to users running the [Celery Executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html). It determines how many tasks each Celery Worker can run at any given time. If this value is not set, the Celery Executor will run a maximum of 16 tasks concurrently by default.

  This number is limited by `dag_concurrency`. If you have 1 Worker and want it to match your environment's capacity, `worker_concurrency` should be equal to `parallelism`. If you increase `worker_concurrency`, you might also need to provision additional CPU and/or memory for your Workers.   

- **`parsing_processes`** is the maximum number of threads that can run on the Airflow Scheduler at once. Increasing the value of `parallelism` results in additional strain on the Scheduler, so we recommend increasing `parsing_processes` as well. If you notice a delay in tasks being scheduled, you might need to increase this value or provision additional resources for your Scheduler. If you're running on Astronomer, read [Configure your Airflow Deployment](https://www.astronomer.io/docs/cloud/stable/deploy/configure-deployment#scale-core-resources) for more information on scaling up your Scheduler.

    > **Note:** This setting was renamed in Airflow 1.10.14. In earlier versions, it is defined as `max_threads` ([source](https://github.com/apache/airflow/commit/486134426bf2cd54fae1f75d9bd50715b8369ca1)).

- **`max_active_runs_per_dag`** determines the maximum number of active DAG Runs (per DAG) the Airflow Scheduler can handle at any given time. If this is set to 16, that means the Scheduler can handle up to 16 active DAG runs per DAG. In Airflow, a [DAG Run](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html) represents an instantiation of a DAG in time, much like a task instance represents an instantiation of a task.

### Concurrency Example

Let's assume we have an Airflow environment that uses the default settings defined above and runs 4 Celery Workers. If we have 4 Celery Workers and `worker_concurrency=16`, we could theoretically run 64 tasks at once. Because `parallelism=32`, however, only 32 tasks are able to run at once across Airflow.

If all of these tasks exist within a single DAG and `dag_concurrency=16`, however, we'd be further limited to a maximum of 16 tasks at once.

## DAG-level Airflow Settings

There are two primary DAG-level Airflow settings users can define in code:

- **`max_active_runs`** is the maximum number of active DAG Runs allowed for the DAG in question. Once this limit is hit, the Scheduler will not create new active DAG Runs. If this setting is not defined, the value of `max_active_runs_per_dag` (described above) is assumed.

  ```
  # Allow a maximum of 3 active runs of this DAG at any given time
  dag = DAG('my_dag_id', max_active_runs=3)
  ```

- **`concurrency`** is the maximum number of task instances allowed to run concurrently across all active DAG runs of the DAG for which this setting is defined. This allows you to set 1 DAG to be able to run 32 tasks at once, while another DAG might only be able to run 16 tasks at once. If this setting is not defined, the value of `dag_concurrency` (described above) is assumed.

  For example:

  ```
  # Allow a maximum of concurrent 10 tasks across a max of 3 active DAG runs
  dag = DAG('my_dag_id', concurrency=10,  max_active_runs=3)
  ```

## Task-level Airflow Settings

There are two primary task-level Airflow settings users can define in code:

- **`pool`** is a way to limit the number of concurrent instances of a specific type of task. This is great if you have a lot of Workers or DAG Runs in parallel, but you want to avoid an API rate limit or otherwise don't want to overwhelm a data source or destination. For more information, read [Pools](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=pools#pools) in Airflow's documentation.

- **`task_concurrency`** is a limit to the amount of times the same task can execute across multiple DAG Runs.

  For example, you might set the following in your task definition:

  ```
  t1 = PythonOperator(pool='my_custom_pool', task_concurrency=14)
  ```

### Airflow Pools Best Practices

Let's assume an Airflow environment with the Celery Executor uses the default `airflow.cfg` settings above. Let's also assume we have a DAG with 50 tasks that each pull data from a REST API. When the DAG starts, 16 Celery Workers will be accessing the API at once, which may result in throttling errors from the API. What if we want to limit the rate of tasks, but only for tasks that access this API?

Using pools, we can control how many tasks can run across a specific subset of DAGs. If we assign a single pool to multiple tasks, the pool ensures that no more than a given number of tasks between the DAGs are running at once. As you scale Airflow, you'll want to use pools to manage resource usage across your tasks.

To create a pool:

1. In the Airflow UI, go to **Admin** > **Pools**.

2. Create a pool with a name and a number of slots. In this example, we created a pool with 5 slots. This means that no more than 5 tasks assigned to the pool can run at a single time.

    ![image](https://assets2.astronomer.io/main/guides/airflow-scaling-workers/create_pool.png)

3. Assign your tasks to the pool:

  ```python
    t1 = MyOperator(
      task_id='pull_from_api',
      dag=dag,
      pool='My_REST_API'
    )
  ```

> **Note:** If you're developing locally with the Astronomer CLI, you can define Airflow Pools in the `airflow_settings.yaml` file that was automatically generated when you initialized your Airflow project with `$ astro dev init`. You can use this file to set Pools, Variables, and Connections without needing to manually recreate them in the Airflow UI whenever you restart your environment. For more information, read [Customize your Airflow Image on Astronomer](https://www.astronomer.io/docs/cloud/stable/develop/customize-image#configure-airflowsettingsyaml).
