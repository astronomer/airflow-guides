---
title: "Using SubDAGs in Airflow"
description: "Using SubDAGs to build modular workflows in Airflow."
date: 2018-05-23T00:00:00.000Z
slug: "subdags"
heroImagePath: null
tags: ["DAGs", "Subdags"]
---
<!-- markdownlint-disable-file -->
> **Note:** Astronomer highly recommends avoiding SubDAGs if the intended use of the SubDAG is to simply group tasks within a DAG's Graph View.  Airflow 2.0 introduces [Task Groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#taskgroup) which is a UI grouping concept that satisfies this purpose without the performance and functional issues of SubDAGs.  While the `SubDagOperator` will continue to be supported, Task Groups are intended to replace it long-term.


Most DAGs consist of patterns that often repeat themselves. ETL DAGs that are written to best practice usually all share the pattern of grabbing data from a source, loading it to an intermediary file store or _staging_ table, and then pushing it into production data.

Depending on your set up, using a [SubDagOperator](https://registry.astronomer.io/providers/apache-airflow/modules/subdagoperator) could make your DAG cleaner.


Suppose the DAG looks like:

![no_subdag](https://assets.astronomer.io/website/img/guides/workflow_no_subdag.png)

The pattern between extracting and loading the data is clear. The same workflow can be generated through SubDAGs:

![subdag](https://assets.astronomer.io/website/img/guides/subdag_dag.png)

Each of the SubDAGs can be zoomed in on:

![zoom](https://assets.astronomer.io/website/img/guides/zoomed_in.png)

The zoomed view reveals a granular view of the task:

![tasks](https://assets.astronomer.io/website/img/guides/subdag_tasks.png)

SubDAGs should be generated through a "DAG factory" - an external file that returns DAG objects.

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

This object should then be called when instantiating the `SubDagOperator`:

```python
load_tasks = SubDagOperator(
    task_id="load_tasks",
    subdag=load_subdag(
        parent_dag_name="example_subdag_operator",
        child_dag_name="load_tasks",
        args=default_args
    ),
    default_args=default_args,
    dag=dag,
)

```

- The SubDAG should be named with a `parent.child` style or Airflow will throw an error.
- The state of the `SubDagOperator` and the tasks themselves are independent - a `SubDagOperator` marked as success (or failed) will not affect the underlying tasks. _This can be dangerous._
- SubDAGs should be scheduled the same as their parent DAGs or unexpected behavior might occur.

## Avoiding Deadlock

_Greedy subdags_

SubDAGs are not currently first-class citizens in Airflow. Although it is in the community's roadmap to fix this, many organizations using Airflow have outright banned them because of how they are executed.

Airflow 1.10 has changed the default SubDAG execution method to use the Sequential Executor to work around deadlocks caused by SubDAGs.


### Slots on the worker pool

The `SubDagOperator` kicks off an entire DAG when it is put on a worker slot. Each task in the child DAG takes up a slot until the entire SubDAG has completed. The parent operator will take up a worker slot until each child task has completed. This could cause delays in other task processing

In mathematical terms, each SubDAG is behaving like a _vertex_ (a single point in a graph) instead of a _graph_.

Depending on the scale and infrastructure, a specialized queue can be added just for SubDAGs (assuming a `CeleryExecutor`), but a cleaner workaround is to avoid SubDAGs entirely.

## Grouping

<!-- markdownlint-disable MD033 -->
<iframe src="https://fast.wistia.net/embed/iframe/nb88lb9jza" title="branchpythonoperator Video" allow="autoplay; fullscreen" allowtransparency="true" frameborder="0" scrolling="no" class="wistia_embed" name="wistia_embed" allowfullscreen msallowfullscreen width="100%" height="100%" style="aspect-ratio:16/9"></iframe>

It's not uncommon to find yourself with hundreds of tasks in a DAG. Chances are, that's what you have right now. The problem is, the more tasks you have, the more difficult it becomes to maintain your DAG. This is where the concept of "grouping" comes in.

- What are the limitations of the SubDAGs?
- Should I still use them?
- Is there another way of grouping tasks in Airflow?

Find out on the [Astronomer's Grouping Course](https://academy.astronomer.io/airflow-grouping) for FREE today!

See you there!
