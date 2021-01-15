---
title: "Using SubDAGs in Airflow"
description: "Using SubDAGs to build modular workflows in Airflow."
date: 2018-05-23T00:00:00.000Z
slug: "subdags"
heroImagePath: null
tags: ["DAGs", "Subdags"]
---
<!-- markdownlint-disable-file -->
Most DAGs consist of patterns that often repeat themselves. ETL DAGs that are written to best practice usually all share the pattern of grabbing data from a source, loading it to an intermediary file store or _staging_ table, and then pushing it into production data.

Depending on your set up, using a subdag operator could make your DAG cleaner.

Suppose the DAG looks like:

![no_subdag](https://assets.astronomer.io/website/img/guides/workflow_no_subdag.png)

The pattern between extracting and loading the data is clear. The same workflow can be generated through subdags:

![subdag](https://assets.astronomer.io/website/img/guides/subdag_dag.png)

Each of the subdags can be zoomed in on:

![zoom](https://assets.astronomer.io/website/img/guides/zoomed_in.png)

The zoomed view reveals a granular view of the task:

![tasks](https://assets.astronomer.io/website/img/guides/subdag_tasks.png)

Subdags should be generated through a "DAG factory" - an external file that returns dag objects.

```python
def load_subdag(parent_dag_name, child_dag_name, args):
    dag_subdag = DAG(
        dag_id='{0}.{1}'.format(parent_dag_name, child_dag_name),
        default_args=args,
        schedule_interval="@daily",
    )
    with dag_subdag:
        for i in range(5):
            t = DummyOperator(
                task_id='load_subdag_{0}'.format(i),
                default_args=args,
                dag=dag_subdag,
            )

    return dag_subdag

```

This object should then be called when instantiating the SubDagOperator:

```python
load_tasks = SubDagOperator(
        task_id='load_tasks',
        subdag=load_subdag('example_subdag_operator',
                           'load_tasks', default_args),
        default_args=default_args,
        dag=dag,
    )
```

- The subdag should be named with a `parent.child` style or Airflow will throw an error.
- The state of the SubDagOperator and the tasks themselves are independent - a SubDagOperator marked as success (or failed) will not affect the underlying tasks._This can be dangerous_
- SubDags should be scheduled the same as their parent DAGs or unexpected behavior might occur.

## Avoiding Deadlock

_Greedy subdags_

SubDags are not currently first class citizens in Airflow. Although it is in the community's roadmap to fix this, many organizations using Airflow have outright banned them because of how they are executed.

### Slots on the worker pool

The SubDagOperator kicks off an entire DAG when it is put on a worker slot. Each task in the child DAG takes up a slot until the entire SubDag has completed. The parent operator will take up a worker slot until each child task has completed. This could cause delays in other task processing

In mathematical terms, each SubDag is behaving like a _vertex_ (a single point in a graph) instead of a _graph_.

Depending on the scale and infrastructure, a specialized queue can be added just for SubDags (assuming a CeleryExecutor), but a cleaner workaround is to avoid subdags entirely.

**Astronomer highly recommends staying away from SubDags. Airflow 1.10 has changed the default SubDag execution method to use the Sequential Executor to work around deadlocks caused by SubDags**
