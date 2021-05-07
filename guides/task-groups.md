---
title: "Using Task Groups in Airflow"
description: "Using Task Groups to build modular workflows in Airflow."
date: 2021-05-05T00:00:00.000Z
slug: "task-groups"
heroImagePath: null
tags: ["DAGs", "Subdags", "Task Groups", "Best Practices"]
---

## Task Groups Overview

In December 2020, [Task Groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#taskgroup) were introduced with the release of [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0). They are a UI grouping concept intended to replace SubDAGS.

SubDAGs are DAGs embedded in DAGs whereas Task Groups exist in your original DAG. Tasks Groups allow you to group and organize your tasks within your DAG's graph view, without the added complexity and performance issues of SubDAGs (i.e. deadlocking, worker slots, etc.)

### Creating Task Groups

To use Task Groups you'll need to use the following import statement.
```python 
    from airflow.utils.task_group import TaskGroup
```

When creating Task Groups, you can use the same dependency operators (<< and >>), these will be applied to all the tasks within the grouping.

```python
    t0 = DummyOperator(task_id='start')

    # Start Task Group definition
    with TaskGroup(group_id='group1') as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        t1 >> t2
    # End Task Group definition
    
    t3 = DummyOperator(task_id='end')

    t0 >> tg1 >> t3
```
This animated gif shows the above example with the UI interactions of expanding and collapsing the Task Group.

![UI Task Group](https://assets2.astronomer.io/main/guides/task-groups/task-groups-ui.gif)

**Note:** When your task is within a task group, your callable task ID will be group_id.task_id. This ensures the uniqueness of the task_id across the DAG. This is important to remember when calling specific tasks like for XCOM passing or branching operator decisions. 

#### Dynamically Generating Task Groups

Task Groups can be dynamically generated to make use of patterns within your code. 

When calling an API, you may call a number of objects that have similar downstream tasks. This allows you to group by API objects for a simpler UI experience, that can be drilled into to see specific task statuses.

```python
    for g_id in range(1,3):
        with TaskGroup(group_id=f'group{g_id}') as tg1:
            t1 = DummyOperator(task_id='task1')
            t2 = DummyOperator(task_id='task2')

            t1 >> t2
```
![Dynamic Task Group](https://assets2.astronomer.io/main/guides/task-groups/dynamic_task_groups.png)

##### Ordering Tasks Groups

By default using a loop to generate your tasks groups, will put them in parallel. In cases where your tasks groups are dependent on elements of another task group then you'll want to run them sequentially. For example, when processing tables with foreign keys your primary table records will need to exist before you can load your foreign table.

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
![Task Group Dependencies](https://assets2.astronomer.io/main/guides/task-groups/task_group_dependencies.png)

#### Nesting Task Groups

For additional complexity, you can nest Task Groups. 

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
![Nested Task Groups](https://assets2.astronomer.io/main/guides/task-groups/nested_task_groups.png)
