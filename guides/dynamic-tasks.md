---
title: "Dynamic Tasks in Airflow"
description: "How to dynamically create tasks at runtime in your Airflow DAGs."
date: 2022-04-22T00:00:00.000Z
slug: "dynamic-tasks"
heroImagePath: null
tags: ["Tasks"]
---

## Overview

With the release of Airflow 2.3 (LINK?), users can write DAGs that dynamically generate parallel tasks at runtime. This feature, known as dynamic task mapping, is a paradigm shift for DAG design in Airflow. Prior to Airflow 2.3, tasks could only be generated dynamically at the time the DAG was parsed, meaning you had to change your DAG code if you needed to adjust tasks based on some external factor. Now, you can easily design your DAGs to respond to external criteria by creating a varied number of tasks each time they are run.

In this guide, we'll cover the concept of dynamic task mapping, and a couple of example implementations showing how to use this feature for common use cases.

## Dynamic Task Concepts

Airflow's dynamic task mapping feature it built off of the [MapReduce](https://en.wikipedia.org/wiki/MapReduce) programming model. The map procedure takes a set of inputs and creates a single task for each one. The reduce procedure, which is optional, allows a task to operate on the collected output of a mapped task.

In practice, DAG authors have two new functions available to implement this feature:

- `expand()`, which passes the input you want to map on to a particular parameter of the operator
- `partial()`, which passes parameters that stay constant for all mapped instances of the operator

Put together, you can have a task that looks like this:

```python
@task
    def add(x: int, y: int):
        return x + y

    added_values = add.partial(y=10).expand(x=[1, 2, 3])
```

This will result in three mapped `add` tasks, one for each entry in the `x` input list, where `y` remains constant in each task.

There are a couple of things to keep in mind when working with mapped tasks:

- You *can* use the results of an upstream task as the input to a mapped task (in fact, this is where the real flexibility comes with this feature). The only requirement is that the upstream task return a value in a dict or list form. If using traditional operators (not decorated tasks), the mapping values must be stored in XCom.
- You *can* map over multiple parameters. This will result in a cross product with one task for each combination of parameters.
- You *can* use the results of a mapped task as input to a downstream mapped task.
- You *can't* map over all parameters. For example, `task_id`, `pool`, and many `BaseOperator` arguments are not mappable.

For more high level examples of how to apply dynamic task mapping functions in different cases, check out the Airflow docs (LINK).

The Airflow UI gives us observability for mapped tasks in both the Graph View and the Grid View.

In the Graph View, any mapped tasks will be indicated by a set of brackets `[ ]` following the task ID. The number in the brackets will update for each DAG run to reflect how many mapped instances were created.

