---
title: "Branching in Airflow"
description: "Use Apache Airflow's BranchPythonOperator and ShortCircuitOperator to execute conditional branches in your workflow"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-branch-operator"
heroImagePath: null
tags: ["DAGs", "Operators", "Basics", "Tasks"]
---

## Overview

When designing your data pipelines, you may encounter use cases that require more complex task dependencies than "Task A preceeds Task B which preceeds Task C." For example, you may have a use case where you need to decide between multiple tasks to execute based on the results of an upstream task. Or you may have a case where *part* of your pipeline should only run under certain conditions. Fortunately, Airflow has multiple options for building conditional logic and/or branching into your DAGs.

In this guide, we'll cover examples using the `BranchPythonOperator` and `ShortCircuitOperator`, other available branching operators, and additional resources for implementing conditional logic in your Airflow DAGs.

## BranchPythonOperator

A powerful tool in Airflow is branching via the [BranchPythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/branchpythonoperator). The `BranchPythonOperator` is similar to the [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator) in that it takes a Python function as an input, but it returns a task id (or list of task_ids) to decide which part of the graph to go down. This can be used to iterate down certain paths in a DAG based off the result of a function.

> Note: The full example code in this section, as well as other examples using the `BranchPythonOperator`, can be found on the [Astronomer Registry](https://registry.astronomer.io/dags/example-branch-operator).


In a DAG, the `BranchPythonOperator` will take this function as an argument:

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

![skipped](https://assets2.astronomer.io/main/guides/branching.png)

The DAG will proceed based on the output of the function passed in.

## ShortCircuitOperator

The `BranchPythonOperator` is great for any sort of _conditional_ logic to determine which dependency to respect. Other use cases may call for the [ShortCircuitOperator](https://registry.astronomer.io/providers/apache-airflow/modules/shortcircuitoperator):

```python
class ShortCircuitOperator(PythonOperator, SkipMixin):
    """
    Allows a workflow to continue only if a condition is met. Otherwise, the
    workflow "short-circuits" and downstream tasks are skipped.
    The ShortCircuitOperator is derived from the PythonOperator. It evaluates a
    condition and short-circuits the workflow if the condition is False. Any
    downstream tasks are marked with a state of "skipped". If the condition is
    True, downstream tasks proceed as normal.
    The condition is determined by the result of `python_callable`.
    """
    def execute(self, context):
        condition = super().execute(context)
        self.log.info("Condition result is %s", condition)

        if condition:
            self.log.info('Proceeding with downstream tasks...')
            return

        self.log.info('Skipping downstream tasks...')

        downstream_tasks = context['task'].get_flat_relatives(upstream=False)
        self.log.debug("Downstream task_ids %s", downstream_tasks)

        if downstream_tasks:
            self.skip(context['dag_run'], context['ti'].execution_date, downstream_tasks)

        self.log.info("Done.")
```

Notice that given the base `PythonOperator`, children operators can be easily written to incorporate more specific logic.

## Other Branch Operators

SQL branch operator

## Additional Branching Resources

<!-- markdownlint-disable MD033 -->
<iframe src="https://fast.wistia.net/embed/iframe/9c4267f3e4" title="branchpythonoperator Video" allow="autoplay; fullscreen" allowtransparency="true" frameborder="0" scrolling="no" class="wistia_embed" name="wistia_embed" allowfullscreen msallowfullscreen width="100%" height="450"></iframe>

There is much more to the BranchPythonOperator than simply choosing one task over another.

- What if you want to trigger your tasks only on specific days? And not on holidays?  
- What if you want to trigger a DAG Run only if the previous one succeeded?

For more guidance and best practices on common use cases like the ones above, try out Astronomer's
[Academy Course on Branching](https://academy.astronomer.io/branching-course) for free today.

See you there! ❤️ 
