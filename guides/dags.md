---
title: "Introduction to Airflow DAGs"
description: "How to write your first DAG in Apache Airflow"
date: 2018-05-21T00:00:00.000Z
slug: "dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Airflow UI", "DAGs", "Basics"]
---

In Airflow, a DAG is a data pipeline defined in Python code. DAG stands for "directed, acyclic, graph". In that graph, each node represents a task which completes a unit of work, and each edge represents a dependency between tasks. There is no limit to what a DAG can do so long as tasks remain acyclic (tasks cannot create data that goes on to self-reference).

In this guide, we'll cover everything you need to know to get started writing a DAG, including how to define a DAG in Python, how to run the DAG on your local computer using the Astro CLI, and how to view and monitor the DAG in the Airflow UI.

## Presumed Knowledge

## Creating DAGs

DAGs in Airflow are defined in a Python script that is placed in Airflow's `DAG_FOLDER`. Airflow will execute the code in this folder and will load any DAG objects. If you are working with the Astro CLI, DAG scripts can be placed in the `dags/` folder. 

Most DAGs will follow this general flow within a Python script:

- Imports: Any needed Python packages are imported at the top of the DAG script. This will always include a `dag` function import, and may also include provider packages or other general Python packages.
- DAG instantiation: A DAG object is created and any DAG-level parameters such as the schedule interval are set.
- Task instantiation: Each task is defined by calling an operator and providing necessary task-level parameters.
- Dependencies: Any dependencies between tasks are set using bitshift operators (`<<` and `>>`), the `set_upstream()` or `set_downstream` functions, or the `chain()` function. Note that if you are using the TaskFlow API, dependencies are inferred based on the task function calls.

For example, the following DAG is generated when you initialize an Astro project:

```python
import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task # DAG and task decorators for interfacing with the TaskFlow API


@dag(
    # This defines how often your DAG will run, or the schedule by which your DAG runs. In this case, this DAG
    # will run daily
    schedule_interval="@daily",
    # This DAG is set to run for the first time on January 1, 2021. Best practice is to use a static
    # start_date. Subsequent DAG runs are instantiated based on scheduler_interval
    start_date=datetime(2021, 1, 1),
    # When catchup=False, your DAG will only run for the latest schedule_interval. In this case, this means
    # that tasks will not be run between January 1, 2021 and 30 mins ago. When turned on, this DAG's first
    # run will be for the next 30 mins, per the schedule_interval
    catchup=False,
    default_args={
        "retries": 2, # If a task fails, it will retry 2 times.
    },
    tags=['example']) # If set, this tag is shown in the DAG view of the Airflow UI
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

Astronomer recommends creating one Python file for each DAG. Some advanced use cases might require dynamically generating DAG files, which can also be accomplished using Python.

## Running DAGs

## Viewing DAGs

Airflow UI
States

One of the key pieces of data stored in Airflow’s metadata database is **State**. States are used to keep track of what condition task instances and DAG Runs are in. In the screenshot below, we can see how states are represented in the Airflow UI:


DAG Runs and tasks can have the following states:

### DAG States

- **Running (Lime):** DAG is currently being executed.
- **Success (Green):** DAG was executed successfully.
- **Failed (Red):** The task or DAG failed.

### Task States

- **None (Light Blue):** No associated state. Syntactically - set as Python None.
- **Queued (Gray):** The task is waiting to be executed, set as queued.
- **Scheduled (Tan):** The task has been scheduled to run.
- **Running (Lime):** The task is currently being executed.
- **Failed (Red):** The task failed.
- **Success (Green):** The task was executed successfully.
- **Skipped (Pink):** The task has been skipped due to an upstream condition.
- **Shutdown (Blue):** The task is up for retry.
- **Removed (Light Grey):** The task has been removed.
- **Retry (Gold):** The task is up for retry.
- **Upstream Failed (Orange):** The task will not run because of a failed upstream dependency.