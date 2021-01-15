---
title: "Managing Dependencies in Apache Airflow"
description: "An overview of dependencies and triggers in Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "managing-dependencies"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dependencies.png"
tags: ["Best Practices", "Dependencies", "Basics"]
---
<!-- markdownlint-disable-file -->
## Managing Dependencies

_The logic between tasks_

Each DAG object contains a set of tasks that are related by dependencies - the "directed" in directed acyclic graph.

Dependencies are one of Airflow's most powerful and popular features - they allow for previously long, brittle jobs to be broken down into granular parts that are safer, more modular, and reusable.

### Simple Dependencies

Dependencies can be set syntactically or through bitshift operators.

![title](https://assets.astronomer.io/website/img/guides/simple_scheduling.png)

This logic can be set three ways:

- `d1.set_downstream(d2)`<br> `d2.set_downstream(d3)` <br> `d3.set_downstream(d4)`<br> <br>
- `d4.set_upstream(d3)` <br> `d3.set_upstream(d2)` <br> `d2.set_upstream(d1)`<br> <br>
- `d1 >> d2 >> d3 >> d4` <br> <br>
- `d4 << d3 << d2 << d1`


To set groups of dependencies, you can use lists or tuples as well.

```python
d1 >> d2 >> (d3, d4)

d1 >> d2 >> [d3, d4]
```

Both of these are equivalent, and set `d3` and `d4` downstream of d2.

All three are in line with best practice as long as it is written consistently - do **not** do:

- `d1.set_downstream(d2)`<br> `d2 >>d3` <br> `d4.set_upstream(d3)`<br>


### Dynamically Setting Dependencies

For a large number of tasks, dependencies can be set in loops:

![title](https://assets.astronomer.io/website/img/guides/loop_dependencies.png)

Recall that tasks are identified by their `task_id` and associated `DAG` object - not by the type of operator. Consider this:

```python
with dag:

    final_task = DummyOperator(task_id='final')

    for i in range(0, 3):
        d1 = DummyOperator(task_id='task_{0}'.format(i))
        for j in range(0, 3):
            d2 = PythonOperator(task_id='task_{0}'.format(i),
                                python_callable=test_callable,
                                provide_context=True)

            d1 >> d2 >> final_task
```

_ What happens here?_

### Trigger Rules

_Complex Dependencies_

By default, workflows are triggered when upstream tasks have succeeded. However, more complex trigger rules can be implemented.

Operators have a [trigger_rule](https://airflow.apache.org/concepts.html#trigger-rules) that defines how the task gets triggered. The default `all_success` rule dictates that the task should be triggered when all upstream dependent tasks have reached the `success` state.

Each trigger rule can have specific use cases: <br> <br>
**all_success:** (default) all parents have succeeded <br>
**all_failed:** all parents are in a failed or upstream_failed state <br>
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

**Note:** Similar logic can be implemented by specifying an `on_failure_callback` if using a PythonOperator. The `trigger_rule` is better used when triggering a custom operator.

Though trigger rules can be convenient, they can also be unsafe and the same logic can usually be implemented using safer features.

A common use case of exotic trigger rules is a task downstream of all  other tasks that kicks off the necessary logic.

#### The `one_success` rule

This rule is particularly helpful when setting up a "safety check" DAG - a DAG that runs as a safetycheck to all your data. If one of the "disaster checks" come back as `True`, the downstream disaster task can run the necessary logic.

**Note:** The same logic can be implemented with the `one_failed` rule.

#### The `all_failed` rule

`all_failed` tells a task to run when all upstream tasks have failed and can be used to execute a fail condition for a workflow.

The workflow may look something like this:
![all_failed](https://assets.astronomer.io/website/img/guides/trigger_notification_fail.png)

**Note:** The final task was set to `skipped`

Once again, the same functionality can be achieved by using the `PythonBranchOperator`, a `TriggerDagOperator`,  or just configuring reporting in moore specific way.

### Triggers with LatestOnlyOperator

When scheduling tasks with complex trigger rules with dates in the past, there may be instances where certain tasks can run independently of time and others shouldn't.

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
 