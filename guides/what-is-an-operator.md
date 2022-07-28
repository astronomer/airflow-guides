---
title: "Operators 101"
description: "An introduction to Operators in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-an-operator"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Operators", "Tasks", "Basics"]
---

## Overview

Operators are the building blocks of Airflow DAGs. They contain the logic of how data is processed in a pipeline. Each task in a DAG is defined by instantiating an operator.

There are many different types of operators available in Airflow. Some operators execute general code provided by the user, like a Python function, while other operators perform very specific actions such as transferring data from one system to another.

In this guide, we'll cover the basics of using operators in Airflow and show an example of how to implement them in a DAG.

> **Note:** To browse and search all of the available operators in Airflow, visit the [Astronomer Registry](https://registry.astronomer.io/modules?types=operators), the discovery and distribution hub for Airflow integrations.


## Operator Basics

Under the hood, operators are Python classes that encapsulate logic to do a unit of work. They can be thought of as a wrapper around each unit of work that defines the actions that will be completed and abstracts away a lot of code you would otherwise have to write yourself. When you create an instance of an operator in a DAG and provide it with its required parameters, it becomes a task.

All operators inherit from the abstract [BaseOperator class](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/baseoperator/index.html), which contains the logic to execute the work of the operator within the context of a DAG.

The work each operator does varies widely. Some of the most frequently used operators in Airflow are:

- [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator): Executes a Python function.
- [BashOperator](https://registry.astronomer.io/providers/apache-airflow/modules/bashoperator): Executes a bash script.
- [KubernetesPodOperator](https://registry.astronomer.io/providers/kubernetes/modules/kubernetespodoperator): Executes a task defined as a Docker image in a Kubernetes Pod.
- [SnowflakeOperator](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator): Executes a query against a Snowflake database.

Operators are easy to use and typically only a few parameters are required. There are a few details that every Airflow user should know about operators:

- The [Astronomer Registry](https://registry.astronomer.io/modules?types=operators) is the best place to go to learn about what operators are out there and how to use them.
- The core Airflow package that contains basic operators such as the PythonOperator and BashOperator. These operators are automatically available in your Airflow environment. All other operators are part of provider packages, which must be installed separately. For example, the SnowflakeOperator is part of the [Snowflake provider](https://registry.astronomer.io/providers/snowflake).
- If an operator exists for your specific use case, you should always use it over your own Python functions or [hooks](https://www.astronomer.io/guides/what-is-a-hook). This makes your DAGs easier to read and maintain.
- If an operator doesn't exist for your use case, you can extend operator to meet your needs. For more on how to customize operators, check out our previous [Anatomy of an Operator webinar](https://www.astronomer.io/events/webinars/anatomy-of-an-operator).
- [Sensors](https://www.astronomer.io/guides/what-is-a-sensor) are a type of operator that wait for something to happen. They can be used to make your DAGs more event-driven.
- [Deferrable Operators](https://www.astronomer.io/guides/deferrable-operators) are a type of operator that release their worker slot while waiting for their work to be completed. This can result in cost savings and greater scalability. Astronomer recommends using deferrable operators whenever one exists for your use case and your task takes longer than about a minute. Note that you must be using Airflow 2.2+ and have a triggerer running to use deferrable operators. 
- Any operator that interacts with a service external to Airflow will typically require a connection so that Airflow can authenticate to that external system. More information on how to set up connections can be found in our guide on [managing connections](https://www.astronomer.io/guides/connections/) or in the examples to follow.


## Example Implementation

This example shows how to use several common operators in a DAG used to transfer data from S3 to Redshift and perform data quality checks. 

> **Note:** The full code and repository for this example can be found on the [Astronomer Registry](https://registry.astronomer.io/dags/simple-redshift-3).

The following operators are used:

- [EmptyOperator](https://registry.astronomer.io/providers/apache-airflow/modules/dummyoperator): This operator is part of core Airflow and does nothing. It is used to organize the flow of tasks in the DAG.
- [PythonDecoratedOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator): This operator is part of core Airflow and executes a Python function. It is functionally the same as the PythonOperator, but it instantiated using the `@task` [decorator](https://www.astronomer.io/guides/airflow-decorators/).
- [LocalFilesystemToS3Operator](https://registry.astronomer.io/providers/amazon/modules/localfilesystemtos3operator): This operator is part of the [AWS provider](https://registry.astronomer.io/providers/amazon) and is used to upload a file from a local filesystem to S3. 
- [S3ToRedshiftOperator](https://registry.astronomer.io/providers/amazon/modules/s3toredshiftoperator): This operator is part of the [AWS provider](https://registry.astronomer.io/providers/amazon) and is used to transfer data from S3 to Redshift.
- [PostgresOperator](https://registry.astronomer.io/providers/postgres/modules/postgresoperator): This operator is part of the [Postgres provider](https://registry.astronomer.io/providers/postgres) and is used to execute a query against a Postgres database.
- [SQLCheckOperator](https://registry.astronomer.io/providers/apache-airflow/modules/sqlcheckoperator): This operator is part of core Airflow and is used to perform checks against a database using a SQL query.

The following code shows how each of those operators can be instantiated in a DAG file to define the pipeline:

```python
import hashlib
import json

from airflow import DAG, AirflowException
from airflow.decorators import task
from airflow.models import Variable
from airflow.models.baseoperator import chain
from airflow.operators.empty_operator import EmptyOperator
from airflow.utils.dates import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator
)
from airflow.providers.amazon.aws.transfers.s3_to_redshift import (
    S3ToRedshiftOperator
)
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.sql import SQLCheckOperator
from airflow.utils.task_group import TaskGroup


# The file(s) to upload shouldn't be hardcoded in a production setting, 
# this is just for demo purposes.
CSV_FILE_NAME = "forestfires.csv"
CSV_FILE_PATH = f"include/sample_data/forestfire_data/{CSV_FILE_NAME}"

with DAG(
    "simple_redshift_3",
    start_date=datetime(2021, 7, 7),
    description="""A sample Airflow DAG to load data from csv files to S3 
                 and then Redshift, with data integrity and quality checks.""",
    schedule_interval=None,
    template_searchpath="/usr/local/airflow/include/sql/redshift_examples/",
    catchup=False,
) as dag:

    """
    Before running the DAG, set the following in an Airflow 
    or Environment Variable:
    - key: aws_configs
    - value: { "s3_bucket": [bucket_name], "s3_key_prefix": [key_prefix],
             "redshift_table": [table_name]}
    Fully replacing [bucket_name], [key_prefix], and [table_name].
    """

    upload_file = LocalFilesystemToS3Operator(
        task_id="upload_to_s3",
        filename=CSV_FILE_PATH,
        dest_key="{{ var.json.aws_configs.s3_key_prefix }}/" + CSV_FILE_PATH,
        dest_bucket="{{ var.json.aws_configs.s3_bucket }}",
        aws_conn_id="aws_default",
        replace=True,
    )

    @task
    def validate_etag():
        """
        #### Validation task
        Check the destination ETag against the local MD5 hash to ensure 
        the file was uploaded without errors.
        """
        s3 = S3Hook()
        aws_configs = Variable.get("aws_configs", deserialize_json=True)
        obj = s3.get_key(
            key=f"{aws_configs.get('s3_key_prefix')}/{CSV_FILE_PATH}",
            bucket_name=aws_configs.get("s3_bucket"),
        )
        obj_etag = obj.e_tag.strip('"')
        # Change `CSV_FILE_PATH` to `CSV_CORRUPT_FILE_PATH` for the "sad path".
        file_hash = hashlib.md5(
            open(CSV_FILE_PATH).read().encode("utf-8")).hexdigest()
        if obj_etag != file_hash:
            raise AirflowException(
                f"""Upload Error: Object ETag in S3 did not match 
                hash of local file."""
            )

    # Tasks that were created using decorators have to be called to be used
    validate_file = validate_etag()

    #### Create Redshift Table
    create_redshift_table = PostgresOperator(
        task_id="create_table",
        sql="create_redshift_forestfire_table.sql",
        postgres_conn_id="redshift_default",
    )

    #### Second load task
    load_to_redshift = S3ToRedshiftOperator(
        task_id="load_to_redshift",
        s3_bucket="{{ var.json.aws_configs.s3_bucket }}",
        s3_key="{{ var.json.aws_configs.s3_key_prefix }}"
        + f"/{CSV_FILE_PATH}",
        schema="PUBLIC",
        table="{{ var.json.aws_configs.redshift_table }}",
        copy_options=["csv"],
    )

    #### Redshift row validation task
    validate_redshift = SQLCheckOperator(
        task_id="validate_redshift",
        conn_id="redshift_default",
        sql="validate_redshift_forestfire_load.sql",
        params={"filename": CSV_FILE_NAME},
    )

    #### Row-level data quality check
    with open("include/validation/forestfire_validation.json") as ffv:
        with TaskGroup(group_id="row_quality_checks") as quality_check_group:
            ffv_json = json.load(ffv)
            for id, values in ffv_json.items():
                values["id"] = id
                SQLCheckOperator(
                    task_id=f"forestfire_row_quality_check_{id}",
                    conn_id="redshift_default",
                    sql="row_quality_redshift_forestfire_check.sql",
                    params=values,
                )

    #### Drop Redshift table
    drop_redshift_table = PostgresOperator(
        task_id="drop_table",
        sql="drop_redshift_forestfire_table.sql",
        postgres_conn_id="redshift_default",
    )

    begin = EmptyOperator(task_id="begin")
    end = EmptyOperator(task_id="end")

    #### Define task dependencies
    chain(
        begin,
        upload_file,
        validate_file,
        create_redshift_table,
        load_to_redshift,
        validate_redshift,
        quality_check_group,
        drop_redshift_table,
        end
    )

```

The resulting DAG looks like this:

![DAG Graph](https://assets2.astronomer.io/main/guides/operators-101/example_dag_graph.png)

There are a few things to note about the operators in this DAG:

- Every operator is given a `task_id`. This is a required parameter, and the value provided will be shown as the name of the task in the Airflow UI.
- Each operator requires different parameters based on the work it does. For example, the PostgresOperator has a `sql` parameter for the SQL script to be executed, and the S3ToRedshiftOperator has parameters to define the location and keys of the files being copied from S3 and the Redshift table receiving the data.
- Connections to external systems are passed in most of these operators. The parameters `conn_id`, `postgres_conn_id`, and `aws_conn_id` all point to the names of the relevant connections stored in Airflow.
