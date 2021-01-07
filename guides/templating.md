---
title: "Templating and Macros in Airflow"
description: "How to leverage the power of Jinja Templating when writing your DAGs."
date: 2018-05-23T00:00:00.000Z
slug: "templating"
heroImagePath: null
tags: ["Templating", "Best Practices", "Basics"]
---
<!-- markdownlint-disable-file -->
Macros are used to pass dynamic information into task instances at runtime. Since all top-level code in DAG files is interpreted every scheduler "heartbeat," macros and templating allow run-time tasks to be offloaded to the executor instead of the scheduler.  <br> <br>
Apart from efficiency, they're also powerful tools in forcing jobs to be idempotent.

## Common Macros and Templates

A list of default variables accessible in all templates can be found here: https://airflow.apache.org/code.html#macros

Common macros include:

- A timestamp for incremental ETL
- A decryption key for an external system
- Custom user defined parameters for complex operators

## Setting a Template

Templates can be set directly in the DAG file:

```python
dag = DAG('example_template_once_v2',
          schedule_interval='@once',
          default_args=default_args)


def test(**kwargs):

    first_date = kwargs.get('execution_date', None)
    next_execution_date = '{{ next_execution_date }}'

    print("NEXT EXECUTION DATE {0}".format(next_execution_date))
    print("EXECUTION DATE: {0}".format(first_date))


with dag:
    execution_date = '{{ execution_date }}' # Access execution date template
    t1 = PythonOperator(
        task_id='show_template',
        python_callable=test,
        op_args={'execution_date': execution_date},
        provide_context=True)


```

## Rendering Tasks

Since templated information is rendered at run-time, it can be helpful to see what the final inputs are for templated tasks.

From the Github to Redshift workflow we have been working with, we execute a post load transform to make reporting easier:

```python
get_individual_issue_counts = \
    """
    INSERT INTO github.issue_count_by_user
    (SELECT login, sum(count) as count, timestamp
     FROM
            ((SELECT
                m.login, count(i.id),
                cast('{{ execution_date + macros.timedelta(hours=-4) }}' as timestamp) as timestamp
            FROM github.astronomerio_issues i
            JOIN github.astronomerio_members m
            ON i.assignee_id = m.id
            WHERE i.state = 'open'
            GROUP BY m.login
            ORDER BY login)
        UNION
            (SELECT
                m.login, count(i.id),
                cast('{{ execution_date + macros.timedelta(hours=-4) }}' as timestamp) as timestamp
            FROM github.astronomerio_issues i
            JOIN github.astronomerio_members m
            ON i.assignee_id = m.id
            WHERE i.state = 'open'
            GROUP BY m.login
            ORDER BY login)
        UNION
            (SELECT
                m.login,
                count(i.id),
                cast('{{ execution_date + macros.timedelta(hours=-4) }}' as timestamp) as timestamp
            FROM github."airflow-plugins_issues" i
            JOIN github."airflow-plugins_members" m
            ON i.assignee_id = m.id
            WHERE i.state = 'open'
            GROUP BY m.login
            ORDER BY login))
    GROUP BY login, timestamp);
    """
```

Notice that the `execution_date` template and the `timedelta` macro (to make up for the time difference) is being written into the SQL. The runtime values for this task can be seen from the UI:

![task_details](https://assets.astronomer.io/website/img/guides/task_details.png)

On the *Rendered* tab

![rendered_sql](https://assets.astronomer.io/website/img/guides/rendered_sql.png)

The corresponding timestamp has been rendered into the TaskInstance.

## Using Templating for Idempotency

One of templating's best use-cases is turning tasks idempotent.

Any sort of intermediate file, timebased SQL, or anything else that has the time as an input should always be templated.

Luckily, this usually only requires changing a few lines of code:

**1) Specify the field as a `template_field` at the operator level- notice that this requires no changes to the parameters being templated.**

`https://github.com/airflow-plugins/google_analytics_plugin/blob/master/operators/google_analytics_reporting_to_s3_operator.py#L41`

```python
template_fields = ('s3_key', 'since', 'until')
```

**2) Define the corresponding values in the DAG file:**

`https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/google_analytics_to_redshift.py#L131`

```python
SINCE = "{{{{ macros.ds_add(ds, -{0}) }}}}".format(str(LOOKBACK_WINDOW))
UNTIL = "{{ ds }}"

S3_KEY = 'google_analytics/{0}/{1}_{2}_{3}.json'.format(REDSHIFT_SCHEMA,
                                                                GOOGLE_ANALYTICS_CONN_ID,
                                                                view_id,
                                                                "{{ ts_nodash }}")
```

**3) Instantiate the Operator with the right values:**

`https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/google_analytics_to_redshift.py#L136`

```python
g = GoogleAnalyticsReportingToS3Operator(task_id='get_google_analytics_data',
                                                 google_analytics_conn_id=GOOGLE_ANALYTICS_CONN_ID,
                                                 view_id=view_id,
                                                 since=SINCE,
                                                 until=UNTIL,
                                                 sampling_level=SAMPLING_LEVEL,
                                                 dimensions=DIMENSIONS,
                                                 metrics=METRICS,
                                                 page_size=PAGE_SIZE,
                                                 include_empty_rows=INCLUDE_EMPTY_ROWS,
                                                 s3_conn_id=S3_CONN_ID,
                                                 s3_bucket=S3_BUCKET,
                                                 s3_key=S3_KEY
                                                 )
```

## Schedule Based Templates

Since macros are rendered at runtime, a DAG's `schedule_interval` should be taken into account when testing and deploying DAGs.

Consider the following DAG:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 5, 26),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('example_template_once_v2',
          schedule_interval='@once',
          default_args=default_args)


def test(**kwargs):

    first_date = kwargs.get('execution_date', None)
    next_execution_date = '{{ next_execution_date }}'

    print("NEXT EXECUTION DATE {0}".format(next_execution_date))
    print("EXECUTION DATE: {0}".format(first_date))


with dag:
    execution_date = '{{ execution_date }}'
    t1 = PythonOperator(
        task_id='show_template',
        python_callable=test,
        template_dict={'execution_date': execution_date},
        provide_context=True)

```

**What would the output value be?**
