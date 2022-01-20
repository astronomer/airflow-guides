---
title: "Scaling Out Airflow"
description: "How to tune your Airflow environment so it scales with your DAGs."
date: 2019-03-13T00:00:00.000Z
slug: "airflow-scaling-workers"
heroImagePath: null
tags: ["Workers", "Concurrency", "Parallelism", "DAGs"]
---

## Overview

One of Apache Airflow's biggest strengths is its scalability assuming good supporting infrastructure. To make the most of Airflow, there are a few key settings that you should consider modifying as you scale up your data pipelines.

Airflow exposes a number of parameters that are closely related to DAG and task-level performance. These fall into 3 categories:

- Environment-level settings
- DAG-level settings
- Task-level settings

In this guide, we'll walk through the key parameters in each category that can be leveraged to tune performance in Airflow. We'll also touch on how choice of executor can impact scaling, and how to respond to common scaling related issues.

> Note: This guide focuses on parameters for Airflow 2.0+. Where noted, some parameters may have different names in earlier Airflow versions.

## Parameter Tuning

Airflow has many parameters that impact scaling as your number of DAGs and tasks grows. Tuning these settings can impact DAG parsing and task scheduling performance, parallelism in your Airflow environment, and more. 

The reason Airflow has so many knobs at different levels is that, as an agnostic orchestrator, Airflow is used for a wide variety of use cases and by a wide variety of personas. Airflow admins or DevOps engineers might look to tune scaling parameters at the environment level to ensure their supporting infrastructure isn't overstressed, while DAG authors might look to tune scaling parameters at the DAG or task level to ensure their pipelines don't overwhelm external systems. Keeping in mind at what level you are trying to tune performance will help with understanding each parameter's purpose and choosing which parameter(s) to modify.

### Environment-level Settings

Environment-level settings are those that impact your entire Airflow environment (all DAGs). They will all have default values, which can be overridden by setting the appropriate environment variable or modifying your `airflow.cfg` file. Generally, all default values can be found in the [Airflow Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html). To check current values for an existing Airflow environment, go to **Admin** > **Configurations** in the Airflow UI. For more information, read [Setting Configuration Options](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html) in Airflow's documentation.

> **Note:** If you're running on Astronomer, you should modify these parameters via Environment Variables. For more information, read [Environment Variables on Astronomer](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables).

You should look to modify environment-level settings if you are trying to tune performance across *all* of the DAGs in your Airflow environment. This is particularly relevant if you are ensuring your DAGs can run adequately on your supporting infrastructure. The following settings are relevant:

#### Core Settings

Core settings control the number of processes running concurrently and how long those processes can run. The associated environment variables for all parameters in this section are of the form `AIRFLOW__CORE__PARAMETER_NAME`.

- **`parallelism`:** Default 32. This is the maximum number of tasks that can run concurrently within a single Airflow environment. If this setting is set to 32, no more than 32 tasks can run at once across all DAGs. Think of this as "maximum active tasks anywhere." If you notice that tasks are stuck queued for extended periods of time, this is a value you may want to increase.

- **`max_active_tasks_per_dag`:** (formerly `dag_concurrency`) Default 16. This determines how many task instances the Airflow Scheduler is able to schedule at once per DAG. Think of this as "maximum tasks that can be scheduled at once, per DAG." Use this setting to prevent any one DAG from taking up too many of the available slots from parallelism or your pools. This helps DAGs to be good neighbors to one another.

  If you increase the amount of resources available to Airflow (such as Celery workers or Kubernetes resources) and notice that tasks are still not running as expected, you might have to increase the values of both `parallelism` and `max_active_tasks_per_dag`.

- **`max_active_runs_per_dag`:** Default 16. This determines the maximum number of active DAG Runs (per DAG) the Airflow Scheduler can create at any given time. In Airflow, a [DAG Run](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html) represents an instantiation of a DAG in time, much like a task instance represents an instantiation of a task. This parameter is most relevant when backfilling or if Airflow has to catch up from missed DAG Runs. Consider how you want to handle these scenarios when setting this parameter.

- **`dag_file_processor_timeout`:**: Default 50 seconds. This is how long a `DagFileProcessor`, which processes a DAG file, can run before timing out.

