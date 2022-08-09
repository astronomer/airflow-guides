---
title: "The Astro Python SDK for ETL"
description: "Using the Astro Python SDK to implement ETL use cases in Airflow."
date: 2022-01-10T00:00:00.000Z
slug: "astro-python-sdk-etl"
heroImagePath: null
tags: ["Astro", "ETL", "SQL"]
---

The [Astro Python SDK](https://github.com/astro-projects/astro) is an open source Python package maintained by Astronomer that provides tools to improve the DAG authoring experience for Airflow users. The available decorators and functions allow you to write DAGs based on how you want your data to move by simplifying the data transformation process between different environments.

In this guide, we’ll demonstrate how you can use the Astro Python SDK functions for ETL use cases. The resulting DAGs will be easier to write and read, and require less code.

## Astro Python SDK ETL Functionality

The Astro Python SDK makes implementing ETL use cases easier by allowing you to seamlessly transition between Python and SQL for each step in your process. Details like creating dataframes, storing intermediate results, passing context and data between tasks, and creating Airflow task dependencies are all managed automatically. This means that you can focus solely on writing execution logic in whichever language you need without having to worry about Airflow orchestration logic.

More specifically, the Astro Python SDK has the following functions that are helpful when implementing an ETL framework (for a full list of functions and documentation, check out the [Readme](https://github.com/astronomer/astro-sdk)):

- `load_file`: If the data you’re starting with is in CSV or parquet files (stored locally or on S3 or GCS), you can use this function to load it into your database.
- `transform`: This function allows you to transform your data with a SQL query.  It uses a `SELECT` statement that you define to automatically store your results in a new table. By default, the `output_table` is placed in a `tmp_astro` schema and is given a unique name each time the DAG runs, but you can overwrite this behavior by defining a specific `output_table` in your function. You can then pass the results of the `transform` downstream to the next task as if it were a native Python object.
- `dataframe`: Similar to `transform` for SQL, the `dataframe` function allows you to implement a transformation on your data using Python. You can easily store the results of the `dataframe` function in your database by specifying an `output_table`, which is useful if you want to switch back to SQL in the next step or load your final results to your database.

In the next section, we’ll show a practical example implementing these functions.

## Example ETL Implementation

To show the Astro Python SDK in action, we’ll start with a simple ETL use case. In this first scenario, we need to load data from two CSVs in S3 into Snowflake. Then, we need to combine the data and perform some transformations before loading it into a results table. First we'll show how to implement this using built-in Airflow features, and then we'll show how the Astro Python SDK can make it easier.

### The DAG before the Astro Python SDK

Here is our ETL DAG implemented with OSS Airflow operators and decorators, as well as the TaskFlow API. We take "homes" data from two CSVs in S3, load them to Snowflake, and perform two transformation tasks before appending the results to a reporting table.

```python
from datetime import datetime
import pandas as pd

from airflow.decorators import dag, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

S3_BUCKET = 'bucket_name'
S3_FILE_PATH = '</path/to/file/'
SNOWFLAKE_CONN_ID = 'snowflake'
SNOWFLAKE_SCHEMA = 'schema_name'
SNOWFLAKE_STAGE = 'stage_name'
SNOWFLAKE_WAREHOUSE = 'warehouse_name'
SNOWFLAKE_DATABASE = 'database_name'
SNOWFLAKE_ROLE = 'role_name'
SNOWFLAKE_SAMPLE_TABLE = 'sample_table'
SNOWFLAKE_RESULTS_TABLE = 'result_table'

@task(task_id='extract_data')
def extract_data():
    # Join data from two tables and save to dataframe to process
    query = ''''
    SELECT * FROM billing_data
    LEFT JOIN subscription_data
    ON customer_id=customer_id
    '''
    # Make connection to Snowflake and execute query
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = hook.get_conn()
    cur = conn.cursor()
    cur.execute(query)

    results = cur.fetchall()
    column_names = list(map(lambda t: t[0], cur.description))

    df = pd.DataFrame(results)
    df.columns = column_names

    return df.to_json()

@task(task_id='transform_data')
def transform_data(xcom: str) -> str:
    # Transform data by pivoting
    df = pd.read_json(xcom)

    transformed_df = df.pivot_table(index='DATE', 
                                    values='CUSTOMER_NAME', 
                                    columns=['TYPE'], 
                                    aggfunc='count').reset_index()

    transformed_str = transformed_df.to_string()

    # Save results to S3 so they can be loaded back to Snowflake
    s3_hook = S3Hook(aws_conn_id="s3_conn")
    s3_hook.load_string(transformed_str, 'transformed_file_name.csv', bucket_name=S3_BUCKET, replace=True)


@dag(start_date=datetime(2021, 12, 1), schedule_interval='@daily', catchup=False)

def classic_billing_dag():

    load_subscription_data = S3ToSnowflakeOperator(
        task_id='load_subscription_data',
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        s3_keys=[S3_FILE_PATH + '/subscription_data.csv'],
        table=SNOWFLAKE_SAMPLE_TABLE,
        schema=SNOWFLAKE_SCHEMA,
        stage=SNOWFLAKE_STAGE,
        file_format="(type = 'CSV',field_delimiter = ',')",
    )

    load_transformed_data = S3ToSnowflakeOperator(
        task_id='load_transformed_data',
        snowflake_conn_id=SNOWFLAKE_CONN_ID,
        s3_keys=[S3_FILE_PATH + '/transformed_file_name.csv'],
        table=SNOWFLAKE_RESULTS_TABLE,
        schema=SNOWFLAKE_SCHEMA,
        stage=SNOWFLAKE_STAGE,
        file_format="(type = 'CSV',field_delimiter = ',')",
    )

    extracted_data = extract_data()
    transformed_data = transform_data(extracted_data)
    load_subscription_data >> extracted_data >> transformed_data >> load_transformed_data

classic_billing_dag = classic_billing_dag()
```

![Classic Graph](https://assets2.astronomer.io/main/guides/astro-etl/classic_billing_graph_view.png)

While we achieved our ETL goal with the DAG above, there are a couple of limitations that made this implementation more complicated:

- Since there is no way to pass results from [`SnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator) query to the next task, we had to write our query in a `_DecoratedPythonOperator` function using the [`SnowflakeHook`](https://registry.astronomer.io/providers/snowflake/modules/snowflakehook) and explicitly do the conversion from SQL to a dataframe ourselves.
- Some of our transformations are better suited to SQL, and others are better suited to Python, but transitioning between the two requires extra boilerplate code to explicitly make those conversions.
- While the TaskFlow API makes it easier to pass data between tasks here, it is storing the resulting dataframes as XComs by default. This means that we need to worry about the size of our data. We could implement a custom XCom backend, but that would be extra lift.
- Loading data back to Snowflake after the transformation is complete requires writing extra code to store an intermediate CSV in S3.

### The DAG with the Astro Python SDK

Next, we’ll show how to rewrite the DAG using the Astro Python SDK to alleviate the challenges listed above. 

```python
import os
from datetime import datetime

import pandas as pd
from airflow.decorators import dag

from astro.files import File
from astro.sql import (
    append,
    dataframe,
    load_file,
    run_raw_sql,
    transform,
)
from astro.sql.table import Metadata, Table


SNOWFLAKE_CONN_ID = "snowflake_conn"
AWS_CONN_ID = "aws_conn"

# The first transformation combines data from the two source tables
@transform
def extract_data(homes1: Table, homes2: Table):
    return """
    SELECT *
    FROM {{homes1}}
    UNION
    SELECT *
    FROM {{homes2}}
    """

# Switch to Python (Pandas) for melting transformation to get data into long format
@dataframe
def transform_data(df: pd.DataFrame):
    df.columns = df.columns.str.lower()
    melted_df = df.melt(
        id_vars=["sell", "list"], value_vars=["living", "rooms", "beds", "baths", "age"]
    )

    return melted_df

# Run a raw SQL statement to create the reporting table if it doesn't already exist
@run_raw_sql
def create_reporting_table():
    """Create the reporting data which will be the target of the append method"""
    return """
    CREATE TABLE IF NOT EXISTS homes_reporting (
      sell number,
      list number,
      variable varchar,
      value number
    );
    """

@dag(start_date=datetime(2021, 12, 1), schedule_interval="@daily", catchup=False)
def example_s3_to_snowflake_etl():

    # Initial load of homes data csv's from S3 into Snowflake
    homes_data1 = load_file(
        task_id="load_homes1",
        input_file=File(path="s3://airflow-kenten/homes1.csv", conn_id=AWS_CONN_ID),
        output_table=Table(name="HOMES1", conn_id=SNOWFLAKE_CONN_ID)
    )

    homes_data2 = load_file(
        task_id="load_homes2",
        input_file=File(path="s3://airflow-kenten/homes2.csv", conn_id=AWS_CONN_ID),
        output_table=Table(name="HOMES2", conn_id=SNOWFLAKE_CONN_ID)
    )

    # Define task dependencies
    extracted_data = extract_data(
        homes1=homes_data1,
        homes2=homes_data2,
        output_table=Table(name="combined_homes_data"),
    )

    transformed_data = transform_data(
        df=extracted_data, output_table=Table(name="homes_data_long")
    )

    create_reporting_table = create_reporting_table(conn_id=SNOWFLAKE_CONN_ID)

    # Append transformed data to reporting table
    # Dependency is inferred by passing the previous `transformed_data` task to `source_table` param
    record_results = append(
        source_table=transformed_data,
        target_table=Table(name="homes_reporting", conn_id=SNOWFLAKE_CONN_ID),
        columns=["sell", "list", "variable", "value"],
    )
    record_results.set_upstream(create_results_table)

example_s3_to_snowflake_etl_dag = example_s3_to_snowflake_etl()
```

![Astro Graph](https://assets2.astronomer.io/main/guides/astro-etl/astro_billing_graph_view.png)

The key differences in this implementation are:

- The `load_file` and `append` functions take care of loading our raw data from S3 and transforming data to our reporting table respectively. We didn't have to write any extra code to get the data into Snowflake.
- Using the `transform` function, we easily executed SQL to combine our data from multiple tables. The results are automatically stored in a table in Snowflake. We didn't have to use the `SnowflakeHook` or write any of the code to execute the query.
- We seamlessly transitioned to a transformation in Python with the `df` function without needing to explicitly convert the results of our previous task to a Pandas dataframe. We then wrote the output of our transformation to our aggregated reporting table in Snowflake using the `target_table` parameter, so we didn't have to worry about storing the data in XCom.
- We only had to define our connection in tasks with no upstream (`load_file` and `create_reporting_table`). All downstream task that inherit from a task with a connection defined will use it.

Overall, our DAG with the Astro Python SDK is shorter, simpler to implement, and easier to read. This allows us to implement even more complicated use cases easily while focusing on the movement of our data.
