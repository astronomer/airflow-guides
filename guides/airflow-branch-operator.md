---
title: "Branching in Airflow"
description: "Use Apache Airflow's BranchPythonOperator and ShortCircuitOperator to execute conditional branches in your workflow"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-branch-operator"
heroImagePath: null
tags: ["DAGs", "Operators", "Basics", "Tasks"]
---

## Overview

When designing your data pipelines, you may encounter use cases that require more complex task flows than "Task A > Task B > Task C." For example, you may have a use case where you need to decide between multiple tasks to execute based on the results of an upstream task. Or you may have a case where part of your pipeline should only run under certain external conditions. Fortunately, Airflow has multiple options for building conditional logic and/or branching into your DAGs.

In this guide, we'll cover examples using the `BranchPythonOperator` and `ShortCircuitOperator`, other available branching operators, and additional resources for implementing conditional logic in your Airflow DAGs.

## BranchPythonOperator

One of this simplest ways to implement branching in Airflow is to use the [BranchPythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/branchpythonoperator). Like the [`PythonOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator), the `BranchPythonOperator` takes a Python function as an input. However, the `BranchPythonOperator's` input function must return a list of task IDs that the DAG should proceed with based on some logic. 

For example, we can pass the following function that returns one set of task IDs if the result is greater than 0.5 and a different set if the result is less than or equal to 0.5:

```python
def choose_branch(**kwargs, result):
    if result > 0.5:
        return ['task_a', 'task_b']
    return ['task_c']
```

In general, the `BranchPythonOperator` is a good choice if your branching logic can be easily implemented in a simple Python function.

> Note: The full example code in this section, as well as other examples using the `BranchPythonOperator`, can be found on the [Astronomer Registry](https://registry.astronomer.io/dags/example-branch-operator).

Looking at how to use this operator in a DAG, consider the following example:

```python
"""Example DAG demonstrating the usage of the BranchPythonOperator."""

import random
from datetime import datetime

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.edgemodifier import Label
from airflow.utils.trigger_rule import TriggerRule

with DAG(
    dag_id='example_branch_operator',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    schedule_interval="@daily",
    tags=['example', 'example2'],
) as dag:
    run_this_first = DummyOperator(
        task_id='run_this_first',
    )

    options = ['branch_a', 'branch_b', 'branch_c', 'branch_d']

    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=lambda: random.choice(options),
    )
    run_this_first >> branching

    join = DummyOperator(
        task_id='join',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    for option in options:
        t = DummyOperator(
            task_id=option,
        )

        dummy_follow = DummyOperator(
            task_id='follow_' + option,
        )

        # Label is optional here, but it can help identify more complex branches
        branching >> Label(option) >> t >> dummy_follow >> join
```

In this DAG, we have a simple `lambda` function that randomly chooses between four branches. In the following DAG run screenshot, where `branch_b` was randomly chosen, we see that the two tasks in `branch_b` were successfully run while the others were skipped.

![Branching](https://assets2.astronomer.io/main/guides/airflow-branching/branching.png)

Note that if you have downstream tasks that need to run regardless of which branch is taken, like the `join` task in our example above, you need to update the trigger rule appropriately. The default trigger rule in Airflow is `ALL_SUCCESS`, which means that if upstream tasks are skipped, then the downstream task will not run. In this case, we chose `NONE_FAILED_MIN_ONE_SUCCESS` to indicate that the task should run as long as one upstream task succeeded and no tasks failed.

Finally, note that with the `BranchPythonOperator`, your Python callable *must* return at least one task ID for whichever branch is chosen (i.e. it can't return nothing). If one of the paths in your branching should do nothing, you can use a `DummyOperator` in that branch.

## ShortCircuitOperator

Another option for implementing conditional logic in your DAGs is the [ShortCircuitOperator](https://registry.astronomer.io/providers/apache-airflow/modules/shortcircuitoperator). This operator also takes a Python callable that returns `True` or `False` based on logic implemented for your use case. If `True` is returned, the DAG will continue, and if `False` is returned, all downstream tasks will be skipped.

The `ShortCircuitOperator` is best used in cases where you know that part of your DAG runs only occasionally. For example, maybe your DAG runs daily, but some tasks should only run on Sundays. Or maybe your DAG orchestrates a machine learning model, and tasks that publish the model should only be run if a certain accuracy is reached after training. This type of logic can also be implemented with the `BranchPythonOperator`, but that operator requires a task ID to be returned. The `ShortCircuitOperator` can be cleaner in cases where the conditional logic equates to "run or not" as opposed to "run this or that".

The following DAG shows an example of how to implement the `ShortCircuitOperator`:

```python
"""Example DAG demonstrating the usage of the ShortCircuitOperator."""
from datetime import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import ShortCircuitOperator

with DAG(
    dag_id='example_short_circuit_operator',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    cond_true = ShortCircuitOperator(
        task_id='condition_is_True',
        python_callable=lambda: True,
    )

    cond_false = ShortCircuitOperator(
        task_id='condition_is_False',
        python_callable=lambda: False,
    )

    ds_true = [DummyOperator(task_id='true_' + str(i)) for i in [1, 2]]
    ds_false = [DummyOperator(task_id='false_' + str(i)) for i in [1, 2]]

    chain(cond_true, *ds_true)
    chain(cond_false, *ds_false)

```

> Note: The full example code in this section, as well as other examples using the `ShortCircuitOperator`, can be found on the [Astronomer Registry](https://registry.astronomer.io/dags/example-short-circuit-operator).

In this DAG we have two short circuits, one which will always return `True` and one which will return `False`. When we run the DAG, we can see that tasks downstream of the `True` condition operator ran, while tasks downstream of the `False` condition operator were skipped.

![Short Circuit](https://assets2.astronomer.io/main/guides/airflow-branching/short_circuit.png)

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/events/webinars/best-practices-writing-dags-airflow-2?banner=learn-more-banner-click">Best Practices for Writing DAGs in Airflow 2 Webinar</a></li>
    <li data-icon="→"><a href="/events/webinars/manage-dependencies-between-airflow-deployments-dags-tasks?banner=learn-more-banner-click">Manage Dependencies Between Airflow Deployments, DAGs, and Tasks Webinar</a></li>
    <li data-icon="→"><a href="/blog/machine-learning-pipeline-orchestration?banner=learn-more-banner-click">Machine Learning Pipeline Orchestration</a></li>
</ul>

## Other Branch Operators

Airflow offers a few other branching operators that work similarly to the `BranchPythonOperator` but for more specific contexts: 

- [`BranchSQLOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/branchsqloperator): Branches based on whether a given SQL query returns `true` or `false`
- [`BranchDayOfWeekOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/branchdayofweekoperator): Branches based on whether the current day of week is equal to a given `week_day` parameter
- [`BranchDateTimeOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/branchdatetimeoperator): Branches based on whether the current time is between `target_lower` and `target_upper` times

All of these operators take `follow_task_ids_if_true` and `follow_task_ids_if_false` parameters which provide the list of task(s) to include in the branch based on the logic returned by the operator.

## Additional Branching Resources

<!-- markdownlint-disable MD033 -->
<iframe src="https://fast.wistia.net/embed/iframe/9c4267f3e4" title="branchpythonoperator Video" allow="autoplay; fullscreen" allowtransparency="true" frameborder="0" scrolling="no" class="wistia_embed" name="wistia_embed" allowfullscreen msallowfullscreen width="100%" height="450"></iframe>

There is much more to the BranchPythonOperator than simply choosing one task over another.

- What if you want to trigger your tasks only on specific days? And not on holidays?  
- What if you want to trigger a DAG Run only if the previous one succeeded?

For more guidance and best practices on common use cases like the ones above, try out Astronomer's
[Academy Course on Branching](https://academy.astronomer.io/branching-course) for free today.

See you there! ❤️ 
