---
title: "Trigger DAGs in Airflow"
description: "How to use DAGs to trigger secondary DAG kickoffs in Airflow."
date: 2018-05-23T00:00:00.000Z
slug: "trigger-dag-operator"
heroImagePath: "https://assets.astronomer.io/website/img/guides/trigger.png"
tags: ["Templating", "Best Practices", "Basics"]
---

As workflows are being developed and built upon by different team members, they tend to get more complex.

The first level of complexity can usually be handled by some sort of error messaging - throw an error notification to a particular person or group based on a workflow's failure.

Branching can be helpful for performing conditional logic - execute a set of tasks based off of a condition. For situations where that is not enough - **The TriggerDagRunOperator can be used to kick off entire DAGs.**

`https://github.com/apache/incubator-airflow/blob/master/airflow/operators/dagrun_operator.py`

## Define a controller and a target  DAG

The TriggerDagRunOperator needs a controller - a task that decides the outcome based on some condition, and a target, a DAG that is kicked off or not depending on the condition.

The controller task takes the form a python callable:

```python
def conditionally_trigger(context, dag_run_obj):
    """
    This function decides whether or not to Trigger the remote DAG
    """
    rand = random.randint(0, 1)

    dag_run_obj.payload = {'message': '{0} was chosen'.format(rand)}
    pp.pprint(dag_run_obj.payload)

    if rand == 1:
        return dag_run_obj
```

If the `dag_run_obj` is returned, the target DAG can will be triggered. The `dag_run_obj` can also be passed with context parameters.

```python
def target_function(**kwargs):
    print("Remotely received value of {} for key=message".
          format(kwargs['dag_run'].conf['message']))
```

The `target` DAG should always be set to `None` for its schedule - the DAG should only be triggered by an external condition.

## Use Cases

Trigger DAGs are a great way to separate the logic between a "safety check" and the logic to execute in case those checks aren't accomplished.

These sorts of checks are a good fail safe to add to the end of a workflow, downstream of the data ingestion layer.

On the same note, they can be used to monitor Airflow itself.

## Metadata Trigger DAGs

Error notifications can be set through various levels through a DAG, but propagating whose  between different DAGs can valuable for other reasons. Suppose that after 5  DAG failures, you wanted to trigger a systems check

### Sensors and TriggerDAGs

#### Airflow on Airflow

As Airflow operations are being scaled up, error reporting gets increasingly difficult. The more failure emails that are being sent out, the less each notification matters. Furthermore, a certain threshold of failures could indicate a deeper issue in another system.

Using a Sensor and TriggerDag can provide a clean solution to this issue,

#### Checking the database for a threshold of failures

#### DagFailureSensor

A sensor can be used to check the metadatabase for the status of DagRuns. If the number of failed runs is above a certain threshold (different for each DAG), the next task can trigger a systems check DAG.

```json
checks = [
    {'dag_name': 'example_dag',
     'lookback_days': 5,
     'threshold': 3,
     'poke_interval': 200},

    {'dag_name': 'dag_one',
     'lookback_days': 2,
     'threshold': 1,
     'poke_interval': 100},

    {'dag_name': 'dag_two',
     'lookback_days': 3,
     'threshold': 4,
     'poke_interval': 50}
]
```

The sensor can then be implemented as such:

```python
for check in checks:
    sensor = DagFailureSensor(task_id='sensor_task_{0}'
                                  .format(check['dag_name']),
                                  dag_name=check['dag_name'],
                                  initial_date='{{ ts }}',
                                  lookback_days=check['lookback_days'],
                                  threshold=check['threshold'],
                                  poke_interval=check['poke_interval']
                                  )
    trigger = TriggerDagRunOperator(task_id='trigger_systems_check_{0}'
                                        .format(check['dag_name']),
                                        trigger_dag_id=check['trigger_dag_target'],
                                        python_callable=trigger_sys_dag)
    first_task >> sensor >> trigger
```

![system_check_controller](https://assets.astronomer.io/website/img/guides/system_check_controller.png)

#### Adding Trigger Rules

Depending on the rest of the infrastructure, different "checks" may all trigger the same system level check.

If that is the case, TriggerDagOperators should be set with a different `trigger_rule`

```python
with dag:
    first_task = DummyOperator(task_id='last_task')

    trigger = TriggerDagRunOperator(task_id='trigger_systems_check',
                                    trigger_dag_id='total_system_check',
                                    python_callable=trigger_sys_dag,
                                    trigger_rule=TriggerRule.ONE_SUCCESS)

    for check in checks:

        sensor = DagFailureSensor(task_id='sensor_task_{0}'
                                  .format(check['dag_name']),
                                  dag_name=check['dag_name'],
                                  initial_date='{{ ts }}',
                                  lookback_days=check['lookback_days'],
                                  threshold=check['threshold'],
                                  poke_interval=check['poke_interval']
                                  )

        first_task >> sensor >> trigger
```

![system_check_controller](https://assets.astronomer.io/website/img/guides/trigger_rule_sensor_dag.png)
