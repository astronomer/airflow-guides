---
title: "Using Task Groups in Airflow"
description: "Using Task Groups to build modular workflows in Airflow."
date: 2021-05-05T00:00:00.000Z
slug: "task-groups"
heroImagePath: null
tags: ["DAGs", "Subdags", "Task Groups", "Best Practices"]
---

## Overview

Prior to the release of [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) in December 2020, in order to group tasks and create modular workflows within Airflow users had to use SubDAGs. SubDAGs were a way of presenting a cleaner looking DAG by capitalizing on code patterns. For example, ETL DAGs usually share a pattern of tasks that extract data from a source, transform the data, and load it somewhere. The SubDAG can visually group the repetitive tasks into one UI task, making the pattern between tasks clearer.

However, SubDAGs are really DAGs embedded in your DAG which can create both performance and functional issues:
- When the SubDAG is triggered, the SubDAG and child tasks take up work slots until the entire SubDAG is complete. This can delay other task processing and, depending on your number of worker slots, can lead to deadlocking.
- SubDAGs have their own parameters, schedule, and enabled settings. When these are not consistent with their parent DAG, unexpected behavior can occur.

Unlike SubDAGs, [Task Groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#taskgroup) are just a UI grouping concept; allowing you to group and organize your tasks within your DAG's graph view without the added complexity and performance issues of SubDAGs (and with less code!).

In this guide, we'll walk through how to create task groups and show some example DAGs to demonstrate their scalability in more complicated DAGs.

## Creating Task Groups

To use Task Groups you'll need to use the following import statement.

```python 
from airflow.utils.task_group import TaskGroup
```

In our first example, we will create a basic task group with two tasks inside and set its dependencies. You can use dependency operators (`<<` and `>>`) on task groups the same way that you can with individual tasks. Dependencies applied to the task group are applied across the inner tasks.

Below we instantiate our task group with our `with statement` and provide a `group_id`. Inside our task group, we define our two tasks and their dependencies on each other. Then we add our dependencies to the task group, which automatically applies the same dependencies across the inner tasks. 

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

> **Note:** When your task is within a task group, your callable `task_id` will be the `task_id` prefixed with the `group_id` (i.e. `group_id.task_id`). This ensures the uniqueness of the task_id across the DAG. This is important to remember when calling specific tasks like for XCOM passing or branching operator decisions.

## Dynamically Generating Task Groups

Like tasks and [DAGs](https://www.astronomer.io/guides/dynamically-generating-dags), tasks groups can be dynamically generated to make use of patterns within your code. In an ETL DAG, you may call different API endpoints (i.e. a customer and contact table) that have similar downstream tasks but that can be processed independently. Here we can group the tasks by API endpoint, that like manually written task groups, can be drilled into from the Airflow UI to see specific tasks if needed. In the code below, we iterate over our desired groupings, creating multiple groups, with the same inner tasks where their passed parameters can change based on the `group_id`.

```python
for g_id in range(1,3):
    with TaskGroup(group_id=f'group{g_id}') as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        t1 >> t2
```

This shows the expanded view of the task groups we generated above.

![Dynamic Task Group](https://assets2.astronomer.io/main/guides/task-groups/dynamic_task_groups.png)

What if your task groups can't be processed independently? Next, we'll show how to call task groups and define dependencies between them.

## Ordering Tasks Groups

By default, using a loop to generate your task groups will put them in parallel. If your tasks groups are dependent on elements of another task group, you'll want to run them sequentially. For example, when loading tables with foreign keys, your primary table records will need to exist before you can load your foreign table.

In the example below, our group 3 that we're dynamically generating has foreign keys to both group 1 and group 2. We create an empty list and append our task group airflow objects as they are generated. Using this list we reference the task groups and define their dependencies on each other.

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

This shows the task group dependencies. 

![Task Group Dependencies](https://assets2.astronomer.io/main/guides/task-groups/task_group_dependencies.png)

## Conditioning on Task Groups

In the above example, we added an additional task to group 1 based on our `group_id`. This was to demonstrate that even though we're dynamically creating task groups and tasks to take advantage of patterns we can still introduce variations to the pattern while avoiding redundant code that builds each task group definition manually.

## Nesting Task Groups

For additional complexity, you can nest task groups. Building on our previous ETL example, when calling API endpoints we may need to process new records for each endpoint before we can process updates, as the new records need to be loaded first.

In the code below, our top task group represents our new record processing and our updated record processing. The sub group represents our API endpoint processing. 

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

This shows the expanded view of the nested task groups we generated above.

![Nested Task Groups](https://assets2.astronomer.io/main/guides/task-groups/nested_task_groups.png)

## Takeaways

Task groups are a dynamic and scalable UI grouping concept that solve for the functional and performance issues of SubDAGs. 

Ultimately task groups give you the flexibility to group and organize your tasks in a number of ways, to help guide your usage of them think about:
- What patterns exist in your DAG?
- How can simplifying your DAG's graph can better communicate its purpose?