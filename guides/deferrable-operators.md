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

With the release of Airflow 2.2, Airflow has introduced a new way to run tasks in your environment: Deferrable operators. These operators leverage Python's [asyncio](https://docs.python.org/3/library/asyncio.html) library to efficiently run tasks waiting for an external resource to finish. This frees up your workers, allowing you to utilize those resources more effectively. In this guide, we'll walk through the concepts of deferrable operators, as well as the new components introduced to Airflow related to this feature.

## Deferrable Operator Concepts

There are some terms and concepts that are important to understand when discussing deferrable operators:

- **asyncio:** This is the Python [library](https://docs.python.org/3/library/asyncio.html) that is used as a foundation for multiple asynchronous frameworks. This library is core to Deferrable Operators functionality, and is used when writing triggers.
- **Triggers:** These are small, asynchronous pieces of Python code. Due to their asynchronous nature, they coexist efficiently in a single process known as the triggerer.
- **Triggerer:** This is a new airflow service (like a scheduler or a worker) that runs an [asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-event-loop) in your Airflow environment. Running a triggerer component is essential for using deferrable operators. Depending on the available resources and the workload of your triggers, you can run hundreds to thousands of triggers in a single triggerer process.
- **Deferred:** This is a new Airflow task state (medium purple color) introduced to indicate that a task has paused its execution, released the worker slot, and has submitted a trigger to be picked up by the triggerer process to continue the task’s execution.

With traditional operators, a task might poll an external system while waiting for a process to complete. Even though the task might not be doing significant work, it would still occupy a worker slot. This can prevent other tasks from running. Visually, that looks something like the diagram below:

![Classic Worker](https://assets2.astronomer.io/main/guides/deferrable-operators/classic_worker_process.png)

With deferrable operators, worker slots can be released while a task is waiting for an external system. The task is then deferred (suspended), and polling is offloaded to the triggerer, which can run many asynchronous polling tasks concurrently in a single process. When the terminal status for the job is received, the task resumes, taking a worker slot while it finishes. Visually, that looks like this updated diagram:

![Deferrable Worker](https://assets2.astronomer.io/main/guides/deferrable-operators/deferrable_operator_process.png)

## When and Why to Use Deferrable Operators

In general, deferrable operators should be used whenever you have long-running tasks that might occupy a worker slot for longer than is necessary and you want to reduce Airflow’s resource utilization. For example, if you have many sensor tasks using deferrable operators may reduce costs. In particular, if you are currently working with Smart Sensors to poll an external job or system, deferrable operators will be a preferable, more stable solution and better supported by Airflow in the long term.

Currently, the following operators are available in Airflow as deferrable:

- [TimeSensorAsync](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/time_sensor/index.html?highlight=timesensor#module-contents)
- [DateTimeSensorAsync](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/date_time/index.html#airflow.sensors.date_time.DateTimeSensorAsync)

However, this list will grow quickly as the Airflow community makes more investments into these operators. In the meantime, you can also create your own (more on this in the last section). Additionally, Astronomer maintains some deferrable operators [available only on Astronomer Runtime](https://docs.astronomer.io/cloud/deferrable-operators/#astronomers-deferrable-operators).

There are numerous benefits to using deferrable operators. Some of the most notable are:

- **Reduced Resource Consumption:** Depending on the workload, one triggerer can run hundreds of deferred tasks concurrently. This can lead to a reduction in the number of workers needed to run tasks during periods of high concurrency. With less workers needed, you are able to scale down the underlying infrastructure of your Airflow environment.
- **Resiliency Against Restarts:** Triggers are stateless by design. This means your deferred tasks will not be set to a failure state if a triggerer needs to be restarted due to a deployment or infrastructure issue. They will resume once a triggerer is up and running in your environment.
- **Paves the Way to Event-Based DAGs:** The presence of `asyncio` in core Airflow is seen as the basis for event-triggered DAGs.

## Example Workflow Using Deferrable Operators

Let's say we have a DAG that is scheduled to run a sensor every minute, and where each task can take up to 20 minutes. Using the default settings with 1 worker, we can see that after 20 minutes we have 16 tasks running, each holding a worker slot:

![Classic Tree View](https://assets2.astronomer.io/main/guides/deferrable-operators/classic_tree_view.png)

As worker slots are held during task execution time, we would need at least 20 worker slots available for this DAG to ensure future runs are not delayed. In order to increase concurrency, we would need to add additional resources to our Airflow infrastructure (e.g. another worker pod). 

With Airflow 2.2, we can leverage a deferrable operator to offload this idle work from the Workers. This will release the worker slot from sensing for job status, so it can complete other work across your Airflow environment. With our updated DAG below, we see that all 20 tasks have entered a state of deferred, indicating that the sensing jobs will now be run by triggers in the triggerer process. This process is designed to handle these types of jobs at scale, with the potential of 100's of sensing processes running concurrently on a single triggerer.

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
       pool="async",
   )

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
       pool="sync",
   )
```

## Running Deferrable Tasks in your Airflow Environment

To start a triggerer process, run `airflow triggerer` in your Airflow environment. You should see an output similar to the below image.

![Triggerer Logs](https://assets2.astronomer.io/main/guides/deferrable-operators/triggerer_logs.png)

Note that if you are using [Astronomer Cloud](https://docs.astronomer.io/cloud/deferrable-operators#prerequisites), the triggerer will be run for you automatically if you are on Astronomer Runtime 4.0+. If you are using Astronomer Enterprise, you can add a triggerer to your Airflow deployment from the deployment settings tab.

As tasks are raised into a deferred state, triggers are registered in the triggerer. You are able to set the number of concurrent triggers that can be run in a single triggerer process with the [`default_capacity`](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#triggerer) configuration setting in Airflow. This can also be set via the `AIRFLOW__TRIGGERER__DEFAULT_CAPACITY` environment variable. By default, this variable's value is `1,000`.

### High Availability

Note that triggers are designed to be highly-available. You can implement this by starting multiple triggerer processes. Similar to the [HA scheduler](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduler.html#running-more-than-one-scheduler) introduced in Airflow 2.0, Airflow ensures that they co-exist with correct locking and HA. You can reference the [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html#high-availability) for further information on this topic.

### Creating Your Own Deferrable Operator

If you have an operator that would benefit from being asynchronous but does not yet exist in OSS Airflow or Astronomer Runtime, you can create your own. The [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html#writing-deferrable-operators) have great instructions to get you started.
