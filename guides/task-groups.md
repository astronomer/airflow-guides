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

Unlike SubDAGs, [Task Groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#taskgroups) are just a UI grouping concept. Starting in Airflow 2.0, you can use Task Groups to organize tasks within your DAG's graph view in the Airflow UI. This avoids the added complexity and performance issues of SubDAGs, all while using less code!

In this guide, we'll walk through how to create Task Groups and show some example DAGs to demonstrate their scalability.

## Creating Task Groups

To use Task Groups you'll need to use the following import statement.

```python 
from airflow.utils.task_group import TaskGroup
```

For our first example, we'll instantiate a Task Group using a `with` statement and provide a `group_id`. Inside our Task Group, we'll define our two tasks, `t1` and `t2`, and their respective dependencies. 

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

In the Airflow UI, Task Groups look like tasks with blue shading. When we expand `group1` by clicking on it, we see blue circles where the Task Group's dependencies have been applied to the grouped tasks. The task(s) immediately to the right of the first blue circle (`t1`) get the group's upstream dependencies and the task(s) immediately to the left (`t2`) of the last blue circle get the group's downstream dependencies. 

![UI Task Group](https://assets2.astronomer.io/main/guides/task-groups/task_groups_ui.gif)

> **Note:** When your task is within a Task Group, your callable `task_id` will be the `task_id` prefixed with the `group_id` (i.e. `group_id.task_id`). This ensures the uniqueness of the task_id across the DAG. This is important to remember when calling specific tasks with XCOM passing or branching operator decisions.

## Using the Task Group Decorator

Another way of defining Task Groups in your DAGs is by using the Task Group decorator. Note that this feature requires Airflow 2.1+. The Task Group decorator works like other [decorators in Airflow](https://www.astronomer.io/guides/airflow-decorators) by allowing you to define your Task Group with less boilerplate code using the TaskFlow API. Using Task Group decorators doesn't change the functionality of Task Groups, but if you already use task decorators in your DAGs then they can make your code formatting more consistent.

To use the decorator, add `@task_group` before a Python function which calls the functions of tasks that should go in the Task Group. For example:

```python
@task_group(group_id="tasks")
def my_independent_tasks():
    task_a()
    task_b()
    task_c()
```

This function creates a Task Group with three independent tasks that are defined elsewhere in the DAG.

You can also create a Task Group of dependent tasks:

```python
@task_group(group_id="tasks")
def my_dependent_tasks():
    return task_a(task_b(task_c()))
```

The following DAG shows a full example implementation of the Task Group decorator, including passing data between tasks before and after the Task Group:

```python
import json
from airflow.decorators import dag, task, task_group

import pendulum

@dag(schedule_interval=None, start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), catchup=False)

def task_group_example():

    @task(task_id='extract', retries=2)
    def extract_data():
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'
        order_data_dict = json.loads(data_string)
        return order_data_dict

    @task()
    def transform_sum(order_data_dict: dict):
        total_order_value = 0
        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    @task()
    def transform_avg(order_data_dict: dict):
        total_order_value = 0
        for value in order_data_dict.values():
            total_order_value += value
            avg_order_value = total_order_value / len(order_data_dict)

        return {"avg_order_value": avg_order_value}

    @task_group
    def transform_values(order_data_dict):
        return {'avg': transform_avg(order_data_dict), 'total': transform_sum(order_data_dict)}

    @task()
    def load(order_values: dict):
        print(f"Total order value is: {order_values['total']['total_order_value']:.2f} and average order value is: {order_values['avg']['avg_order_value']:.2f}")

    load(transform_values(extract_data()))

    
task_group_example = task_group_example()
```

The resulting DAG looks like this:

![Decorated Task Group](https://assets2.astronomer.io/main/guides/task-groups/decorated_task_group.png)

There are a few things to consider when using the Task Group decorator:

- If downstream tasks require the output of tasks that are in the Task Group decorator, then the Task Group function must return a result. In the previous example, we return a dictionary with two values, one from each of the tasks in the Task Group, that are then passed to the downstream `load()` task.
- If your Task Group function returns an output, you can simply call the function from your DAG with the TaskFlow API like in the previous example. If your Task Group function does not return any output, you must use bitshift operators (`<<` or `>>`) to define dependencies to the Task Group like you would with a standard task.


## Dynamically Generating Task Groups

[Just like with DAGs](https://www.astronomer.io/guides/dynamically-generating-dags), Task Groups can be dynamically generated to make use of patterns within your code. In an ETL DAG, you might have similar downstream tasks that can be processed independently, such as when you call different API endpoints for data that needs to be processed and stored in the same way. For this use case, we can dynamically generate Task Groups by API endpoint. Just like with manually written Task Groups, generated Task Groups can be drilled into from the Airflow UI to see specific tasks. 

In the code below, we use iteration to create multiple Task Groups. While the tasks and dependencies remain the same across Task Groups, we can change which parameters are passed in to each Task Group based on the `group_id`:

```python
for g_id in range(1,3):
    with TaskGroup(group_id=f'group{g_id}') as tg1:
        t1 = DummyOperator(task_id='task1')
        t2 = DummyOperator(task_id='task2')

        t1 >> t2
```

This screenshot shows the expanded view of the Task Groups we generated above in the Airflow UI:

![Dynamic Task Group](https://assets2.astronomer.io/main/guides/task-groups/dynamic_task_groups.png)

What if your Task Groups can't be processed independently? Next, we'll show how to call Task Groups and define dependencies between them.

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/guides/airflow-passing-data-between-tasks" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Passing Data Between Airflow Tasks', spottedCompany: window.spottedCompany })">Passing Data Between Airflow Tasks</a></li>
    <li data-icon="→"><a href="/events/webinars/taskflow-api-airflow-2.0" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'TaskFlow API in Airflow 2.0 Webinar', spottedCompany: window.spottedCompany })">TaskFlow API in Airflow 2.0 Webinar</a></li>
    <li data-icon="→"><a href="/blog/machine-learning-pipelines-everything-you-need-to-know" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Machine Learning Pipelines: Everything You Need to Know', spottedCompany: window.spottedCompany })">Machine Learning Pipelines: Everything You Need to Know</a></li>
    <li data-icon="→"><a href="/blog/big-data-architecture" onclick="analytics.track('Clicked Learn More List Link', { page: location.href, buttonText: 'Big Data Architecture: Core Components, Use Cases and Limitations', spottedCompany: window.spottedCompany })">Big Data Architecture: Core Components, Use Cases and Limitations</a></li>
</ul>

## Ordering Task Groups

By default, using a loop to generate your Task Groups will put them in parallel. If your Task Groups are dependent on elements of another Task Group, you'll want to run them sequentially. For example, when loading tables with foreign keys, your primary table records need to exist before you can load your foreign table.

In the example below, our third dynamically generated Task Group has a foreign key constraint on both our first and second dynamically generated Task Groups, so we'll want to process it last. To do this, we'll create an empty list and append our Task Group objects as they are generated. Using this list, we can reference the Task Groups and define their dependencies to each other:

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

In the above example, we added an additional task to `group1` based on our `group_id`. This was to demonstrate that even though we're dynamically creating Task Groups to take advantage of patterns, we can still introduce variations to the pattern while avoiding code redundancies from building each Task Group definition manually.

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
