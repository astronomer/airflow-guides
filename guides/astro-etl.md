---
title: "Astro for ETL"
description: "Using the `astro` library to implement ETL use cases in Airflow."
date: 2022-01-10T00:00:00.000Z
slug: "astro-etl"
heroImagePath: null
tags: ["astro", "ETL", "SQL"]
---

## Overview

The [`astro` library](https://github.com/astro-projects/astro) is an open source Python package maintained by Astronomer that provides tools to improve the DAG authoring experience for Airflow users. The available decorators and functions allow you to write DAGs based on how you want your data to move, while simplifying the transformation process between different environments.

In this guide, we’ll demonstrate how you can use `astro` functions for ETL use cases. The resulting DAGs will be easier to write and read, and require less code.

## Astro ETL Functionality

The `astro` library makes implementing ETL use cases easier by allowing you to seamlessly transition between Python and SQL for each step in your process. Steps like creating dataframes, storing intermediate results, passing context and data between tasks, and creating Airflow task dependencies are all taken care of for you. This allows you focus solely on writing execution logic in whichever language is most suited for each step, without having to worry about Airflow orchestration logic on top of it.

More specifically, `astro` has the following functions that are helpful when implementing an ETL framework (for a full list of functions, check out the [Readme](https://github.com/astro-projects/astro)):

- `load_file`: if the data you’re starting with is in CSV or parquet files (stored locally or on S3 or GCS), you can use this function to load it into your database.
- `transform`: this function allows you to transform your data with a SQL query. You define the `SELECT` statement, and the results will automatically be stored in a new table. By default, the `output_table` will be placed in a `tmp_astro` schema and will be given a unique name each time the DAG runs, but you can overwrite this behavior by defining a specific `output_table` in your function. You can then pass the results of the `transform` downstream to the next task as if it were a native Python object.
- `dataframe`: similar to `transform` for SQL, the `dataframe` function allows you to implement a transformation on your data using Python. You can easily store the results of the `dataframe` function in your database by specifying an `output_table`, which is useful if you want to switch back to SQL in the next step or load final results to your database.

In the next section, we’ll show a practical example implementing these functions.

## Example ETL Implementation

To show `astro` for ETL in action, we’ll take a pretty common use case: managing billing data. We need to extract customer subscription data by joining data from a CSV on S3 with the results of a query to our Snowflake database. Then we perform some transformations on the data before loading it into a results table. Below we’ll show what the original DAG looked like, and then how `astro` can make it easier.

### The DAG Before Astro

Here is our billing subscription ETL DAG implemented with OSS Airflow operators and decorators and making use of the TaskFlow API:

```python
from datetime import datetime
import pandas as pd

from airflow import DAG
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
        s3_keys=[S3_FILE_PATH + '/trasnformed_file_name.csv'],
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

While we achieved our ETL goal with the DAG above, there are a couple of limitations that make the implementation more complicated:

- Since there is no way to pass results from `SnowflakeOperator` query to the next task, we have to write our query in a `_DecoratedPythonOperator` function using the `SnowflakeHook`, and do the conversion from SQL to a dataframe explicitly ourselves.
- Some of our transformations are better suited to SQL, and others are better suited to Python, but transitioning between the two requires extra boilerplate code to explicitly make those conversions.
- While the TaskFlow API makes it easier to pass data between tasks here, it is storing the resulting dataframes in as XComs by default. This means we need to worry about the size of our data. We could implement a custom XCom backend, but that would be extra lift.
- Loading data back to Snowflake after the transformation is complete requires storing an intermediate CSV in S3, and writing the code to do so ourselves.

### The DAG With Astro

Next, we’ll show how to rewrite the DAG using `astro` to alleviate the challenges listed above. 

```python
from airflow.decorators import dag
from astro import sql as aql
from astro.sql.table import Table
from astro import dataframe as df

from datetime import datetime
import pandas as pd

SNOWFLAKE_CONN_ID = "snowflake"
S3_FILE_PATH = '</path/to/file/'

# Start by selecting data from two source tables in Snowflake
@aql.transform()
def extract_data(subscriptions: Table, customer_data: Table):
    return """SELECT * FROM {subscriptions}
    LEFT JOIN {customer_data}
    ON customer_id=customer_id"""

# Switch to Pandas for pivoting transformation
@df
def transform_data(df: pd.DataFrame):
    transformed_df = df.pivot_table(index='DATE', 
                                    values='CUSTOMER_NAME', 
                                    columns=['TYPE'], 
                                    aggfunc='count').reset_index()

    return transformed_df


@dag(start_date=datetime(2021, 12, 1), schedule_interval='@daily', catchup=False)

def astro_billing_dag():
    # Load subscripton data
    load_subscription_data = aql.load_file(
        path=S3_FILE_PATH + '/subscription_data.csv',
        file_conn_id="my_s3_conn",
        output_table=Table(table_name="subscription_data", conn_id=SNOWFLAKE_CONN_ID),
    )
    # Define task dependencies
    extracted_data = extract_data(subscriptions=load_subscription_data,
                                    customer_data=Table('customer_data', conn_id=SNOWFLAKE_CONN_ID, schema='SANDBOX_KENTEND'))

    transformed_data = transform_data(extracted_data, output_table=Table('aggregated_bills'     conn_id=SNOWFLAKE_CONN_ID))
    
    # Append transformed data to billing table
    load_transformed_data = aql.append(
        conn_id="snowflake",
        append_table="aggregated_bills",
        columns=["DATE", "CUSTOMER_ID", "AMOUNT"],
        main_table="SANDBOX_KENTEND.billing_reporting",
    )

    transformed_data >> load_transformed_data

astro_billing_dag = astro_billing_dag()
```

![Astro Graph](https://assets2.astronomer.io/main/guides/astro-etl/astro_billing_graph_view.png)

The key differences in this implementation are:

- The `astro` functions `load_file` and `append` take care of loading our raw data from S3 and transformed data to our reporting table respectively. We didn't have to write any explicit code to get the data into Snowflake.
- Using the `transform` function, we can easily execute SQL to combine our data from multiple tables. The results are automatically stored in a table in Snowflake. We didn't have to use the `SnowflakeHook` or write any of the code to execute the query.
- We seamlessly transition to a transformation in Python with the `df` function, without needing to explicitly convert the results of our previous task to a Pandas dataframe. We then write the output of our transformation to our "aggregated_bills" table in Snowflake using the `output_table` parameter, so we don't have to worry about storing the data in XCom.

Overall, our DAG with `astro` is shorter, simpler to implement, and easier to read. This allows us to implement even more complicated use cases easily while focusing on the movement of our data.
