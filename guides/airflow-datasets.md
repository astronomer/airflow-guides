---
title: "Datasets and Data Driven Scheduling in Airflow"
description: "Using datasets to implement DAG dependencies and scheduling in Airflow."
date: 2022-09-01T00:00:00.000Z
slug: "airflow-datasets"
tags: ["DAGs", "Dependencies", "Scheduling"]
---

The release of [Airflow 2.4](link release notes!) includes a new concept of datasets and data dependencies. This means that DAGs that touch the same data will have explicit, visible relationships, and DAGs can be scheduled based on updates to these datasets. This feature is a big step forward in making Airflow data-aware, and vastly expands Airflow's scheduling capabilities beyond time-based methods like Cron.

This feature will help with many common use cases, such as when a data engineering team has a DAG that creates a dataset, and an analytics team has a DAG that completes analysis of that data. Using datasets, the data analytics team can ensure their DAG runs only when the data engineering team's DAG has finished publishing the dataset.

In this guide, we'll explain the concept of datasets in Airflow and how to use them to implement triggering of DAGs based on dataset updates.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- Airflow scheduling concepts. See [Scheduling and Timetables in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow/).
- Creating dependencies between DAGs. See [Cross-DAG Dependencies](https://www.astronomer.io/guides/cross-dag-dependencies/).

## Dataset Concepts

Airflow's datasets feature allows you to define datasets in your Airflow environment and use them to create dependencies between DAGs. You can define a dataset by instantiating the `Dataset` class and providing a URI. The URI can be any string, including an arbitrary name.

Then you can reference the dataset in a task by providing it to the `outlets` parameter. `outlets` is part of the `BaseOperator`, so it is available to every Airflow operator. Defining an outlet tells Airflow that that task updates that dataset.

```python
from airflow import DAG, Dataset

# Define datasets
dag1_dataset = Dataset('s3://dataset1/output_1.txt')
dag2_dataset = Dataset('s3://dataset2/output_2.txt')


with DAG(
    dag_id='dataset_upstream1',
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule='@daily',
) as dag1:

    BashOperator(
        task_id='upstream_task_1', 
        bash_command="sleep 5",
        outlets=[dag1_dataset] # Define which dataset is updated by this task
    )

    BashOperator(
        task_id='upstream_task_2', 
        bash_command="sleep 5",
        outlets=[dag2_dataset] # Define which dataset is updated by this task
    )
```

Once a dataset is defined, any DAGs in your Airflow environment can be configured to run when that dataset is updated, rather than running on a schedule. For example, if you have a DAG that should run when `dag1_dataset` and `dag2_dataset` are updated, you provide the names of the dependent datasets to that DAG's schedule.

```python
dag1_dataset = Dataset('s3://dataset1/output_1.txt')
dag2_dataset = Dataset('s3://dataset2/output_2.txt')

with DAG(
    dag_id='dataset_downstream_1_2',
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=[dag1_dataset, dag2_dataset],
    tags=['downstream'],
) as dag3:

    BashOperator(
        task_id='downstream_2',
        bash_command="sleep 5"
    )
```

Any number of datasets can be provided to the `schedule` parameter as a list. The DAG will be triggered once all of those datasets have been updated.

There are a couple of things to keep in mind when working with datasets:

- Datasets can only be used by DAGs in the *same* Airflow environment.
- For now, Airflow only monitors datasets within the context of DAGs and tasks. It does not monitor updates to datasets within an external system that occur outside of Airflow.
- DAGs that are scheduled on a dataset will be triggered every time that dataset is updated. For example, if `DAG1` and `DAG2` both operate on `dataset_a`, a DAG dependent on `dataset_a` will run *both* when `DAG1` completes and when `DAG2` completes.
- DAGs scheduled on a dataset will be triggered as soon as the first *task* that operates on that dataset finishes, even if there are downstream tasks in that DAG that also operate on the dataset.

LINK HERE TO AIRFLOW DOCS

The Airflow UI gives you observability for datasets and data dependencies in the DAG's schedule, the new **Datasets** tab, and the **DAG Dependencies** view.

On the **DAGs** view, we can see that our `dataset_downstream_1_2` DAG is scheduled on two upstream datasets (one in `dataset_upstream1` and `dataset_upstream2`), and its next run is pending one dataset update. At this point the `dataset_upstream` DAG has run and updated its dataset, but the `dataset_upstream2` DAG has not.

![DAGs View](https://assets2.astronomer.io/main/guides/data-driven-scheduling/dags_view_dataset_schedule.png)

The new **Datasets** tab shows a list of all datasets in your Airflow environment, including how many tasks update the dataset ("Producing tasks"), and how many DAGs are scheduled on updates to that dataset ("Consuming DAGs").

![Datasets View](https://assets2.astronomer.io/main/guides/data-driven-scheduling/datasets_view.png)

The **DAG Dependencies** view (found under the **Browse** tab) shows a graph of all dependencies between DAGs (in green) and datasets (in orange) in your Airflow environment.

![DAG Dependencies View](https://assets2.astronomer.io/main/guides/data-driven-scheduling/dag_dependencies.png)

## Example Implementation

 