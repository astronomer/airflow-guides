---
title: "Managing Dependencies in Apache Airflow"
description: "An overview of dependencies and triggers in Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "managing-dependencies"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dependencies.png"
tags: ["Best Practices", "Dependencies", "Basics"]
---

## Overview

Dependencies are one of Airflow's most powerful and popular features - they define the [relationships between tasks](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html#relationships).  Dependencies allow you to define flexible pipelines in Airflow that follow data engineering best practices by keeping your tasks atomic. 

In this guide we'll cover the many ways you can implement dependencies in Airflow, including:

- Basic task dependencies
- Dynamically setting dependencies
- Dependencies with Task Groups
- Dependencies with the TaskFlow API
- Trigger rules

For a detailed presentation of all these topics, check out our webinar on [managing dependencies in Airflow](https://www.astronomer.io/events/webinars/manage-dependencies-between-airflow-deployments-dags-tasks/). 

Note that this guide focuses on within-DAG dependencies (i.e. dependencies between tasks in the same DAG). If you are looking to implement dependencies _between DAGs_, check out our guide on [cross-DAG dependencies](https://www.astronomer.io/guides/cross-dag-dependencies).

## Basic Dependencies

Basic dependencies between Airflow tasks can be set in two ways:

- Using bitshift operators `<<` and `>>`
- Using the `set_upstream` and `set_downstream` methods

For example, if we have a DAG with four sequential tasks like the screenshot below, the dependencies can be set in four ways:

![title](https://assets.astronomer.io/website/img/guides/simple_scheduling.png)

- `t0.set_downstream(t1)`<br> `t1.set_downstream(t2)` <br> `t2.set_downstream(t3)`<br> <br>
- `t3.set_upstream(t2)` <br> `t2.set_upstream(t1)` <br> `t1.set_upstream(t0)`<br> <br>
- `t0 >> t1 >> t2 >> t3` <br> <br>
- `t3 << t2 << t1 << t0`

All of these methods are equivalent, and which you choose is a matter of personal preference. Best practice is to use one method consistently (i.e. don't mix bitshift operators and `set_upstream`/`set_downstream`).

You can also use lists or tuples to set parallel dependencies. For example: 

- `t0 >> t1 >> (t2, t3)`
- `t0 >> t1 >> [t2, t3]`

Both of these are equivalent, and set `t2` and `t3` downstream of t1. 

![title](https://assets.astronomer.io/website/img/guides/simple_scheduling.png)

Note that you cannot set dependencies between lists (e.g. `[t0, t1] >> [t2, t3]` will throw an error). If you need to set parallel cross-dependencies in this manner, you can use Airflow's [`chain` function](https://github.com/apache/airflow/blob/main/airflow/models/baseoperator.py#L1650). 


## Dynamically Setting Dependencies

For a large number of tasks, dependencies can be set in loops:

![title](https://assets.astronomer.io/website/img/guides/loop_dependencies.png)

Recall that tasks are identified by their `task_id` and associated `DAG` object - not by the type of operator. Consider this:

```python
with dag:

    final_task = DummyOperator(task_id='final')

    for i in range(0, 3):
        d1 = DummyOperator(task_id='task_{0}'.format(i))
        for j in range(0, 3):
            d2 = PythonOperator(task_id='task_{0}_{1}'.format(i, j),
                                python_callable=test_callable,
                                provide_context=True)

            d1 >> d2 >> final_task
```


## Dependencies with Task Groups

[Task groups](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#taskgroups) are a UI grouping concept released with Airflow 2 that can visually group tasks in the Airflow UI. For more on task groups in general, including how to create them and when to use them, check out our [task groups guide](https://www.astronomer.io/guides/task-groups).

When working with dependencies within task groups, it is important to note that dependencies can be set both inside and outside the group. For example, in the DAG code below we have a start task, a task group with two dependent tasks, and an end task that need to happen sequentially. The dependencies between the two tasks in the task group are set within the task group's context (`t1 >> t2`). The dependencies between the task group and the start/end tasks are set within the DAG's context (`t0 >> tg1 >> t3`).

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

This code results in a DAG that looks like this:



For more examples of setting dependencies within different types of task groups, check out the guide linked above.

## Dependencies with the TaskFlow API

## Trigger Rules

By default, workflows are triggered when upstream tasks have succeeded. However, more complex trigger rules can be implemented.

Operators have a [trigger_rule](https://airflow.apache.org/concepts.html#trigger-rules) that defines how the task gets triggered. The default `all_success` rule dictates that the task should be triggered when all upstream dependent tasks have reached the `success` state.

Each trigger rule can have specific use cases: <br> <br>
**all_success:** (default) all parents have succeeded <br>
**all_failed:** all parents are in a failed or upstream\_failed state <br>
**all_done:** all parents are done with their execution <br>
**one_failed:** fires as soon as at least one parent has failed, it does not wait for all parents to be done <br>
**one_success:** fires as soon as at least one parent succeeds, it does not wait for all parents to be done <br>
**dummy:** dependencies are just for show, trigger at will <br>

TriggerRules are defined as Airflow Utils:

### Different Use Cases

_Extendability vs Safety_

#### The `one_failed` rule

When you have a critically important but _brittle_ task in a workflow (i.e. a large machine learning job, some reporting task, etc.), a good safety check would be adding a task that handles the failure logic. This logic can be implemented dynamically based on how the DAG is being generated.

```python
# Define the tasks that are "brittle."
# Generally advisable when working with data drops from vendors/FTPs

job_info = [
    {
        'job_name': 'train_model',
        'brittle': True
    },
    {
        'job_name': 'execute_query',
        'brittle': False

    }]


# Define some failure handling

def fail_logic(**kwargs):
    # Implement fail_logic here.
    return


with dag:
    for job in job_info:
        d1 = DummyOperator(task_id=job['job_name'])

        # Generate a task based on a condition

        if job['brittle']:
            d2 = PythonOperator(task_id='{0}_{1}'.format(job['job_name'],
                                                         'fail_logic',),
                                python_callable=fail_logic,
                                provide_context=True,
                                trigger_rule=TriggerRule.ONE_FAILED)
            d1 >> d2
        for i in range(0, 5):
            downstream = DummyOperator(
                task_id='{0}_{1}'.format(job['job_name'], i))

            d1 >> downstream
```

![one_failed](https://assets.astronomer.io/website/img/guides/fail_logic_notification.png)

**Note:** Similar logic can be implemented by specifying an `on_failure_callback` if using a [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator). The `trigger_rule` is better used when triggering a custom operator.

Though trigger rules can be convenient, they can also be unsafe and the same logic can usually be implemented using safer features.

A common use case of exotic trigger rules is a task downstream of all  other tasks that kicks off the necessary logic.

#### The `one_success` rule

This rule is particularly helpful when setting up a "safety check" DAG - a DAG that runs as a safety check to all your data. If one of the "disaster checks" come back as `True`, the downstream disaster task can run the necessary logic.

**Note:** The same logic can be implemented with the `one_failed` rule.

#### The `all_failed` rule

`all_failed` tells a task to run when all upstream tasks have failed and can be used to execute a fail condition for a workflow.

The workflow may look something like this:
![all_failed](https://assets.astronomer.io/website/img/guides/trigger_notification_fail.png)

**Note:** The final task was set to `skipped`

Once again, the same functionality can be achieved by using the [BranchPythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/branchpythonoperator), a [TriggerDagRunOperator](https://registry.astronomer.io/providers/apache-airflow/modules/triggerdagrunoperator), or just configuring reporting in more specific way.

### Triggers with LatestOnlyOperator

When scheduling tasks with complex trigger rules with dates in the past, there may be instances where certain tasks can run independently of time and others shouldn't.  The [LatestOnlyOperator](https://registry.astronomer.io/providers/apache-airflow/modules/latestonlyoperator) handles this scenario.

The parameters can also be set in the DAG configuration as above - the scheduling may get a bit messy, but it can save computing resources and add a layer of safety.

```python
job_info = [
    {
        'job_name': 'train_model',
        'brittle': True,
        'latest_only': True
    },
    {
        'job_name': 'execute_query',
        'brittle': False,
        'latest_only': False

    }]

with dag:
    start = DummyOperator(task_id='kick_off_dag')
    for job in job_info:
        d1 = DummyOperator(task_id=job['job_name'])

        # Generate a task based on a condition

        if job['brittle']:
            d2 = PythonOperator(task_id='{0}_{1}'.format(job['job_name'],
                                                         'fail_logic',),
                                python_callable=fail_logic,
                                provide_context=True,
                                trigger_rule=TriggerRule.ONE_FAILED)
            d1 >> d2
        start >> d1

        if job['latest_only']:
            latest_only = LatestOnlyOperator(task_id='latest_only_{0}'
                                             .format(job['job_name']))
            d1 >> latest_only

        for i in range(0, 5):
            downstream = DummyOperator(
                task_id='{0}_{1}'.format(job['job_name'], i))
            if job['latest_only']:
                latest_only >> downstream
            else:
                d1 >> downstream
```

![skipped](https://assets.astronomer.io/website/img/guides/trigger_rule_latest_only_skipped.png)
<br>
Computing resources would be saved on past DAG runs.
<br>

![tree](https://assets.astronomer.io/website/img/guides/trigger_latest_only_tree.png)
The latest run would execute the necessary downstream logic.