- **`dagbag_import_timeout`:**: Default 30 seconds. This is how long the `dagbag` can import DAG objects before timing out. It must be lower than the value set for `dag_file_processor_timeout`. If your DAG processing logs show timeouts, or if your DAG is not showing up either in the list of DAGs or the import errors, try increasing this value. You can also try increasing this value if your tasks aren't executing, since workers need to fill up the `dagbag` when tasks execute.

#### Scheduler Settings

Scheduler settings control how the scheduler parses DAG files and creates DAG runs. The associated environment variables for all parameters in this section are of the form `AIRFLOW__SCHEDULER__PARAMETER_NAME`.

- **`min_file_process_interval`:** Default 30 seconds. Each DAG file is parsed every `min_file_process_interval` number of seconds. Updates to DAGs are reflected after this interval. Having a low number here will increase scheduler CPU usage. If you have dynamic DAGs created by complex code, you may want to increase this value to avoid negative scheduler performance impacts.

- **`dag_dir_list_interval`:** Default 300 seconds (5 minutes). This is how often to scan the DAGs directory for new files. The lower the number, the faster new DAGs will be processed but the higher your CPU usage.

  It is helpful know how long it takes to parse your DAGs (`dag_processing.total_parse_time`) to know what values to choose for `min_file_process_interval` and `dag_dir_list_interval`. If your `dag_dir_list_interval` is less than the amount of time it takes to parse each DAG, you may see performance issues.

- **`parsing_processes`:** (formerly `max_threads`) Default 2. The scheduler can run multiple processes in parallel to parse dags. This setting defines how many processes will run. We recommend setting a value of 2 x vCPU. Increasing this value can help serialize DAGs more efficiently if you have a large number of them. Note that if you are running multiple schedulers, this value will apply to *each* of them.

- **`file_parsing_sort_mode`**: Default `modified_time`. This determines how the scheduler will list and sort DAG files to decide the parsing order. Set to one of: `modified_time`, `random_seeded_by_host` and `alphabetical`.

- **`scheduler_heartbeat_sec`:** Default 5 seconds. The scheduler constantly tries to trigger new tasks. This defines how often the scheduler should run (in seconds).

- **`max_dagruns_to_create_per_loop`:** Default 10. This is the max number of DAGs to create DagRuns for per scheduler loop. You can use this option to free up resources for scheduling tasks by **decreasing** the value.

- **`max_tis_per_query`:** Default 512. This parameter changes the batch size of queries to the metastore in the main scheduling loop. If the value is higher, you can process more `tis` per query, but your query may become too complex and create a performance bottleneck. 

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/blog/airflow-dbt-1" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Building a Scalable Analytics Architecture with Airflow and dbt', spottedCompany: window.spottedCompany })">Building a Scalable Analytics Architecture with Airflow and dbt</a></li>
    <li data-icon="→"><a href="/case-studies/datasembly" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Datasembly: From One Airflow Instance to Multiple Deployments with Astronomer', spottedCompany: window.spottedCompany })">Datasembly: From One Airflow Instance to Multiple Deployments with Astronomer</a></li>
    <li data-icon="→"><a href="https://registry.astronomer.io/providers/google/modules/dataprocscaleclusteroperator" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Astronomer Registry: DataprocScaleClusterOperator', spottedCompany: window.spottedCompany })">Astronomer Registry: DataprocScaleClusterOperator</a></li>
</ul>

### DAG-level Airflow Settings

DAG-level settings apply only to specific DAGs and are defined in your DAG code. You should look to modify DAG-level settings if you want to performance tune a particular DAG, especially in cases where that DAG is hitting an external system (e.g. an API or database) that might cause performance issues if hit too frequently. In general, DAG-level settings will supersede environment-level settings for the same topic.

There are three primary DAG-level Airflow settings users can define in code:

- **`max_active_runs`:** This is the maximum number of active DAG Runs allowed for the DAG in question. Once this limit is hit, the Scheduler will not create new active DAG Runs. If this setting is not defined, the value of `max_active_runs_per_dag` (described above) is assumed.

  ```python
  # Allow a maximum of 3 active runs of this DAG at any given time
  dag = DAG('my_dag_id', max_active_runs=3)
  ```

  If are utilizing `catchup` or `backfill` for your DAG, consider defining this parameter to ensure you don't accidentally trigger a high number of DAG runs.
