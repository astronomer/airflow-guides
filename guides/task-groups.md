---
title: "Using Task Groups in Airflow"
description: "Using Task Groups to build modular workflows in Airflow."
date: 2021-05-05T00:00:00.000Z
slug: "task-groups"
heroImagePath: null
tags: ["DAGs", "Subdags", "Task Groups", "Best Practices"]
---

## Overview

Prior to the release of [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) in December 2020, the only way to group tasks and create modular workflows within Airflow was to use SubDAGs. SubDAGs were a way of presenting a cleaner looking DAG by capitalizing on code patterns. For example, ETL DAGs usually share a pattern of tasks that extract data from a source, transform the data, and load it somewhere. The SubDAG would visually group the repetitive tasks into one UI task, making the pattern between tasks clearer.

However, SubDAGs were really just DAGs embedded in other DAGs. This caused both performance and functional issues:

- When a SubDAG is triggered, the SubDAG and child tasks take up worker slots until the entire SubDAG is complete. This can delay other task processing and, depending on your number of worker slots, can lead to deadlocking.
- SubDAGs have their own parameters, schedule, and enabled settings. When these are not consistent with their parent DAG, unexpected behavior can occur.

Unlike SubDAGs, [Task Groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#taskgroup) are just a UI grouping concept. Starting in Airflow 2.0, you can use Task Groups to organize tasks within your DAG's graph view in the Airflow UI. This avoids the added complexity and performance issues of SubDAGs, all while using less code!

In this guide, we'll walk through how to create Task Groups and show some example DAGs to demonstrate their scalability.

## Creating Task Groups

To use Task Groups you'll need to use the following import statement.

```python 
from airflow.utils.task_group import TaskGroup
```


For our first example, we'll instantiate a Task Group using a `with` statement and provide a `group_id`. Inside our task group, we'll define our two tasks, `t1` and `t2`, and their respective dependencies. 

You can use dependency operators (`<<` and `>>`) on Task Groups in the same way that you can with individual tasks. Dependencies applied to a Task Group are applied across its tasks. In the following code, we'll add additional dependencies to `t0` and `t3` to the Task Group, which automatically applies the same dependencies across `t1` and `t2`:  

```python
t0 = DummyOperator(task_id='start')

# Start Task Group definition
with TaskGroup(group_id='group1') as tg1:
    t1 = DummyOperator(task_id='task1')
    t2 = DummyOperator(task_id='task2')

    t1 >> t2
# End Task Group definition
    
t3 = DummyOperator(task_id='end')

# Set Task Group's (tg1) dependencies
t0 >> tg1 >> t3
```

This animated visual shows the above example with the UI interactions of expanding and collapsing the Task Group.

![UI Task Group](https://assets2.astronomer.io/main/guides/task-groups/task_groups_ui.gif)

> **Note:** When your task is within a task group, your callable `task_id` will be the `task_id` prefixed with the `group_id` (i.e. `group_id.task_id`). This ensures the uniqueness of the task_id across the DAG. This is important to remember when calling specific tasks with XCOM passing or branching operator decisions.

## Dynamically Generating Task Groups

Like tasks and [DAGs](https://www.astronomer.io/guides/dynamically-generating-dags), tasks groups can be dynamically generated to make use of patterns within your code. In an ETL DAG, you may call different API endpoints (i.e. a customer and contact table) that have similar downstream tasks but that can be processed independently. Here we can group the tasks by API endpoint, that like manually written task groups, can be drilled into from the Airflow UI to see specific tasks if needed. In the code below, we iterate over our desired groupings which creates multiple groups, with the same inner tasks where their passed parameters can change based on the `group_id`.

```python
for g_id in range(1,3):
    with TaskGroup(group_id=f'group{g_id}') as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        t1 >> t2
```

This screenshot shows the expanded view of the Task Groups we generated above in the Airflow UI:

![Dynamic Task Group](https://assets2.astronomer.io/main/guides/task-groups/dynamic_task_groups.png)

What if your task groups can't be processed independently? Next, we'll show how to call task groups and define dependencies between them.

## Ordering Tasks Groups

By default, using a loop to generate your task groups will put them in parallel. If your tasks groups are dependent on elements of another task group, you'll want to run them sequentially. For example, when loading tables with foreign keys, your primary table records need to exist before you can load your foreign table.

In the example below, our group 3 that we're dynamically generating has foreign keys to both group 1 and group 2 so we'll want to process it last. We create an empty list and append our task group airflow objects as they are generated. Using this list we reference the task groups and define their dependencies to each other.

```python
groups = []
for g_id in range(1,4):
    tg_id = f'group{g_id}'
    with TaskGroup(group_id=tg_id) as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        t1 >> t2

        if tg_id == 'group1':
            t3 = DummyOperator(task_id='task3')
            t1 >> t3
                
        groups.append(tg1)

[groups[0] , groups[1]] >> groups[2]
```

The following screenshot shows how these Task Groups appear in the Airflow UI:

![Task Group Dependencies](https://assets2.astronomer.io/main/guides/task-groups/task_group_dependencies.png)

### Conditioning on Task Groups

In the above example, we added an additional task to `group1` based on our `group_id`. This was to demonstrate that even though we're dynamically creating Task Groups to take advantage of patterns, we can still introduce variations to the pattern while avoiding code redundancies from building each task group definition manually.

## Nesting Task Groups

For additional complexity, you can nest Task Groups. Building on our previous ETL example, when calling API endpoints we may need to process new records for each endpoint before we can process updates to them.

In the following code, our top-level Task Groups represent our new and updated record processing, while the nested Task Groups represent our API endpoint processing:

```python
groups = []
for g_id in range(1,3):
    with TaskGroup(group_id=f'group{g_id}') as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        sub_groups = []
        for s_id in range(1,3):
            with TaskGroup(group_id=f'sub_group{s_id}') as tg2:
                st1 = DummyOperator(task_id='task1')
                st2 = DummyOperator(task_id='task2')

                st1 >> st2
                sub_groups.append(tg2)

        t1 >> sub_groups >> t2
        groups.append(tg1)

groups[0] >> groups[1]
```

The following screenshot shows the expanded view of the nested Task Groups in the Airflow UI:

![Nested Task Groups](https://assets2.astronomer.io/main/guides/task-groups/nested_task_groups.png)

## Takeaways

Task Groups are a dynamic and scalable UI grouping concept that eliminate the functional and performance issues of SubDAGs. 

Ultimately, Task Groups give you the flexibility to group and organize your tasks in a number of ways. To help guide your implementation of Task Groups, think about:

- What patterns exist in your DAGs?
- How can simplifying your DAG's graph better communicate its purpose?
