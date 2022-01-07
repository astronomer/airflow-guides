---
title: "Introduction to Airflow Decorators"
description: "An overview of Airflow decorators and how they can improve the DAG authoring experience."
date: 2021-12-27T00:00:00.000Z
slug: "airflow-decorators"
heroImagePath: null
tags: ["DAGs", "Basics", "astro"]
---

## Overview

Since Airflow 2.0, decorators have been available for some functions as an alternative DAG authoring experience to traditional operators. In Python, [decorators](https://realpython.com/primer-on-python-decorators/) are functions that take another function as an argument and extend the behavior of that function. In the context of Airflow, decorators provide a simpler, cleaner way to define your tasks and DAG. 

In this guide, we'll cover the benefit of decorators, the decorators available in Airflow, and decorators provided in Astronomer's open source `astro` library. We'll also show examples throughout and address common questions about when to use decorators and how to combine them with traditional operators in a DAG.

## When and Why To Use Decorators

The purpose of decorators in Airflow is to simplify the DAG authoring experience by eliminating the boilerplate code required by traditional operators. The result can be cleaner DAG files that are more concise and easier to read. Currently, decorators can be used for Python and SQL functions.

In general, whether to use decorators is a matter of developer preference and style. Generally, a decorator and the corresponding traditional operator will have the same functionality. One exception to this is the `astro` library of decorators (more on these below), which do not have equivalent traditional operators. You can also easily mix decorators and traditional operators within your DAG if your use case requires that.

## How to Use Airflow Decorators

Airflow decorators were introduced as part of the TaskFlow API, which also handles passing data between tasks using XCom and inferring task dependencies automatically. To learn more about the TaskFlow API, check out [Astronomer's webinar](https://www.astronomer.io/events/webinars/taskflow-api-airflow-2.0) or the Apache Airflow [TaskFlow API tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html#tutorial-on-the-taskflow-api). 

Using decorators to define your Python functions as tasks is easy. Let's take a before and after example. In the "traditional" DAG below, we have a basic ETL flow where we have tasks to get data from an API, process the data, and store it.

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from datetime import datetime
import json
from typing import Dict
import requests
import logging

API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

def _extract_bitcoin_price():
    return requests.get(API).json()['bitcoin']

def _process_data(ti):
    response = ti.xcom_pull(task_ids='extract_bitcoin_price')
    logging.info(response)
    processed_data = {'usd': response['usd'], 'change': response['usd_24h_change']}
    ti.xcom_push(key='processed_data', value=processed_data)

def _store_data(ti):
    data = ti.xcom_pull(task_ids='process_data', key='processed_data')
    logging.info(f"Store: {data['usd']} with change {data['change']}")

with DAG('classic_dag', schedule_interval='@daily', start_date=datetime(2021, 12, 1), catchup=False) as dag:
    
    extract_bitcoin_price = PythonOperator(
        task_id='extract_bitcoin_price',
        python_callable=_extract_bitcoin_price
    )

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=_process_data
    )

    store_data = PythonOperator(
        task_id='store_data',
        python_callable=_store_data
    )

    extract_bitcoin_price >> process_data >> store_data
```

We can now rewrite this DAG using decorators, which will eliminate the need to explicitly instantiate `PythonOperators`. 

```python
from airflow.decorators import dag, task

from datetime import datetime
from typing import Dict
import requests
import logging

API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"


@dag(schedule_interval='@daily', start_date=datetime(2021, 12, 1), catchup=False)
def taskflow():

    @task(task_id='extract', retries=2)
    def extract_bitcoin_price() -> Dict[str, float]:
        return requests.get(API).json()['bitcoin']

    @task(multiple_outputs=True)
    def process_data(response: Dict[str, float]) -> Dict[str, float]:
        logging.info(response)
        return {'usd': response['usd'], 'change': response['usd_24h_change']}

    @task
    def store_data(data: Dict[str, float]):
        logging.info(f"Store: {data['usd']} with change {data['change']}")

    store_data(process_data(extract_bitcoin_price()))

dag = taskflow()
```

The resulting DAG has much less code and is easier to read. Notice that it also doesn't require using `ti.xcom_pull` and `ti.xcom_push` to pass data between tasks. This is all handled by the TaskFlow API when we define our task dependencies with `store_data(process_data(extract_bitcoin_price()))`. 

Here are some other things to keep in mind when using decorators:

- For any decorated object in your DAG file, you must call them so that Airflow can register the task or DAG (e.g. `dag = taskflow()`).
- When you define a task, the `task_id` will default to the name of the function you decorated. If you want to change that, you can simply pass a `task_id` to the decorator as we do in the `extract` task above. Similarly, other task level parameters such as retries or pools can be defined within the decorator (see the example with `retries` above).
- You can decorate a function that is imported from another file with something like the following:

    ```python
    from include.my_file import my_function

    @task
    def taskflow_func():
        my_function()
    ```
    
    This is recommended in cases where you have lengthy Python functions since it will make your DAG file easier to read. 

### Mixing Decorators with Traditional Operators

If you have a DAG that uses `PythonOperator` and other operators that don't have decorators, you can easily combine decorated functions and traditional operators in the same DAG. For example, we can add an `EmailOperator` to the previous example by updating our code to the following:

```python
from airflow.decorators import dag, task
from airflow.operators.email_operator import EmailOperator

from datetime import datetime
from typing import Dict
import requests
import logging

API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

@dag(schedule_interval='@daily', start_date=datetime(2021, 12, 1), catchup=False)
def taskflow():

    @task(task_id='extract', retries=2)
    def extract_bitcoin_price() -> Dict[str, float]:
        return requests.get(API).json()['bitcoin']

    @task(multiple_outputs=True)
    def process_data(response: Dict[str, float]) -> Dict[str, float]:
        logging.info(response)
        return {'usd': response['usd'], 'change': response['usd_24h_change']}

    @task
    def store_data(data: Dict[str, float]):
        logging.info(f"Store: {data['usd']} with change {data['change']}")

    email_notification = EmailOperator(
        task_id='email_notification',
        to='noreply@astronomer.io',
        subject='dag completed',
        html_content='the dag has finished'
    )

    store_data(process_data(extract_bitcoin_price())) >> email_notification

dag = taskflow()
```

Note that when adding traditional operators, dependencies are still defined using bitshift operators.

## Astro Project Decorators

The [`astro` library](https://github.com/astro-projects/astro) provides decorators and modules that allow data engineers to think in terms of data transformations rather than Airflow concepts when writing DAGs. The goal is to allow DAG writers to focus on defining *execution* logic without having to worry about orchestration logic.

The library contains SQL and dataframe decorators that greatly simplify your DAG code and allow you to directly define tasks without boilerplate operator code. It also allows you to transition seamlessly between SQL and Python for transformations without having to explicitly pass data between tasks or convert the results of queries to dataframes and vice versa. For a full description of functionality, check out the [repo Readme](https://github.com/astro-projects/astro).

To use the `astro` library, you need to install the `astro-projects` package in your Airflow environment and enable pickling (`AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True`). 

To show `astro` in action, we'll use a simple ETL example. We have data on adoptions from two different animal shelters that we need to aggregate, clean, transform, and append to a reporting table. Some of these tasks are better suited to SQL, and some to Python, but we can easily combine both using `astro` functions. The DAG looks like this:

```python
from airflow.decorators import dag
from astro.sql import transform, append
from astro.sql.table import Table
from astro import dataframe

from datetime import datetime, timedelta
import pandas as pd

SNOWFLAKE_CONN = "snowflake"
SCHEMA = "example_schema"

# Start by selecting data from two source tables in Snowflake
@transform
def combine_data(center_1: Table, center_2: Table):
    return """
    SELECT * FROM {center_1}
    UNION 
    SELECT * FROM {center_2}
    """

# Clean data using SQL
@transform
def clean_data(input_table: Table):
    return '''
    SELECT * 
    FROM {input_table} 
    WHERE TYPE NOT LIKE 'Guinea Pig'
    '''

# Switch to Pandas for pivoting transformation
@dataframe
def aggregate_data(df: pd.DataFrame):
    adoption_reporting_dataframe = df.pivot_table(index='DATE', 
                                                values='NAME', 
                                                columns=['TYPE'], 
                                                aggfunc='count').reset_index()
    return adoption_reporting_dataframe


@dag(start_date=datetime(2021, 1, 1),
    max_active_runs=1,
    schedule_interval='@daily', 
    default_args={
        'email_on_failure': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=5)
    },
    catchup=False
    )
