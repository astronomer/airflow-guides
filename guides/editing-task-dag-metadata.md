---
title: "Editing Task and DAG Metadata"
description: "What are DAGs and how they are constructed in Apache Airflow?"
date: 2018-05-21T00:00:00.000Z
slug: "editing-task-dag-metadata"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["DAGs", "Database", "Tasks"]
---

## Editing DagRuns and TaskInstance History

Airflow stores all metadata about `TaskInstances` and `DagRuns` in the metadata database.

A lot of the visualizations in the UI pull from the database, but others are determined every scheduler loop.

### Changing Task Names

Suppose you have an hourly DAG that syncs a list of tables between two data sources.

```python

tables = ['table_one', 'table_two', 'table_three']


with dag:
    start = DummyOperator(task_id='start')
    for table in tables:
        t1 = DummyOperator(task_id='sync_{0}'.format(table))
        start >> t1

```

Suppose after a couple of days of running this workflow, another table needs to be synced.


```python

tables = ['table_one', 'table_two', 'table_three', 'table_four']


with dag:
    start = DummyOperator(task_id='start')
    for table in tables:
        t1 = DummyOperator(task_id='sync_{0}'.format(table))
        start >> t1

```

For `DagRuns` that have already completed (whether successfully or not) after the new task was added, the new task would have no state.

![change_task_name](https://assets.astronomer.io/website/img/guides/changing_task_name.png)

Similar behavior would happen when changing a preexisting task's name:

```python
tables = ['table_one', 'table_two', 'table_three_new', 'table_four']
```

![change_task_name_two](https://assets.astronomer.io/website/img/guides/changing_task_name_two.png)


No task named `sync_table_three` shows up in the `GraphView` since that view is rendered each time the DAG file is parsed. However, in the _Browse->Task Instances_ view:

![task_run_view](https://assets.astronomer.io/website/img/guides/sync_table_three_task_run_view.png)

This view shows the `sync_table_three` TaskInstances that are stored in the Airflow UI.

#### Rerunning the DAGs

By default, the new task won't run for the older `DagRuns` as they are already in a `final` state. However, the `DagRuns` can have their state changed in the UI:


![set_dag_to_running](https://assets.astronomer.io/website/img/guides/set_dag_to_running.png)


Changing the state to `Running` will make the scheduler look at that `DagRun` and try to schedule any tasks that need doing so.



### Changing DAG Names

For now, the Airflow database does not store the state of the DAG itself (we are working to change that).
This means that just like task instances, there may be parts of the metadata that are hidden from the UI when changing a DAG's attributes.

```python
dag = DAG(
    dag_id='changing_dag_name',
    max_active_runs=3,
    schedule_interval="@hourly",
    default_args=default_args
)
...          
```

If the `dag_id` changes, all metadata will start being associated with the new ID's metadata. Since the list of DAGs is rendered during each scheduler loop, trying to access the old `dag_id` metadata directly in the UI will yield an error:

![new_dag_id](https://assets.astronomer.io/website/img/guides/changing_dag_name_new_dag.png)


However, like in `TaskInstances`, the _Browse->DagRuns_ view still has the old ID's metadata since that view reads _directly_ from the database.
