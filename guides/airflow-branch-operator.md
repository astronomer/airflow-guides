---
title: "Branching in Airflow"
description: "Use Apache Airflow's BranchPythonOperator and ShortCircuitOperator to execute conditional branches in your workflow"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-branch-operator"
heroImagePath: null
tags: ["DAGs", "Operators", "Basics", "Tasks"]
---

## BranchPythonOperator

A powerful tool in Airflow is branching via the [BranchPythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/branchpythonoperator). The `BranchPythonOperator` is similar to the [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator) in that it takes a Python function as an input, but it returns a task id (or list of task_ids) to decide which part of the graph to go down. This can be used to iterate down certain paths in a DAG based off the result of a function.

```python
def return_branch(**kwargs):

    branches = ['branch_0,''branch_1', 'branch_2', 'branch_3', 'branch_4']

    return random.choice(branches)
```

In a DAG, the `BranchPythonOperator` will take this function as an argument:

```python
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from airflow.models import DAG
import random

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 5, 26),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def return_branch(**kwargs):
    branches = ['branch_0,''branch_1', 'branch_2', 'branch_3', 'branch_4']
    return random.choice(branches)

with DAG("branch_operator_guide", default_args=default_args, schedule_interval=None) as dag:
    kick_off_dag = DummyOperator(task_id='run_this_first')

    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=return_branch,
        provide_context=True)

    kick_off_dag >> branching

    for i in range(0, 5):
        d = DummyOperator(task_id='branch_{0}'.format(i))
        for j in range(0, 3):
            m = DummyOperator(task_id='branch_{0}_{1}'.format(i, j))
            d >> m
        branching >> d
```

![skipped](https://assets2.astronomer.io/main/guides/branching.png)

The DAG will proceed based on the output of the function passed in.

> Note: You can't have an empty path when skipping tasks - the `skipped` state will apply to all tasks immediately downstream of whatever task is skipped. Depending on your use case, it may make sense to add a `DummyOperator` downstream of a task that can be skipped before the branches from the `BranchPythonOperator` meet.

Under the hood, the `BranchPythonOperator` simply inherits the `PythonOperator`:

```python
class BranchPythonOperator(PythonOperator, SkipMixin):
    """
    Allows a workflow to "branch" or follow a path following the execution
    of this task.
    It derives the PythonOperator and expects a Python function that returns
    a single task_id or list of task_ids to follow. The task_id(s) returned
    should point to a task directly downstream from {self}. All other "branches"
    or directly downstream tasks are marked with a state of ``skipped`` so that
    these paths can't move forward. The ``skipped`` states are propagated
    downstream to allow for the DAG state to fill up and the DAG run's state
    to be inferred.
    """
    def execute(self, context):
        branch = super().execute(context)
        self.skip_all_except(context['ti'], branch)

```

`https://github.com/apache/airflow/blob/master/airflow/operators/python_operator.py#L133`

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
