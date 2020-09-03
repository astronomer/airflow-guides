---
title: "Scheduling Tasks in Airflow"
description: "Overview of the Airflow scheduler"
date: 2018-05-21T00:00:00.000Z
slug: "scheduling-tasks"
heroImagePath: "https://assets.astronomer.io/website/img/guides/SchedulingTasksinAirflow_preview.png"
tags: ["Building DAGs", "Scheduling Tasks", "Airflow"]
---

# Scheduling Tasks

The Airflow scheduler monitors all tasks and all DAGs to ensure that everything is executed according to schedule. The Airflow scheduler, the heart of the application, "heartbeats" the DAGs folder at a configurable interval to inspect tasks for whether or not they can be triggered.

However, actually scheduling these task can be tricky, as much of it is driven by cron syntax and the way it handles time periods is not always intuitive.

## Dag Runs

A DagRun is an object representing an instantiation **of the DAG in time**.

Each DAG may or may not have a schedule, which informs how DAG Runs are created. schedule_interval is defined as a DAG arguments, and receives a cron expression as a `str`, or a `datetime.timedelta` object.

Alternatively, you can also use one of these cron “preset”:
https://airflow.apache.org/scheduler.html

## Scheduling Parameters

A DAG's schedule is defined by a few key things:

**dag_id**: The `id` of the DAG and the unique identifier.

**start_date**: This is the `execution_date` for the first DAG run.

**end_date**: The date the DAG should stop running, usually set as none. If you do not include an end_date, the DAG will run until turned off.

Some other helpful parameters include:

**execution_timeout**: The maximum time a task should be able to run - the task will fail if it runs for more than this time.

**retries**: The number of retries performed before the task fails

**retry_delay**: The delay between retries.

A full list of parameters can be found at:
https://airflow.readthedocs.io/en/stable/_modules/airflow/models.html#DAG


## Schedule Intervals

### Execution Date

If you run a DAG on a schedule_interval of one day (`@daily`), the run stamped 2018-01-01 will be trigger soon after 2018-01-01T23:59. In other words, the job instance is started once the period it covers has ended.

The scheduler runs your DAG one schedule_interval AFTER the start date, at the END of the period.This is based on the idea that the data for a certain period does not arrive until the **END** of the period.

Suppose you are testing a DAG on **4/30/18** that should be scheduled to run daily going forward:


```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('example_dag_one',
            schedule_interval='@daily',
            default_args=default_args)

t1 = BashOperator(
    task_id='print_date1',
    bash_command='sleep 2m',
    dag=dag)

t2 = BashOperator(
    task_id='print_date2',
    bash_command='sleep 2m',
    dag=dag)

t3 = BashOperator(
    task_id='print_date3',
    bash_command='sleep 2m',
    dag=dag)

t2.set_upstream(t1)
t3.set_upstream(t2)
```

When the scheduler taps this DAG, it will generate a DAG run for each day from the `start_date` to 4/30/18, and then for each day going forward up until the current day:

![scheduling_ex](https://assets.astronomer.io/website/img/guides/ucg_scheduling.png)

In this example DAG it won't really cause many problems, but if this DAG were hitting an external system (e.g. making API calls, querying a database, etc.) it could get problematic.


**Note**: Based on your Airflow configurations, it will only generate a DAG few runs at a time.

This can be avoided by setting `catchup=False` (by default, it is set to `True`), which tells the scheduler not to have the DAG runs "catch up" to the current date.

**Note:** `catchup` can be set to `False` by default in airflow.cfg

https://airflow.apache.org/scheduler.html#backfill-and-catchup


```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2018, 1, 1),
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retry_delay': timedelta(minutes=5),
}

dag = DAG('example_dag_one',
            schedule_interval='@daily',
            catchup=False,
            default_args=default_args)

t1 = BashOperator(
    task_id='print_date1',
    bash_command='sleep 2m',
    dag=dag)

t2 = BashOperator(
    task_id='print_date2',
    bash_command='sleep 2m',
    dag=dag)

t3 = BashOperator(
    task_id='print_date3',
    bash_command='sleep 2m',
    dag=dag)

t2.set_upstream(t1)
t3.set_upstream(t2)
```

This DAG only gets one DAG run scheduled once on 4/30 due to the catchup parameter:

![once_scheduled](https://assets.astronomer.io/website/img/guides/ucg_scheduling_catchup.png)

### Using catchup effectively

The `catchup` parameter can be dangerous (use up all your API calls, put a large load on your database,  etc.), but it can also be used effectively.

Suppose you are backfilling data from the last year (or a set of ranges) from Google Analytics or from some external source into a data warehouse.

Instead of running one big API call, `catchup=True` along with a `schedule_interval` set to `'@daily'` will have Airflow schedule them separately into daily API calls.

### Use additional parameters when scheduling catchups

Deploying a DAG with **`catchup=True`** can fit a use case, but consider using additional scheduling parameters for added safety.

**`depends_on_past`**: When set to `True`, task instance will run chronologically sequentially, relying on the previously scheduled task instance to suceed before executing.

This will ensure sequential data loads, but may also stop progress if a job is left to run unmonitored.

**`wait_for_downstream`**: A stronger version of `depends_on_past` that is extended to a DAG level instead of a task level. The entire DAG will need to run successfully for the next DAG run to start.

###  LatestOnlyOperator
_Additional safety._

The [LatestOnlyOperator](https://airflow.apache.org/concepts.html#latest-run-only) can explicity accomplish the same functionality as some of the scheduling parameters (assuming default `trigger_rules`). The `LatestOnlyOperator` skips all tasks that are not for the most recent DagRun.

This can be helpful for tasks that are naturally idempotent or can be run independently of time (i.e. no time based input).

**Consider:**


```python
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False,
}

dag = DAG('latest_only_example',
          schedule_interval='@daily',
          default_args=default_args)
with dag:

    l_o = LatestOnlyOperator(task_id='latest_only')

    for i in range(0, 3):
        t1 = BashOperator(
            task_id='print_date_{0}'.format(i),
            bash_command='sleep 2m',
            dag=dag)
        l_o >> t1
```

All tasks downstream of the LatestOnlyOperator are skipped on all DagRuns _past_ DagRuns.

![latest_only_example](https://assets.astronomer.io/website/img/guides/latest_only_scheduling.png)
At the task level, skipped downstream tasks:
![latest_only_detail](https://assets.astronomer.io/website/img/guides/skipped_latest_only.png)
