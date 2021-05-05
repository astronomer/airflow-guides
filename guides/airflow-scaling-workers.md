---
title: "Scaling Out Airflow"
description: "How to scale out Airflow workers and the settings needed to maximize parallelism"
date: 2019-03-13T00:00:00.000Z
slug: "airflow-scaling-workers"
heroImagePath: null
tags: ["Workers", "Concurrency", "Parallelism", "DAGs"]
---
<!-- markdownlint-disable-file -->
One of Airflow's most important features is its ability to run at any scale. Because Airflow is 100% code, you need to only update a few key settings across your environment when to scale up your data pipelines.

In this guide, we'll walk through the key Airflow components related to scale. We'll also provide guidance on when and how to scale Airflow to best suit your needs.

## Scale Airflow Using Settings

One of the ways you can control the scale of Airflow is through environment-level settings. These can be configured either in your `airflow.cfg` file or through setting environment variables.

The following table includes some of they key settings you'll want to update when scaling Airflow:

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
</table>


- `parallelism` is the maximum number of task instances that can run concurrently on Airflow. By default, across all running DAGs, no more than 32 tasks will run at one time. You might want to increase this value if you notice that tasks are stuck in a queue for extended periods of time.

- `dag_concurrency` is the maximum number of tasks that can run concurrently within a specific DAG. By default, a DAG can have a maximum of 16 tasks running at once.

    If you scale the computational resources of Airflow, such as Celery Workers or Kubernetes pods, and still notice that tasks aren't running as expected, you might have to increase the values of both `parallelism` and `dag_concurrency`.

- `worker_concurrency` is the maximum number of tasks that a single Celery Worker can process at once. This setting applies only when using the Celery Executor.

    If you increase `worker_concurrency`, you might also need to provision additional CPU and/or memory for your workers.

- `parsing_processes` is the maximum number of threads that can run on the Scheduler at once. Scaling up DAG-level settings like `parallelism` results in additional strain on the Scheduler, so we recommend scaling this alongside your other settings. If you notice a delay in tasks being scheduled, you might need to increase this value or provision additional CPU and/or memory for your Scheduler.

    > **Note:** In Airflow 1.10.13 and prior versions, the parsing_processes setting is called max_threads

Putting it all together, let's assume we have an Airflow environment that uses all of the default settings and uses 4 Celery Workers to process tasks. Because we have 4 Celery Workers and `worker_concurrency=16`, we could theoretically run 64 tasks at once. Because `parallelism=32`, however, only 32 tasks are able to run at once across Airflow. Moreover, if all of these tasks exist within a single DAG, we'd be able to run only 16 tasks at once because `dag_concurrency=16`.

## Scale Airflow Using Pools

Finally, **pools** are a way of limiting the number of concurrent instances of a specific type of task. This is great if you have a lot of workers in parallel, but you don’t want to overwhelm a source or destination.

For example, let's assume Airflow uses the default `airflow.cfg` settings above. Let's also assume we have a DAG with 50 tasks that each pull data from a REST API. When the DAG starts, 16 workers will be accessing the API at once, which may result in throttling errors from the API. What if we want to limit the rate of tasks, but only for tasks that access this API?

Using pools, we can control how many tasks can run across a specific subset of DAGs. If we assign a single pool to multiple tasks, the pool ensures that no more than a given number of tasks between the DAGs are running at once. As you scale Airflow, you'll want to use pools to manage resource usage across your tasks.

To create a pool:

1. In the Airflow UI, go to **Admin** > **Pools**.

2. Create a pool with a name and a number of slots. In this example, we created a pool with 5 slots, meaning that no more than 5 tasks assigned to the pool can run at a single time:

    ![image](https://assets2.astronomer.io/main/guides/airflow-scaling-workers/create_pool.png)

3. Assign your tasks to the pool:

    ```python
    t1 = MyOperator(
      task_id='pull_from_api',
      dag=dag,
      pool='My_REST_API'
    )
```
