---
title: "Passing Data Between Airflow Tasks"
description: "Methods for sharing metadata and information between tasks in your Apache Airflow DAGs."
date: 2021-03-12T00:00:00.000Z
slug: "airflow-passing-data-between-tasks"
tags: ["DAGs", "XCom", "Tasks", "Dependencies"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/airflow-guide-passing-data-between-tasks).

## Introduction

Sharing data between tasks is a very common use case in Airflow. If you've been writing DAGs, you probably know that breaking them up into appropriately small tasks is best practice for debugging and recovering quickly from failures. But, maybe one of your downstream tasks requires metadata about an upstream task, or processes the results of the task immediately before it. 

There are a few methods you can use to implement data sharing between your Airflow tasks. In this guide, we'll walk through the two most commonly used methods, discuss when to use each, and show some example DAGs to demonstrate the implementation. 

Before we dive into the specifics, there are a couple of high-level concepts that are important when writing DAGs where data is shared between tasks. 

### Ensure Idempotency

An important concept for any data pipeline, including an Airflow DAG, is [idempotency](https://en.wikipedia.org/wiki/Idempotence). This is the property whereby an operation can be applied multiple times without changing the result. We often hear about this concept as it applies to your entire DAG; if you execute the same DAGRun multiple times, you will get the same result. However, this concept also applies to tasks within your DAG; if every task in your DAG is idempotent, your full DAG will be idempotent as well. 

When designing a DAG that passes data between tasks, it is important to ensure that each task is idempotent. This will help you recover and ensure no data is lost should you have any failures.

### Consider the Size of Your Data

Knowing the size of the data you are passing between Airflow tasks is important when deciding which implementation method to use. As we'll describe in detail below, XComs are one method of passing data between task, but they are only appropriate for small amounts of data. Large data sets will require a method making use of intermediate storage and possibly utilizing an external processing framework.

## XCom

The first method for passing data between Airflow tasks is to use XCom, which is a key Airflow feature for sharing task data.

### What is XCom

[XCom](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=xcom#concepts-xcom) (short for cross-communication) is a native feature within Airflow. XComs allow tasks to exchange task metadata or small amounts of data. They are defined by a key, value, and timestamp. 

XComs can be "pushed", meaning sent by a task, or "pulled", meaning received by a task. When an XCom is pushed, it is stored in Airflow's metadata database and made available to all other tasks. Any time a task returns a value (e.g. if your Python callable for your PythonOperator has a return), that value will automatically be pushed to XCom. Tasks can also be configured to push XComs by calling the `xcom_push()` method. Similarly, `xcom_pull()` can be used in a task to receive an XCom. 

You can view your XComs in the Airflow UI by navigating to Admin → XComs. You should see something like this:

![XCom UI](https://assets2.astronomer.io/main/guides/xcom/xcom_ui.png)

### When to Use XComs

XComs should be used to pass **small** amounts of data between tasks. Things like task metadata, dates, model accuracy, or single value query results are all ideal data to use with XCom. 

While there is nothing stopping you from passing small data sets with XCom, be very careful when doing so. This is not what XCom was designed for, and using it to pass data like pandas dataframes can degrade the performance of your DAGs and take up storage in the metadata database. 

XCom cannot be used for passing large data sets between tasks. The limit for the size of the XCom is determined by which metadata database you are using:

- Postgres: 1 Gb
- SQLite: 2 Gb
- MySQL: 64 Kb

You can see that these limits aren't very big. And even if you think your data might squeak just under, don't use XComs. Instead, see the section below on using intermediary data storage, which is more appropriate for larger chunks of data.  

### XCom Backends

It is possible to use a different service (such as S3) to store XComs and change the serialization and deserialization behavior of tasks results in XCom by setting up a custom XCom backend. This is a concept in its own right, so we won't go into too much detail here, but you can start by reading more about it in the [Apache Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=xcom#custom-xcom-backend).

### Example DAGs

In this section, we'll show a couple of example DAGs that use XCom to pass data between tasks. For this example, we're interested in analyzing the increase in total number of Covid tests for the current day for a particular state. To implement this use case, we will have one task that makes a request to the [Covid Tracking API](https://covidtracking.com/data/api) and pulls the `totalTestResultsIncrease` parameter from the results. We will then use another task to take that result and complete some sort of analysis. This is a valid use case for XCom, because the data being passed between the tasks is a single integer.

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import requests
import json

url = 'https://covidtracking.com/api/v1/states/'
state = 'wa'

def get_testing_increase(state, ti):
    """
    Gets totalTestResultsIncrease field from Covid API for given state and returns value
    """
    res = requests.get(url+'{0}/current.json'.format(state))
    testing_increase = json.loads(res.text)['totalTestResultsIncrease']

    ti.xcom_push(key='testing_increase', value=testing_increase) 

def analyze_testing_increases(state, ti):
    """
    Evaluates testing increase results
    """
    testing_increases=ti.xcom_pull(key='testing_increase', task_ids='get_testing_increase_data_{0}'.format(state))
    print('Testing increases for {0}:'.format(state), testing_increases)
    #run some analysis here

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('xcom_dag',
         start_date=datetime(2021, 1, 1),
         max_active_runs=2,
         schedule_interval=timedelta(minutes=30),
         default_args=default_args,
         catchup=False
         ) as dag:

    opr_get_covid_data = PythonOperator(
        task_id = 'get_testing_increase_data_{0}'.format(state),
        python_callable=get_testing_increase,
        op_kwargs={'state':state}
    )

    opr_analyze_testing_data = PythonOperator(
        task_id = 'analyze_data',
        python_callable=analyze_testing_increases,
				op_kwargs={'state':state}
    )

    opr_get_covid_data >> opr_analyze_testing_data
```

In this DAG we have two PythonOperators which share data using the `xcom_push` and `xcom_pull` functions. Note that in the `get_testing_increase` function, we used the `xcom_push` method so that we could specify the `key` name. Alternatively, we could have made the function return the `testing_increase` value, because any value returned by an operator in Airflow will automatically be pushed to XCom; if we had used this method, the XCom key would be "returned_value". 

For the `xcom_pull` call in the `analyze_testing_increases` function, we specify the `key` and `task_ids` associated with the XCom we want to retrieve. Note that this allows you to pull any XCom value (or multiple values) at any time into a task; it does not need to be from the task immediately prior as shown in this example

If we run this DAG and then go to the XComs page in the Airflow UI, we see that a new row has been added for our `get_testing_increase_data_wa` task with the key `testing_increase` and Value returned from the API.

![Example XCom](https://assets2.astronomer.io/main/guides/xcom/example_xcom.png)

In the logs for the `analyze_data` task, we can see the value from the prior task was printed, meaning the value was successfully retrieved from XCom.

![Example XCom Log](https://assets2.astronomer.io/main/guides/xcom/example_xcom_log.png)

## TaskFlow API

Another way to implement this use case is to use the [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html) that was released with Airflow 2.0. With the TaskFlow API, returned values are pushed to XCom as usual, but XCom values can be pulled simply by adding the key as an input to the function as shown in the following DAG:

```python
from airflow.decorators import dag, task
from datetime import datetime

import requests
import json

url = 'https://covidtracking.com/api/v1/states/'
state = 'wa'

default_args = {
    'start_date': datetime(2021, 1, 1)
}

@dag('xcom_taskflow_dag', schedule_interval='@daily', default_args=default_args, catchup=False)
def taskflow():

    @task
    def get_testing_increase(state):
        """
        Gets totalTestResultsIncrease field from Covid API for given state and returns value
        """
        res = requests.get(url+'{0}/current.json'.format(state))
        return{'testing_increase': json.loads(res.text)['totalTestResultsIncrease']}

    @task
    def analyze_testing_increases(testing_increase: int):
        """
        Evaluates testing increase results
        """
        print('Testing increases for {0}:'.format(state), testing_increase)
        #run some analysis here

    analyze_testing_increases(get_testing_increase(state))

dag = taskflow()
```

This DAG is functionally the same as the first one, but thanks to the TaskFlow API there is less code required overall, and no additional code required for passing the data between the tasks using XCom. 

## Intermediary Data Storage

As mentioned above, XCom can be a great option for sharing data between tasks because it doesn't rely on any tools external to Airflow itself. However, it is only designed to be used for very small amounts of data. What if the data you need to pass is a little bit larger, for example a small dataframe?

The best way to manage this use case is to use intermediary data storage. This means saving your data to some system external to Airflow at the end of one task, then reading it in from that system in the next task. This is commonly done using cloud file storage such as S3, GCS, Azure Blob Storage, etc., but it could also be done by loading the data in either a temporary or persistent table in a database.

We'll note here that while this is a great way to pass data that is too large to be managed with XCom, you should still exercise caution. Airflow is meant to be an orchestrator, not an execution framework. If your data is very large, it is probably a good idea to complete any processing using a framework like Spark or compute-optimized data warehouses like Snowflake or dbt.

### Example DAG

Building off of our Covid example above, let's say instead of a specific value of testing increases, we are interested in getting all of the daily Covid data for a state and processing it. This case would not be ideal for XCom, but since the data returned is a small dataframe, it is likely okay to process using Airflow.

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta

from io import StringIO
import pandas as pd
import requests

s3_conn_id = 's3-conn'
bucket = 'astro-workshop-bucket'
state = 'wa'
date = '{{ yesterday_ds_nodash }}'

def upload_to_s3(state, date):
    '''Grabs data from Covid endpoint and saves to flat file on S3
    '''
    # Connect to S3
    s3_hook = S3Hook(aws_conn_id=s3_conn_id)

    # Get data from API
    url = 'https://covidtracking.com/api/v1/states/'
    res = requests.get(url+'{0}/{1}.csv'.format(state, date))

    # Save data to CSV on S3
    s3_hook.load_string(res.text, '{0}_{1}.csv'.format(state, date), bucket_name=bucket, replace=True)

def process_data(state, date):
    '''Reads data from S3, processes, and saves to new S3 file
    '''
    # Connect to S3
    s3_hook = S3Hook(aws_conn_id=s3_conn_id)

    # Read data
    data = StringIO(s3_hook.read_key(key='{0}_{1}.csv'.format(state, date), bucket_name=bucket))
    df = pd.read_csv(data, sep=',')

    # Process data
    processed_data = df[['date', 'state', 'positive', 'negative']]

    # Save processed data to CSV on S3
    s3_hook.load_string(processed_data.to_string(), '{0}_{1}_processed.csv'.format(state, date), bucket_name=bucket, replace=True)

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG('intermediary_data_storage_dag',
         start_date=datetime(2021, 1, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:
    
    generate_file = PythonOperator(
        task_id='generate_file_{0}'.format(state),
        python_callable=upload_to_s3,
        op_kwargs={'state': state, 'date': date}
    )

    process_data = PythonOperator(
        task_id='process_data_{0}'.format(state),
        python_callable=process_data,
        op_kwargs={'state': state, 'date': date}
    )

    generate_file >> process_data
```

In this DAG we make use of the `S3Hook` to save data retrieved from the API to a CSV on S3 in the `generate_file` task. The `process_data` task then grabs that data from S3, converts it to a dataframe for processing, and then saves the processed data back to a new CSV on S3.