def animal_adoptions_etl():
    # Define task dependencies
    combined_data = combine_data(center_1=Table('ADOPTION_CENTER_1', conn_id=SNOWFLAKE_CONN, schema=SCHEMA),
                                        center_2=Table('ADOPTION_CENTER_2', conn_id=SNOWFLAKE_CONN, schema=SCHEMA))

    cleaned_data = clean_data(combined_data)
    aggregated_data = aggregate_data(cleaned_data,
                                    output_table=Table('aggregated_adoptions', conn_id=SNOWFLAKE_CONN))
    
    # Append transformed data to reporting table
    reporting_data = append(
        conn_id=SNOWFLAKE_CONN,
        append_table="aggregated_adoptions",
        columns=["DATE", "CAT", "DOG"],
        main_table=SCHEMA+".adoption_reporting",
    )

    aggregated_data >> reporting_data

animal_adoptions_etl_dag = animal_adoptions_etl()
```

![Astro ETL](https://assets2.astronomer.io/main/guides/decorators/astro_etl_graph.png)

The general steps in the DAG are:

1. Combine data from our two source tables. We use a `transform()` function since we are running a SQL statement on tables that already exist in our database. We define the source tables with the `Table()` parameter when we call the function (`center_1=Table('ADOPTION_CENTER_1', conn_id="snowflake", schema='SANDBOX_KENTEND')`).
2. Run another `transform()` function to clean the data; we don't report on guinea pig adoptions in this example, so we remove them from the dataset. Note that each `transform` function will store results in a table in your database. You can specify an `output_table` to store the results in a specific table, or you can let `astro` create a table in a default temporary schema for you by not defining any output.
3. Transform the data by pivoting using Python. Pivoting is notoriously difficult in Snowflake, so we seamlessly switch to Pandas. In this task we specify an `output_table` that we want the results stored in.
4. Append the results to an existing reporting table using the `append` function. 

Note that by simply defining our task dependencies when calling the functions (e.g. `cleaned_data = clean_data(combined_data)`), `astro` takes care of passing all context and metadata between the tasks. The result is a DAG where we accomplished some tricky transformations without having to write a lot of Airflow code or transition between SQL and Python.

## List of Available Airflow Decorators

There are a limited number of decorators available to use with Airflow, although more will be added in the future. This list provides a reference of what is currently available so you don't have to dig through source code:

- `astro` project [SQL and dataframe decorators](https://github.com/astro-projects/astro)
- DAG decorator (`@dag()`)
- Task decorator (`@task()`), which creates a Python task
- Python Virtual Env decorator (`@task.virtualenv()`), which runs your Python task in a virtual environment
- Docker decorator (`@task.docker()`), which creates a `DockerOperator` task
- TaskGroup decorator (`@task_group()`)

As of Airflow 2.2, you can also [create your own custom task decorator](https://airflow.apache.org/docs/apache-airflow/stable/howto/create-custom-decorator.html).
