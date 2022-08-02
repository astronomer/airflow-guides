---
title: "Introduction to Airflow DAGs"
description: "How to write your first DAG in Apache Airflow"
date: 2018-05-21T00:00:00.000Z
slug: "dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Airflow UI", "DAGs", "Basics"]
---

In Airflow, a DAG is a data pipeline defined in Python code. DAG stands for "directed, acyclic, graph". In that graph, each node represents a task which completes a unit of work, and each edge represents a dependency between tasks. There is no limit to what a DAG can do so long as tasks remain acyclic (tasks cannot create data that goes on to self-reference).

In this guide, we'll cover how to define a DAG in Python, DAG parameters that all users should be aware of, and how to view and monitor DAGs in the Airflow UI.

## Presumed Knowledge

To get the most out of this guide, users should have knowledge of:

- What Airflow is and when to use it
- Airflow operators

The following resources are recommended:

- [Introduction to Apache Airflow](https://www.astronomer.io/guides/intro-to-airflow)
- [Operators 101](https://www.astronomer.io/guides/what-is-an-operator)
- [Python Documentation](https://docs.python.org/3/tutorial/index.html)

## Writing a DAG

DAGs in Airflow are defined in a Python script that is placed in Airflow's `DAG_FOLDER`. Airflow will execute the code in this folder and will load any DAG objects. If you are working with the Astro CLI, DAG scripts can be placed in the `dags/` folder. 

Most DAGs will follow this general flow within a Python script:

- Imports: Any needed Python packages are imported at the top of the DAG script. This will always include a `dag` function import, and may also include provider packages or other general Python packages.
- DAG instantiation: A DAG object is created and any DAG-level parameters such as the schedule interval are set.
- Task instantiation: Each task is defined by calling an operator and providing necessary task-level parameters.
- Dependencies: Any dependencies between tasks are set using bitshift operators (`<<` and `>>`), the `set_upstream()` or `set_downstream` functions, or the `chain()` function. Note that if you are using the TaskFlow API, dependencies are inferred based on the task function calls.

For example, the following is a basic DAG that loads data from S3 to Snowflake, runs a Snowflake query, and sends an email.

```python
from airflow import DAG

from airflow.operators.email_operator import EmailOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator

from datetime import datetime, timedelta


with DAG('s3_to_snowflake',
         start_date=datetime(2020, 6, 1),
         schedule_interval='@daily',
         default_args={
            'retries': 1,
            'retry_delay': timedelta(minutes=5)
        },
         catchup=False
         ) as dag:

        load_file = S3ToSnowflakeOperator(
            task_id='load_file',
            s3_keys=['key_name.csv'],
            stage='snowflake_stage',
            table='my_table',
            schema='my_schema',
            file_format='csv',
            snowflake_conn_id='snowflake_default'
        )

        snowflake_query = SnowflakeOperator(
            task_id="run_query",
            sql='SELECT COUNT(*) FROM my_table'
        )

        send_email = EmailOperator(
            task_id='send_email',
            to='noreply@astronomer.io',
            subject='Snowflake DAG',
            html_content='<p>The Snowflake DAG completed successfully.<p>'
        )

        load_file >> snowflake_query >> send_email

```

> **Note:** The example DAG above makes use of the [Snowflake provider package](https://registry.astronomer.io/providers/snowflake). Providers are Python packages separate from core Airflow that contain hooks, operators, and sensors to integrate Airflow with third party services. The [Astronomer Registry](https://registry.astronomer.io/) is the best place to go to learn about available Airflow providers.

Astronomer recommends creating one Python file for each DAG. Some advanced use cases might require dynamically generating DAG files, which can also be accomplished using Python.

### Writing DAGs with the TaskFlow API

Since Airflow 2.0, the TaskFlow API has been available as an alternative DAG authoring experience to traditional operators like the ones shown in the previous example. With the TaskFlow API, you can define your DAG and any PythonOperator tasks using decorators. The purpose of decorators in Airflow is to simplify the DAG authoring experience by eliminating the boilerplate code. Whether to author DAGs in this way is a matter of developer preference and style. 

For example, the following DAG is generated when you initialize an Astro project:

```python
import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task

@dag(
    schedule_interval="@daily",
    start_date=datetime(2021, 1, 1),
    catchup=False,
    default_args={
        "retries": 2
    },
    tags=['example'])
def example_dag_basic():
    """
    ### Basic ETL Dag
    This is a simple ETL data pipeline example that demonstrates the use of
    the TaskFlow API using three simple tasks for extract, transform, and load.
    For more information on Airflow's TaskFlow API, reference documentation here:
    https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html
    """

    @task()
    def extract():
        """
        #### Extract task
        A simple "extract" task to get data ready for the rest of the
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'

        order_data_dict = json.loads(data_string)
        return order_data_dict

    @task(multiple_outputs=True) # multiple_outputs=True unrolls dictionaries into separate XCom values
    def transform(order_data_dict: dict):
        """
        #### Transform task
        A simple "transform" task which takes in the collection of order data and
        computes the total order value.
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple "load" task that takes in the result of the "transform" task and prints it out,
        instead of saving it to end user review
        """

        print(f"Total order value is: {total_order_value:.2f}")

    # Call the task functions to instantiate them and infer dependencies
    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])

# Call the dag function to register the DAG
example_dag_basic = example_dag_basic()
```

In the DAG above, tasks are instantiated using the `@task` decorator, and the DAG is instantiated using the `@dag` decorator. When using decorators, you must call the DAG and task functions in the same DAG file for Airflow to register them.

## DAG Parameters

## Viewing DAGs