![Mapped Graph](https://assets2.astronomer.io/main/guides/dynamic-tasks/mapped_task_graph.png)

Clicking on the mapped task, we have a new Mapped Instances drop down where we can choose a specific instance to perform task actions on.

![Mapped Actions](https://assets2.astronomer.io/main/guides/dynamic-tasks/mapped_instances_task_actions.png)

Selecting one of the mapped instances provides links to other views like you would see for any other Airflow task: Instance Details, Rendered, Log, XCom, etc.

![Mapped Views](https://assets2.astronomer.io/main/guides/dynamic-tasks/mapped_instance_views.png)

Similarly, the Grid View shows task details and history for each mapped task. All mapped tasks will be combined into one row on the grid (shown as `load_files_to_snowflake [ ]` in this example), and clicking into that task will provide details on each individual mapped instance.

![Mapped Grid](https://assets2.astronomer.io/main/guides/dynamic-tasks/mapped_grid_view.png)

## Example Implementations

In this section we'll show how to implement dynamic task mapping for two classic use cases: processing files in S3 and implementing a pluggable ML Ops pipeline. The first will highlight use of traditional Airflow operators, and the second will use decorated functions and the TaskFlow API.

### Processing Files From S3

For our first example, we'll implement one of the most common use cases for dynamic tasks: processing files in S3. In this scenario, we will use an ELT framework to extract data from files in S3, load it into Snowflake, and then transform the data using Snowflmappake's built-in compute. We assume that files will be dropped daily, but we don't know how many will arrive each day. We'll leverage dynamic task mapping to create a unique task for each file at runtime. This gives us the benefit of atomicity, better observability, and easier recovery from failures.

The DAG below has the following steps:

1. Uses a decorated Python operator to get the current list of files from S3. The S3 prefix passed to this function is parameterized with `ds_nodash` so it pulls files only for the execution date of the DAG run (e.g. for a DAG run on April 12th, we would assume the files landed in a folder named `20220412/`).
2. Using the results of the first task, map an `S3ToSnowflakeOperator` for each file.
3. Move the daily folder of processed files into a `processed/` folder while,
4. Simultaneously (with step 3), run a Snowflake query that transforms the data. The query is located in a separate SQL file in our `include/` directory. 
5. Delete the folder of daily files now that it has been moved to `processed/` for record keeping.

```python
from airflow import DAG
from airflow.decorators import task
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3_copy_object import S3CopyObjectOperator
from airflow.providers.amazon.aws.operators.s3_delete_objects import S3DeleteObjectsOperator

from datetime import datetime

@task
def get_s3_files(current_prefix):
    s3_hook = S3Hook(aws_conn_id='s3')
    current_files = s3_hook.list_keys(bucket_name='my-bucket', prefix=current_prefix + "/", start_after_key=current_prefix + "/")
    return [[file] for file in current_files]


with DAG(dag_id='mapping_elt', 
        start_date=datetime(2022, 4, 2),
        catchup=False,
        template_searchpath='/usr/local/airflow/include',
        schedule_interval='@daily') as dag:

    copy_to_snowflake = S3ToSnowflakeOperator.partial(
        task_id='load_files_to_snowflake', 
        stage='MY_STAGE',
        table='COMBINED_HOMES',
        schema='MYSCHEMA',
        file_format="(type = 'CSV',field_delimiter = ',', skip_header=1)",
        snowflake_conn_id='snowflake').expand(s3_keys=get_s3_files(current_prefix="{{ ds_nodash }}"))

    move_s3 = S3CopyObjectOperator(
        task_id='move_files_to_processed',
        aws_conn_id='s3',
        source_bucket_name='my-bucket',
        source_bucket_key="{{ ds_nodash }}"+"/",
        dest_bucket_name='my-bucket',
        dest_bucket_key="processed/"+"{{ ds_nodash }}"+"/"
    )

    delete_landing_files = S3DeleteObjectsOperator(
        task_id='delete_landing_files',
        aws_conn_id='s3',
        bucket='my-bucket',
        prefix="{{ ds_nodash }}"+"/"
    )

    transform_in_snowflake = SnowflakeOperator(
        task_id='run_transformation_query',
        sql='/transformation_query.sql',
        snowflake_conn_id='snowflake'
    )

    copy_to_snowflake >> [move_s3, transform_in_snowflake]
    move_s3 >> delete_landing_files
```

The Graph View of the DAG looks like this:

SCREENSHOT

Keep in mind the format needed for the parameter you are mapping on. In the example above, we write our own Python function to get the S3 keys because the `S3toSnowflakeOperator` requires *each* `s3_key` parameter to be in a list format, and the `s3_hook.list_keys` function returns a single list with all keys. By writing our own simple function, we can turn the hook results into a list of lists that can be used by the downstream operator. 

### Making a Pluggable ML Ops Pipeline

 Dynamic tasks can be very useful for productionizing machine learning pipelines. ML Ops often includes some sort of dynamic component. The following use cases are common:

 - train different models
 - hyperparameter train a single model
 - create a different model for each customer

 In the example DAG below, we implement the first of these use cases. We also highlight how dynamic task mapping is simple to implement with decorated tasks.