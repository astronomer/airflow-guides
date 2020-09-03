---
title: "Scaling out Airflow"
description: "How to scale out Airflow workers and the settings needed to maximize parallelism"
date: 2019-03-13T00:00:00.000Z
slug: "airflow-scaling-workers"
heroImagePath: null
tags: ["Workers", "Concurrency", "Parallelism", "Airflow"]
---

As data pipelines grow in complexity, the need to have a flexible and scalable architecture is more important than ever. Airflow's Celery Executor makes it easy to scale out workers horizontally when you need to execute lots of tasks in parallel. There are however some "gotchas" to look out for. Even folks familiar with using the Celery Executor might wonder, "Why are more tasks not running even after I add workers?""

This common issue is the result of a number of different Airflow settings you can tweak to reach max parallelism and performance. Settings are maintained in the airflow.cfg file and can also be overridden using environment variables.

See the guide on [Airflow Executors](https://www.astronomer.io/guides/airflow-executors-explained/) for more info on which executor is right for you.

Here are the settings and their default values.

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
    <td>max_threads</td>
    <td>AIRFLOW__SCHEDULER__MAX_THREADS</td>
    <td align="center">2</td>
  </tr>
</table>


**parallelism** is the max number of task instances that can run concurrently on airflow. This means that across all running DAGs, no more than 32 tasks will run at one time.

**dag_concurrency** is the number of task instances allowed to run concurrently within a *specific dag*. In other words, you could have 2 DAGs running 16 tasks each in parallel, but a single DAG with 50 tasks would also only run 16 tasks - not 32

These are the main two settings that can be tweaked to fix the common "Why are more tasks not running even after I add workers?"

**worker_concurrency** is related, but it determines how many tasks a single worker can process. So, if you have 4 workers running at a worker concurrency of 16, you could process up to 64 tasks at once. Configured with the defaults above, however, only 32 would actually run in parallel. (and only 16 if all tasks are in the same DAG)

**Pro tip:** If you increase worker_concurrency, make sure your worker has enough resources to handle the load. You may need to increase CPU and/or memory on your workers. Note: This setting only impacts the CeleryExecutor

If you're using Astronomer, you can configure both worker resources and environment variables directly through the UI. For more info and screenshots of our sweet sliders, check out our Astronomer UI guide [here](https://www.astronomer.io/docs/astronomer-ui/).

![image](https://assets2.astronomer.io/main/guides/airflow-scaling-workers/worker_slider.png)

### Scheduler Impact

If you decide to increase these settings, Airflow will be able to scale up and process many tasks in parallel. This could however put a strain on the scheduler. For example, you may notice delays in task execution, tasks remaining a in `queued` state for longer than expected, or gaps in the Gantt chart of the Airflow UI.

The **max_threads = 2** setting can be used to increase the number of threads running on the scheduler. This can prevent the scheduler from getting behind, but may also require more resources. If you increase this, you may need to increase CPU and/or memory on your scheduler. This should be set to n-1 where n is the number of CPUs of your scheduler.

On Astronomer, simply increase the slider on the Scheduler to increase CPU and memory.

![image](https://assets2.astronomer.io/main/guides/airflow-scaling-workers/scheduler_slider.png)

### Pools

Finally, **pools** are a way of limiting the number of concurrent instances of a specific type of task. This is great if you have a lot of workers in parallel, but you don’t want to overwhelm a source or destination.

For example, with the default settings above, and a DAG with 50 tasks to pull data from a REST API, when the DAG starts, you would get 16 workers hitting the API at once and you may get some throttling errors back from your API. You can create a pool and give it a limit of 5. Then assign all of the tasks to that pool. Even though you have plenty of free workers, only 5 will run at one time.

You can create a pool directly in the Admin section of the Airflow web UI

![image](https://assets2.astronomer.io/main/guides/airflow-scaling-workers/create_pool.png)

And then assign your task to the pool
```python
t1 = MyOperator(
  task_id='pull_from_api',
  dag=dag,
  pool='My_REST_API'
)
```
