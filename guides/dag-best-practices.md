---
title: "DAG Writing Best Practices in Apache Airflow"
description: "How to create effective, clean, and functional DAGs."
date: 2018-05-21T00:00:00.000Z
slug: "dag-best-practices"
heroImagePath: "https://assets.astronomer.io/website/img/guides/bestwritingpractices.png"
tags: ["DAGs", "Best Practices", "Basics", "Templating", "Tasks"]
---

Writing Airflow DAGs is typically a pretty easy skill to pick up if you know a little bit of Python; you just need to instantiate your DAG and your operators and you're off and running. However, writing optimized DAGs that make the most of Airflow can sometimes feel like more of an art than a science. In this guide, we'll cover some best practices when writing DAGs that will help ensure your pipelines are efficient and sustainable.

In general, most of the best practices we cover here fall into two categories: DAG design, and using Airflow as an orchestrator. For an in-depth walk through and examples of some of the concepts covered here, check out our DAG writing best practices [webinar recording](https://www.astronomer.io/blog/dag-writing-best-practices-in-apache-airflow), and our [Github repo](https://github.com/astronomer/webinar-dag-writing-best-practices) with good and bad example DAGs.


## Idempotency

Before we jump into best practices specific to Airflow, we'll call out one, idempotency, which applies to all data pipelines. Idempotency is very important, and you may notice that other best practices in this guide are in part to support this one.

[Idempotency]((https://en.wikipedia.org/wiki/Idempotence)) is the concept whereby an operation can be repeated multiple times without changing the result. A common example is a crosswalk button; no matter how many times you push the button, you're going to get the same result. With a DAG, this translates to the same DAG, if run multiple times, will generate the same results. Applying this concept will make recovery from any failures in your DAGs easier, and ensure data loss is prevented.

## DAG Design

The first category of best practices specific to Airflow relate to DAG design. These are practices that will help ensure your DAGs are idempotent, efficient, and readable.

### Keep Tasks Atomic

When breaking up your pipeline into individual tasks, ideally each task should be atomic. This means each task should be responsible for one operation that can be re-run independently of the others, which supports idempotency.

### Use Template Fields, Variables, and Macros

Using templated fields in Airflow allows for the field to be set using environment variables and jinja templating. Doing so helps keep your DAGs idempotent, and ensures you aren't executing functions on every scheduler heartbeat (see the section below on avoiding top level code for more about this).

For example, if your DAG needs to be date parameterized you should use an Airflow date variable rather than a Python function that determines the date.

```python
# Variables used by tasks
# Bad example - Define today's and yesterday's date using datetime module
today = datetime.today()
yesterday = datetime.today() - timedelta(1)
```

The example above creates date variables that can be used by tasks by calling `datetime` package functions. If this code is in the DAG file, these functions will be executed on every scheduler heartbeat, which may not be performant. Even more importantly, this doesn't produce an idempotent DAG; if you needed to rerun a previously failed DAG Run for a past date, you wouldn't be able to do so with this implementation because the date variable is relative to the actual date, not the DAG execution date. 

A better way of implementing is using an Airflow variable:

```python
# Variables used by tasks
# Good example - Define yesterday's date with an Airflow variable
yesterday = {{ yesterday_ds_nodash }}
```

Airflow has many built in [variables and macros](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html) that can easily be used, or you can create your own templated field to pass in information at runtime. For more on this topic check out our guide on [templating and macros in Airflow](https://www.astronomer.io/guides/templating).


### Incremental Record Filtering

Wherever possible, it is ideal to break out your pipelines into incremental extracts and loads. For example, if you have a DAG that runs hourly, each DAG Run should process only records from that hour, rather than the whole dataset. This results in each DAG Run representing only a small subset of your total dataset, which means that a failure in one subset of the data won't prevent the rest of your DAG Runs from completing successfully, and you can rerun the DAG for only the data that failed rather than reprocessing the entire dataset. This contributes to keeping your DAGs idempotent.

There are multiple ways you can achieve incremental pipelines. The two best and most common methods are described below.

#### Last Modified Date

Using a last modified date is the gold standard for incremental loads. Ideally, each record in your source system has a column containing the last time the record was modified. Every DAG Run then looks for records that were updated within its specified date parameters.

For example, with a DAG that runs hourly, each DAG Run will be responsible for loading any records that fall between the start and end of its hour. If any of those runs fail, it will not impact other runs.

#### Sequence IDs

When a last modified date is not available, a sequence or incrementing ID can be used for incremental loads. This logic works best when the source records are only being appended to and never updated. If the source records are updated you should seek to implement a last modified date in that source system and key your logic off of that. In the case of the source system not being updated, basing your incremental logic off of a sequence ID can be a sound way to filter pipeline records without a last modified date.


### Avoid Top Level Code in Your DAG File

In the case of an Airflow DAG, we use "top level code" to mean any code that isn't part of your DAG or operator instantiations. 

Airflow executes all code in the `DAGS_Folder` on every scheduler heartbeat, so from a technical perspective even a small amount of top level code can cause performance issues. You especially don't want top level code that is making requests to external systems, like an API or a database, or any function calls outside of your tasks. Additionally, lots of top level code in your DAG files makes them harder to read, maintain, update, and debug.

Try to treat your DAG file like a config file and leave all the heavy lifting for hooks and operators. If your DAGs need to access additional code such as a SQL script or a Python function, keep that code in a separate file that can be read into your DAG.

For example, if you have a `PostgresOperator` that is executing a SQL query, you don't want to put that query directly into your DAG file like this:

```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

#Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

#Instantiate DAG
with DAG('bad_practices_dag_1',
         start_date=datetime(2021, 1, 1),
         max_active_runs=3,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:

    t0 = DummyOperator(task_id='start')  

    #Bad example with top level SQL code in the DAG file
    query_1 = PostgresOperator(
        task_id='covid_query_wa',
        postgres_conn_id='postgres_default',
        sql='''with yesterday_covid_data as (
                SELECT *
                FROM covid_state_data
                WHERE date = {{ params.today }}
                AND state = 'WA'
            ),
            today_covid_data as (
                SELECT *
                FROM covid_state_data
                WHERE date = {{ params.yesterday }}
                AND state = 'WA'
            ),
            two_day_rolling_avg as (
                SELECT AVG(a.state, b.state) as two_day_avg
                FROM yesterday_covid_data a
                JOIN yesterday_covid_data b 
                ON a.state = b.state
            )
            SELECT a.state, b.state, c.two_day_avg
            FROM yesterday_covid_data a
            JOIN today_covid_data b
            ON a.state=b.state
            JOIN two_day_rolling_avg c
            ON a.state=b.two_day_avg;''',
            params={'today': today, 'yesterday':yesterday}
    )
```

Instead, you would want to keep that SQL code in a separate file (`covid_state_query.sql` below), and call it into your DAG like this:

```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

#Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

#Instantiate DAG
with DAG('good_practices_dag_1',
         start_date=datetime(2021, 1, 1),
         max_active_runs=3,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False,
         template_searchpath='/usr/local/airflow/include' #include path to look for external files
         ) as dag:

        query = PostgresOperator(
            task_id='covid_query_{0}'.format(state),
            postgres_conn_id='postgres_default',
            sql='covid_state_query.sql', #reference query kept in separate file
            params={'state': "'" + state + "'"}
        )
```

### Use a Consistent Method for Task Dependencies

In Airflow, task dependencies can be set multiple ways. You can use `set_upstream()` and `set_downstream()` functions, or use `<<` or `>>` operators. Which method you use is a matter of personal preference, but for readability it's best practice to choose a consistent method.

For example, instead of mixing methods like this:

```python
task_1.set_downstream(task_2)
task_3.set_upstream(task_2)
task_3 >> task_4
```

Try to be consistent with something like this:

```python
task_1 >> task_2 >> [task_3, task_4]
```


## Use Airflow as an Orchestrator

The next category of best practices is to use Airflow as an orchestrator; this will allow you to make the most of Airflow as it was designed, and ensure it can scale to meet your needs. Sticking to the following best practices will help ensure you don't experience common pitfalls using Airflow as the right tool for the wrong job.

### Make Use of Provider Packages

A good way to ensure you're using Airflow as it was designed is to make use of [provider packages](https://airflow.apache.org/docs/apache-airflow-providers/) to orchestrate jobs with other tools. One of the best things about Airflow is its robust and active community, which has resulted in many integrations between Airflow and other tools in the data ecosystem. Wherever possible, it's best practice to make use of these existing integrations. This allows for easier Airflow adoption for teams that may already be using existing tools, and means you have to write less code since many existing hooks and operators have taken care of that for you.

For easy discovery of all the great provider packages out there, check out the [Astronomer Registry](https://registry.astronomer.io/).

### Don't Use Airflow as a Processing Framework

Airflow was not designed to be a processing framework. Since DAGs are written in Python, you have the power of Python behind you and it can be tempting to make use of data processing libraries like Pandas. However, processing large amounts of data within your Airflow tasks will not scale well, and should only be used in cases where the data are limited in size. A better option for scalability is to offload any heavy duty processing to a framework like [Apache Spark](https://spark.apache.org/), and use Airflow to orchestrate those jobs.

If you must process small data within Airflow, we would recommend the following:

- Ensure your Airflow infrastructure has the necessary resources.
- Use the Kubernetes Executor to isolate task processing and have more control over resources at the task level.
- Use a [custom XCom backend](https://www.astronomer.io/guides/custom-xcom-backends) if you need to pass any data between the tasks so you don't overload your metadata database.

### Use Intermediary Data Storage

It can be tempting to write your DAGs so that they move data directly from your source to destination. It usually makes for less code and involves fewer pieces, but doing so removes your ability to re-run just the extract or load portion of the pipeline individually. By putting an intermediary storage layer such as S3 or SQL Staging tables in between your source and destination, you can separate the testing and re-running of the extract and load.

Depending on your data retention policy, you could modify the load logic and re-run the entire historical pipeline without having to re-run the extracts. This is also useful in situations where you no longer have access to the source system (e.g. hit an API limit).

### Use an ELT Framework

Whenever possible, look to implement an ELT (extract, load, transform) data pipeline pattern with your DAGs. This means that you should look to offload as much of the transformation logic to the source systems or the destinations systems as possible, and is one way of ensuring you aren't using Airflow as your processing framework. Many modern data warehouse tools, such as [Snowflake](https://www.snowflake.com/), give you easy to access to compute to support the ELT framework, and are easily used in conjunction with Airflow.


## Other Best Practices

Finally, here are a few other noteworthy best practices that don't fall under the two categories above.

### Use a Consistent File Structure

Having a consistent file structure for Airflow projects can help keep things organized and easy to adopt when working with Airflow both within teams and across teams. At Astronomer, we use:

```bash
├── dags/ # Where your DAGs go
│   ├── example-dag.py # An example dag that comes with the initialized project
├── Dockerfile # For Astronomer's Docker image and runtime overrides
├── include/ # For any other files you'd like to include
├── plugins/ # For any custom or community Airflow plugins
├── packages.txt # For OS-level packages
└── requirements.txt # For any Python packages

```

### Use DAG Name and Start Date Properly

You should always use a static `start_date` with your DAGs. A dynamic start_date is misleading, and can cause failures when clearing out failed task instances and missing DAG runs.

Additionally, if you change the `start_date` of your DAG you should also change the DAG name. Changing the `start_date` of a DAG creates a new entry in Airflow's database, which could confuse the scheduler because there will be two DAGs with the same name but different schedules.

Changing the name of a DAG also creates a new entry in the database, which powers the dashboard, so follow a consistent naming convention since changing a DAG's name doesn't delete the entry in the database for the old name.

### Set Retries at the DAG Level

Even if your code is perfect, failures happen. In a distributed environment where task containers are executed on shared hosts, it's possible for tasks to be killed off unexpectedly. When this happens you may see Airflow's logs mention a [zombie process]((https://en.wikipedia.org/wiki/Zombie_process)).

Issues like this can be resolved by using task retries. Best practice is to set retries as a `default_arg` so they are applied at the DAG level, and get more granular for specific tasks only where necessary. A good range to try is ~2–4 retries.
