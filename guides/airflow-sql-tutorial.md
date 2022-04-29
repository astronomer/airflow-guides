---
title: "Using Airflow to Execute SQL"
description: "Executing queries, parameterizing queries, and embedding SQL-driven ETL in Apache Airflow DAGs."
date: 2020-12-07T00:00:00.000Z
slug: "airflow-sql-tutorial"
tags: ["Database", "SQL", "DAGs"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/airflow-sql-tutorial).

## Overview

Executing SQL queries is one of the most common use cases for data pipelines. Whether you're extracting and loading data, calling a stored procedure, or executing a complex query for a report, Airflow has you covered. Using Airflow, you can orchestrate all of your SQL tasks elegantly with just a few lines of boilerplate code.

In this guide, we'll cover general best practices for executing SQL from your DAG, showcase Airflow's available SQL-related operators, and demonstrate how to use Airflow for a few common SQL use cases.

## Best Practices for Executing SQL From Your DAG

No matter which database and flavor of SQL you're using, there are many ways to execute  your queries using Airflow. Once you determine how to execute your queries, the following tips will help you keep your DAGs clean, readable, and efficient for execution.

### Use Hooks and Operators

Using hooks and operators whenever possible makes your DAGs easier to read, easier to maintain, and more performant. Airflow has many SQL-related operators available that can significantly limit the code needed to execute your queries.

### Keep Lengthy SQL Code out of your DAG

Best practice is to avoid top-level code in your DAG file. If you have a SQL query, it should be kept in its own .sql file and imported into your DAG.

For example, at Astronomer we use the following file structure to store scripts like SQL queries in the `include/` directory:

```bash
├─ dags/  
|    ├─ example-dag.py  
├─ plugins/  
├─ include/  
|    ├─ query1.sql  
|    ├─ query2.sql    
├─ Dockerfile  
├─ packages.txt  
└─ requirements.txt
```

An exception to this rule could be very short queries (such as SELECT * FROM table); putting one-line queries like this directly in the DAG can be done if it makes your code more readable.

### Keep Transformations in SQL

Remember that Airflow is primarily an orchestrator, not a transformation framework. While you have the full power of Python in your DAG, best practice is to offload as much of your transformation logic as possible to third party transformation frameworks. With SQL, this means completing the transformations within your query whenever possible.

## SQL-Related Operators

