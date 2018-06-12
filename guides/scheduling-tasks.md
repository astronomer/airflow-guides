---
title: "Scheduling Tasks with Airflow"
description: "Overview of the Airflow scheduler"
date: 2018-05-21T00:00:00.000Z
slug: "scheduling-tasks"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/SchedulingTasksinAirflow_preview.png"
tags: ["Building DAGs", "Scheduling Tasks", "Airflow"]
---

The Airflow scheduler monitors all tasks and all DAGs to ensure that everything is executed according to schedule. The Airflow scheduler, the heart of the application, "heartbeats" the DAGs folder every couple of seconds to inspect tasks for whether or not they can be triggered.

However, actually scheduling these task can be tricky, as much of it is driven by cron syntax and the scheduler tends to "schedule everything".

## Dag Runs

A DAG Run is an object representing an instantiation **of the DAG in time**.

Each DAG may or may not have a schedule, which informs how DAG Runs are created. schedule_interval is defined as a DAG arguments, and receives a cron expression as a `str`, or a `datetime.timedelta` object.

Alternatively, you can also use one of these cron “preset”:
https://airflow.apache.org/scheduler.html

## Key Scheduling Parameters

A DAG's schedule is defined by:

**start_date**: This is the `execution_date` for the first DAG run.

**end_date**: The date the DAG should stop running, usually set as none.

**execution_timeout**: The maximum time a task should be able to run - the task will fail if it runs for more than this time.

**retries**: The number of retries performed before the task fails

**retry_delay**: The delay between retries.

## Scheduling When Testing

Suppose you are testing a DAG on **4/30/18** that should be scheduled to run daily going forward:

```py
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

When the scheduler taps this DAG, it will generate a DAG run for each day from the `start_date` to 4/30/18, and then for each day going forward:

![](https://cdn.astronomer.io/website/img/guides/ucg_scheduling.png)

In this example DAG it won't really cause many problems, but if this DAG were hitting an external system (e.g. making API calls, querying a database, etc.) it could get problematic.

**Note**: Based on your Airflow configurations, it will only generate a DAG few runs at a time.

This can be avoided by setting `catchup=False` (by default, it is set to `True`), which tells the scheduler not to have the DAG runs "catch up" to the current date.

https://airflow.apache.org/scheduler.html#backfill-and-catchup

```py
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

![](https://cdn.astronomer.io/website/img/guides/ucg_scheduling_catchup.png)

### Using catchup effectively

The `catchup` parameter can be dangerous (use up all your API calls, put a large load on your database,  etc.), but it can also be used effectively.

Suppose you are backfilling data from the last year (or a set of ranges) from Google Analytics or from some external source into a data warehouse.

Instead of running one big API call, `catchup=True` along with a `schedule_interval` set to `'@daily'` will have Airflow schedule them separately into daily API calls.

With the right file templating - you can get each day's file in a separate fille:

```py
"""
This is an excerpt from an internal Google Analytics dag

It will generate a separate API request, file in S3, and load into redshift
(the data will be appended for each table for each day) for each day's request
from the start_date until today's date.

This way, if you find yourself needing to load the data into another table, you can just
run the load tasks instead of making the entire request again.
"""

execution_date = '{{ execution_date }}'
next_execution_date = '{{ next_execution_date }}'

view_id = '120725274'  # External Traffic
# view_id = '120726983' # Desktop


COPY_PARAMS = ["COMPUPDATE OFF",
               "STATUPDATE OFF",
               "JSON 'auto'",
               "TIMEFORMAT 'auto'"
               "TRUNCATECOLUMNS",
               "region as 'us-east-1'"]

...

default_args = {
    'start_date': datetime(2018, 4, 24),
    'email': ['viraj@astronomer.io'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(
    'a_core_reporting_test_v4',
    schedule_interval='@daily',
    default_args=default_args,
    catchup=True #Set catchup to True
)
with dag:

    start = DummyOperator(task_id='start')
    for pipeline in pipelines:
        google_analytics = GoogleAnalyticsReportingToS3Operator(
            task_id='ga_reporting_{endpoint}_to_s3'.format(
                endpoint=pipeline['name']),
            google_analytics_conn_id=google_analytics_conn_id,
            view_id=view_id,
            since=execution_date,
            until=next_execution_date,
            sampling_level='LARGE',
            filters=pipeline['filtersExpression'],
            dimensions=pipeline['dimensions'],
            metrics=pipeline['metrics'],
            page_size=5000,
            include_empty_rows=True,
            s3_conn_id=s3_conn_id,
            s3_bucket=s3_bucket,
            s3_key='ga_reporting_{endpoint}_{time_string}'.format(
                endpoint=pipeline['name'], time_string=time_string)
        )

        s3_to_redshift = S3ToRedshiftOperator(
            task_id='ga_reporting_{endpoint}_to_redshift'.format(
                endpoint=pipeline['name']),
            redshift_conn_id=redshift_conn_id,
            redshift_schema='ucg_test_google_analytics',
            table='{0}'.format(pipeline['name']),
            s3_conn_id=s3_conn_id,
            s3_bucket=s3_bucket,
            s3_key='ga_reporting_{endpoint}_{time_string}'.format(
                endpoint=pipeline['name'], time_string=time_string),
            copy_params=COPY_PARAMS,
            origin_schema=pipeline['schema'],
            schema_location='local',
            # Set the load_type to  append!
            load_type='append')


        start >> google_analytics >> s3_to_redshift
```        

![](https://cdn.astronomer.io/website/img/guides/ucg_ga_ga_scheduled.png)

**Note:** Your GA service account may only be bound to a limited number of concurrent connections.

Deploying a DAG with `catchup=True` can fit a use case, but consider using additional scheduling paramters for added safety.

`depends_on_past`: When set to `True`, task instance will run chronologically sequentially, relying on the previously scheduled task instance to suceed before executing.

This will ensure sequential data loads, but may also stop progress if a job is left to run unmonitored.

`wait_for_downstream`: A stronger version of `depends_on_past` that is extended to a DAG level instead of a task level. The entire DAG will need to run successfully for the next DAG run to start.
