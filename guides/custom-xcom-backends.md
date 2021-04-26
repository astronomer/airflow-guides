---
title: "Custom XCom Backends"
description: "Creating a custom XCom backend with Airflow 2.0."
date: 2021-04-07T00:00:00.000Z
slug: "custom-xcom-backends"
heroImagePath: null
tags: ["Plugins", "XCom"]
---


## Overview

In December 2020, the Apache Airflow project took a huge step forward with the release of [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0). One of the main new features in this release was the [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#taskflow-api), which was introduced to solve the challenge of explicitly passing messages between Airflow tasks. The TaskFlow API abstracts the task and dependency management layer away from users, which greatly improves the experience of working with XComs.

One of the features of the TaskFlow API that increases the flexibility of XComs is support for a [custom XCom backend](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=xcom#custom-xcom-backend). This means that rather than store XComs in Airflow's metadata database by default, you can push and pull XComs to and from an external system such as S3, GCS, or HDFS. You can also implement your own serialization / deserialization methods to define how XComs are handled. 

This guide discusses the benefits of using an XCom backend, shows an example of implementing an XCom backend with S3, and describes how to set this up if you're running Airflow on the Astronomer platform.

If you're new to working with XComs or the TaskFlow API and want some background before diving into custom XCom Backends, check out the [Airflow documentation on XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=xcom#xcoms) and our [webinar on using the TaskFlow API](https://www.astronomer.io/blog/taskflow-api-in-airflow-2-0).

## When to Use Custom XCom Backends

Before we dive into the details on *how* to set up an XCom backend, we want to briefly touch on *when* you might want to do so and, importantly, when you might not.

XCom backends provide much more flexibility than you would have using traditional XComs with Airflow's metadata database. When using a custom XCom backend:

-  XComs don't need to be JSON serializable because you can store the data however you want. 
- The size of your XCom information is not limited by the size of your metadata database. 
- You can implement custom retention or backup policies.
- You can access XComs without needing to access the metadata database. 

This is more ideal for production environments because you can more easily manage what happens to your XComs over time, and you don't need to worry about periodically cleaning up the metadata database with another DAG.

All of this can be great if you want to pass information between your tasks flexibly and sustainably, such as when you are using an operator that returns metadata by default. However, even though a custom XCom backend will allow you to pass more data between your tasks, Airflow is still not designed to be a processing framework. 

XComs were designed to pass *messages* between your tasks, such as metadata or other small amounts of data. If you want to pass large amounts of data between tasks, we recommend using an external processing framework such as Apache Spark, and using Airflow only for orchestration. 

For more information on these concepts, read [Passing Data Between Airflow Tasks](https://www.astronomer.io/guides/airflow-passing-data-between-tasks).

### Example Use Case: Great Expectations

Using [Great Expectations](https://greatexpectations.io/) with Airflow is an ideal use case for implementing a custom XCom backend. Great Expectations is an open source Python-based data validation framework. Thanks to the [Great Expectations Airflow provider](https://registry.astronomer.io/providers/great-expectations), it integrates seamlessly with Airflow.

The `GreatExpectationsOperator` can be used in Airflow DAGs to perform data quality checks before moving to downstream tasks (for more information on using Great Expectations with Airflow, check out our [guide](https://www.astronomer.io/guides/airflow-great-expectations) on the topic). The operator returns various results from the tests that were run on your data. 

Because these results are not returned in a JSON serializable format, the only way to use them with the default XCom backend is to enable XCom pickling. Given the security implications of pickling, this is not ideal for a production environment.  

These drawbacks can be solved by implementing a custom XCom backend which programmatically handles the results and saves them to an external file system.

## Setting Up an XCom Backend

In this section, we'll cover the general steps for setting up an XCom backend with Airflow. Note that the steps here assume you are running Airflow in a Dockerized set-up. If you are using Astronomer, see the next topic for detailed instructions on how to complete these steps on the platform.

### 1. Configure Your Backend

The first step to setting up a custom XCom backend is to configure the backend you want to use. This guide describes how to set up an S3 backend on AWS, but the process would be similar if you used another service such as Azure blob storage or GCS.

In your S3 account:

1. Create a bucket. In S3, make sure to block public access, enable versioning, and give the bucket a unique name.
2. Create a policy for your bucket that will allow Airflow to access it. Ensure the policy allows read and write actions over the bucket as shown in the following screenshot:

    ![XCom Backend Policy](https://assets2.astronomer.io/main/guides/xcom/xcom_backend_policy.png)

3. Create a user (e.g. "airflow-xcoms") with Programmatic access and attach the policy you created in Step 2 to that user. Note the access and secret keys for the next step.

### 2. Configure Your Airflow Environment

The next step is defining a connection so your Airflow environment can connect to your custom backend. To do so for this example with S3, you can either define the `AIRFLOW_CONN_AWS_DEFAULT` environment variable, or set up an `aws_default` connection in the UI. 

> Note: If Airflow is running in the same environment as your XCom Backend (e.g. Airflow is running in EC2 and your backend is an S3 bucket), you can likely assume a Role rather than having to provide credentials, which is in general more secure.

For this example, we set up the connection in the UI. Using the access credentials from the user generated in the section above, that looks something like this:

![XCom Backend Connection](https://assets2.astronomer.io/main/guides/xcom/xcom_backend_connection_secret.png)

### 3. Configure Your Serialization/Deserialization Methods

The final step to setting up your custom XCom backend is configuring your serialization/deserialization methods and applying them to your Airflow environment. Serialization and deserialization define how your XComs are programmatically handled when passing them between Airflow and your custom backend. 

The main benefit to implementing a custom method here is that unlike regular XComs, which only allow for JSON serializable messages, you can handle any datatype in whatever way suits your use case. Your custom XCom backend class will inherit from Airflow's `BaseXCom` class, so you may want to start by reviewing [that code](https://github.com/apache/airflow/blob/master/airflow/models/xcom.py) to see how it works.

For this example, we'll define a Python file with serialization/deserialization methods that works with pandas dataframes. When a task pushes an XCom value of a pandas dataframe type to your backend, the data will be converted to a CSV and saved to S3. When pulling the XCom (deserializing) from the backend, the method will convert the CSV back into a pandas dataframe. Note that the name of your XCom backend bucket must be specified in the class.

```python
from typing import Any
from airflow.models.xcom import BaseXCom
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import pandas as pd
import uuid

class S3XComBackend(BaseXCom):
    PREFIX = "xcom_s3://"
    BUCKET_NAME = "your-bucket-name"

    @staticmethod
    def serialize_value(value: Any):
        if isinstance(value, pd.DataFrame):

            hook        = S3Hook()
            key         = "data_" + str(uuid.uuid4())
            filename    = f"{key}.csv"

            value.to_csv(filename)
            hook.load_file(
                filename=filename,
                key=key,
                bucket_name=S3XComBackend.BUCKET_NAME,
                replace=True
            )
            value = S3XComBackend.PREFIX + key
        return BaseXCom.serialize_value(value)

    @staticmethod
    def deserialize_value(result) -> Any:
        result = BaseXCom.deserialize_value(result)
        if isinstance(result, str) and result.startswith(S3XComBackend.PREFIX):
            hook    = S3Hook()
            key     = result.replace(S3XComBackend.PREFIX, "")
            filename = hook.download_file(
                key=key,
                bucket_name=S3XComBackend.BUCKET_NAME,
                local_path="/tmp"
            )
            result = pd.read_csv(filename)
        return result

```

Now, to add this class to your Airflow environment, complete the following steps:

1. Create a folder & file in your host directory and paste the `S3XComBackend` class code above into the file:

    ```docker
    # Create a folder/file in your host directory
    include/s3_xcom_backend.py
    ```

2. Mount the folder created above as a Docker volume in your Airflow project. If you're using docker-compose, you can do so by adding the following to your `docker-compose.yaml` file:

    ```docker
    volumes:
    - ./include:/opt/airflow/include
    ```

3. Specify your XCom backend by defining the `AIRFLOW__CORE__XCOM_BACKEND` Airflow environment variable. If you're using docker-compose, you can do so by adding the following to your `docker-compose.yaml` file:

    ```docker
    environment:
    - AIRFLOW__CORE__XCOM_BACKEND=include.s3_xcom_backend.S3XComBackend
    ```

> Note: to run this docker-compose example, you need to set your Python Path in your `docker-compose.yaml` file (e.g. `PYTHONPATH: /opt/airflow/`).

When you restart Airflow and run a DAG with pandas dataframe XComs, you should see those XComs get pushed to your S3 backend:

![XCom Backend S3 XComs](https://assets2.astronomer.io/main/guides/xcom/xcom_backend_s3_xcoms.png)

> Note: if you make any changes to your XCom Backend class by modifying `s3_xcom_backend.py`, you will need to restart Airflow (in this example, with `docker-compose down && docker-compose up -d`) for those changes to take effect.

## Using XCom Backends on the Astronomer Platform

Now that we've shown the general steps for setting up a custom XCom backend, in this section we'll show how to apply those steps when working with Airflow on the Astronomer platform. For this example, we'll use the Great Expectations use case for storing operator results XComs as described above.

> Note: All supporting code for this section can be found in [this repo](https://github.com/astronomer/custom-xcom-backend-tutorial).

First, use the following steps to configure your XCom backend on the Astronomer platform:

1. Configure your backend (S3, GCS, etc.) as described in Section 1 from the previous example.
2. Open an existing Astronomer project, or initialize a new one using `astro dev init` (if you don't already have the Astronomer CLI, install it using the [CLI Quickstart](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart) before completing these steps).
3. Add the XCom backend Python file with serialization/deserialization methods as shown below to the `include/` directory of your Astronomer project.
4. Add the `AIRFLOW__CORE_XCOM_BACKEND` environment variable to your Astronomer project. For this example, it should look like `AIRFLOW__CORE__XCOM_BACKEND=include.s3_xcom_backend.S3XComBackend`. There are a few ways to add an environment variable to your Astronomer Deployment, which are detailed in Astronomer's [Environment Variables guide](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables). In this case, we added the variable to our Dockerfile.
5. Deploy your project code to Astronomer, or start Airflow locally by running `astro dev start`.
6. Add an Airflow connection to connect to your backend as described in the previous example. Note that if you are using a secrets backend with Astronomer, you can add the connection there.
7. Test your new XCom backend by running the example DAG below.

For this example, we have created serialization and deserialization methods that take the results of the `GreatExpectationsOperator`, convert them to JSON, and save to a file on S3. Our custom backend class looks like this:

```python
from typing import Any
from airflow.models.xcom import BaseXCom
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import json
import uuid

class S3XComBackend(BaseXCom):
    PREFIX = "xcom_s3://"
    BUCKET_NAME = "kenten-xcom-backend-testing"

    @staticmethod
    def serialize_value(value: Any):
        if not isinstance(value, (str, dict, list)):
            hook        = S3Hook()
            key         = "data_" + str(uuid.uuid4())
            filename    = f"{key}.json"

            with open(filename, 'w') as f:
                json.dump(json.loads(str(value)), f)

            hook.load_file(
                filename=filename,
                key=key,
                bucket_name=S3XComBackend.BUCKET_NAME,
                replace=True
            )
            value = S3XComBackend.PREFIX + key
        return BaseXCom.serialize_value(value)

    @staticmethod
    def deserialize_value(result) -> Any:
        result = BaseXCom.deserialize_value(result)
        if isinstance(result, str) and result.startswith(S3XComBackend.PREFIX):
            hook    = S3Hook()
            key     = result.replace(S3XComBackend.PREFIX, "")
            filename = hook.download_file(
                key=key,
                bucket_name=S3XComBackend.BUCKET_NAME,
                local_path="/tmp"
            )
            result = json.load(filename)
        return result
```

To test this, we used a variation of the example DAG in the [Great Expectations provider page](https://registry.astronomer.io/providers/great-expectations) on the Astronomer Registry. Note that in order for this DAG to work, you will also need Great Expectations checkpoints, validation suits, and data to test; all of this can be found in the [example repo](https://github.com/astronomer/custom-xcom-backend-tutorial).

Our example DAG looks likes this:

```python
from airflow import DAG
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

import logging
import os
from datetime import datetime, timedelta

# This runs an expectation suite against a sample data asset. You may need to change these paths if you do not have your `data`
# directory living in a top-level `include` directory. Ensure the checkpoint yml files have the correct path to the data file.
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_file = os.path.join(base_path, 'include',
                         'data/yellow_tripdata_sample_2019-01.csv')
ge_root_dir = os.path.join(base_path, 'include', 'great_expectations')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='example_great_expectations_dag',
    start_date=datetime(2021, 1, 1),
    max_active_runs=1,
    schedule_interval='@daily',
    default_args=default_args,
    catchup=False 
    ) as dag:

    ge_batch_kwargs_pass = GreatExpectationsOperator(
        task_id='ge_batch_kwargs_pass',
        expectation_suite_name='taxi.demo',
        batch_kwargs={
            'path': data_file,
            'datasource': 'data__dir'
        },
        data_context_root_dir=ge_root_dir,
    )

    # This runs an expectation suite against a data asset that passes the tests
    ge_batch_kwargs_list_pass = GreatExpectationsOperator(
        task_id='ge_batch_kwargs_list_pass',
        assets_to_validate=[
            {
                'batch_kwargs': {
                    'path': data_file,
                    'datasource': 'data__dir'
                },
                'expectation_suite_name': 'taxi.demo'
            }
        ],
        data_context_root_dir=ge_root_dir,
    )

    # This runs a checkpoint that will pass. Make sure the checkpoint yml file has the correct path to the data file.
    ge_checkpoint_pass = GreatExpectationsOperator(
        task_id='ge_checkpoint_pass',
        run_name='ge_airflow_run',
        checkpoint_name='taxi.pass.chk',
        data_context_root_dir=ge_root_dir,
    )

    
    ge_batch_kwargs_list_pass >> ge_batch_kwargs_pass >> ge_checkpoint_pass
```

When we run this DAG, we will see three XCom files in our S3 bucket, one for each operator. With this implementation, we didn't need to enable XCom pickling, we can version and access our XCom data easily, and we are not filling up the Airflow metadata database, making this a much more sustainable way of using this popular operator.