- **`max_active_tasks`:** This is the total number of tasks that can run at the same time for a given DAG run. It essentially controls the parallelism within your DAG. If this setting is not defined, the value of `max_active_tasks_per_dag` (described above) is assumed.
- **`concurrency`:** This is the maximum number of task instances allowed to run concurrently across all active DAG runs of the DAG for which this setting is defined. This allows you to set 1 DAG to be able to run 32 tasks at once, while another DAG might only be able to run 16 tasks at once. If this setting is not defined, the value of `max_active_tasks_per_dag` (described above) is assumed.

  For example:

  ```python
  # Allow a maximum of concurrent 10 tasks across a max of 3 active DAG runs
  dag = DAG('my_dag_id', concurrency=10,  max_active_runs=3)
  ```

### Task-level Airflow Settings

Task-level settings can be used to implement even finer grain control within a specific DAG(s) and are defined in your operators. You should look to modify task-level settings if you have specific types of tasks that are known to cause performance issues. 

There are two primary task-level Airflow settings users can define in code:

- **`max_active_tis_per_dag`:** Formerly `task_concurrency`. This is a limit to the amount of times the same task can run concurrently across all DAG Runs. For instance, if a task reaches out to an external resource such as a data table that you do not want multiple tasks modifying at once, you can set this value to 1.

  You can set the following in your task definition:

  ```python
  t1 = PythonOperator(pool='my_custom_pool', max_active_tis_per_dag=14)
  ```

- **`pool`:** Pools are a way to limit the number of concurrent instances of an arbitrary group of tasks. This is useful if you have a lot of workers or DAG runs in parallel, but you want to avoid an API rate limit or otherwise don't want to overwhelm a data source or destination. For more information, read our [Airflow Pools Guide](https://www.astronomer.io/guides/airflow-pools).


## Executors and Scaling

Depending on which executor you choose for your Airflow environment, there are a couple of additional concepts to keep in mind when scaling.

### Celery Executor

The [Celery executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html) utilizes standing workers to run tasks. Scaling with the Celery executor involves choosing both the number and size of the workers available to Airflow. The more workers you have available in your environment, or the larger your workers are, the more capacity you have to run tasks concurrently.

You can also tune your **`worker_concurrency`** (environment variable `AIRFLOW__CELERY__WORKER_CONCURRENCY`), which determines how many tasks each Celery worker can run at any given time. If this value is not set, the Celery executor will run a maximum of 16 tasks concurrently by default. If you increase `worker_concurrency`, you might also need to provision additional CPU and/or memory for your workers.   

### Kubernetes Executor

The [Kubernetes executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html) launches a pod in a Kubernetes cluster for each task. Since each task runs in its own pod, resources can be specified on an individual task level.

When performance tuning with the Kubernetes executor, it is important to keep in mind the supporting infrastructure of your Kubernetes cluster. Many users will enable auto-scaling on their cluster to ensure they get the benefit of Kubernetes' elasticity.

You can also tune your **`worker_pods_creation_batch_size`** (environment variable `AIRFLOW__KUBERNETES__WORKER_PODS_CREATION_BATCH_SIZE`), which determines how many pods can be created per scheduler loop. The default is 1, but most users will want to increase this number for better performance, especially if you have concurrent tasks. How high you can increase the value depends on the tolerance of your Kubernetes cluster.

## Potential Scaling Issues

Scaling your Airflow environment can be more of an art than a science, and is highly dependent on your supporting infrastructure and your DAGs. There are too many potential scaling issues to address them all here, but below are some commonly encountered issues and possible parameters to change. 

- Issue: Tasks scheduling latency is high
    - Potential cause: The scheduler may not have enough resources to parse DAGs in order to then schedule tasks.
    - Try changing: `worker_concurrency` (if using Celery), `parallelism`
- Issue: DAGs are stuck in queued state, but not running
    - Potential cause: The number of tasks being scheduled may be beyond the capacity of your Airflow infrastructure.
    - Try changing: If using the Kubernetes executor, check that there are available resources in the namespace and check if `worker_pods_creation_batch_size` can be increased. If using the Celery executor, check if `worker_concurrency` can be increased.
- Issue: An individual DAG is having trouble running tasks in parallel, while other DAGs seem unaffected
    - Potential cause: Possible DAG-level bottleneck
    - Try changing: `max_active_task_per_dag`, pools (if using them), or overall `parallelism`

For help with other scaling issues, consider joining the [Apache Airflow Slack](https://airflow.apache.org/community/) or [reach out to Astronomer](https://www.astronomer.io/get-astronomer/).
