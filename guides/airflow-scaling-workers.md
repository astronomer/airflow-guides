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

The reason Airflow has so many nobs at different levels is that, as an agnostic orchestrator, Airflow is used for a wide variety of use cases and by a wide variety of personas. Airflow admins or devops engineers might look to tune scaling parameters at the environment level to ensure their supporting infrastructure isn't overstressed, while DAG authors might look to tune scaling parameters at the DAG or task level to ensure their pipelines don't overwhelm external systems. Keeping in mind at what level you are trying to tune performance will help with understanding each parameter's purpose and choosing which parameter(s) to modify.

### Environment-level Settings

Environment-level settings are those that impact your entire Airflow environment (all DAGs). They will all have default values, which can be overriden by setting the appropriate environment variable or modifying your `airflow.cfg` file. Generally, all default values can be found in the [Airflow Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html). To check current values for an existing Airflow environment, go to **Admin** > **Configurations** in the Airflow UI. For more information, read [Setting Configuration Options](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html) in Airflow's documentation.

> **Note:** If you're running on Astronomer, you should modify these parameters via Environment Variables. For more information, read [Environment Variables on Astronomer](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables).

You should look to modify environment-level settings if you are trying to tune performance across *all* of the DAGs in your Airflow environment. This is particularly relevant if you are ensuring your DAGs can run adequately on your supporting infrastructure. The following settings are relevant:

#### Core Settings

Core settings control the number of processes running concurrently and how long those processes can run. The associated environment variables for all parameters in this section are of the form `AIRFLOW__CORE__PARAMETER_NAME`.

- **`parallelism`:** Default 32. This is the maximum number of tasks that can run concurrently within a single Airflow environment. If this setting is set to 32, no more than 32 tasks can run at once across all DAGs. Think of this as "maximum active tasks anywhere." If you notice that tasks are stuck in a queue for extended periods of time, this is a value you may want to increase.

- **`max_active_tasks_per_dag`:** (formerly `dag_concurrency`) Default 16. This determines how many task instances the Airflow Scheduler is able to schedule at once per DAG. Think of this as "maximum tasks that can be scheduled at once, per DAG."

  If you increase the amount of resources available to Airflow (such as Celery Workers or Kubernetes Pods) and notice that tasks are still not running as expected, you might have to increase the values of both `parallelism` and `max_active_tasks_per_dag`.

- **`max_active_runs_per_dag`:** Default 16. This determines the maximum number of active DAG Runs (per DAG) the Airflow Scheduler can create at any given time. In Airflow, a [DAG Run](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html) represents an instantiation of a DAG in time, much like a task instance represents an instantiation of a task.

- **`dag_file_processor_timeout`:**: Default 30 seconds. This is how long a DagFileProcessor, which processes a DAG file, can run before timing out. If your DAG processing logs show timeouts, try increasing this value.

- **`dagbag_import_timeout`:**: Default 30 seconds. This is how long the dagbag can import DAG objects before timing out. It must be lower than the value set for `dag_file_processor_timeout`.

#### Scheduler Settings

Scheduler settings control how the scheduler parses DAG files and creates DAG runs. The associated environment variables for all parameters in this section are of the form `AIRFLOW__SCHEDULER__PARAMETER_NAME`.

- **`min_file_process_interval`:** Default 30 seconds. Each DAG file is parsed every `min_file_process_interval` number of seconds. Updates to DAGs are reflected after this interval. Having a low number here will increase scheduler CPU usage. If you have dynamic DAGs created by complex code, you may want to increase this value to avoid negative scheduler performance impacts.

- **`dag_dir_list_interval`:** Default 300 seconds (5 minutes). This is how often to scan the DAGs directory for new files. The lower the number, the faster new DAGs will be processed but the higher your CPU usage.

  It is helpful know how long it takes to parse your DAGs (`dag_processing.total_parse_time`) to know what values to choose for `min_file_process_interval` and `dag_dir_list_interval`. If your `dag_dir_list_interval` is less than the amount of time it takes to parse each DAG, you may see performance issues.

- **`parsing_processes`:** (formerly `max_threads`) Default 2. The scheduler can run multiple processes in parallel to parse dags. This defines how many processes will run. Increasing this value can help serialize DAGs more efficiently if you have a large number of them. Note that if you are running multiple schedulers, this value will apply to *each* of them.

- **`file_parsing_sort_mode`**: Default `modified_time`. This determines how the scheduler will list and sort DAG files to decide the parsing order. Set to one of: `modified_time`, `random_seeded_by_host` and `alphabetical`.

- **`scheduler_heartbeat_sec`:** Default 5 seconds. The scheduler constantly tries to trigger new tasks. This defines how often the scheduler should run (in seconds).

- **`max_dagruns_to_create_per_loop`:** Default 10. This is the max number of DAGs to create DagRuns for per scheduler loop. You can use this option to free up resources for scheduling tasks by **decreasing** the value.

- **`max_dagruns_per_loop_to_schedule`:** Default 20. 

- **`max_tis_per_query`:** Default 512. This parameter changes the batch size of queries to the metastore in the main scheduling loop. If the value is higher, you can process more `tis` per query, 

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/blog/airflow-dbt-1" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Building a Scalable Analytics Architecture with Airflow and dbt', spottedCompany: window.spottedCompany })">Building a Scalable Analytics Architecture with Airflow and dbt</a></li>
    <li data-icon="→"><a href="/case-studies/datasembly" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Datasembly: From One Airflow Instance to Multiple Deployments with Astronomer', spottedCompany: window.spottedCompany })">Datasembly: From One Airflow Instance to Multiple Deployments with Astronomer</a></li>
    <li data-icon="→"><a href="https://registry.astronomer.io/providers/google/modules/dataprocscaleclusteroperator" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Astronomer Registry: DataprocScaleClusterOperator', spottedCompany: window.spottedCompany })">Astronomer Registry: DataprocScaleClusterOperator</a></li>
</ul>

### DAG-level Airflow Settings

There are two primary DAG-level Airflow settings users can define in code:

`max_active_tasks`

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

### Task-level Airflow Settings

There are two primary task-level Airflow settings users can define in code:

- **`pool`** is a way to limit the number of concurrent instances of a specific type of task. This is great if you have a lot of Workers or DAG Runs in parallel, but you want to avoid an API rate limit or otherwise don't want to overwhelm a data source or destination. For more information, read [Pools](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=pools#pools) in Airflow's documentation.

- **`task_concurrency`** is a limit to the amount of times the same task can execute across multiple DAG Runs.

  For example, you might set the following in your task definition:

  ```
  t1 = PythonOperator(pool='my_custom_pool', task_concurrency=14)
  ```


## Executors and Scaling

Depending on which executor you choose for your Airflow environment, there are a couple of additional concepts to keep in mind when scaling.

### Celery Executor

The [Celery executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html) utilizes standing workers to run tasks. Scaling with the Celergy executor involves choosing both the number and size of the workers available to Airflow. The more workers you have available in your environment, or the larger your workers are, the more capacity you have to run tasks concurrently.

You can also tune your **`worker_concurrency`**, which determines how many tasks each Celery worker can run at any given time. If this value is not set, the Celery executor will run a maximum of 16 tasks concurrently by default.

Your `worker_concurrency` is limited by `max_active_tasks_per_dag`. If you increase `worker_concurrency`, you might also need to provision additional CPU and/or memory for your workers.   

### Kubernetes Executor

`worker_pods_creation_batch_size` for k8s executor

## Potential Scaling Issues
