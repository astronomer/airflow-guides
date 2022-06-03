---
title: "Deferrable Operators"
description: "How to implement deferrable operators to save cost and resources with Airflow."
date: 2021-12-25T00:00:00.000Z
slug: "deferrable-operators"
heroImagePath: null
tags: ["Operators", "Concurrency", "Resources", "Sensors", "Workers"]
---

## Overview

Prior to Airflow 2.2, all task execution occurred within your worker resources. For tasks whose work was occurring outside of Airflow (e.g. a Spark Job), your tasks would sit idle waiting for a success or failure signal. These idle tasks would occupy worker slots for their entire duration, potentially queuing other tasks and delaying their start times.

With the release of Airflow 2.2, Airflow has introduced a new way to run tasks in your environment: deferrable operators. These operators leverage Python's [asyncio](https://docs.python.org/3/library/asyncio.html) library to efficiently run tasks waiting for an external resource to finish. This frees up your workers, allowing you to utilize those resources more effectively. In this guide, we'll walk through the concepts of deferrable operators, which operators are deferrable, and the new components introduced to Airflow related to this feature.

## Deferrable Operator Concepts

There are some terms and concepts that are important to understand when discussing deferrable operators:

- **[asyncio](https://docs.python.org/3/library/asyncio.html):** This Python library is used as a foundation for multiple asynchronous frameworks. This library is core to deferrable operator's functionality, and is used when writing triggers.
- **Triggers:** These are small, asynchronous pieces of Python code. Due to their asynchronous nature, they coexist efficiently in a single process known as the triggerer.
- **Triggerer:** This is a new airflow service (like a scheduler or a worker) that runs an [asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-event-loop) in your Airflow environment. Running a triggerer is essential for using deferrable operators.
- **Deferred:** This is a new Airflow task state (medium purple color) introduced to indicate that a task has paused its execution, released the worker slot, and submitted a trigger to be picked up by the triggerer process.

> Note: The terms "deferrable" and "async" or "asynchronous" are often used interchangeably. They mean the same thing in this context.

With traditional operators, a task might submit a job to an external system (e.g. a Spark Cluster) and then poll the status of that job until it completes. Even though the task might not be doing significant work, it would still occupy a worker slot during the polling process. As worker slots become occupied, tasks may be queued resulting in delayed start times. Visually, this is represented in the diagram below:

![Classic Worker](https://assets2.astronomer.io/main/guides/deferrable-operators/classic_worker_process.png)

With deferrable operators, worker slots can be released while polling for job status. When the task is deferred (suspended), the polling process is offloaded as a trigger to the triggerer, freeing up the worker slot. The triggerer has the potential to run many asynchronous polling tasks concurrently, preventing this work from occupying your worker resources. When the terminal status for the job is received, the task resumes, taking a worker slot while it finishes. Visually, this is represented in the diagram below:

![Deferrable Worker](https://assets2.astronomer.io/main/guides/deferrable-operators/deferrable_operator_process.png)

## When and Why To Use Deferrable Operators

In general, deferrable operators should be used whenever you have tasks that occupy a worker slot while polling for a condition in an external system. For example, using deferrable operators for sensor tasks (e.g. poking for a file on an SFTP server) can result in efficiency gains and reduced operational costs. In particular, if you are currently working with [smart sensors](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html#smart-sensors), you should consider using deferrable operators instead. Compared to smart sensors, which were deprecated in Airflow 2.2.4, deferrable operators are more flexible and better supported by Airflow.

Currently, the following deferrable operators are installed by default in core Airflow:

- [TimeSensorAsync](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/time_sensor/index.html?highlight=timesensor#module-contents)
- [DateTimeSensorAsync](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/date_time/index.html#airflow.sensors.date_time.DateTimeSensorAsync)

You can use additional deferrable operators built and maintained by Astronomer by installing the open source [Astronomer Providers](https://github.com/astronomer/astronomer-providers) Python package. The operators and sensors in this package are deferrable versions of commonly used operators. For example, the package includes:

- `SnowflakeOperatorAsync`
- `DatabricksSubmitRunOperatorAsync`
- `HttpSensorAsync`
 
For a full list of deferrable operators and sensors available in the `astronomer-providers` package, check out the [Changelog](https://astronomer-providers.readthedocs.io/en/stable/changelog.html). You can also create your own deferrable operator if one does not already exist for your use case (more on this in the last section of this guide).

There are numerous benefits to using deferrable operators. Some of the most notable are:

- **Reduced resource consumption:** Depending on the available resources and the workload of your triggers, you can run hundreds to thousands of deferred tasks in a single triggerer process. This can lead to a reduction in the number of workers needed to run tasks during periods of high concurrency. With less workers needed, you are able to scale down the underlying infrastructure of your Airflow environment.
- **Resiliency against restarts:** Triggers are stateless by design. This means your deferred tasks will not be set to a failure state if a triggerer needs to be restarted due to a deployment or infrastructure issue. Once a triggerer is back up and running in your environment, your deferred tasks will resume.
- **Paves the way to event-based DAGs:** The presence of `asyncio` in core Airflow is a potential foundation for event-triggered DAGs.

## Example Workflow Using Deferrable Operators

Let's say we have a DAG that is scheduled to run a sensor every minute, where each task can take up to 20 minutes. Using the default settings with 1 worker, we can see that after 20 minutes we have 16 tasks running, each holding a worker slot:

![Classic Tree View](https://assets2.astronomer.io/main/guides/deferrable-operators/classic_tree_view.png)

Because worker slots are held during task execution time, we would need at least 20 worker slots available for this DAG to ensure that future runs are not delayed. To increase concurrency, we would need to add additional resources to our Airflow infrastructure (e.g. another worker pod). 

```python
from datetime import datetime
from airflow import DAG
from airflow.sensors.date_time import DateTimeSensor
 
with DAG(
   "sync_dag",
   start_date=datetime(2021, 12, 22, 20, 0),
   end_date=datetime(2021, 12, 22, 20, 19),
   schedule_interval="* * * * *",
   catchup=True,
   max_active_runs=32,
   max_active_tasks=32
) as dag:
 
   sync_sensor = DateTimeSensor(
       task_id="sync_task",
       target_time="""{{ macros.datetime.utcnow() + macros.timedelta(minutes=20) }}""",
   )
```

By leveraging a deferrable operator for this sensor, we are able to achieve full concurrency while allowing our worker to complete additional work across our Airflow environment. With our updated DAG below, we see that all 20 tasks have entered a state of deferred, indicating that these sensing jobs (triggers) have been registered to run in the triggerer process.

![Deferrable Tree View](https://assets2.astronomer.io/main/guides/deferrable-operators/deferrable_tree_view.png)

```python
from datetime import datetime
from airflow import DAG
from airflow.sensors.date_time import DateTimeSensorAsync
 
with DAG(
   "async_dag",
   start_date=datetime(2021, 12, 22, 20, 0),
   end_date=datetime(2021, 12, 22, 20, 19),
   schedule_interval="* * * * *",
   catchup=True,
   max_active_runs=32,
   max_active_tasks=32
) as dag:
 
   async_sensor = DateTimeSensorAsync(
       task_id="async_task",
       target_time="""{{ macros.datetime.utcnow() + macros.timedelta(minutes=20) }}""",
   )
```

## Running Deferrable Tasks in your Airflow Environment

To start a triggerer process, run `airflow triggerer` in your Airflow environment. You should see an output similar to the below image.

![Triggerer Logs](https://assets2.astronomer.io/main/guides/deferrable-operators/triggerer_logs.png)

Note that if you are running Airflow on [Astro](https://docs.astronomer.io/cloud/deferrable-operators#prerequisites), the triggerer runs automatically if you are on Astro Runtime 4.0+. If you are using Astronomer Software 0.26+, you can add a triggerer to an Airflow 2.2+ deployment in the **Deployment Settings** tab. This [guide](https://docs.astronomer.io/enterprise/configure-deployment#triggerer) details the steps for configuring this feature in the platform.

As tasks are raised into a deferred state, triggers are registered in the triggerer. You can set the number of concurrent triggers that can run in a single triggerer process with the [`default_capacity`](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#triggerer) configuration setting in Airflow. This can also be set via the `AIRFLOW__TRIGGERER__DEFAULT_CAPACITY` environment variable. By default, this variable's value is `1,000`.

### High Availability

Note that triggers are designed to be highly-available. You can implement this by starting multiple triggerer processes. Similar to the [HA scheduler](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduler.html#running-more-than-one-scheduler) introduced in Airflow 2.0, Airflow ensures that they co-exist with correct locking and HA. You can reference the [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html#high-availability) for further information on this topic.

### Creating Your Own Deferrable Operator

If you have an operator that would benefit from being asynchronous but does not yet exist in OSS Airflow or Astronomer Providers, you can create your own. The [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html#writing-deferrable-operators) have great instructions to get you started.