Airflow has many operators available out of the box that make working with SQL easier. Here we'll highlight some commonly used ones that we think you should be aware of, but note that this list isn't comprehensive. For more documentation about Airflow operators, head [here](https://airflow.apache.org/docs/stable/_api/airflow/operators/index.html#).

> **Note:** In Airflow 2.0, provider packages are separate from the core of Airflow. If you are running 2.0, you may need to install separate packages (e.g. `apache-airflow-providers-snowflake`) to use the hooks, operators, and connections described here. In an Astronomer project this can be accomplished by adding the packages to your `requirements.txt` file. To learn more, read [Airflow Docs on Provider Packages](https://airflow.apache.org/docs/apache-airflow-providers/index.html).

### Action Operators

In Airflow, action operators execute a function. You can use action operators (or hooks if no operator is available) to execute a SQL query against a database. Commonly used SQL-related action operators include:

- [PostgresOperator](https://registry.astronomer.io/providers/postgres/modules/postgresoperator)
- [MssqlHook](https://registry.astronomer.io/providers/mssql/modules/mssqlhook)
- [MysqlOperator](https://registry.astronomer.io/providers/mysql/modules/mysqloperator)
- [SnowflakeOperator](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator)
- [BigQueryOperator](https://registry.astronomer.io/providers/google/modules/bigqueryexecutequeryoperator)

### Transfer Operators

Transfer operators move data from a source to a destination. For SQL-related tasks, they can often be used in the 'Extract-Load' portion of an ELT pipeline and can significantly reduce the amount of code you need to write. Some examples are:

- [S3ToSnowflakeTransferOperator](https://registry.astronomer.io/providers/snowflake/modules/s3tosnowflakeoperator)
- [S3toRedshiftOperator](https://registry.astronomer.io/providers/amazon/modules/s3toredshiftoperator)
- [GCSToBigQueryOperator](https://registry.astronomer.io/providers/google/modules/gcstobigqueryoperator)
- [PostgresToGCSOperator](https://registry.astronomer.io/providers/google/modules/postgrestogcsoperator)
- [BaseSQLToGCSOperator](https://registry.astronomer.io/providers/google/modules/basesqltogcsoperator)
- [VerticaToMySqlOperator](https://registry.astronomer.io/providers/mysql/modules/verticatomysqloperator)

## Examples

With those basic concepts in mind, we'll show a few examples of common SQL use cases. For this tutorial we will use [Snowflake](https://www.snowflake.com/), but note that the concepts shown can be adapted for other databases.

### Example 1 - Executing a Query

In this first example, we use a DAG to execute two simple interdependent queries. To do so we use the [SnowflakeOperator](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator).

First we need to define our DAG:

```python
from airflow import DAG
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('call_snowflake_sprocs',
         start_date=datetime(2020, 6, 1),
         max_active_runs=3,
         schedule_interval='@daily',
         default_args=default_args,
         template_searchpath='/usr/local/airflow/include',
         catchup=False
         ) as dag:

         opr_call_sproc1 = SnowflakeOperator(
             task_id='call_sproc1',
             snowflake_conn_id='snowflake',
             sql='call-sproc1.sql'
         )
         opr_call_sproc2 = SnowflakeOperator(
             task_id='call_sproc2',
             snowflake_conn_id='snowflake',
             sql='call-sproc2.sql'
         )

         opr_call_sproc1 >> opr_call_sproc2
```

The `template_searchpath` argument in the DAG definition tells the DAG to look in the given folder for scripts, so we can now put our two SQL scripts in the `include/` directory. In this example, those scripts are 'call-sproc1.sql' and 'call-sproc2.sql', which contain the following SQL code respectively:

```sql
-- call-sproc1
CALL sp_pi();
```

```sql
-- call-sproc2
CALL sp_pi_squared();
```

`sp_pi()` and `sp_pi_squared()` are two stored procedures that we have defined in our Snowflake instance. Note that the SQL in these files could be any type of query you need to execute; sprocs are used here just as an example.

Finally, we need to set up a connection to Snowflake. There are a few ways to manage connections using Astronomer, including [IAM roles](https://docs.astronomer.io/software/integrate-iam), [secrets managers](https://docs.astronomer.io/software/secrets-backend), and the [Airflow API](https://docs.astronomer.io/software/airflow-api). For this example, we set up a connection using the Airflow UI. In this DAG our connection is called `snowflake`, and the connection should look something like this:

![Snowflake Connection](https://assets2.astronomer.io/main/guides/sql-tutorial/snowflake_connection.png)

With the connection established, we can now run the DAG to execute our SQL queries.

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/blog/best_airflow_etl_tools" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'How to Select the Best ETL Tool to Integrate with Airflow?', spottedCompany: window.spottedCompany })">How to Select the Best ETL Tool to Integrate with Airflow?</a></li>
    <li data-icon="→"><a href="/blog/data-pipeline" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Data Pipeline: Components, Types and Best Practices', spottedCompany: window.spottedCompany })">Data Pipeline: Components, Types and Best Practices</a></li>
    <li data-icon="→"><a href="/guides/airflow-sql-data-quality-tutorial" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Airflow Data Quality Checks with SQL Operators', spottedCompany: window.spottedCompany })">Airflow Data Quality Checks with SQL Operators</a></li>
</ul>

### Example 2 - Executing a Query with Parameters

Using Airflow, you can also parameterize your SQL queries to make them more dynamic. Let's say we have a query that selects data from a table for a date that we want to dynamically update. We can execute the query using the same setup as in Example 1, with a few adjustments.

Our DAG will look like this:

```python
from airflow import DAG
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG('parameterized_query',
         start_date=datetime(2020, 6, 1),
         max_active_runs=3,
         schedule_interval='@daily',
         default_args=default_args,
         template_searchpath='/usr/local/airflow/include',
         catchup=False
         ) as dag:

         opr_param_query = SnowflakeOperator(
             task_id='param_query',
             snowflake_conn_id='snowflake',
             sql='param-query.sql'
         )
```

The DAG is essentially the same as the one in Example 1: we have a `SnowflakeOperator` that will execute a query stored in the `param-query.sql` script in our include/ directory. The difference is in the query itself:

```sql
SELECT *
FROM STATE_DATA
WHERE date = {{ yesterday_ds_nodash }}
```

In this example, we have parameterized the query to dynamically select data for yesterday's date  using a built-in Airflow variable with double curly brackets. The rendered template in the Airflow UI looks like this:

![Rendered Template](https://assets2.astronomer.io/main/guides/sql-tutorial/rendered_template.png)

We recommend using Airflow variables or macros whenever possible to increase flexibility and make your workflows [idempotent](https://en.wikipedia.org/wiki/Idempotence). The above example will work with any Airflow variables; for example, we could access a variable from our Airflow config like this:

```sql
SELECT *
FROM STATE_DATA
WHERE state = {{ conf['state_variable'] }}
```

If you need a parameter that is not available as a built-in variable/macro, such as a value from another task in your DAG, you can also pass that parameter into your query using the operator like this:

```python
opr_param_query = SnowflakeOperator(
             task_id='param_query',
             snowflake_conn_id='snowflake',
             sql='param-query.sql',
			 params={"date":mydatevariable}
         )
```

And then reference that param in your SQL file like this:

```sql
SELECT *
FROM STATE_DATA
WHERE date = {{ params.date }}
```

### Example 3 - Loading Data

Our next example loads data from an external source into a table in our database. We grab data from an API and save it to a flat file on S3, which we then load into Snowflake.

We use the [S3toSnowflakeTransferOperator](https://registry.astronomer.io/providers/snowflake/modules/s3tosnowflakeoperator) to limit the code we have to write.

First, we create a DAG that pulls COVID data from an [API endpoint](https://covidtracking.com/data/api) for California, Colorado, Washington, and Oregon, saves the data to comma-separated values (CSVs) on S3, and loads each of those CSVs to Snowflake using the transfer operator. Here's the DAG code:

```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from plugins.operators.s3_to_snowflake_operator import S3ToSnowflakeTransferOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import os
import requests
S3_CONN_ID = 'astro-s3-workshop'
BUCKET = 'astro-workshop-bucket'
name = 'covid_data'  # swap your name here

def upload_to_s3(endpoint, date):
    # Instantiate
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

    # Base URL
    url = 'https://covidtracking.com/api/v1/states/'

    # Grab data
    res = requests.get(url+'{0}/{1}.csv'.format(endpoint, date))

    # Take string, upload to S3 using predefined method
    s3_hook.load_string(res.text, '{0}_{1}.csv'.format(endpoint, date), bucket_name=BUCKET, replace=True)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

endpoints = ['ca', 'co', 'wa', 'or']

date = '{{ yesterday_ds_nodash }}'

with DAG('covid_data_s3_to_snowflake',
         start_date=datetime(2020, 6, 1),
         max_active_runs=3,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:

    t0 = DummyOperator(task_id='start')   

    for endpoint in endpoints:
        generate_files = PythonOperator(
            task_id='generate_file_{0}'.format(endpoint),
            python_callable=upload_to_s3,
            op_kwargs={'endpoint': endpoint, 'date': date}
        )

        snowflake = S3ToSnowflakeTransferOperator(
            task_id='upload_{0}_snowflake'.format(endpoint),
            s3_keys=['{0}_{1}.csv'.format(endpoint, date)],
            stage='covid_stage',
            table='STATE_DATA',
            schema='SANDBOX_KENTEND',
            file_format='covid_csv',
            snowflake_conn_id='snowflake'
        )

        t0 >> generate_files >> snowflake
```

Here's a graph view of the DAG:

![Covid-to-Snowflake Graph](https://assets2.astronomer.io/main/guides/sql-tutorial/covid_to_snowflake_graph_view.png)

First, there are a few things we need to configure in Snowflake to make this DAG work:

1. A table that will receive the data (`STATE_DATA` in this example)
2. A Snowflake stage (`covid_stage`) and file format (`covid_csv`) defined. If you aren't familiar with this setup, refer to the documentation [here](https://docs.snowflake.com/en/user-guide/data-load-s3.html).

Next, we need to set up our Airflow connections. This example requires two:

1. A connection to S3 (established using `astro-s3-workshop` in the DAG above).
2. A connection to Snowflake (established using `snowflake` See Example 1 for a screenshot of what the connection should look like).

After this setup, we're ready to run the DAG! After a successful run, we can see our new data for today's date in the table.

![Snowflake Data](https://assets2.astronomer.io/main/guides/sql-tutorial/snowflake_data_populated.png)

Note that while this example is specific to Snowflake, the concepts apply to any database you might be using. If a transfer operator doesn't exist for your specific source and destination tools, you can always write your own (and maybe contribute it back to the Airflow project)!

## Example 4 - Using Pandas

While we stated above that the best practice is to use SQL-related operators and keep any data transformations in SQL, for some use cases this doesn't work. For instance, pivoting data into a new format for a report can be difficult to complete with SQL alone. In this next example, we show how you can make use of Python libraries to integrate your SQL into a Python function.

The following DAG pivots a table of data in Snowflake into a wide format for a report using Python:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
from plugins.operators.s3_to_snowflake_operator import S3ToSnowflakeTransferOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import pandas as pd

filename = 'pivoted_data'
S3_CONN_ID = 'astro-s3-workshop'
BUCKET = 'astro-workshop-bucket'

def pivot_data(**kwargs):
    #Make connection to Snowflake
    hook = SnowflakeHook(snowflake_conn_id='snowflake')
    conn = hook.get_conn()

    #Define SQL query
    query = 'SELECT DATE, STATE, POSITIVE FROM STATE_DATA;'

    #Read data into pandas dataframe
    df = pd.read_sql(query, conn)

    #Pivot dataframe into new format
    pivot_df = df.pivot(index='DATE', columns='STATE', values='POSITIVE').reset_index()

    #Save dataframe to S3
    s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
    s3_hook.load_string(pivot_df.to_csv(index=False),
                        '{0}.csv'.format(filename),
                        bucket_name=BUCKET,
                        replace=True)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG('pandas_processing',
         start_date=datetime(2020, 6, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:

        opr_pivot_data = PythonOperator(
            task_id='pivot_data',
            python_callable=pivot_data
        )

        opr_load_data = S3ToSnowflakeTransferOperator(
            task_id='load_data',
            s3_keys=['{0}.csv'.format(filename)],
            stage='covid_stage',
            table='PIVOT_STATE_DATA',
            schema='SANDBOX_KENTEND',
            file_format='covid_csv',
            snowflake_conn_id='snowflake'
        )

        opr_pivot_data >> opr_load_data
```

In the DAG, the Python function `pivot_data` executes the SQL query and saves the results in a pandas dataframe using the `read_sql` function. It then pivots the data to the desired format and  saves the it to S3. Lastly, the downstream task `opr_load_data`  loads that data back to Snowflake using the transfer operator described in Example 3.


## Example 5 - Using Dag-Factory

If you have SQL users who aren't familiar with Airflow or don't know any Python, they can use [dag-factory](https://github.com/ajbosco/dag-factory) to generate DAGs using a YAML configuration file.

Once you've installed dag-factory in your Airflow environment (in Astronomer you can add it to your `requirements.txt` file), you can add your SQL query tasks to a YAML configuration file in the `include/` directory like this:

```yaml
dag_factory_query:
  default_args:
    owner: 'example_owner'
    start_date: 2020-12-02
    retries: 1
    retry_delay_sec: 300
  schedule_interval: '0 3 * * *'
  concurrency: 1
  max_active_runs: 1
  dagrun_timeout_sec: 60
  default_view: 'tree'  # or 'graph', 'duration', 'gantt', 'landing_times'
  orientation: 'LR'  # or 'TB', 'RL', 'BT'
  tasks:
    task_1:
      operator: airflow.contrib.operators.snowflake_operator.SnowflakeOperator
      snowflake_conn_id: 'snowflake'
      sql: 'SELECT * FROM STATE_DATA'
```

Then, create a DAG file:

```python
from airflow import DAG
import dagfactory

dag_factory = dagfactory.DagFactory("/usr/local/airflow/include/config_file.yml")

dag_factory.clean_dags(globals())
dag_factory.generate_dags(globals())
```

Once that's complete, we can see our new DAG in the Airflow UI:

![DAG Factory Graph](https://assets2.astronomer.io/main/guides/sql-tutorial/dag_factory_graph_view.png)

## Additional Resources

<!-- markdownlint-disable MD033 -->
<iframe src="https://fast.wistia.net/embed/iframe/4qne4y6pph" title="Airflow SQL Tutorial DAG Factory" allow="autoplay; fullscreen" allowtransparency="true" frameborder="0" scrolling="no" class="wistia_embed" name="wistia_embed" allowfullscreen msallowfullscreen width="100%" height="450"></iframe>

In this guide we covered how to interact with your SQL database from Airflow and important best practices when doing so. But there are still some outstanding questions:

- How does it work behind the scenes?
- What if you want to retrieve data with the PostgresOperator?
- Is it scalable?

Find out more on Astronomer's [Academy Course on Airflow SQL](https://academy.astronomer.io/airflow-sql) for free today.
